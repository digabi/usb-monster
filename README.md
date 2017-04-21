# usb-monster

Command-line tools for creating massive number of USB memory sticks.

 * [fat/](fat/README.md) Create FAT32 filesystem and copy files. No verify.
 * [dd/](dd/README.md) Write `dd` images. Verifies all media.
 * [dd-curses/](dd-curses/README.md) Write `dd` images and verifies written disks.
   A state-of-the-art curses-based UI displays progress etc. This what we currently use
   at the MEB and what what you're probably looking for.
 * [env_arch/](env_arch/README.md) Automated setup for Arch Linux live/installation media.
   Make a `usb-monster` workstation with an one-liner!
