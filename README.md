# USB-monster

Command-line tool and GUI for creating massive number of USB memory sticks and cron scripts
to download and unzip latest Abitti image files.

 * [src/](src/README.md) Write `dd` images and verifies written disks.
   A state-of-the-art curses-based UI displays progress etc. This is what we currently
   use at the MEB to write USB memory sticks.
 * `downloader/` Cron scripts which download latest Abitti images to `/opt/abitti-images`
 * [speed-test/](speed-test/README.md) Scripts which have been used to benchmark
   USB memory sticks in the MEB tendering processes.

## Installing USB-monster

USB-monster can be installed to recent versions of Debian and Ubuntu. The recommended
way to install is described in the [YTL Linux README](https://github.com/digabi/ytl-linux/blob/main/README.md).

However, you can install the latest package from the release page:

 1. Get the latest `.deb` from [release page](https://github.com/digabi/usb-monster/releases)
 1. Install: `sudo apt install ./digabi-usb-monster_X.X.X_all.deb`

## Using USB-monster

 1. Download the image file. It can be raw disk image (typically `.dd`, `.img` or `.iso`)
    or a `.zip` file with the balenaEtcher file structure. Abitti is being [shipped](https://www.abitti.fi/fi/paivitykset/)
    in the latter format.
 1. Start the `usb-digabi-monster` from the start menu or from the command line (`usb-digabi-monster`).
 1. Choose the image file.
 1. To write the disk images you have to have `sudo` access. Enter your password to claim
    you ownership to these rights.
 1. Insert USB sticks and press any key to scan the USBs.
 1. Press Enter to start writing.

## Using USB-monster from the command line

You can skip the GUI stuff and just execute the writer. This works for the raw images only.

 * `sudo /usr/local/lib/digabi-usb-monster/write_dd.py /path/to/image.dd`
 * Skip verification process: \
   `sudo /usr/local/lib/digabi-usb-monster/write_dd.py -n /path/to/image.dd`

## Disabling Abitti Downloader

To disable Abitti Downloader cron job edit `/etc/default/abitti-downloader` and comment
the `ENABLE_DOWNLOADER` value:

```
# To disable automatic Abitti download comment following line or set value to empty
#ENABLE_DOWNLOADER=1
```

## Publising a new version

 1. Update Changelog (below) and `src/VERSION`, push changes and wait GitHub Action "Build And Publish" to finish
 1. Go to [releases](https://github.com/digabi/usb-monster/releases). There should be a new draft release with a `.deb` file attached. Press the Edit button.
 1. Enter the new version number to "Tag version" field (e.g. "v1.6.0" - note the "v")
 1. Fill "Release title" Field
 1. Copy release note markup from `README.md` to "Describe this release" textarea
 1. Click "Publish release"

## Changelog

### 1.2.0 The Last Stick

 * Runs on Python 3 instead of Python 2 for an easier install to Ubuntu 22.04
 * Remove temporary raw image files on exit

### 1.1.0 A New Hope

 * Open and write Etcher-style Abitti images
 * Cron-based Abitti Downloader checks for new images every hour
 * Write disk image with dd option `oflag=dsync` and 5M block size to increase accuracy of the write speed limit
 * Removed USB-Monster specific repository in favour of YTL Linux repository
 * Upgraded privilege escalation from `sudo` to `pkexec`
 * Build `.deb` packages with GitHub Actions
