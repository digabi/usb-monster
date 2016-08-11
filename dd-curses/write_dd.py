#!/usr/bin/python2
# -*- coding: utf-8 -*-

import curses, re, sys, os, time, shlex, subprocess
from dd_writer import dd_writer

COL_USBID = 1
COL_DEVPATH = 15
COL_STATUS = 25
COL_WRITE = 35

AUDIO_OK = "ok.wav"
AUDIO_ERROR = "error.wav"

# See get_usb_path(), this is a global cache variable
USB_PATH_CACHE = {}

def my_exit (code, message):
	screen.clear()
	curses.flash()
	screen.addstr(1,1,message, curses.A_BOLD)
	screen.addstr(3,1,"Press SPACE to exit")
	screen.refresh()
	
	while screen.getch() != ord(' '):
		screen.refresh()
		
	curses.endwin()
	sys.exit(code)

def my_log (message):
	f = open("/tmp/write_dd_debug.log", "a")
	f.write(message+"\n")
	f.close()

def is_readable (path):
	return os.access(path, os.R_OK)

def play_file (filepath):
	null_file = open("/dev/null", "w")
	subprocess.Popen(shlex.split("aplay %s" % filepath), stdout=null_file, stderr=null_file)
	
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
		
	output_tuplet = subprocess.Popen(shlex.split("udevadm info %s" % device), stdout=subprocess.PIPE).communicate()
	output = str(output_tuplet[0])
	re_result = re.search(r'ID_PATH=.+\-usb-(.+?)-', output)
	if re_result:
		USB_PATH_CACHE[device] = re_result.group(1)
		return re_result.group(1)
	
	return None

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

def update_writer_status (my_writers, current_usbs = None):
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
		item = (this_device, get_usb_path(this_device))
		writer_ids.append(item)
	
	for this_device_tuple in sorted(writer_ids, key=lambda device: device[1]):
		this_device = this_device_tuple[0]
		this_usb_path = this_device_tuple[1]
		this_writer = my_writers[this_device]
		
		status = this_writer.update_write_status()
		
		writer_count += 1
		
		# Get coordinates for status row
		writer_coords = get_writer_status_coords(writer_count)
		
		screen.addstr(writer_coords['y'], writer_coords['x']+COL_USBID, this_usb_path)
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
	
# Main program
screen = curses.initscr()
screen.clear()

# Check parameter
try:
	image_file = sys.argv[1]
except:
	my_exit(1, "You have to give image file as the only parameter")

if not is_readable(image_file):
	my_exit(1, "File %s is not readable")
	
# FIXME: Check that image_file exists, is readable etc.
screen.addstr(0, 1, "Image file: %s" % image_file, curses.A_DIM)
	
# Create writers
while True:
	# Find all USB disks which are not mounted
	update_message("Searching for USB devices...")
	all_usbs = enum_usbs()
	
	# Show number of usb devices
	winsize = screen.getmaxyx()
	screen.addstr(0, winsize[1]-4, "% 3d" % len(all_usbs))
	
	screen.move(2,1)
	screen.clrtobot()

	writers = {}
	update_message("Creating writers...")
	for this_usb in all_usbs:
		# Create writers for all USB devices
		writers[this_usb] = dd_writer()

	# Update screen
	update_writer_status(writers)
	
	update_message("Press X to exit, Enter to write, any other to rescan USBs...")
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
while update_writer_status(writers) > 0:
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

	status_now = update_writer_status(writers, now_usbs)
	
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

