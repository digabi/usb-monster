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

DD_IMAGE=$1
if [ ${DD_IMAGE} == "" ]; then
	echo "usage: $0 path_to_dd_image"
	exit 1
fi

if [ ! -f ${DD_IMAGE} ]; then
	echo "$0: dd image file ${DD_IMAGE} not found."
	exit 1
fi

# Calculate MD5sum (if not already there)
if [ ! -f ${DD_IMAGE}.md5 ]; then
	echo -n "Calculating MD5 sum..."
	md5sum ${DD_IMAGE} >${DD_IMAGE}.md5
	echo "OK"
fi

# Get file size & MD5
DD_IMAGE_SIZE=$(stat -c%s "${DD_IMAGE}")
DD_IMAGE_MD5=$(cut --delimiter=' ' -f 1 <${DD_IMAGE}.md5)

# Create temporary directory for verify statuses
TMPDIR=$(mktemp -d)

enum_usbs
echo "USBs: ${USBS}"

# Write dd image to all USB disks

echo -n "Starting write: "
for THIS_USB in ${USBS}; do
	echo -n "${THIS_USB} "
	( dd if=${DD_IMAGE} of=${THIS_USB} bs=${DD_IMAGE_SIZE} >/dev/null 2>/dev/null ) &
done
echo ""

echo -n "Waiting for dd write processes to terminate..."
wait
sleep ${SLEEP_BETWEEN}
echo "OK"

# Drop memory cache
echo -n "Clear memory cache..."
sync
echo 3 > /proc/sys/vm/drop_caches
echo "OK"

# Verify drives

echo -n "Starting to verify: ${THIS_USB}"
for THIS_USB in ${USBS}; do
	echo -n "${THIS_USB} "
	BASE=`basename ${THIS_USB}`
	( dd if=${THIS_USB} count=1 bs=${DD_IMAGE_SIZE} 2>/dev/null | md5sum >${TMPDIR}/${BASE} ) &
done
echo ""

echo -n "Waiting for verify processes to terminate..."
wait
sleep ${SLEEP_BETWEEN}
echo "OK"

# Look for probably defected drives

while [ ${#USBS} -gt 1 ]; do

	enum_usbs
	
	for THIS_USB in ${USBS}; do
		BASE=`basename ${THIS_USB}`
		THIS_MD5=`cut --delimiter=' ' -f 1 <${TMPDIR}/${BASE}`
		if [ "${DD_IMAGE_MD5}" != "${THIS_MD5}" ]; then
			echo "Verify failed: ${THIS_USB}"
		fi
	done

	echo "------------"
done

rm -fR ${TMPDIR}
