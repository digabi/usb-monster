# Write dd image to USB media

`write_dd.sh`
 * Calculates a MD5 sum for the given dd image file and stores it to same directory with the image
 * Writes given dd image to all USB media
 * Clears file cache from RAM
 * Verifies the dd image from the USB media to the calculated MD5

These actions are carried out to all detected usb devices which do not have
any mounted filesystems.

## Usage

 1. Disable automount etc.
 2. Execute as root (`bash write_dd.sh path/to_image.dd`)
 3. If the failing device(s) is reported
    after the writing process. Removing sticks one by one tells you when you have removed a failed device
    as the device path is removed from the list if (failed) devices.
 
## Requires

dd, md5sum, head, zenity.

Must be executed as superuser.

