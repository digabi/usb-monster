# usb-monster

Command-line tools for creating massive number of USB memory sticks.

 * [fat/](fat/README.md) Create FAT32 filesystem and copy files. No verify.
 * [dd/](dd/README.md) Write `dd` images. Verifies all media.
 * [dd-curses/](dd-curses/README.md) Write `dd` images and verifies written disks.
   A state-of-the-art curses-based UI displays progress etc. This what we currently use
   at the MEB and what what you're probably looking for.
 * [doc/](doc/README.md) Instructions for creating an USB-monsterised Linux workstation.

## Installing USB-monster

USB-monster can be installed to recent versions of Debian and Ubuntu.

 1. Import signing key:
    ```
    sudo bash -c 'wget -O - https://digabi.github.io/usb-monster/gpg.key | apt-key add -'
    ```

 1. Add repo to your sources:
    ```
    sudo bash -c 'echo "deb https://digabi.github.io/usb-monster/debian stable contrib" >/etc/apt/sources.list.d/usbmonster.list'
    ```

 1. `sudo apt-get update`

 1. `sudo apt-get install digabi-dd-curses`

After this the USB-monster updates automatically as part of the standard update process.

## Updating digabi-dd-curses.deb

 1. Make sure you have the private key to sign the repository:
    ```
    gpg --list-key
    gpg: checking the trustdb
    gpg: marginals needed: 3  completes needed: 1  trust model: pgp
    gpg: depth: 0  valid:   1  signed:   0  trust: 0-, 0q, 0n, 0m, 0f, 1u
    /home/matti/.gnupg/pubring.kbx
    ------------------------------
    pub   rsa4096 2019-05-28 [SC]
      0EEA516CC168C3078D93CEAEF0CB5A7157202474
    uid           [ultimate] Abitti Team <abitti@ylioppilastutkinto.fi>
    ```
    If not you'll find the instructions to key handling in the [documentation](doc/DEBIAN-REPO.md).

 1. Make sure you have `reprepro` installed.

 1. Check that the signing key hash (`0EEA516CC168C3078D93CEAEF0CB5A7157202474`) matches to
    the key in `docs/debian/conf/distributions`

 1. Update `dd-curses/VERSION`

 1. Create new package and update repository: `make update-repo-deb`

 1. Commit and push changes.
