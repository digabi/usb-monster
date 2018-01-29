# -*- coding: utf-8 -*-

# This class updates image counter JSON file

import os, errno, json

class write_counter (object):
    def __init__ (self, config_path):
        self.config_path = config_path

    def mkdir_p(self, path):
        try:
            os.makedirs(path)
        except OSError as exc:  # Python >2.5
            if exc.errno == errno.EEXIST and os.path.isdir(path):
                pass
            else:
                raise

    def read_counter (self, image_path):
        # Gets existing counter from config file

        try:
            with open("%s/write-counter.json" % self.config_path) as json_file:
                current_counter = json.load(json_file)
        except:
            return 0

        if image_path in current_counter:
            return current_counter[image_path]

        return 0

    def add_counter_by_one (self, image_path):
        # Add existing counter by one

        # Read current data
        try:
            with open("%s/write-counter.json" % self.config_path) as json_file:
                current_counter = json.load(json_file)
        except:
            current_counter = {}

        # Add counter by one
        if image_path in current_counter:
            current_counter[image_path] += 1
        else:
            current_counter[image_path] = 1

        # Write counter data
        if not os.access(self.config_path, os.W_OK):
            self.mkdir_p(self.config_path)

        f=open("%s/write-counter.json" % self.config_path, "w")
        f.write(json.dumps(current_counter))
        f.close()
