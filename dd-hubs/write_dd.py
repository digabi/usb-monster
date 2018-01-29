#!/usr/bin/python2
# -*- coding: utf-8 -*-

import curses, re, sys, os, time, shlex, subprocess, inspect, json
from os.path import expanduser

# Add subfolder "lib" to modules path
cmd_subfolder = os.path.realpath(os.path.abspath(os.path.join(os.path.split(inspect.getfile( inspect.currentframe() ))[0],"lib")))
if cmd_subfolder not in sys.path:
	sys.path.insert(0, cmd_subfolder)

from dd_helper import dd_helper
from usb_mapper import usb_mapper
from write_counter import write_counter
from usb_path_mapper import usb_path_mapper

COL_USBID = 1
COL_DEVPATH = 10
COL_STATUS = 22
COL_WRITE = 32

AUDIO_OK = "ok.wav"
AUDIO_ERROR = "error.wav"

# Path to usb-monster settings
SETTINGS_PATH = expanduser("~")+'/.config/usb-monster/'

def my_exit (code, message):
	my_log("Exited with code %d: %s" % (code, message))

	screen.clear()
	curses.flash()
	screen.addstr(1,0,message, curses.A_BOLD)
	screen.addstr(3,0,"Press SPACE to exit")
	screen.refresh()

	while screen.getch() != ord(' '):
		screen.refresh()

	curses.endwin()
	sys.exit(code)

def my_log (message):
	try:
		f = open("/tmp/write_dd_debug.log", "a")
		if type(message) is str:
			f.write(message+"\n")
		else:
			f.write(json.dumps(message)+"\n")
		f.close()
	except:
		pass

def is_readable (path):
	return os.access(path, os.R_OK)

def play_file (filepath):
	if is_readable(filepath):
		null_file = open("/dev/null", "w")
		try:
			subprocess.Popen(shlex.split("aplay %s" % filepath), stdout=null_file, stderr=null_file)
		except:
			# Failed to play tone (maybe there is no aplay): don't care
			pass

def is_mounted (path):
	f = open("/proc/mounts")
	lines = f.readlines()
	f.close()

	path_re = re.compile('^'+path)

	for this_line in lines:
		if path_re.search(this_line):
			return True

	return False

def enum_usbs ():
	# Return array of non-mounted usb devices
	usbs = []

	usb_re = re.compile('usb')

	for this_blockdr in os.listdir('/sys/block/'):
		check_path = os.path.realpath("/sys/block/%s/device" % this_blockdr)

		if check_path != None and usb_re.search(check_path):
			blockdr_devpath = "/dev/"+this_blockdr
			if not is_mounted(blockdr_devpath):
				usbs.append(blockdr_devpath)

	return usbs

def get_window_size_xy ():
	# Get screen size
	winsize = screen.getmaxyx()

	return { 'x': winsize[1], 'y': winsize[0] }

def get_writer_status_coords (writer_n):
	screen_size = get_window_size_xy()

	col_height = screen_size['y']-3
	col_width = screen_size['x']/2

	column = (writer_n-1) / col_height
	row = (writer_n-1) % col_height

	return { 'x': column * col_width, 'y': row+2 }

def get_new_mapping (my_screen):
	# Make sure there are no USBs present

	usbs_present = True

	while usbs_present:
		current_usbs = enum_usbs()
		update_corner(my_screen, "USBs: % 3d" % len(current_usbs))
		if len(current_usbs) > 0:
			update_message(my_screen, "To start USB mapping process please remove all USB sticks!")
			time.sleep(1)
		else:
			usbs_present = False

	curses.echo()
	hubs = int(get_input(my_screen, "Number of USB hubs in your setting:"))
	ports = int(get_input(my_screen, "Number of USB ports in each USB hub:"))

	# Create new USB path mapper object to resolve device paths to USB paths
	upm = usb_path_mapper()

	new_mapping = []

	# Key input to non-blocking mode
	my_screen.timeout(0)
	curses.noecho()

	for this_port in range(1,ports+1):
		for this_hub in range(1,hubs+1):
			update_message(my_screen, "Insert USB to hub %d, port %d - SPACE: skip this, S: skip mapping, X: exit" % (this_hub, this_port))

			still_loop = True

			while still_loop:
				new_usbs = enum_usbs()
				added_usbs = list(set(new_usbs) - set(current_usbs))

				if len(added_usbs) == 0:
					# Check for space bar
					key = my_screen.getch()
					if key == ord(' '):
						my_log("Skipped mapping: %d:%d" % (this_hub, this_port))
						still_loop = False
						update_message(my_screen, "Skipping hub %d, port %d..." % (this_hub, this_port))
						time.sleep(2)
					elif key == ord('x') or key == ord('X'):
						my_exit(0, "User terminated while creating USB mapping")
					elif key == ord('s') or key == ord('S'):
						update_message(my_screen, "Skipping USB mapping, using an empty map")
						time.sleep(2)
						my_log("User skipped USB mapping, returns an empty map")
						return []
					else:
						time.sleep(0.5)
				elif len(added_usbs) == 1:
					# We have one USB added
					curses.flash()
					new_mapping.append([this_hub, this_port, upm.get_usb_path(added_usbs[0])])
					my_log("New mapping: %d:%d %s" % (this_hub, this_port, upm.get_usb_path(added_usbs[0])))
					curses.flash()
					current_usbs = new_usbs
					still_loop = False
				else:
					update_message(my_screen, "Please insert only one USB at a time!")

	curses.echo()

	return new_mapping

def update_writer_status (screen, my_writers, max_coords, current_usbs = None):
	# Returns array of removed devices
	writer_count = 0

	removed_devices = []

	screen.addstr(2, 0, "")

	for this_hub in range(1,max_coords[0]+1):
		for this_port in range(1,max_coords[1]+1):
			# Get screen coordinates for status row
			writer_count += 1
			writer_coords = get_writer_status_coords(writer_count)

			coord_str = "%d : %d" % (this_hub, this_port)

			screen.addstr(writer_coords['y'], writer_coords['x']+COL_USBID, coord_str)
			screen.clrtoeol()

			for this_device in my_writers.iterkeys():
				this_writer = my_writers[this_device]
				if this_writer.get_usbhub_coords() == coord_str:
					# this_writer is at this_hub:this_port (coord_str)
					status = this_writer.update_write_status()

					screen.addstr(writer_coords['y'], writer_coords['x']+COL_DEVPATH, this_device)
					screen.clrtoeol()
					screen.addstr(writer_coords['y'], writer_coords['x']+COL_STATUS, this_writer.update_write_status_str(status))
					screen.clrtoeol()

					if status == 1 or status == 2:
						# Now writing (1) or verifying (2)
						status_line = this_writer.get_dd_status()
						if status_line != None:
							screen.addstr(writer_coords['y'], writer_coords['x']+COL_WRITE, status_line)
					elif status == 3 or status == 4 or status == 5:
						# Write finished as ok (3), error (4) or verify error (5)

						if current_usbs != None:
							if this_device in current_usbs:
								device_present = "PRESENT"
							else:
								device_present = "-"
								removed_devices.append({'device': this_device, 'status': status})

							if status == 3:
								screen.addstr(writer_coords['y'], writer_coords['x']+COL_WRITE, device_present, curses.color_pair(1))
							else:
								screen.addstr(writer_coords['y'], writer_coords['x']+COL_WRITE, device_present, curses.color_pair(2))

	screen.clrtobot()

	screen.refresh()

	return removed_devices

def writer_loop (my_screen, usb_mapper, write_counter, image_file):
	# Main writer loop - write USB memory sticks until stopped by pressing X

	# Create new USB path mapper object to resolve device paths to USB paths
	upm = usb_path_mapper()

	# This dictionary holds all writer objects
	writers = {}

	status_previous = None

	current_usbs = []
	curses.noecho()
	my_screen.timeout(0)

	screen.addstr(0, 0, "Image file: %s   %d" % (image_file, write_counter.read_counter(image_file)), curses.color_pair(3))

	update_message(my_screen, "Insert USB sticks to start write and remove them when finished, X to exit...")

	continue_writers = True
	while continue_writers:
		new_usbs = enum_usbs()
		update_corner(my_screen, "USBs: % 3d" % len(new_usbs))
		added_usbs = list(set(new_usbs) - set(current_usbs))

		# Create writers for all newly added USB sticks
		for this_usb in added_usbs:
			# Create writers for all USB devices
			usbcoords = usb_mapper.get_hub_coords_str(upm.get_usb_path(this_usb))
			my_log("Creating writer for device %s located at %s (%s)" % (this_usb, usbcoords, upm.get_usb_path(this_usb)))

			if not os.access(this_usb, os.W_OK):
				my_exit(1, "You don't have write access to %s. Are you sure you are root?" % this_usb)

			writers[this_usb] = dd_helper()
			writers[this_usb].set_usbhub_coords(usbcoords)
			writers[this_usb].write_image(image_file, this_usb)

		current_usbs = new_usbs

		key = screen.getch()
		if key == ord('x') or key == ord('X'):
			continue_writers = False

		# Check status
		removed_devices = update_writer_status(my_screen, writers, usb_mapper.get_max(), new_usbs)

		for this_removed_device in removed_devices:
			upm.changed(this_removed_device['device'])
			del writers[this_removed_device['device']]
			my_log("Removed %s with status %d" % (this_removed_device['device'], this_removed_device['status']))
			if this_removed_device['status'] == 3:
				play_file(AUDIO_OK)
				write_counter.add_counter_by_one(image_file)
				screen.addstr(0, 0, "Image file: %s   %d" % (image_file, write_counter.read_counter(image_file)), curses.color_pair(3))
			else:
				play_file(AUDIO_ERROR)
				curses.flash()

		time.sleep(0.3)

def update_message (screen, new_message):
	my_log("Message: %s" % new_message)
	screen.addstr(1, 0, new_message, curses.A_BOLD)
	screen.clrtoeol()
	screen.refresh()

def update_corner (screen, new_message):
	winsize = screen.getmaxyx()
	screen.addstr(0, winsize[1]-len(new_message), new_message)
	screen.refresh()

def get_input (screen, new_message):
	screen.addstr(1, 0, new_message, curses.A_BOLD)
	screen.clrtoeol()
	screen.refresh()

	str_input = screen.getstr(1, len(new_message)+2, 10)

	return str_input

# Main program
my_log("Started")

screen = curses.initscr()
screen.clear()

curses.start_color()
curses.echo()
curses.init_pair(1, curses.COLOR_GREEN, curses.COLOR_BLACK)
curses.init_pair(2, curses.COLOR_RED, curses.COLOR_BLACK)
curses.init_pair(3, curses.COLOR_YELLOW, curses.COLOR_BLACK)

# Check parameter
try:
	image_file = sys.argv[1]
except:
	my_exit(1, "You have to give image file as the only parameter")

if not is_readable(image_file):
	my_exit(1, "File %s is not readable")

my_log("Image file: %s" % image_file)

# Create or read existing USB mapping
usb_mapper = usb_mapper(SETTINGS_PATH)
if usb_mapper.if_config():
	my_log("Using old USB mapper data")
else:
	# Create new config for USB mapper
	my_log("Creating new USB mapper data")
	usb_mapper.set_config(get_new_mapping(screen))
	usb_mapper.write_config()

# Create counter
write_counter = write_counter(SETTINGS_PATH)

# Do writing
writer_loop(screen, usb_mapper, write_counter, image_file)

screen.nodelay(0)

# Finish
curses.endwin()

my_log("Normal termination")
