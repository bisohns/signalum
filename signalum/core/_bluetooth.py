# performs a simple device inquiry, followed by a remote name request of each
# discovered device

import datetime as dt
import os
import struct
import sys
import time
import logging

import bluetooth
import bluetooth._bluetooth as bluez
import matplotlib.animation as animation
import matplotlib.pyplot as plt
import numpy as np
from scipy.interpolate import interp1d
from ._base import show_header, term

DEVICE_ID = 0
VALUES_PER_FRAME = 50
CATEGORY_VALUES = [0, -10, -30, -50, -70]
OUT_OF_RANGE = (-300, -200)
NAME_DICT =  dict()

def printpacket(pkt):
    for c in pkt:
        sys.stdout.write("%02x " % struct.unpack("B",c)[0])


def read_inquiry_mode(sock):
    """returns the current mode, or -1 on failure"""
    # save current filter
    old_filter = sock.getsockopt( bluez.SOL_HCI, bluez.HCI_FILTER, 14)

    # Setup socket filter to receive only events related to the
    # read_inquiry_mode command
    flt = bluez.hci_filter_new()
    opcode = bluez.cmd_opcode_pack(bluez.OGF_HOST_CTL, 
            bluez.OCF_READ_INQUIRY_MODE)
    bluez.hci_filter_set_ptype(flt, bluez.HCI_EVENT_PKT)
    bluez.hci_filter_set_event(flt, bluez.EVT_CMD_COMPLETE);
    bluez.hci_filter_set_opcode(flt, opcode)
    sock.setsockopt( bluez.SOL_HCI, bluez.HCI_FILTER, flt )

    # first read the current inquiry mode.
    bluez.hci_send_cmd(sock, bluez.OGF_HOST_CTL, 
            bluez.OCF_READ_INQUIRY_MODE )

    pkt = sock.recv(255)

    status,mode = struct.unpack("xxxxxxBB", pkt)
    if status != 0: mode = -1

    # restore old filter
    sock.setsockopt( bluez.SOL_HCI, bluez.HCI_FILTER, old_filter )
    return mode

def write_inquiry_mode(sock, mode):
    """returns 0 on success, -1 on failure"""
    # save current filter
    old_filter = sock.getsockopt( bluez.SOL_HCI, bluez.HCI_FILTER, 14)

    # Setup socket filter to receive only events related to the
    # write_inquiry_mode command
    flt = bluez.hci_filter_new()
    opcode = bluez.cmd_opcode_pack(bluez.OGF_HOST_CTL, 
            bluez.OCF_WRITE_INQUIRY_MODE)
    bluez.hci_filter_set_ptype(flt, bluez.HCI_EVENT_PKT)
    bluez.hci_filter_set_event(flt, bluez.EVT_CMD_COMPLETE);
    bluez.hci_filter_set_opcode(flt, opcode)
    sock.setsockopt( bluez.SOL_HCI, bluez.HCI_FILTER, flt )

    # send the command!
    bluez.hci_send_cmd(sock, bluez.OGF_HOST_CTL, 
            bluez.OCF_WRITE_INQUIRY_MODE, struct.pack("B", mode) )

    pkt = sock.recv(255)

    status = struct.unpack("xxxxxxB", pkt)[0]

    # restore old filter
    sock.setsockopt( bluez.SOL_HCI, bluez.HCI_FILTER, old_filter )
    if status != 0: return -1
    return 0

def device_inquiry_with_with_rssi(sock, show_name=False):
    # save current filter
    old_filter = sock.getsockopt( bluez.SOL_HCI, bluez.HCI_FILTER, 14)

    # perform a device inquiry on bluetooth device #0
    # The inquiry should last 8 * 1.28 = 10.24 seconds
    # before the inquiry is performed, bluez should flush its cache of
    # previously discovered devices
    flt = bluez.hci_filter_new()
    bluez.hci_filter_all_events(flt)
    bluez.hci_filter_set_ptype(flt, bluez.HCI_EVENT_PKT)
    sock.setsockopt( bluez.SOL_HCI, bluez.HCI_FILTER, flt )

    duration = 1
    max_responses = 255
    cmd_pkt = struct.pack("BBBBB", 0x33, 0x8b, 0x9e, duration, max_responses)
    # TODO Optimize code for performance
    # update the global device name dictionary before sending hci cmd(which changes mode)
    if show_name:
        NAME_DICT.update(dict(bluetooth.discover_devices(lookup_names=True)))
    bluez.hci_send_cmd(sock, bluez.OGF_LINK_CTL, bluez.OCF_INQUIRY, cmd_pkt)

    results = []
    data = f"{term.underline}Name \t\t\t MAC Address \t\t\t RSSI\n{term.normal}"

    done = False
    while not done:
        pkt = sock.recv(255)
        ptype, event, plen = struct.unpack("BBB", pkt[:3])
        if event == bluez.EVT_INQUIRY_RESULT_WITH_RSSI:
            pkt = pkt[3:]
            nrsp = bluetooth.get_byte(pkt[0])
            for i in range(nrsp):
                # get human readable addr
                addr = bluez.ba2str( pkt[1+6*i:1+6*i+6] )
                rssi = bluetooth.byte_to_signed_int(
                        bluetooth.get_byte(pkt[1+13*nrsp+i]))
                # retrieve device name, or assign address as name
                try:
                    name = NAME_DICT[addr]
                except:
                    name = addr
                results.append( ( addr, rssi, name ) )
                data += ("%s\t %s\t\t %d\n" % (name, addr, rssi))
        elif event == bluez.EVT_INQUIRY_COMPLETE:
            done = True
        elif event == bluez.EVT_CMD_STATUS:
            status, ncmd, opcode = struct.unpack("BBH", pkt[3:7])
            if status != 0:
                print("uh oh...")
                printpacket(pkt[3:7])
                done = True
        elif event == bluez.EVT_INQUIRY_RESULT:
            pkt = pkt[3:]
            nrsp = bluetooth.get_byte(pkt[0])
            for i in range(nrsp):
                addr = bluez.ba2str( pkt[1+6*i:1+6*i+6] )
                results.append( ( addr, -1 , "UNK") )
                print("[%s] (no RRSI)" % addr)
        else:
            logging.debug("unrecognized packet type 0x%02x" % ptype)
        logging.debug("event %s", event)

    # restore old filter
    sock.setsockopt( bluez.SOL_HCI, bluez.HCI_FILTER, old_filter )
    # print all the data at once since blessings clears the screen just before
    if len(results):
        print(term.clear())
        show_header()
        print(data)
#     if len(results)< 1:
#         print("No devices found in nearby range")
    return results

def animate(i, xs, val_dict, ax, sock):
    """
    Instance function to create matplotlib graph
    
    """
    # TODO Hide/cutout devices with rssi < -200
    results = device_inquiry_with_with_rssi(sock)
    # append datetime string as a float to represent time axis
    xs.append(float(dt.datetime.now().strftime("%H.%M%S")))
    NAME_DICT.update({i[0]: i[2] for i in results})
    for i in results:
        try:
            # check for dict key if it exists
            affect_list = val_dict[i[0]]
            affect_list.append(i[1])
        except: 
            # create new list with prior values out of range
            val_dict[i[0]]= list()
            val_dict[i[0]].extend([np.random.random_integers(*OUT_OF_RANGE) \
                 for i in range(len(xs))])

    ax.clear()
    # limit both axis to VALUES_PER_FRAME values at a time maximum
    xs = xs[-VALUES_PER_FRAME:]
    for i in val_dict:
        device_name = NAME_DICT[i]
        val_dict[i] = val_dict[i][-VALUES_PER_FRAME:]
        # if device has dissapeared, append zeros to make up length
        if len(val_dict[i]) < len(xs):
            val_dict[i].extend([np.random.random_integers(*OUT_OF_RANGE) \
                 for i in range(len(xs) - len(val_dict[i]))])
        # smoothen out x axis before display
        x = np.array(xs)
        y = np.array(val_dict[i])
        x_new = np.linspace(x.min(), x.max(), 500)
        # check if points are enough to interpolate on and use box(nearest) interpolation
        # to display levels to this
        if len(x) > 2:
            f = interp1d(x, y, kind='nearest')
            y_smooth = f(x_new)
            # plot smooth plot with scatter point plots
            ax.plot(x_new, y_smooth, label=device_name)
        else:
            ax.plot(xs, y, label=device_name)
        #ax.scatter(xs, y)
    # display legend
    ax.legend()

    plt.xticks([])
    # plt.subplots_adjust(bottom=0.30)
    plt.title("Simulation RSSI over time")
    plt.ylabel("DBMS")
    # plt.hlines(CATEGORY_VALUES, 0, max(xs), linestyle="dashed")

def bluelyze(**kwargs):
    print(term.clear())
    show_header()
    show_graph = kwargs.pop("graph")
    show_name = kwargs.pop("show_name")
    try:
        sock = bluez.hci_open_dev(DEVICE_ID)
    except:
        print("error accessing bluetooth device...")
        sys.exit(1)
    
    try:
        mode = read_inquiry_mode(sock)
    except Exception as e:
        print("error reading inquiry mode.  ")
        print("Are you sure this a bluetooth 1.2 device?")
        print(e)
        sys.exit(1)
    print("current inquiry mode is %d" % mode)
    
    if mode != 1:
        print("writing inquiry mode...")
        try:
            result = write_inquiry_mode(sock, 1)
        except Exception as e:
            print("error writing inquiry mode.  Are you sure you're root?")
            print(e)
            sys.exit(1)
        if result != 0:
            print("error while setting inquiry mode")
        print("result: %d" % result)


    if show_graph:
        # change background style
        plt.style.use('dark_background')
        # Create figure for plotting
        fig = plt.figure("Real Time Bluetooth RSSI")
        ax = fig.add_subplot(1, 1, 1)
        xs = []
        results = device_inquiry_with_with_rssi(sock, show_name=show_name) 
        # initialize dictionary to store real time values of devices
        val_dict = {key: list() for key,value,name in results}
        ani = animation.FuncAnimation(fig, animate, fargs=(xs, val_dict, ax, sock), interval=100)
        plt.show()    
    else:
        while True:
            device_inquiry_with_with_rssi(sock, show_name=show_name)

