# Write dd image to USB media (curses version)

This is the USB-monster used by Matriculation Examination Board to write
large amounts of USB sticks.

## Creating digabi-dd-curses.deb

To create a Debian installation package containing USB monster and its tools:
 * Install [fpm](https://fpm.readthedocs.io/en/latest/)
 * Execute `create-deb.sh` (e.g. `BUILD_NUMBER=71 ./create-deb.sh`)

## Highest Level: digabi-usb-monster

The package installs `digabi-usb-monster.desktop` which executes `digabi-usb-monster`. This asks image path file and executes `digabi-dd-curses` in `x-terminal-emulator` via `sudo`. The script tries different methods executing `sudo` to get superuser privileges.

Example:

`digabi-usb-monster`

## Low Level: digabi-dd-curses

`digabi-dd-curses` disables automount and Abitti-specific service `digabi-monitor-usb-errors` monitoring USB issues. It gets image file as a parameter.

Example:

`sudo ./digabi-dd-curses /path/to/image.dd`

## The Lowest Possbile Level: write_dd.py and dd_writer.py

`write_dd.py` is the Python 2 script which creates the neat ncurses UI and orchestrates the individual writers. Each write is executed as its own process by `dd_writer.py`. Before executing `write_dd` you should disable automount.

`write_dd.py`
 * Calculates a MD5 sum for the given dd image file and stores it to same directory with the image
 * Writes given dd image to all USB media
 * Verifies the dd image from the USB media to the calculated MD5
 * If you need some debugging set `USB_MONSTER_DD_WRITER_DEBUG=1`, e.g. `sudo -E ./write_dd.py /tmp/test-image.dd` (see `src/dd_writer.py` for details)

These actions are carried out to all detected USB devices which do not have
any mounted filesystems.

Example:

`sudo python3 ./write_dd.py /path/to/image.dd`

## Requirements

dd, md5sum, head, python 3, readlink, python `psutil`

Must be executed as superuser.

Required packages:
 * Debian Bullseye: coreutils, pv, python3, python3-psutil
