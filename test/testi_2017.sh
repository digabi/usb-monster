#!/bin/bash

TIKKU=$1
DEV=$2

if [ "${TIKKU}" == "" ]; then
	echo "Kerro tikun nimi!"
	exit 1
fi

if [ "${DEV}" == "" ]; then
	echo "Kerro laitteen polku, esim /dev/sdb"
	exit 1
fi

if [ ! -b ${DEV} ]; then
	echo "Virhe! ${DEV} ei ole block device!"
	exit 1
fi

DEVNAME=`udevadm info --query=all -n ${DEV} | grep "ID_SERIAL="`
DEVID=`udevadm info --query=all -n ${DEV} | perl -ne 'if (/ID_VENDOR_ID=(.+)/) { print "$1\n"; }'`

MOUNTPOINT=/tmp/testi.$$
mkdir ${MOUNTPOINT}

LOG=/mnt/root/usb-tikkutesti/${DEVID}/${TIKKU}.log
mkdir -p /mnt/root/usb-tikkutesti/${DEVID}

NOW=`date`
echo "" >>${LOG}
echo "" >>${LOG}
echo "--Testi alkaa ${NOW} ${TIKKU}" >>${LOG}
echo "--Laite: ${TIKKU}" >>${LOG}
udevadm info --query=all -n ${DEV} >>${LOG}
echo "Logfile: ${LOG}"
echo "Laite: ${DEVNAME}"
echo "ID: ${DEVID}"

if [ "${DEVID}" == "" ]; then
	echo "Virhe: DEVID ei ole asetettu"
	exit 1
fi

#gnome-terminal -e "tail -f ${LOG}"

echo "--Lineaarinen kirjoitusnopeus ${TIKKU}" >>${LOG}
dd if=/dev/zero of=${DEV} bs=1M count=2000 >>${LOG} 2>>${LOG}
echo "--Lineaarinen lukunopeus ${TIKKU}" >>${LOG}
dd if=${DEV} of=/dev/null bs=1M count=2000 >>${LOG} 2>>${LOG}

NOW=`date`
echo "--Testi valmis ${NOW} ${TIKKU}" >>${LOG}

less ${LOG}

