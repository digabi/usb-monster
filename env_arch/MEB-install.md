# Installing Arch Linux for USB copying workstation

This documentation and installation process was used to install Arch 
Linux 2017.08.01 to local hard disk. Arch Linux was used since it offers 
latest kernel with no USB stack hickups.

Before starting make sure you're connected to the internet. Arch 
live/install environment receives network settings automatically via 
DHCP when cable is connected.

```
loadkeys fi
timedatectl set-ntp true
fdisk /dev/sda
	o
	[ remove all existing partitions using commands p and d ]
	n
	p
	1
	[default]
	+10G
	[ if you're notified about old partition signature you should remove it ]
	n
	p
	2
	[default]
	+10G
	[ if you're notified about NTFS signature you should remove it ]
	t
	2
	82
	w
mkfs.ext4 /dev/sda1
mount /dev/sda1 /mnt
mkswap /dev/sda2
swapon /dev/sda2
pacstrap /mnt base grub
genfstab -p /mnt >> /mnt/etc/fstab
arch-chroot /mnt
ln -sf /usr/share/zoneinfo/Europe/Helsinki /etc/localtime
hwclock --systohc --utc
nano -w /etc/locale.gen
```
 * Uncomment line en_US.UTF-8 UTF-8
 * exit by saving with Ctrl-X
 * save changes
```
locale-gen
echo "LANG=en_US.UTF-8" >>/etc/locale.conf
echo "usb-monster" >/etc/hostname
nano -w /etc/hosts
```
 * Add "usb-monster" to the lines containing "127.0.0.1" and "::1"
 * Exit by saving with Ctrl-X
```
passwd
```
 * give a new root password twice
```
grub-install --target=i386-pc /dev/sda
grub-mkconfig -o /boot/grub/grub.cfg
exit
umount -R /mnt
reboot
```
 * Remove the live/install boot media
 * After the reboot
```
Log in as user: root, password: [your root password]
loadkeys fi
echo "KEYMAP=fi" >>/etc/vconsole.conf
nano /etc/systemd/network/digabi.network
```
 * Write following file
```
[Match]
name=en*

[Network]
DHCP=ipv4
```
 * exit by saving with Ctrl-X
```
systemctl enable systemd-networkd
systemctl start systemd-networkd
```
 * Make sure your eno1 gets IPv4 address by issuing `ip a`
```
systemctl enable systemd-resolved
ln -sf /run/systemd/resolve/resolv.conf /etc/resolv.conf
systemctl start systemd-resolved
```
 * Now you should be able to `ping www.ylioppilastutkinto.fi`
```
fdisk /dev/sda
	n
	p
	3
	[default]
	+100G
	w

reboot

[ wait for the reboot and log in again as root ]

mkfs.ext4 /dev/sda3
echo "/dev/sda3 /opt ext4 defaults 0 1" >>/etc/fstab
mount /opt

pacman -S xorg-server
1 [this is the default]
pacman -S xorg-drivers
```
 * accept default = all
```
pacman -S lxde
```
 * accept default = all
```
systemctl enable lxdm
localectl set-x11-keymap fi
systemctl start lxdm

Log in as user: root, password: [your root password]
Start > System Tools > LXTerminal
```

You might encounter problems logging in to a system without any regular 
users. After entering user and password the LXDE appears to hang. You 
get the root desktop after selecting Reboot or Shutdown from the bottom 
right. To avoid this shortcoming add a normal user to the system:

```
useradd normal
passwd normal
```

You can log in as root by selecting "More..." from the login screen.

## Fonts

```
pacman -S ttf-ubuntu-font-family
```

For terminal: Ubuntu Mono (Start > System Tools > LXTerminal > Edit > 
Preferences)

You have to logout/login before you'll see Ubuntu fonts here)

## Additional packages needed

Install these packages (`pacman -S xxx`):
 * git
 * pv
 * python2
 * alsa-utils
 * pulseaudio
 * pulseaudio-alsa

```
pacman -S git pv python2 alsa-utils pulseaudio pulseaudio-alsa
```

## Install MEB usb-monster scripts

```
cd /opt
git clone https://github.com/digabi/usb-monster.git
ln -s usb-monster/dd-curses/write_dd.py write_dd
```

## Searching for packages

To find packages containing file X:

 * (First time: `pacman -S pkgfile && pkgfile --update`)
 * `pkgfile x`

To search packages from the repo:

 * pacman -Ss searchterm
 
To search locally installed packages:

 * pacman -Qs searchterm

## Updating system

To update system (if you get 404:s when trying to install new stuff)

 * `pacman -Syu`
