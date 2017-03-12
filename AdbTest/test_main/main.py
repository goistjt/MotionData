#!/usr/bin/python
import sys
import string
import os
import subprocess

cmd = 'C:\\Android\sdk\\platform-tools\\adb pull sdcard/Android/data/edu.rose_hulman.nswccrane.dataacquisition/files/sessions C:\\Users\\Steve\\Documents'
s = subprocess.check_output(cmd.split())
print(s.split(bytes("\r\n", "utf-8")))
