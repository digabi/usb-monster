# Arch Linux

The scripts in this directory set up usb-monster for Arch Linux Live image
(https://www.archlinux.org/download/). The scripts have been tested with `2016.03.01`.

You may want to use Arch instead of Debian/Ubuntu as it offers the latest
kernel which results better USB performance.

## Usage

Get and execute script:

	# wget -O - https://raw.githubusercontent.com/digabi/usb-monster/master/env_arch/setenv.sh | bash
	# cd /mnt/home/usb   \[OR\]   cd /mnt/home/ytl

List audio devices:

	# pactl list sinks
	
	Sink #0
	State: SUSPENDED
	Name: alsa_output.pci-0000_00_05.0.analog-stereo
	Description: Built-in Audio Analog Stereo
	...more output...
	
	Sink #1
	...even more output...

Select the desired device by giving sink number (Sink #NNN) as a parameter:

	sh usb-monster/env_arch/setsink.sh N

Writing the sticks

	./write_dd.sh yo.../koe.dd

The setup script (`setenv.sh`) has installed iostat for you. Select second
virtual terminal and execute

	# cd /mnt/home/usb   \[OR\]   cd /mnt/home/ytl
	# sh usb-monster/env_arch/iostat.sh
