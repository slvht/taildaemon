#!/usr/bin/python

import glob
import time
import os
import tailing


class Settings():

    def __init__(self):
        pass

    errors = []
    

    def read_conf(self):
        self.errors = []
        with open("settings.conf") as file:
            for line in file:
                line = line.strip()
                self.errors.append(line)
        with open("settings.conf") as cfile:
            for line in cfile:
                line = line.strip()
                if line.find("log_dir") != -1:
                    val = line.split('=')
                    self.log_dir = val[1]
                if line.find("log_filters") != -1:
                    val = line.split('=')
                    self.log_filters = val[1].split(',')
                    print self.log_filters
                if line.find("tcpdump_timeout") != -1:
                    val = line.split('=')
                    self.t_timeout = int(val[1])


def dir_scan(old_list, file_filter_tmp):
    while True:
        list_of_files = glob.glob(file_filter_tmp)
        new_files = list(set(list_of_files).difference(set(old_list)))

        if new_files:
            for new_file in new_files:
                start_worker(new_file, settings)
        old_list = list_of_files
        time.sleep(5)


def get_all_files(file_filter):
    return glob.glob(file_filter)


# Select just the files that match our patterns
def file_filter(file_name):
    if is_text(file_name):
        for filter in settings.log_filters:
            if file_name.find(filter) != -1:
                return True
    return False


# Avoid dirs and binary files
def is_text(filename):
    if os.path.isfile(filename):
        with open(filename, 'rb') as f:
            for block in f:
                if b'\0' in block:
                    return False
    else:
        return False
    return True


# Start tail workers for a list of files
def start_workers(file_list, settings):
    # Start a tail thread for each log
    for file in file_list:
        # Filename filter - according to config
        if file_filter(file):
            print "Starting Tail thread for " + file
            tail = tailing.TailThread(file, settings)
            tail.start()


# Start tail work for a single file
def start_worker(file, settings):
    if file_filter(file):
        print "Starting Tail thread for " + file
        tail = tailing.TailThread(file, settings)
        tail.start()
    else:
        pass


def main():
    print settings.log_dir
    current_files = get_all_files(settings.log_dir)

    start_workers(current_files, settings)

    dir_scan(current_files, settings.log_dir)


settings = Settings()
settings.read_conf()

if __name__ == '__main__':
    main()
