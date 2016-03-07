#!/bin/bash

LOG_FILE=~/write_dd.log
SLEEP_BETWEEN=5
DD_BLOCK_SIZE=1M

# Make errors to these devices to test error-checking
# Double-check that you're not using thes device paths as HD etc!
#TEST_DEVICES="/dev/sdd"
# Don't make any errors
TEST_DEVICES=

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
			write_message "[Skipping mounted USB disk ${DEV_USBDISK}] "
			NOP=1
		else
			USBS="${USBS} ${DEV_USBDISK}"
		fi
	fi
done
USBS_COUNT=`echo "${USBS}" | wc -w`
}

function write_message {
	NOW=`date`
	echo "${NOW} $1" >>${LOG_FILE}
	echo -n "$1"
}

function write_message_nl {
	write_message "$1"
	echo ""
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

write_message_nl "USBs: ${USBS} (${USBS_COUNT})"

if [ "${USBS_COUNT}" == "0" ]; then
	echo "$0: No writeable USB sticks found"
	exit 1
fi

# Write dd image to all USB disks

write_message "Starting write: "
UCOUNT=0
for THIS_USB in ${USBS}; do
	write_message "${THIS_USB} "
	( dd if=${DD_IMAGE} of=${THIS_USB} bs=${DD_BLOCK_SIZE} >/dev/null 2>/dev/null ) &
	let "UCOUNT = UCOUNT + 1"
done
write_message_nl "(${UCOUNT})"

write_message "Waiting for dd write processes to terminate..."
wait
sleep ${SLEEP_BETWEEN}
write_message_nl "OK"

# Drop memory cache
write_message "Clear memory cache..."
sync
echo 3 > /proc/sys/vm/drop_caches
write_message_nl "OK"

# Make errors

for THIS_USB in ${TEST_DEVICES}; do
	write_message "Creating errors to ${THIS_USB}..."
	dd if=/dev/random of=${THIS_USB} bs=${DD_BLOCK_SIZE} count=1 2>/dev/null
	write_message_nl "OK"
done

# Verify drives

write_message "Starting to verify: "
UCOUNT=0
for THIS_USB in ${USBS}; do
	write_message "${THIS_USB} "
	BASE=`basename ${THIS_USB}`
	( dd if=${THIS_USB} bs=${DD_BLOCK_SIZE} 2>/dev/null | head -c ${DD_IMAGE_SIZE} | md5sum >${TMPDIR}/${BASE} ) &
	let "UCOUNT = UCOUNT + 1"
done
write_message_nl "(${UCOUNT})"

write_message "Waiting for verify processes to terminate..."
wait
sleep ${SLEEP_BETWEEN}
write_message_nl "OK"

# Look for probably defected drives

write_message "Waiting the operator to remove the memory sticks..."

let "USBS_COUNT_LAST = -1"
let "ERROR_COUNT_LAST = -1"

while [ ${#USBS} -gt 1 ]; do

	enum_usbs
	
	let "ERROR_COUNT = 0"
	for THIS_USB in ${USBS}; do
		BASE=`basename ${THIS_USB}`
		THIS_MD5=`cut --delimiter=' ' -f 1 <${TMPDIR}/${BASE}`
		if [ "${DD_IMAGE_MD5}" != "${THIS_MD5}" ]; then
			echo "Verify failed: ${THIS_USB}"
			let "ERROR_COUNT = ERROR_COUNT + 1"
		fi
	done
	
	if [ ${ERROR_COUNT_LAST} -ge 0 ] && [ ${ERROR_COUNT} -ne ${ERROR_COUNT_LAST} ]; then
		# One or more USB sticks with error was removed
		aplay error.wav >/dev/null 2>/dev/null &
	else
		if [ ${USBS_COUNT_LAST} -ge 0 ] && [ ${USBS_COUNT} -ne ${USBS_COUNT_LAST} ]; then
			# One or more USB sticks was removed
			aplay ok.wav >/dev/null 2>/dev/null &
		fi
	fi

	let "USBS_COUNT_LAST = USBS_COUNT"
	let "ERROR_COUNT_LAST = ERROR_COUNT"

	echo "------------ (USBS: ${USBS_COUNT}, Errors. ${ERROR_COUNT})"
done

rm -fR ${TMPDIR}

write_message_nl "Normal termination"

