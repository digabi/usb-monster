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
way to install is with [YTL Linux](https://github.com/digabi/ytl-linux).

### Using USB-monster with YTL Linux

Install USB-monster:
```
sudo apt update && sudo apt install digabi-usb-monster
```

The default behaviour of Cinnamon (thus, YTL Linux) is to automount all USB memories inserted into
the workstation. Before starting to use USB Monster this feature should be disabled by entering
following commands:

```
gsettings set org.cinnamon.desktop.media-handling automount-open false
gsettings set org.cinnamon.desktop.media-handling automount false
```

These commands are per-user so your Abitti server user (e.g. the default `school`) can have the automount
on while the USB-monster user may have the automount turned off. 

### Install USB-monster without YTL Linux

Here are the steps to install USB Monster to your non-YTL Linux deb-based distro:
 * Import the key: \
   `wget -qO- https://linux.abitti.fi/apt-signing-key.pub | sudo tee /etc/apt/trusted.gpg.d/ytl-linux.asc`
 * Add our repo to your sources: \
   `sudo bash -c 'echo "deb https://linux.abitti.fi/deb ytl-linux main" >/etc/apt/sources.list.d/usbmonster.list'`
 * Update your packages and install: \
   `sudo apt update && sudo apt install digabi-usb-monster`

After this your USB Monster will be updated automatically.

If you have added the signing key with legacy `apt-key` tool and get `Key is stored in legacy trusted.gpg keyring` errors
you can change the location of the key with following procedure:

```
$ sudo apt-key del "19A4 3050 953F DEC0 F0D6  2C81 1B26 415C 1E66 6A78"
Warning: apt-key is deprecated. Manage keyring files in trusted.gpg.d instead (see apt-key(8)).
OK
$ wget -qO- https://linux.abitti.fi/apt-signing-key.pub | sudo tee /etc/apt/trusted.gpg.d/ytl-linux.asc
-----BEGIN PGP PUBLIC KEY BLOCK-----

mQINBF/OM8EBEADbtIT8en8PLczP2egPDeBXIXaSsQFzGgCBGd1vjCLbe1bhZ3ii
O/FWr2QqORnbzrNim5VyzeZ8Qq4Yj0XoQNhvkw9eD2old1mThjra5BMesMNXHnEB
PG6LAfPFDE9hsUaQDIJrHRO09GKlMJDIFX/cSPkzlQw2Pnzf6UTY8E2L6CORPWih
...
ZZYZdDCRzHPA90AVFdev65Yd+2xt+JjmnbldS6z7HaIiCeT5XhhhgSd9AUoM+Hyu
NkP7g8coWb57JQj63AgO9ukfqYuR4XqQHW3ga6U4cKhPUU1ChE5H
=swfs
-----END PGP PUBLIC KEY BLOCK-----
```

Run `sudo apt update` and make sure the legacy keyring warning has disappeared.

### Manual installation

However, you can install the latest package from the release page:

 1. Get the latest `.deb` from [release page](https://github.com/digabi/usb-monster/releases)
 1. Install: `sudo dpkg -i ./digabi-usb-monster_X.X.X_all.deb`

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

### 1.2.2 The Stick Awakens

 * Abitti image downloader (see `/etc/default/abitti-downloader`) is disabled by default
 * Image file dialog accepts `.iso` files
 * Use SHA256 instead of MD5 to verify disk integrity because of known limitations of MD5

### 1.2.1 Attack of the Cloned Sticks

 * Show ABITTI/SERVER version string in temporary image file name when using Etcher-style image files
 * Very integrity of the unzipped Etcher-style image
 * Make temporary raw image files readable only to the current user
 * Remove MD5 hashes of temporary raw image files

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
