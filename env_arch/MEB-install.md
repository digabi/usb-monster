# Installing Arch Linux for USB copying workstation

This documentation and installation process was used to install Arch Linux to
local hard disk. Arch Linux was used since it offers latest kernel with
no USB stack hickups.

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
	n
	p
	2
	[default]
	+10G
	t
	2
	82
	w
mkfs.ext4 /dev/sda1
mkswap /dev/sda2
mount /dev/sda1 /mnt
swapon /dev/sda2
pacstrap /mnt base grub
genfstab -p /mnt >> /mnt/etc/fstab
arch-chroot /mnt
ln -s /usr/share/zoneinfo/Europe/Helsinki /etc/localtime
hwclock --systohc --utc
nano -w /etc/locale.gen
```
 * Uncomment line en_US.UTF-8 UTF-8
 * exit by saving with Ctrl-X
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
 * give the password twice
```
grub-install --target=i386-pc /dev/sda
grub-mkconfig -o /boot/grub/grub.cfg
exit
umount -R /mnt
reboot
```
 * After the reboot
```
Log in as user: root, password: ytl
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

mkfs.ext4 /dev/sda3
echo "/dev/sda3 /opt ext4 defaults 0 1" >>/etc/fstab
mount /opt

pacman -S xorg-server
1 [this is the default]
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

Log in as user: root, password: ytl
Start > System Tools > LXTerminal
```

## Fonts

```
pacman -S ttf-ubuntu-font-family
```
For terminal: Ubuntu Mono (Start > System Tools > LXTerminal > Edit > Preferences)
For system: Newspaper Regular 10 (Start > Preferences > Desktop Preferences. You have to logout/login before you'll see Ubuntu fonts here)

## Additional packages needed

Install these packages (`pacman -S xxx`):
 * git
 * pv
 * alsa-utils
 * pulseaudio
 * pulseaudio-alsa

## Searching for packages

To find packages containing file X:

 * (First time: `pacman -S pkgfile && pkgfile --update`)
 * `pkgfile x`

## Updating system

To update system (if you get 404:s when trying to install new stuff)

 * `pacman -Syu`
