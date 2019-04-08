"""@desc 
		Detect wifi on windows and linux

 	@author 
 		Domnan Diretnan
 		Artificial Intelligence Enthusiast & Software Engineer.
 		Email: diretnandomnan@gmail.com
 		Github: https://github.com/deven96
 		GitLab: https://gitlab.com/Deven96

 	@project
 		@create date 2019-02-14 11:27:46
 		@modify date 2019-02-14 11:27:46

	@license
		MIT License
		Copyright (c) 2018. Domnan Diretnan. All rights reserved

 """

import os
import subprocess

def linux_list():
    """
    parse nmcli results and return a list of
    ("SSID", "SECURITY", "SIGNAL", "RATE")
    """
    ssid_instruction = "nmcli -f ssid dev wifi"
    security_instruction = "nmcli -f security dev wifi"
    signal_instruction = "nmcli -f signal dev wifi"
    rate_instruction = "nmcli -f rate dev wifi"

    INTERFACE = [
        ssid_instruction,
        security_instruction,
        signal_instruction,
        rate_instruction
    ]

    main_list = list()
    for i in INTERFACE:
        cmd = subprocess.Popen(i, shell=True, stdout=subprocess.PIPE)
        sublist = []
        for line in cmd.stdout:
            sublist.append(line.decode("utf-8").strip(" \n"))
        sublist = sublist[1:]
        main_list.append(sublist)
    final_result = list(zip(*main_list))
    print(final_result)
    return final_result

def windows_list():
    results = subprocess.check_output(["netsh", "wlan", "show", "network"])
    results = results.decode("ascii") # needed in python 3
    results = results.replace("\r","")
    ls = results.split("\n")
    ls = ls[4:]
    ssids = []
    x = 0
    while x < len(ls):
        if x % 5 == 0:
            ssids.append(ls[x])
        x += 1
    return ssids

def platform():
    """
    detect the platform the system is run on
    """
    if os.name.startswith('nt'):
        return "windows"
    elif os.name.startswith('posix'):
        return "linux"

def wifi_list():
    """
    lists all wifi networks and their ssid's

    :rtype: list
    """
    if platform() is "linux":
        print ("Detected Linux OS")
        return linux_list()
    if platform() is "windows":
        print ("Detected Windows OS")
        return windows_list()


if __name__ == "__main__":
    wifi_list()