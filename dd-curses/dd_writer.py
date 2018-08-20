# -*- coding: utf-8 -*-

import subprocess, signal, select, re, fcntl, os, hashlib, time, psutil, stat

class dd_writer (object):
	def __init__ (self):
		self.DD_BLOCK_SIZE="10240"
		self.STATUS_CODE_LEGEND = ['-', 'writing', 'verifying', 'finished', 'error', 'failed', 'timeout', '(timeout)']
		self.RE_OUTPUT = { 'megs': '([\d,]+..?)', 'eta': 'ETA (\d+\:\d+\:\d+)', 'speed': '\[([\d,]+..?\/s)', 'percent': '(\d+)%', 'md5sum': '^([0-9a-f]+) ' }
		# Write timeout in seconds to cause status "timeout"
		self.TIMEOUT = 20

		# Use this dictionary to create disk errors (write other image to certain devices), see write_image()
		#self.ALTERNATIVE_IMAGE = { '/dev/sdc': 'dd_writer.py' }

		self.image_file = None
		self.device_file = None
		self.dd_image_size = None
		self.dd_image_md5 = None

		self.status_code = 0
		self.dd_handle = None

		self.dd_operation = ""	# Meaningful values are 'write', 'verify'
		self.dd_previous_status = ""
		self.dd_previous_stdout = ""

		self.timeout_lastchange = None
		self.timeout_last_write_count = None

		self.MD5EXT = '.md5'

	def update_write_status(self, write_count):
		if self.dd_handle == None:
			return self.status_code

		# If we are in timeout mode check if device still exists
		if self.status_code == 6:
			if not self.device_present():
				self.status_code = 7
			return self.status_code

		# Return "resolved timeout" here
		if self.status_code == 7:
			return self.status_code

		retcode = self.dd_handle.poll()

		if retcode == None:
			# Still writing/verifying
			if self.dd_operation == "write":
				if self.if_timeout(write_count):
					self.status_code = 6
					# Reset device
					self.reset_device()
					# Kill writer process
					self.kill_dd()
				else:
					self.status_code = 1
			if self.dd_operation == "verify":
				self.status_code = 2
		elif retcode < 0:
			# Error
			self.status_code = 4
			self.dd_handle = None
		else:
			# Finished
			self.status_code = 4
			if self.dd_operation == "write":
				# Write finished, now start verify
				self.check_md5(self.image_file, self.device_file)
				self.status_code = 2
			elif self.dd_operation == "verify":
				# Verify finished, check MD5

				# Read last message (should be MD5sum)
				self.get_dd_status()

				if self.dd_previous_stdout != None:
					if self.dd_previous_stdout == self.dd_image_md5:
						# Verify ok, finished
						self.status_code = 3
					else:
						# Verify error
						self.status_code = 5
				else:
					# Did not get any stdout, return error
					self.status_code = 4

				self.dd_handle = None

		return self.status_code

	def if_timeout (self, current_write_count):
		if self.timeout_lastchange == None:
			# This is the first entry
			self.timeout_lastchange = time.time()
			self.timeout_last_write_count = current_write_count

			return False

		if current_write_count != self.timeout_last_write_count:
			# Write count has changed
			self.timeout_lastchange = time.time()
			self.timeout_last_write_count = current_write_count

			return False

		secs_since_lastchange = time.time() - self.timeout_lastchange

		if secs_since_lastchange > self.TIMEOUT:
			# Too long time has passed since last change
			return True

		# We haven't reached the timeout
		return False

	def non_block_read(self, output):
		''' even in a thread, a normal read with block until the buffer is full '''
		fd = output.fileno()
		fl = fcntl.fcntl(fd, fcntl.F_GETFL)
		fcntl.fcntl(fd, fcntl.F_SETFL, fl | os.O_NONBLOCK)
		try:
			return str(output.read())
		except:
			return str('')

	def extract_dd_data (self, output):
		result_dict = {}

		for this_re in self.RE_OUTPUT.keys():
			result_dict[this_re] = ""
			re_result = re.search(self.RE_OUTPUT[this_re], output)
			if re_result:
				result_dict[this_re] = re_result.group(1)

		return result_dict

	def get_dd_status(self):
		if self.dd_handle == None:
			return "-"

		# Read stdout_line
		stdout_line = self.non_block_read(self.dd_handle.stdout)
		if (stdout_line != ""):
			# Try to get MD5sum
			stdout_data = self.extract_dd_data(stdout_line)
			if stdout_data['md5sum'] != "":
				self.dd_previous_stdout = stdout_data['md5sum']
			else:
				self.dd_previous_stdout = stdout_line

		# Read stderr_line
		stderr_line = self.non_block_read(self.dd_handle.stderr)

		data = self.extract_dd_data(stderr_line)

		if (data['megs'] != ""):
			self.dd_previous_status = "%s (%s%%) ETA: %s Speed: %s" % (data['megs'], data['percent'], data['eta'], data['speed'])

		return self.dd_previous_status

	def update_write_status_str(self, status_code = None):
		if status_code == None:
			self.update_write_status()
			status_code = self.status_code

		return self.STATUS_CODE_LEGEND[status_code]

	def set_image_size(self, file_path):
		file_data = os.stat(file_path)
		self.dd_image_size = file_data.st_size

	## Fuctions related to image writing

	def write_image (self, file_path, disk_path):
		self.image_file = file_path
		self.device_file = disk_path

		# Do we have alternative image for this?
		try:
			file_path = self.ALTERNATIVE_IMAGE[disk_path]
		except:
			pass

		# Get image file size
		self.set_image_size(file_path)

		self.dd_operation = "write"
		dd_params = ['/bin/sh', '-c', 'dd if=%s bs=%s | pv -f -s %d -B %s | dd of=%s bs=%s' % (file_path, self.DD_BLOCK_SIZE, self.dd_image_size, self.DD_BLOCK_SIZE, self.device_file, self.DD_BLOCK_SIZE) ]
		self.dd_handle = subprocess.Popen(dd_params, stdout=subprocess.PIPE, stderr=subprocess.PIPE)


	## Functions related to MD5 calculation

	def read_md5_file (self, filename):
		md5_filename = "%s%s" % (filename, self.MD5EXT)

		if (os.access(md5_filename, os.F_OK)):
			f = open(md5_filename, "r")
			file_md5 = f.readline().rstrip()
			f.close()

			md5_re = re.search(r'^([0-9a-f]+) ', file_md5)
			if md5_re:
				file_md5 = md5_re.group(1)

			return file_md5

		return None

	def write_md5_file (self, filename, md5str):
		md5_filename = "%s%s" % (filename, self.MD5EXT)

		f = open(md5_filename, "w")
		f.write("%s\n" % md5str)
		f.close()

	def calculate_md5(self, filename, blocksize=2**20):
		m = hashlib.md5()
		with open(filename , "rb" ) as f:
			while True:
				buf = f.read(blocksize)
				if not buf:
					break
				m.update( buf )
		return m.hexdigest()

	def check_md5(self, filename, diskname):
		# Get MD5 of the filename
		self.dd_image_md5 = self.read_md5_file(filename)
		if self.dd_image_md5 == None:
			self.dd_image_md5 = self.calculate_md5(filename)
			self.write_md5_file(filename, self.dd_image_md5)

		self.dd_operation = "verify"
		dd_params = ['/bin/sh', '-c', 'dd if=%s bs=%s | head -c %d | pv -f -s %d | md5sum' % (diskname, self.DD_BLOCK_SIZE, self.dd_image_size, self.dd_image_size) ]
		self.dd_handle = subprocess.Popen(dd_params, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

	## Miscellaneous helpers

	def device_present (self):
		# Returns TRUE if current device file is character device
		try:
			mode = os.stat(self.device_file).st_mode
		except OSError:
			return False

		return stat.S_ISBLK(mode)

	def kill_dd (self):
		if (self.dd_handle != None):
			dd_children = psutil.Process(self.dd_handle.pid).children()

			for this_child in dd_children:
				this_child.terminate()

			self.dd_handle.terminate()

	def reset_device (self):
		dev_re = re.match("/(sd.+)", self.device_file)
		if dev_re != None:
			device_file_short = dev_re.match(1)

			text_file = open("/sys/block/%s/device/delete" % (device_file_short), "w")
			text_file.write("1\n")
			text_file.close()
