# -*- coding: utf-8 -*-

# This class resolves USB devices (e.g. /dev/sdb) to USB paths (e.g. 00/1.2)

import os, re, time

class usb_path_mapper (object):
    def __init__ (self):
        self.cache = {}

    def get_usb_path (self, device, retry_count=0):
        if device in self.cache:
            return self.cache[device]

        try:
            dev_files = os.listdir("/dev/disk/by-path/")
        except OSError:
            dev_files = []

        for this_file in dev_files:
            if os.path.realpath("/dev/disk/by-path/%s" % this_file) == device:
                re_devids = re.search(r'pci-\d+:([a-f0-9]+):.+usb-\d+:([\.\d]+):', this_file)
                if re_devids:
                    devid = re_devids.group(1)+'/'+re_devids.group(2)
                    self.cache[device] = devid
                    return devid
                else:
                    return ""

        if retry_count < 20:
            time.sleep(0.5)
            return self.get_usb_path(device, retry_count+1)

        return ""

    def changed (self, device):
        if device in self.cache:
            del self.cache[device]
