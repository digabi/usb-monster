#!/bin/sh

# Sets burning environment ready after the workstation has been
# booted to Arch Linux live USB.
# 1. Connect the burning machine to Internet.
# 2. Boot
# 3. wget -O - https://raw.githubusercontent.com/digabi/usb-monster/master/env_arch/setenv.sh | bash
# 
# The script expects that your hard disk (/dev/sda1 or /dev/sda5) has
# a ext4 filesystem with images and other tools located at /home/usb or /home/ytl.
#

# Remount root with more space
mount -o remount,size=2G /run/archiso/cowspace

# Set keymap
loadkeys /usr/share/kbd/keymaps/i386/qwerty/fi.map.gz

# Try mounting hard disk and hope that you'll find something
umount /mnt
mount /dev/sda1 /mnt
mount /dev/sda5 /mnt

if [ ! -d /mnt/home ]; then
	echo "Failed to mount hard disk"
	exit 1
fi

# Find home dir
if [ -d /mnt/home/usb ]; then
	BURNHOME=/mnt/home/usb
elif [ -d /mnt/home/ytl ]; then
	BURNHOME=/mnt/home/ytl
else
	echo "Failed to find home directory"
	exit 1
fi

# Install required software
pacman -Syy
pacman --noconfirm -S sysstat
pacman --noconfirm -S alsa-utils
pacman --noconfirm -S git

# Unmute sound
amixer sset Master unmute

# Delete existing burning code and get a fresh one
cd ${BURNHOME}
rm -fR usb-monster
git clone https://github.com/digabi/usb-monster.git
