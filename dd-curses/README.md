# Write dd image to USB media (curses version)

`write_dd.sh`
 * Calculates a MD5 sum for the given dd image file and stores it to same directory with the image
 * Writes given dd image to all USB media
 * Verifies the dd image from the USB media to the calculated MD5

These actions are carried out to all detected usb devices which do not have
any mounted filesystems.

## Usage

 1. Disable automount etc.
 2. Execute as root (`python2 write_dd.sh path/to_image.dd`)
 3. If the failing device(s) is reported
    after the writing process. Removing sticks one by one tells you when you have removed a failed device
    as the device path is removed from the list if (failed) devices.

## Requirements

dd, md5sum, head, python 2.7, readlink, python `psutil`

Must be executed as superuser.

Required packages:
 * Arch Linux: alsa-utils, pv, python2, python2-psutil
 * Debian Jessie: coreutils, alsa-utils, pv, python2.7-minimal, python-psutil

## Documentation specific to MEB copyers

`meb_docs` contains documentation related to copying workstations used by MEB.

 * Mapping between USB IDs and hubs/ports (xlsx file)
 * Connecting USB hubs to copying workstations in a way that the mapping is valid (pptx file)
