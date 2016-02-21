# Create FAT-formatted USB sticks and copy files

`copy_files.sh`
 * erases existing partition table
 * creates a new partition table with single partition
 * creates a FAT32 filesystem to this partition
 * copies given files to this partition

These actions are carried out to all detected usb devices which do not have
any mounted filesystems.

Note: The script *does not* verify the copied files.

## Usage

 1. Disable automount etc.
 2. Create a directory `copy_files/` to your Desktop (i.e. `/home/user/Desktop/copy_files/` and place all
    directories and files to this directory)
 3. Insert USB media to the workstation.
 4. Execute `copy_files.sh`
 5. If the script gets an error (created partition is not a block device) the failing device(a) is reported
    after the writing process. Removing sticks one by one tells you when you have removed a failed device
    as the device path is removed from the list if (failed) devices.
 
