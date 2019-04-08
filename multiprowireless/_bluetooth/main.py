"""@desc 
		Detect bluetooth on windows and linux

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
    parse hcitool results and return a list of
    ("SSID", "SECURITY", "SIGNAL", "RATE")
    """
    scan_instruction = "hcitool scan"

    main_list = list()
    cmd = subprocess.Popen(scan_instruction, shell=True, stdout=subprocess.PIPE)
    for line in cmd.stdout:
        print(line)
    final_result = list(zip(*main_list))
    return final_result

def windows_list():
    pass

def platform():
    """
    detect the platform the system is run on
    """
    if os.name.startswith('nt'):
        return "windows"
    elif os.name.startswith('posix'):
        return "linux"

def bluetooth_list():
    """
    lists all bluetooth networks and their ssid's

    :rtype: list
    """
    if platform() is "linux":
        print ("Detected Linux OS")
        return linux_list()
    if platform() is "windows":
        print ("Detected Windows OS")
        return windows_list()


if __name__ == "__main__":
    bluetooth_list()