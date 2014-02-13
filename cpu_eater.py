#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys, argparse, time, os
from subprocess import call
import multiprocessing

VERSION = 0
PATCHLEVEL = 9
SUBLEVEL = 0

def eater(needtime) :
    endwait = time.time() + float(needtime)
    while time.time() < endwait :
        pass

def argv_gen():
    global args
    parser = argparse.ArgumentParser(description='Generate tasks to occupy certain CPU resource. (Obtain CPU Usage from /proc/stat)')
    parser.add_argument('-c', '--core', type=int, action="store", dest="core", default=-1, help='set usage on specific cpus. if not set, means every core')
    parser.add_argument('-i', '--interval', type=float, action="store", dest="interval", default=1, help='set sample rate, default is 1 sec')
    parser.add_argument('-u', '--usage', type=int, action="store", dest="target_usage", default=0, help='set how much cpu usage you want to see')
    parser.add_argument('-v', '--version', action='version', version='cpu-eater %d.%d.%d' % (VERSION, PATCHLEVEL, SUBLEVEL))
    args = parser.parse_args()

def TRIMz(x):
    global tz
    if x < 0 :
        tz = 0
    else :
        tz = x
    return tz

def dispatcher(core, curr_usage, target_usage, interval) :
    global last_consumer
    needtime = "%.2f" %(float(interval) / 100 * float(target_usage))
    if args.core != -1 :
        p = multiprocessing.Process(target = eater, args = (needtime, ))
        p.start()
        pid = p.pid
        cmd = "taskset -pc %d %d > /dev/null" % (args.core, pid)
        call(cmd, shell=True)
    else :
        for i in range(0, total_core) :
            p = multiprocessing.Process(target = eater, args = (needtime, ))
            p.start()
            pid = p.pid
            cmd = "taskset -pc %d %d > /dev/null" % (i, pid)
            call(cmd, shell=True)

if __name__ == "__main__" :
    tz = 0
    argv_gen()
    curr_usage = 0
    total_core = os.sysconf('SC_NPROCESSORS_ONLN')
    if args.core >= total_core :
        print "Please enter the correct core number"
        print "The valid core value is ",
        for i in range(0, total_core) :
            print "%d " %(i),
        sys.exit()

    while True :
        start_time = time.time()
        fp = open("/proc/stat", "r")
        for i in range(0, args.core + 2) :
            start = fp.readline()
        start = start.split()
        fp.close()

        dispatcher(args.core, curr_usage, args.target_usage, args.interval)

        while time.time() < (start_time + args.interval) :
            time.sleep(float(args.interval)/100.0)
            pass

        fp = open("/proc/stat", "r")
        for i in range(0, args.core + 2) :
            end = fp.readline()
        end = end.split()
        fp.close()
        total_frme = 0
        for i in range(1, 11) :
            total_frme += int(end[i])
            total_frme -= int(start[i])

        if total_frme < 1 :
            total_frme = 1
        scale = 100.0 / float(total_frme)
        curr_usage = (100.0 - (TRIMz(int(end[4]) - int(start[4])) * scale))
        if args.core >= 0 :
            print "CPU%d Utilization : %5.1f%%" % (args.core, curr_usage)
        else :
            print "CPU Utilization : %5.1f%%" % curr_usage

