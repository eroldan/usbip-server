#!/bin/bash
# This script is run by udev when a USB device is connected.
# XXX This script binds all devices matching the rules, while it should only bind the device received as a parameter from udev

SCRIPT_PATH=$(dirname "$(realpath "$0")")
cd $SCRIPT_PATH

# bind any plugged USB device which matchs rules in auto_usbids.txt
./ls_usbids.py | ./bind_usbids.py - auto_usbids.txt

echo 'All done'
