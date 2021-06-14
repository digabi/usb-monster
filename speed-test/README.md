# USB-memory performance tests

Testing script `testi_2016.sh` was used in tendering process summer 2016. It runs `dd`
and `fio` commands and logs its output. `Arch 2016.03.01` was used as the
base distro as its USB stack appears to be solid on our hardware.

The script `testi_2017.sh` was used summer 2017 and it contains only the `dd` part of the
2016 test.

You need to install fio (`pacman -S fio`).

Following figures were used (this is a sample output):

<pre>
--Testi alkaa Sun Jun 19 12:16:13 UTC 2016 4-12
--Laite: 4-12
P: /devices/pci0000:00/0000:00:01.0/0000:01:00.0/usb5/5-2/5-2.1/5-2.1:1.0/host10/target10:0:0/10:0:0:0/block/sdc
N: sdc
S: disk/by-id/usb-IS917_innostor_201207222714-0:0
S: disk/by-path/pci-0000:01:00.0-usb-0:2.1:1.0-scsi-0:0:0:0
E: DEVLINKS=/dev/disk/by-id/usb-IS917_innostor_201207222714-0:0 /dev/disk/by-path/pci-0000:01:00.0-usb-0:2.1:1.0-scsi-0:0:0:0
E: DEVNAME=/dev/sdc
E: DEVPATH=/devices/pci0000:00/0000:00:01.0/0000:01:00.0/usb5/5-2/5-2.1/5-2.1:1.0/host10/target10:0:0/10:0:0:0/block/sdc
E: DEVTYPE=disk
E: ID_BUS=usb
E: ID_INSTANCE=0:0
E: ID_MODEL=innostor
E: ID_MODEL_ENC=innostor\x20\x20\x20\x20\x20\x20\x20\x20
E: ID_MODEL_ID=0917
E: ID_PART_TABLE_TYPE=PMBR
E: ID_PART_TABLE_UUID=84cfcaa7-6671-4d57-98c6-54882c2d88b1
E: ID_PATH=pci-0000:01:00.0-usb-0:2.1:1.0-scsi-0:0:0:0
E: ID_PATH_TAG=pci-0000_01_00_0-usb-0_2_1_1_0-scsi-0_0_0_0
E: ID_REVISION=1.00
E: ID_SERIAL=IS917_innostor_201207222714-0:0
E: ID_SERIAL_SHORT=201207222714
E: ID_TYPE=disk
E: ID_USB_DRIVER=usb-storage
E: ID_USB_INTERFACES=:080650:
E: ID_USB_INTERFACE_NUM=00
E: ID_VENDOR=IS917
E: ID_VENDOR_ENC=IS917\x20\x20\x20
E: ID_VENDOR_ID=1f75
E: MAJOR=8
E: MINOR=32
E: SUBSYSTEM=block
E: TAGS=:systemd:
E: USEC_INITIALIZED=1756287262

--Lineaarinen kirjoitusnopeus 4-12
2000+0 records in
2000+0 records out
2097152000 bytes (2.1 GB, 2.0 GiB) copied, 194.922 s, <b>10.8 MB/s (1)</b>
--Lineaarinen lukunopeus 4-12
2000+0 records in
2000+0 records out
2097152000 bytes (2.1 GB, 2.0 GiB) copied, 226.539 s, <b>9.3 MB/s (2)</b>
--Luodaan tiedostojärjestelmä 4-12
Creating filesystem with 7756288 4k blocks and 1941504 inodes
Filesystem UUID: 18cf96db-e8b2-4bc9-baff-8e615752ac64
Superblock backups stored on blocks: 
	32768, 98304, 163840, 229376, 294912, 819200, 884736, 1605632, 2654208, 
	4096000

Allocating group tables:   0/237
Writing inode tables:   0/237
Creating journal (32768 blocks): done
Writing superblocks and filesystem accounting information:   0/237

--Kirjoitetaan fio_1.conf 4-12
--Kirjoitetaan fio_2.conf 4-12
--fio-testi #1 4-12
random_access: (g=0): rw=randrw, bs=4K-4K/4K-4K/4K-4K, ioengine=libaio, iodepth=1
fio-2.12
Starting 1 process
random_access: Laying out IO file(s) (1 file(s) / 500MB)

random_access: (groupid=0, jobs=1): err= 0: pid=1945: Sun Jun 19 12:30:05 2016
  read : io=2824.0KB, bw=8029B/s, iops=1, runt=360149msec
    slat (usec): min=596, max=2166.6K, avg=63649.76, stdev=234583.70
    clat (usec): min=0, max=12, avg= 1.68, stdev= 2.29
     lat (usec): min=597, max=2166.6K, avg=63652.29, stdev=234583.50
    clat percentiles (usec):
     |  1.00th=[    0],  5.00th=[    0], 10.00th=[    1], 20.00th=[    1],
     | 30.00th=[    1], 40.00th=[    1], 50.00th=[    1], 60.00th=[    1],
     | 70.00th=[    1], 80.00th=[    2], 90.00th=[    2], 95.00th=[   10],
     | 99.00th=[   11], 99.50th=[   11], 99.90th=[   12], 99.95th=[   12],
     | 99.99th=[   12]
    bw (KB  /s): min=    8, max=   80, per=100.00%, avg=20.03, stdev=15.08
  write: io=25948KB, bw=73777B/s, iops=18, runt=360149msec
    slat (usec): min=2, max=756697, avg=320.71, stdev=13212.66
    clat (usec): min=0, max=12, avg= 0.60, stdev= 0.82
     lat (usec): min=2, max=756698, avg=321.52, stdev=13212.67
    clat percentiles (usec):
     |  1.00th=[    0],  5.00th=[    0], 10.00th=[    0], 20.00th=[    0],
     | 30.00th=[    0], 40.00th=[    0], 50.00th=[    1], 60.00th=[    1],
     | 70.00th=[    1], 80.00th=[    1], 90.00th=[    1], 95.00th=[    1],
     | 99.00th=[    1], 99.50th=[    2], 99.90th=[   12], 99.95th=[   12],
     | 99.99th=[   12]
    bw (KB  /s): min=    8, max=  512, per=100.00%, avg=120.41, stdev=110.48
    lat (usec) : 2=96.98%, 4=2.11%, 10=0.01%, 20=0.89%
  cpu          : usr=0.02%, sys=0.07%, ctx=7259, majf=0, minf=12
  IO depths    : 1=100.0%, 2=0.0%, 4=0.0%, 8=0.0%, 16=0.0%, 32=0.0%, >=64=0.0%
     submit    : 0=0.0%, 4=100.0%, 8=0.0%, 16=0.0%, 32=0.0%, 64=0.0%, >=64=0.0%
     complete  : 0=0.0%, 4=100.0%, 8=0.0%, 16=0.0%, 32=0.0%, 64=0.0%, >=64=0.0%
     issued    : total=r=706/w=6487/d=0, short=r=0/w=0/d=0, drop=r=0/w=0/d=0
     latency   : target=0, window=0, percentile=100.00%, depth=1

Run status group 0 (all jobs):
   READ: io=2824KB, aggrb=7KB/s, minb=7KB/s, maxb=7KB/s, mint=360149msec, maxt=360149msec
  WRITE: io=25948KB, aggrb=72KB/s, minb=72KB/s, maxb=72KB/s, mint=360149msec, maxt=360149msec

Disk stats (read/write):
  sdc: ios=706/7310, merge=0/112, ticks=44700/1042163, in_queue=1087514, util=99.92%
--fio-testi #2 4-12
random_access: (g=0): rw=randrw, bs=4K-4K/4K-4K/4K-4K, ioengine=libaio, iodepth=1
fio-2.12
Starting 1 process

random_access: (groupid=0, jobs=1): err= 0: pid=1998: Sun Jun 19 12:39:55 2016
  read : io=5068.0KB, bw=8793B/s, iops=2, runt=590193msec
    slat (usec): min=591, max=1481.7K, avg=44265.70, stdev=179069.20
    clat (usec): min=0, max=12, avg= 1.79, stdev= 2.34
     lat (usec): min=592, max=1481.7K, avg=44268.24, stdev=179068.96
    clat percentiles (usec):
     |  1.00th=[    0],  5.00th=[    1], 10.00th=[    1], 20.00th=[    1],
     | 30.00th=[    1], 40.00th=[    1], 50.00th=[    1], 60.00th=[    1],
     | 70.00th=[    2], 80.00th=[    2], 90.00th=[    2], 95.00th=[   11],
     | 99.00th=[   11], 99.50th=[   11], 99.90th=[   12], 99.95th=[   12],
     | 99.99th=[   12]
    bw (KB  /s): min=    8, max=  120, per=100.00%, avg=20.17, stdev=15.83
  write: io=46132KB, bw=80040B/s, iops=<b>19 (3)</b>, runt=590193msec
    slat (usec): min=2, max=738492, avg=144.46, stdev=7021.59
    clat (usec): min=0, max=13, avg= 0.58, stdev= 0.66
     lat (usec): min=3, max=738494, avg=<b>145.25 (4)</b>, stdev=<b>7021.62 (5)</b>
    clat percentiles (usec):
     |  1.00th=[    0],  5.00th=[    0], 10.00th=[    0], 20.00th=[    0],
     | 30.00th=[    0], 40.00th=[    0], 50.00th=[    1], 60.00th=[    1],
     | 70.00th=[    1], 80.00th=[    1], 90.00th=[    1], 95.00th=[    1],
     | 99.00th=[    1], 99.50th=[    1], 99.90th=[   11], 99.95th=[   12],
     | 99.99th=[   12]
    bw (KB  /s): min=    8, max=  512, per=100.00%, avg=118.41, stdev=107.34
    lat (usec) : 2=96.76%, 4=2.51%, 10=0.01%, 20=0.73%
  cpu          : usr=0.02%, sys=0.08%, ctx=12907, majf=0, minf=12
  IO depths    : 1=100.0%, 2=0.0%, 4=0.0%, 8=0.0%, 16=0.0%, 32=0.0%, >=64=0.0%
     submit    : 0=0.0%, 4=100.0%, 8=0.0%, 16=0.0%, 32=0.0%, 64=0.0%, >=64=0.0%
     complete  : 0=0.0%, 4=100.0%, 8=0.0%, 16=0.0%, 32=0.0%, 64=0.0%, >=64=0.0%
     issued    : total=r=1267/w=11533/d=0, short=r=0/w=0/d=0, drop=r=0/w=0/d=0
     latency   : target=0, window=0, percentile=100.00%, depth=1

Run status group 0 (all jobs):
   READ: io=5068KB, aggrb=8KB/s, minb=8KB/s, maxb=8KB/s, mint=590193msec, maxt=590193msec
  WRITE: io=46132KB, aggrb=78KB/s, minb=78KB/s, maxb=78KB/s, mint=590193msec, maxt=590193msec

Disk stats (read/write):
  sdc: ios=1263/12854, merge=0/167, ticks=55853/1773630, in_queue=1830080, util=99.92%
--Testi valmis Sun Jun 19 12:39:56 UTC 2016 4-12
</pre>

 1. Linear write (e.g. *10.8 MB/s*)
 2. Linear read (e.g. *9.3 MB/s*)
 3. Write iops, note: use second fio output (e.g. *19*)
 4. Write latency, average, note: use second fio output (e.g. *145.25*)
 5. Write latency, standard deviation, note: use second fio output (e.g. *7021.62*)
