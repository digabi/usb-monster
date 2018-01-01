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

COL_USBID = 1
COL_DEVPATH = 10
COL_STATUS = 22
COL_WRITE = 32

AUDIO_OK = "ok.wav"
AUDIO_ERROR = "error.wav"

# See get_usb_path(), this is a global cache variable
USB_PATH_CACHE = {}

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
		check_path = "/sys/block/%s/device" % this_blockdr
		try:
			blockdr_readlink_tuplet = subprocess.Popen(shlex.split("readlink -f %s" % check_path), stdout=subprocess.PIPE).communicate()
			blockdr_readlink = str(blockdr_readlink_tuplet[0]).rstrip()
		except:
			blockdr_readlink = None

		if blockdr_readlink != None and usb_re.search(blockdr_readlink):
			blockdr_devpath = "/dev/"+this_blockdr
			if not is_mounted(blockdr_devpath):
				usbs.append(blockdr_devpath)

	return usbs

def get_usb_path (device):
	if device in USB_PATH_CACHE:
		return USB_PATH_CACHE[device]

	re_devshort = re.search(r'\/([a-z]+)$', device)
	if re_devshort:
		devshort = re_devshort.group(1)
		output_tuplet = subprocess.Popen(["sh", "-c", 'ls -l /dev/disk/by-path/ | grep -E "%s$"' % devshort], stdout=subprocess.PIPE).communicate()
		line = str(output_tuplet[0].rstrip())

		re_devids = re.search(r'pci-\d+:([a-f0-9]+):.+usb-\d+:([\.\d]+):', line)
		if re_devids:
			devid = re_devids.group(1)+'/'+re_devids.group(2)
			USB_PATH_CACHE[device] = devid
			return devid

	return ""

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
		if len(current_usbs) > 0:
			update_message("To start USB mapping process please remove all USB sticks and press any key!")
			key = my_screen.getch()
		else:
			usbs_present = False

	curses.echo()
	hubs = int(get_input("Number of USB hubs in your setting:"))
	ports = int(get_input("Number of USB ports in each USB hub:"))

	new_mapping = []

	# Key input to non-blocking mode
	my_screen.timeout(0)
	curses.noecho()

	for this_hub in range(1,hubs+1):
		for this_port in range(1,ports+1):
			update_message("Insert USB to hub %d, port %d - SPACE: skip this, S: skip mapping, X: exit" % (this_hub, this_port))

			still_loop = True

			while still_loop:
				new_usbs = enum_usbs()
				added_usbs = list(set(new_usbs) - set(current_usbs))

				my_log("added_usbs")
				my_log(added_usbs)

				if len(added_usbs) == 0:
					# Check for space bar
					key = my_screen.getch()
					if key == ord(' '):
						my_log("Skipped mapping: %d:%d" % (this_hub, this_port))
						still_loop = False
						update_message("Skipping hub %d, port %d..." % (this_hub, this_port))
						time.sleep(2)
					elif key == ord('x') or key == ord('X'):
						my_exit(0, "User terminated while creating USB mapping")
					elif key == ord('s') or key == ord('S'):
						update_message("Skipping USB mapping, using an empty map")
						time.sleep(2)
						my_log("User skipped USB mapping, returns an empty map")
						return []
					else:
						time.sleep(0.5)
				elif len(added_usbs) == 1:
					# We have one USB added
					new_mapping.append([this_hub, this_port, get_usb_path(added_usbs[0])])
					my_log("New mapping: %d:%d %s" % (this_hub, this_port, get_usb_path(added_usbs[0])))
					current_usbs = new_usbs
					still_loop = False
				else:
					update_message("Please insert only one USB at a time!")

	curses.echo()

	return new_mapping

def update_writer_status (my_usb_mapper, my_writers, current_usbs = None):
	writer_count = 0
	still_working_count = 0
	current_usbs_count = {
		0: { 0:0, 1:0 },
		1: { 0:0, 1:0 },
		2: { 0:0, 1:0 },
		3: { 0:0, 1:0 },
		4: { 0:0, 1:0 },
		5: { 0:0, 1:0 }
	}

	writer_ids = []
	for this_device in my_writers:
		item = (this_device, my_usb_mapper.get_hub_coords_str(get_usb_path(this_device)))
		writer_ids.append(item)

	for this_device_tuple in sorted(writer_ids, key=lambda device: device[1]):
		this_device = this_device_tuple[0]
		this_usb_connector = this_device_tuple[1]
		this_writer = my_writers[this_device]

		status = this_writer.update_write_status()

		writer_count += 1

		# Get coordinates for status row
		writer_coords = get_writer_status_coords(writer_count)

		screen.addstr(writer_coords['y'], writer_coords['x']+COL_USBID, this_usb_connector)
		screen.clrtoeol()
		screen.addstr(writer_coords['y'], writer_coords['x']+COL_DEVPATH, this_device)
		screen.clrtoeol()
		screen.addstr(writer_coords['y'], writer_coords['x']+COL_STATUS, this_writer.update_write_status_str(status))
		screen.clrtoeol()

		if status == 1 or status == 2:
			# Now writing or verifying
			still_working_count += 1

			status_line = this_writer.get_dd_status()
			if status_line != None:
				screen.addstr(writer_coords['y'], writer_coords['x']+COL_WRITE, status_line)
		else:
			if current_usbs != None:
				if this_device in current_usbs:
					device_present = "PRESENT"
					current_usbs_count[status][1] += 1
				else:
					device_present = "-"
					current_usbs_count[status][0] += 1

				screen.addstr(writer_coords['y'], writer_coords['x']+COL_WRITE, device_present)

	screen.refresh()

	if current_usbs == None:
		return still_working_count
	else:
		return current_usbs_count

def update_message (new_message):
	screen.addstr(1, 1, new_message, curses.A_BOLD)
	screen.clrtoeol()
	screen.refresh()

def update_corner (new_message):
	winsize = screen.getmaxyx()
	screen.addstr(0, winsize[1]-len(new_message), new_message)
	screen.clrtoeol()
	screen.refresh()

def get_input (new_message):
	screen.addstr(1, 0, new_message, curses.A_BOLD)
	screen.clrtoeol()
	screen.refresh()

	str_input = screen.getstr(1, len(new_message)+2, 10)

	return str_input

# Main program
my_log("Started")

screen = curses.initscr()
screen.clear()
curses.echo()

# Check parameter
try:
	image_file = sys.argv[1]
except:
	my_exit(1, "You have to give image file as the only parameter")

if not is_readable(image_file):
	my_exit(1, "File %s is not readable")

screen.addstr(0, 0, "Image file: %s" % image_file, curses.A_DIM)
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

# Create writers
while True:
	# Find all USB disks which are not mounted
	update_message("Searching for USB devices...")
	all_usbs = enum_usbs()

	# Show number of usb devices
	update_corner("USBs: % 3d" % len(all_usbs))

	screen.move(2,1)
	screen.clrtobot()

	writers = {}
	update_message("Creating writers...")
	for this_usb in all_usbs:
		# Create writers for all USB devices
		writers[this_usb] = dd_helper()

	# Update screen
	update_writer_status(usb_mapper, writers)

	update_message("Press X to exit, Enter to write, any other to rescan USBs...")
	# Key input to blocking mode
	screen.timeout(-1)
	key = screen.getch()

	if key == ord('x') or key == ord('X'):
		my_exit(1, "Exiting by user request")
	elif key == 10:
		# Start writing
		break

# Start writing
update_message("Starting writers...")
for this_usb in all_usbs:
	writers[this_usb].write_image(image_file, this_usb)

update_message("Waiting writers to finish...")
while update_writer_status(usb_mapper, writers) > 0:
	time.sleep(1)

update_message("Done! You may now remove the USB memories. Press any key to exit.")

status_previous = None
stop_loop = False
screen.nodelay(1)
while not stop_loop:
	time.sleep(0.5)
	now_usbs = enum_usbs()

	winsize = screen.getmaxyx()
	screen.addstr(0, winsize[1]-4, "% 3d" % len(now_usbs))

	status_now = update_writer_status(usb_mapper, writers, now_usbs)

	if (status_previous and status_now[5][1] != status_previous[5][1]):
		# Removed USB with "failed" status
		play_file(AUDIO_ERROR)
		curses.flash()

	if (status_previous and status_now[4][1] != status_previous[4][1]):
		# Removed USB with "error" status
		play_file(AUDIO_ERROR)
		curses.flash()

	if (status_previous and status_now[3][1] != status_previous[3][1]):
		# Removed USB with "finished" status
		play_file(AUDIO_OK)

	status_previous = status_now

	key = screen.getch()
	if key > -1:
		stop_loop = True

screen.nodelay(0)


# Finish
curses.endwin()

my_log("Normal termination")
