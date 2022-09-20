#!/usr/bin/python3
# -*- coding: utf-8 -*-

import subprocess, signal, select, stat, re, fcntl, os, hashlib, time, psutil, stat

class dd_writer (object):
	def __init__ (self, temp_file_uid = None):
		# Large block size (5 Mb) works at least with small number of USB sticks
		self.DD_BLOCK_SIZE="5242880"
		self.STATUS_CODE_LEGEND = ['-', 'writing', 'verifying', 'finished', 'error', 'failed', 'timeout', '(timeout)', 'slow', '(slow)']
		self.RE_OUTPUT = { 'bytes_transferred': '(\d+)', 'md5sum': '([0-9a-f]{32}) ' }
		# Write timeout in seconds to cause status "timeout"
		self.TIMEOUT = 20
		# Raise "slow" flag if average speed bytes/second is less than this
		self.SLOW = 1*1024*1024 # 1 MiB/s
		# Debug environment variable name, see write_debug()
		self.DEBUG_ENVIRONMENT_VAR = 'USB_MONSTER_DD_WRITER_DEBUG'
		# Debug filename, see write_debug()
		self.DEBUG_FILE_PATH = '/tmp/dd_writer_debug.txt'

		# Use this dictionary to create disk errors (write other image to certain devices), see write_image()
		#self.ALTERNATIVE_IMAGE = { '/dev/sdc': 'dd_writer.py' }

		self.temp_file_uid = temp_file_uid

		self.image_file = None
		self.device_file = None
		self.verify_image = True
		self.dd_image_size = None
		self.dd_image_md5 = None

		self.status_code = 0
		self.dd_handle = None

		self.dd_operation = ""	# Meaningful values are 'write', 'verify'
		self.dd_previous_status = ""
		self.dd_previous_stdout = ""

		self.timeout_lastchange = None
		self.timeout_last_write_count = None

		self.slow_transfer_started = None
		self.slow_bytestransferred = None
		self.slow_bytestransferred_timestamp = None

		self.MD5EXT = '.md5'

	def write_debug(self, debug_arguments):
		debug_setting = False
		try:
			debug_setting = os.environ[self.DEBUG_ENVIRONMENT_VAR]
		except KeyError:
			pass

		if debug_setting:
			f = open(self.DEBUG_FILE_PATH, "a")
			f.write(str(debug_arguments))
			f.write("\n")
			f.close()

	def set_verify(self, new_verify_image_value):
		self.verify_image = new_verify_image_value

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

		# If we are in slow mode check if device still exists
		if self.status_code == 8:
			if not self.device_present():
				self.status_code = 9
			return self.status_code

		# Return "resolved slow" here
		if self.status_code == 9:
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
				elif self.if_slow():
					self.status_code = 8
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
				# Write finished
				if self.verify_image:
					# Start verify
					self.check_md5(self.image_file, self.device_file)
					self.status_code = 2
				else:
					# Verify is disabled - finish write
					self.dd_handle = None
					self.dd_operation = "verify"
					self.status_code = 3
			elif self.dd_operation == "verify":
				# Verify finished, check MD5

				# Read last message (should be MD5sum)
				self.get_dd_status()

				if self.dd_previous_stdout != None:
					if self.dd_previous_stdout == self.dd_image_md5:
						self.write_debug(['verify ok', self.dd_previous_stdout, self.dd_image_md5])
						# Verify ok, finished
						self.status_code = 3
					else:
						self.write_debug(['verify failed', self.dd_previous_stdout, self.dd_image_md5])
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

	def if_slow (self):
		avg_speed = self.get_transfer_speed()
		if (avg_speed > 0) and (avg_speed < self.SLOW):
			return True

		# This is not a slow device
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
			self.write_debug(['exctract_dd_data', this_re, self.RE_OUTPUT[this_re], output])
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

		if (data['bytes_transferred'] != ""):
			try:
				int_bytes_transferred= int(data['bytes_transferred'])
			except:
				int_bytes_transferred = 0

			avg_speed = self.get_transfer_speed(int_bytes_transferred)
			perc_done = self.get_transfer_percent()

			str_bytes_transferred = self.sizeof_fmt(int_bytes_transferred)
			str_avg_speed = self.sizeof_fmt(avg_speed)

			self.dd_previous_status = "%s (%5.1f%%) %s/s" % (str_bytes_transferred.rjust(9), perc_done, str_avg_speed.rjust(8))

		return self.dd_previous_status

	def set_bytes_transferred(self, bytes_transferred = None):
		if bytes_transferred != None:
			if (self.slow_transfer_started == None) or (bytes_transferred < self.slow_bytestransferred):
				self.slow_transfer_started = time.time()

			self.slow_bytestransferred_timestamp = time.time()
			self.slow_bytestransferred = bytes_transferred

	def get_transfer_speed(self, bytes_transferred = None):
		self.set_bytes_transferred(bytes_transferred)

		if (self.slow_transfer_started == None):
			# We haven't been initialised yet, return zero
			return 0

		secs_passed = self.slow_bytestransferred_timestamp - self.slow_transfer_started
		if (secs_passed < 5):
			# Don't report avg speed too early, only after 5 seconds
			return 0

		# Calculate average speed
		avg_speed = 0

		try:
			avg_speed = self.slow_bytestransferred / secs_passed
		except ZeroDivisionError:
			pass

		return avg_speed

	def get_transfer_percent(self, bytes_transferred = None):
		self.set_bytes_transferred(bytes_transferred)

		if (self.slow_bytestransferred == None) or (self.dd_image_size == None):
			return 0

		return (self.slow_bytestransferred / float(self.dd_image_size)) * 100.0

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

		# Zero bytes processed
		self.set_bytes_transferred(0)

		self.dd_operation = "write"
		dd_params = ['/bin/sh', '-c', 'dd if=%s bs=%s | pv -n -b | dd of=%s bs=%s oflag=dsync' % (file_path, self.DD_BLOCK_SIZE, self.device_file, self.DD_BLOCK_SIZE) ]
		self.write_debug(['writing', dd_params])
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

		if self.temp_file_uid is not None:
			try:
				os.chmod(md5_filename, stat.S_IRUSR | stat.S_IWUSR)
			except Exception as e:
				self.write_debug(["Error: Could not change MD5 file permissions", md5_filename, str(e)])

			try:
				os.chown(md5_filename, self.temp_file_uid, -1)
			except Exception as e:
				self.write_debug(["Error: Could not change MD5 file owner", md5_filename, str(e)])

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

		# Zero bytes processed
		self.set_bytes_transferred(0)

		self.dd_operation = "verify"
		dd_params = ['/bin/sh', '-c', 'dd if=%s bs=%s | head -c %d | pv -n -b | md5sum' % (diskname, self.DD_BLOCK_SIZE, self.dd_image_size) ]
		self.write_debug(['verifying', dd_params])
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
			try:
				dd_children = psutil.Process(self.dd_handle.pid).children()
			except:
				dd_children = None

			if dd_children != None:
				for this_child in dd_children:
					try:
						this_child.terminate()
					except:
						pass

			try:
				self.dd_handle.terminate()
			except:
				pass

	def reset_device (self):
		dev_re = re.match("/(sd.+)", self.device_file)
		if dev_re != None:
			device_file_short = dev_re.match(1)

			text_file = open("/sys/block/%s/device/delete" % (device_file_short), "w")
			text_file.write("1\n")
			text_file.close()

	def sizeof_fmt(self, num, suffix='B'):
		for unit in ['','Ki','Mi','Gi','Ti','Pi','Ei','Zi']:
			if abs(num) < 1024.0:
				return "%3.1f%s%s" % (num, unit, suffix)
			num /= 1024.0
		return "%.1f%s%s" % (num, 'Yi', suffix)
