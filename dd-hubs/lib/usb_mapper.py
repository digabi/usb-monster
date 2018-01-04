# -*- coding: utf-8 -*-

# This takes care of the mapping between user's USB address (host, port) and internal USB address
# The internal USB addresses may change in boot

import os, errno, json, re

class usb_mapper (object):
    def __init__ (self, config_path):
        self.config_path = config_path
        self.current_mapping = None

        self.read_config()

    def mkdir_p(self, path):
        try:
            os.makedirs(path)
        except OSError as exc:  # Python >2.5
            if exc.errno == errno.EEXIST and os.path.isdir(path):
                pass
            else:
                raise

    def get_current_boot_id (self):
        f = open("/proc/sys/kernel/random/boot_id", "r")
        this_boot_id = f.readline()
        f.close()

        return this_boot_id.rstrip()

    def if_config (self):
        if self.current_mapping != None:
            return True
        return False

    def read_config (self):
        # Gets existing config from file if the content is still valid (check boot id)

        try:
            with open("%s/usb-mapping.json" % self.config_path) as json_file:
                new_config = json.load(json_file)
        except:
            self.current_mapping = None
            return False

        if new_config['boot_id'] == self.get_current_boot_id():
            self.current_mapping = new_config['mapping']
            return True

        self.current_mapping = None
        return False

    def write_config (self):
        # Write existing config to file

        if not os.access(self.config_path, os.W_OK):
            self.mkdir_p(self.config_path)

        f=open("%s/usb-mapping.json" % self.config_path, "w")

        config = {
            'boot_id': self.get_current_boot_id(),
            'mapping': self.current_mapping
        }

        f.write(json.dumps(config))
        f.close()

    def get_max (self):
        max_hubs = 0
        max_ports = 0

        for this_mapstr in self.current_mapping.iterkeys():
            coords = self.decode_mapstr(this_mapstr)

            if coords[0] > max_hubs:
                max_hubs = coords[0]

            if coords[1] > max_ports:
                max_ports = coords[1]

        return [max_hubs, max_ports]

    def mapping_clear (self):
        self.current_mapping = None

    def encode_mapstr (self, host, port):
        return "%d-%d" % (host, port)

    def decode_mapstr (self, mapstr):
        mapre = re.compile('(\d+)\-(\d+)')
        result = mapre.findall(mapstr)
        return [int(result[0][0]), int(result[0][1])]

    def mapping_add (self, host, port, usbaddr):
        if self.current_mapping == None:
            self.current_mapping = {}

        self.current_mapping[self.encode_mapstr(host, port)] = usbaddr

    def set_config (self, new_config):
        self.mapping_clear()

        for this_coord in new_config:
            self.mapping_add(this_coord[0], this_coord[1], this_coord[2])

    def get_hub_coords (self, usb_path):
        # Return USB hub coordinates for given USB path (e.g. "00/1")

        if self.current_mapping == None:
            return None

        for this_mapstr in self.current_mapping.iterkeys():
            if usb_path == self.current_mapping[this_mapstr]:
                return self.decode_mapstr(this_mapstr)

        return None

    def get_hub_coords_str (self, usb_path):
        hub_coords = self.get_hub_coords(usb_path)
        if hub_coords == None:
            return "Unknown"

        return "%d : %d" % (hub_coords[0], hub_coords[1])

    def get_usbaddr (self, host, port):
        mapstr = self.encode_mapstr(host, port)
        return self.current_mapping[mapstr]
