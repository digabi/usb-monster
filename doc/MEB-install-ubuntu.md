# Installing Ubuntu Linux for USB copying workstation

This documentation was written for Ubuntu Workstation 18.04.

## Install Ubuntu

Install Ubuntu Workstation as you would normally do.

## Install extra packages

Install following packages:

`sudo apt-get install git pv python-psutil exfat-fuse`

## Disable automount

Give following command as the user you intend to for writing:

`gsettings set org.gnome.desktop.media-handling automount false`

## Install MEB usb-monster scripts

```
cd /opt
git clone https://github.com/digabi/usb-monster.git
ln -s usb-monster/dd-curses/write_dd.py write_dd
```

## Profit!

Following example expects test taker's image at `/opt/koe.dd`:

`sudo ./write_dd koe.dd`

## Execute by clicking

Create a following script to your desktop (e.g. ~/Desktop/write_sticks.sh):

```
#!/bin/sh

# Change the path of the image file here
IMAGEFILE=/opt/koe.dd

# Path to write_dd
WRITE_DD=/opt/write_dd

gnome-terminal --hide-menubar --geometry="120x50+0+0" -- sudo ${WRITE_DD} ${IMAGEFILE}
```

Make it executable:

`chmod a+x ~/Desktop/write_sticks.sh`

Tell Nautilus you want to execute scripts when double-clicking them:

`gsettings set org.gnome.nautilus.preferences executable-text-activation launch`
