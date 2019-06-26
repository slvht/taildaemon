#!/usr/bin/python
#
# Author: Silviu Hutanu silviu.hutanu@ro.ibm.com
# Scope: Multithreaded log checker for HANA replication
# Version: 0.1

import threading
import subprocess
import select
import time
import thread


class TailThread(threading.Thread):

    def __init__(self, file_name, settings):
        self.file_name = file_name
        self.settings = settings
        threading.Thread.__init__(self)

    def run(self):
        self.tail_log(self.file_name)

    def tail_log(self, filename):
        f = subprocess.Popen(['tail', '-F', filename], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        p = select.poll()
        p.register(f.stdout)

        while True:
            if p.poll(1):
                line = f.stdout.readline()
                # Search for errors in each new line
                for err in self.settings.errors:
                    if line.find(err) != -1:
                        t = time.localtime()
                        timestamp = time.strftime('%b_%d_%Y_%H_%M', t)
                        print  timestamp + " " + err + ' Error Detected! -> ' + self.file_name;

                        thread.start_new_thread(self.start_dump, ("tdump_" + timestamp, self.settings.t_timeout,))
                    else:
                        pass
                    time.sleep(1)

    # Start a tcpdump capture
    def start_dump(self, filename, timeout):
        if not self.find_proc("tcpdump"):
            filename = "/tmp/" + filename
            dumpcmd = "timeout " + str(timeout) + " tcpdump -w " + filename
            # print " cmd: " + dumpcmd
            tcpdump = subprocess.Popen([dumpcmd], stdin=subprocess.PIPE, stdout=subprocess.PIPE, shell=True)
            while True:
                line = tcpdump.stdout.readline()
                time.sleep(10)
        else:
            print "TCP dump already running"

    # Find if a process is already running
    def find_proc(self, process):
        try:
            pidlist = map(int, subprocess.check_output(["pidof", process]).split())
            return pidlist
        except  subprocess.CalledProcessError:
            return None
