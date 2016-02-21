#!/bin/bash

SLEEP_BETWEEN=5

# Search all USB disks

function enum_usbs () {

USBS=""
for USBDISK in /sys/block/sd*; do
	USBDISK_READLINK=`readlink -f ${USBDISK}/device`

	if [[ $USBDISK_READLINK == *"usb"* ]]; then
		# This is USB drive
		DEV_USBDISK=`basename ${USBDISK}`
		DEV_USBDISK="/dev/${DEV_USBDISK}"
		if grep -qs "${DEV_USBDISK}" /proc/mounts; then
			# echo "Skipping mounted disk ${DEV_USBDISK}"
			NOP=1
		else
			USBS="${USBS} ${DEV_USBDISK}"
		fi
	fi
done
}

enum_usbs
echo "USBs: ${USBS}"

# Delete existing MBR from all USB disks

for THIS_USB in ${USBS}; do
	echo "Starting clear MBR: ${THIS_USB}"
	( dd bs=512 count=1 if=/dev/zero of=${THIS_USB} 2>/dev/null ) &
done

echo -n "Waiting clear MBR processes to terminate..."
wait
sleep ${SLEEP_BETWEEN}
echo "OK"

# Create partition table

for THIS_USB in ${USBS}; do
	echo "Starting create partition table: ${THIS_USB}"
	( parted -s ${THIS_USB} mklabel msdos >/dev/null 2>/dev/null ) &
done

echo -n "Waiting create partition table to terminate..."
wait
sleep ${SLEEP_BETWEEN}
echo "OK"

# Create partitions

for THIS_USB in ${USBS}; do
	echo "Starting create partition: ${THIS_USB}"
	#DISK_SIZE=`parted -s ${THIS_USB} print | awk '/^Disk/ {print $3}' | sed 's/[Mm] [Bb]//'`

	( parted -s ${THIS_USB} mkpart primary fat32 0 100% >/dev/null 2>/dev/null ) &
done

echo -n "Waiting create partition to terminate..."
wait
sleep ${SLEEP_BETWEEN}
echo "OK"

# Create filesystems for all USB disks
# For some not-so-obvious reason this must be done sequentially

#for THIS_USB in ${USBS}; do
#	echo "Create fs: ${THIS_USB}"
#	mkfs.vfat -n "YTL-SEN" ${THIS_USB}1 >/dev/null 2>/dev/null
#done

for THIS_USB in ${USBS}; do
	echo "Starting create fs: ${THIS_USB}"
	( mkfs.vfat -n "YTL-SEN" ${THIS_USB}1 >/dev/null 2>/dev/null ) &
done

echo -n "Waiting create fs to terminate..."
wait
sleep ${SLEEP_BETWEEN}
echo "OK"

# Mount, copy and unmount

for THIS_USB in ${USBS}; do
	echo "Starting copy process: ${THIS_USB}"
	THIS_TEMP=`mktemp -d`
	( mount ${THIS_USB}1 ${THIS_TEMP} && cp -r /home/digabi/Desktop/copy_files/* ${THIS_TEMP}/ && umount ${THIS_TEMP} && rmdir ${THIS_TEMP} ) &
done

echo -n "Waiting copy processes to terminate..."
wait
sleep ${SLEEP_BETWEEN}
echo "OK"

# Look for probably defected drives

while [ ${#USBS} -gt 1 ]; do

	enum_usbs

	echo "------------"

	for THIS_USB in ${USBS}; do
		if [ ! -b ${THIS_USB}1 ]; then
			echo "Error in device ${THIS_USB}"
		fi
	done

done

