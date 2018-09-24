# Installing Ubuntu Linux for USB copying workstation

This documentation was written for Ubuntu Workstation 18.04.

## Install Ubuntu

Install Ubuntu Workstation as you would normally do.

## Install extra packages

Install following packages:

`sudo apt-get install git pv python-psutil`

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
