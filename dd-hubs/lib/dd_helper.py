# -*- coding: utf-8 -*-

# This class takes care of writing image to single device

import subprocess, signal, select, re, fcntl, os, hashlib

class dd_helper (object):
	def __init__ (self):
		self.DD_BLOCK_SIZE="1M"
		self.STATUS_CODE_LEGEND = ['-', 'writing', 'verifying', 'finished', 'error', 'failed']
		self.RE_OUTPUT = {
			'megs': '([\d,]+..?)',
			'eta': 'ETA (\d+\:\d+\:\d+)',
			'speed': '\[\s*([\d,]+.+?\/s)\]',
			'percent': '(\d+)%',
			'md5sum': '^([0-9a-f]+) '
		}

		# Use this dictionary to create disk errors (write other image to certain devices), see write_image()
		#self.ALTERNATIVE_IMAGE = { '/dev/sdc': 'dd_writer.py' }

		self.image_file = None
		self.device_file = None
		self.dd_image_size = None
		self.dd_image_md5 = None

		self.usbhub_coords = None

		self.status_code = 0
		self.dd_handle = None

		self.dd_operation = ""	# Meaningful values are 'write', 'verify'
		self.dd_previous_status = ""
		self.dd_previous_stdout = ""


		self.MD5EXT = '.md5'

	def update_write_status(self):
		if self.dd_handle == None:
			return self.status_code

		retcode = self.dd_handle.poll()

		if retcode == None:
			# Still writing/verifying
			if self.dd_operation == "write":
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

	def set_usbhub_coords (self, new_coords):
		self.usbhub_coords = new_coords

	def get_usbhub_coords (self):
		return self.usbhub_coords
		
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
		dd_params = ['/bin/sh', '-c', 'dd if=%s bs=10240 | pv -f -s %d -B 10240 | dd of=%s bs=10240' % (file_path, self.dd_image_size, self.device_file) ]
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
		dd_params = ['/bin/sh', '-c', 'dd if=%s bs=10240 | head -c %d | pv -f -s %d | md5sum' % (diskname, self.dd_image_size, self.dd_image_size) ]
		self.dd_handle = subprocess.Popen(dd_params, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
