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

echo "--Luodaan tiedostojärjestelmä ${TIKKU}" >>${LOG}
parted -s ${DEV} mklabel gpt >>${LOG}
parted -s ${DEV} mkpart primary 0% 100% >>${LOG} 
mkfs.ext4 ${DEV}1 >>${LOG}
sleep 3

if [ ! -b ${DEV}1 ]; then
	echo "Virhe: ${DEV}1 ei ole block device, en voi mountata"
	exit 1
fi

mount ${DEV}1 ${MOUNTPOINT}

echo "--Kirjoitetaan fio_1.conf ${TIKKU}" >>${LOG}
cat >/${MOUNTPOINT}/fio_1.conf <<EOF
[random_access]
rw=randrw
bs=4k
size=50m
filesize=500m
rwmixwrite=90
fdatasync=1
ioengine=libaio
runtime=360
EOF

echo "--Kirjoitetaan fio_2.conf ${TIKKU}" >>${LOG}
cat >${MOUNTPOINT}/fio_2.conf <<EOF
[random_access]
rw=randrw
bs=4k
size=50m
filesize=500m
rwmixwrite=90
fdatasync=1
ioengine=libaio
EOF

cd ${MOUNTPOINT}
echo "--fio-testi #1 ${TIKKU}" >>${LOG}
fio fio_1.conf >>${LOG}
echo "--fio-testi #2 ${TIKKU}" >>${LOG}
fio fio_2.conf >>${LOG}
cd
umount ${MOUNTPOINT}
rmdir ${MOUNTPOINT}

NOW=`date`
echo "--Testi valmis ${NOW} ${TIKKU}" >>${LOG}

less ${LOG}

