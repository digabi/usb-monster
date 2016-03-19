#!/bin/bash

LOG_FILE=~/write_dd.log
SLEEP_BETWEEN=5
DD_BLOCK_SIZE=1M

# Get script dir (http://stackoverflow.com/questions/59895/can-a-bash-script-tell-what-directory-its-stored-in)
SOURCE="${BASH_SOURCE[0]}"
while [ -h "$SOURCE" ]; do # resolve $SOURCE until the file is no longer a symlink
  DIR="$( cd -P "$( dirname "$SOURCE" )" && pwd )"
  SOURCE="$(readlink "$SOURCE")"
  [[ $SOURCE != /* ]] && SOURCE="$DIR/$SOURCE" # if $SOURCE was a relative symlink, we need to resolve it relative to the path where the symlink file was located
done
SCRIPT_DIR="$( cd -P "$( dirname "$SOURCE" )" && pwd )"

# Make errors to these devices to test error-checking
# Double-check that you're not using thes device paths as HD etc!
# TEST_DEVICES_PHASE_1 fail images after the test write
# TEST_DEVICES_PHASE_2 fail images after the real write
# Examples:
#TEST_DEVICES_PHASE_1="/dev/sdd"
#TEST_DEVICES_PHASE_2="/dev/sde /dev/sdf"
# Don't make any errors
TEST_DEVICES_PHASE_1=
TEST_DEVICES_PHASE_2=

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

function disk_read_md5 {
	# Set
	# BLOCKCOUNT=0 to read whole disk
	# BLOCKCOUNT=1 to read one block
	
	local BLOCKCOUNT=$1
	local __resultvar=$2
	
	# Remove previous MD5 files
	if [ -f "${TMPDIR}/*" ]; then
		rm "${TMPDIR}/*"
	fi
	
	write_message "Starting to read and calculate checksums: "
	UCOUNT=0
	for THIS_USB in ${USBS}; do
		write_message "${THIS_USB} "
		BASE=`basename ${THIS_USB}`
		if [ -b ${THIS_USB} ]; then
			# This is a block device
			if [ "${BLOCKCOUNT}" != "0" ]; then
				( dd if=${THIS_USB} bs=${DD_BLOCK_SIZE} count=1 2>/dev/null | head -c ${DD_BLOCK_SIZE} | md5sum >${TMPDIR}/${BASE} ) &
			else
				( dd if=${THIS_USB} bs=${DD_BLOCK_SIZE} 2>/dev/null | head -c ${DD_IMAGE_SIZE} | md5sum >${TMPDIR}/${BASE} ) &
			fi
		else
			# This is not a block device
			echo "Not a block device" >${TMPDIR}/${BASE}
		fi
		
		let "UCOUNT = UCOUNT + 1"
	done
	write_message_nl "(${UCOUNT})"

	write_message "Waiting for read processes to terminate..."
	wait
	sleep ${SLEEP_BETWEEN}
	write_message_nl "OK"
	
	eval $__resultvar="'${UCOUNT}'"
}

function disk_check_md5 {
	local MD5_CHECKSUM=$1
	local __result_ok_var=$2
	local __result_error_var=$3
	local __result_missing_var=$4
	
	let "OK_COUNT = 0"
	let "ERROR_COUNT = 0"
	let "MISSING_COUNT = 0"
	
	for THIS_USB in ${USBS}; do
		BASE=`basename ${THIS_USB}`
		if [ -e "/dev/${BASE}" ]; then
			# The USB is still inserted
			if [ -f "${TMPDIR}/${BASE}" ]; then
				# MD5 file exists - this is a known device
				THIS_MD5=`cut --delimiter=' ' -f 1 <${TMPDIR}/${BASE}`
				if [ "${MD5_CHECKSUM}" != "${THIS_MD5}" ]; then
					THIS_BUSNODE=`usb_fsnode_to_busnode ${THIS_USB}`
					echo "Verify failed: ${THIS_USB}, resetting ${THIS_BUSNODE}"
					let "ERROR_COUNT = ERROR_COUNT + 1"
					
					# Init device to blink its LED
					$SCRIPT_DIR/usbreset ${THIS_BUSNODE}
				else
					let "OK_COUNT = OK_COUNT + 1"
				fi
			
			else
				# MD5 file does not exist - this device has not been processed
				let "MISSING_COUNT = MISSING_COUNT + 1"
			fi
		fi
	done
	
	eval $__result_ok_var="'${OK_COUNT}'"
	eval $__result_error_var="'${ERROR_COUNT}'"
	eval $__result_missing_var="'${MISSING_COUNT}'"
}

function usb_fsnode_to_busnode {
	# Resolves fsnode (/dev/sdan) to USB bus node (/dev/bus/usb/001/002)
	FSNODE=$1
	
	# Get USB BUSNUM and DEVNUM from udevadm
	_BUSNUM=`udevadm info --attribute-walk --name=${FSNODE} | grep ATTRS\{busnum\} | head -n 1 | grep -o -P "\d*"`
	_DEVNUM=`udevadm info --attribute-walk --name=${FSNODE} | grep ATTRS\{devnum\} | head -n 1 | grep -o -P "\d*"`
	
	# Left pad with zeros
	BUSNUM=$(printf "%03i" ${_BUSNUM})
	DEVNUM=$(printf "%03i" ${_DEVNUM})
	
	echo "/dev/bus/usb/${BUSNUM}/${DEVNUM}"
}

function cleanup_and_exit {
	if [[ "${TMPDIR}" != "" && -d "${TMPDIR}" ]]; then
		echo ""
		rm -fR ${TMPDIR}
	fi
	
	write_message_nl "Bye!"
	
	exit 0
}

# SIGINT (Ctrl-C) traps to a cleanup function
trap cleanup_and_exit INT

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
DD_BLOCK_SIZE_MD5=$(head -c ${DD_BLOCK_SIZE} ${DD_IMAGE} | md5sum | cut --delimiter=' ' -f 1)

# Create temporary directory for verify statuses
TMPDIR=$(mktemp -d)

CONFIRM=first_round

while [ "${CONFIRM}" != "w" ]; do
	clear

	enum_usbs

	write_message_nl "USBs: ${USBS} (${USBS_COUNT})"
	echo ""

	if [ "${USBS_COUNT}" == "0" ]; then
		echo "$0: No writeable USB sticks found"
		exit 1
	fi

	# Ask for user input

	echo "    Enter: Re-read USB sticks"
	echo "C + Enter: Cancel"
	echo "W + Enter: Start write"
	echo ""

	echo -n "Start write? "
	read CONFIRM
	
	# Make lowercase
	CONFIRM=`echo "$CONFIRM" | tr '[:upper:]' '[:lower:]'`
	
	if [ "${CONFIRM}" == "c" ]; then
		# Cancel pressed
		write_message_nl "User cancelled"
		cleanup_and_exit
	fi
done

# Write one-block test image to all USB disks

write_message "Starting test write: "
UCOUNT=0
for THIS_USB in ${USBS}; do
	write_message "${THIS_USB} "
	if [ -b ${THIS_USB} ]; then
		( dd if=${DD_IMAGE} of=${THIS_USB} bs=${DD_BLOCK_SIZE} count=1 >/dev/null 2>/dev/null ) &
	else
		write_message_nl "Warning: ${THIS_USB} is not a block device - USB memory has disappeared"
	fi
	let "UCOUNT = UCOUNT + 1"
done
write_message_nl "(${UCOUNT})"

write_message "Waiting for dd write processes to terminate..."
wait
sleep ${SLEEP_BETWEEN}
write_message_nl "OK"

# Make errors (phase 1)

for THIS_USB in ${TEST_DEVICES_PHASE_1}; do
	write_message "Creating errors to ${THIS_USB}..."
	dd if=/dev/random of=${THIS_USB} bs=${DD_BLOCK_SIZE} count=1 2>/dev/null
	write_message_nl "OK"
done

# Verify test images

disk_read_md5 1 DISK_READ_MD5_TEST_COUNT

# Check test MD5s

disk_check_md5 ${DD_BLOCK_SIZE_MD5} OK_COUNT ERROR_COUNT MISSING_COUNT

if [[ ${ERROR_COUNT} -gt 0 || ${MISSING_COUNT} -gt 0 ]]; then
	# Test write found defected drives

	write_message "Test write failed, waiting the operator to remove the memory sticks..."

	# Set initial values to execute while loop
	let "OK_COUNT_LAST = -1"
	let "ERROR_COUNT_LAST = -1"
	let "MISSING_COUNT_LAST = -1"

	let "OK_COUNT = 1"
	let "ERROR_COUNT = 1"
	let "MISSING_COUNT = 1"

	while [[ ${OK_COUNT} -gt 0 || ${ERROR_COUNT} -gt 0 || ${MISSING_COUNT} -gt 0 ]]; do

		disk_check_md5 ${DD_BLOCK_SIZE_MD5} OK_COUNT ERROR_COUNT MISSING_COUNT
		
		if [ ${ERROR_COUNT_LAST} -ge 0 ] && [ ${ERROR_COUNT} -ne ${ERROR_COUNT_LAST} ]; then
			# One or more USB sticks with error was removed
			aplay ${SCRIPT_DIR}/error.wav >/dev/null 2>/dev/null &
		elif [ ${MISSING_COUNT_LAST} -ge 0 ] && [ ${MISSING_COUNT} -ne ${MISSING_COUNT_LAST} ]; then
			# One or more not-processed-USB sticks was removed
			aplay ${SCRIPT_DIR}/not_processed.wav >/dev/null 2>/dev/null &
		elif [ ${OK_COUNT_LAST} -ge 0 ] && [ ${OK_COUNT} -ne ${OK_COUNT_LAST} ]; then
			# One or more USB sticks was removed
			aplay ${SCRIPT_DIR}/ok.wav >/dev/null 2>/dev/null &
		fi

		let "OK_COUNT_LAST = OK_COUNT"
		let "ERROR_COUNT_LAST = ERROR_COUNT"
		let "MISSING_COUNT_LAST = MISSING_COUNT"

		echo "----TEST---- (OK: ${OK_COUNT}, Errors: ${ERROR_COUNT}, Not processed: ${MISSING_COUNT})"
	done

	write_message_nl "Exiting as test write failed"
	
	cleanup_and_exit
fi

# Write dd image to all USB disks

write_message "Starting write: "
UCOUNT=0
for THIS_USB in ${USBS}; do
	write_message "${THIS_USB} "
	if [ -b ${THIS_USB} ]; then
		( dd if=${DD_IMAGE} of=${THIS_USB} bs=${DD_BLOCK_SIZE} >/dev/null 2>/dev/null ) &
	else
		write_message_nl "Warning: ${THIS_USB} is not a block device - USB memory has disappeared"
	fi
	let "UCOUNT = UCOUNT + 1"
done
write_message_nl "(${UCOUNT})"

write_message "Waiting for dd write processes to terminate..."
wait
sleep ${SLEEP_BETWEEN}
write_message_nl "OK"

# Make errors (phase 2)

for THIS_USB in ${TEST_DEVICES_PHASE_2}; do
	write_message "Creating errors to ${THIS_USB}..."
	dd if=/dev/random of=${THIS_USB} bs=${DD_BLOCK_SIZE} count=1 2>/dev/null
	write_message_nl "OK"
done

# Verify drives

disk_read_md5 0 DISK_READ_MD5_COUNT

# Look for probably defected drives

write_message "Waiting the operator to remove the memory sticks..."

# Set initial values to execute while loop
let "OK_COUNT_LAST = -1"
let "ERROR_COUNT_LAST = -1"
let "MISSING_COUNT_LAST = -1"

let "OK_COUNT = 1"
let "ERROR_COUNT = 1"
let "MISSING_COUNT = 1"

while [[ ${OK_COUNT} -gt 0 || ${ERROR_COUNT} -gt 0 || ${MISSING_COUNT} -gt 0 ]]; do

	disk_check_md5 ${DD_IMAGE_MD5} OK_COUNT ERROR_COUNT MISSING_COUNT
	
	if [ ${ERROR_COUNT_LAST} -ge 0 ] && [ ${ERROR_COUNT} -ne ${ERROR_COUNT_LAST} ]; then
		# One or more USB sticks with error was removed
		aplay ${SCRIPT_DIR}/error.wav >/dev/null 2>/dev/null &
	elif [ ${MISSING_COUNT_LAST} -ge 0 ] && [ ${MISSING_COUNT} -ne ${MISSING_COUNT_LAST} ]; then
		# One or more not-processed-USB sticks was removed
		aplay ${SCRIPT_DIR}/not_processed.wav >/dev/null 2>/dev/null &
	elif [ ${OK_COUNT_LAST} -ge 0 ] && [ ${OK_COUNT} -ne ${OK_COUNT_LAST} ]; then
		# One or more USB sticks was removed
		aplay ${SCRIPT_DIR}/ok.wav >/dev/null 2>/dev/null &
	fi

	let "OK_COUNT_LAST = OK_COUNT"
	let "ERROR_COUNT_LAST = ERROR_COUNT"
	let "MISSING_COUNT_LAST = MISSING_COUNT"

	echo "------------ (OK: ${OK_COUNT}, Errors: ${ERROR_COUNT}, Not processed: ${MISSING_COUNT})"
done

aplay ${SCRIPT_DIR}/finished.wav >/dev/null 2>/dev/null

write_message_nl "Normal termination"

cleanup_and_exit
