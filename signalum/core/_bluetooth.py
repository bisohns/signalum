# performs a simple device inquiry, followed by a remote name request of each
# discovered device

import datetime as dt
import struct
import sys
import time
import logging
import warnings
import binascii

import bluetooth
import bluetooth._bluetooth as bluez
import numpy as np
from scipy.interpolate import interp1d
from tabulate import tabulate
from .utils import RealTimePlot, spin, rssi_to_colour_str
from ._base import show_header, term, \
    MAJOR_CLASSES, MINOR_CLASSES, SERVICES
from ._exceptions import AdapterUnaccessibleError

DEVICE_ID = 0
LOADING_HANDLER = None
VALUES_PER_FRAME = 50
CATEGORY_VALUES = [0, -10, -30, -50, -70]
OUT_OF_RANGE = (-300, -200)
NAME_DICT =  dict()
EXTRA_INFO_DICT = dict()
CLASS_DICT = dict()

def printpacket(pkt):
    for c in pkt:
        sys.stdout.write("%02x " % struct.unpack("B",c)[0])

def get_device_extra(addr):
    """
    return the extra device info from the global dict
    """
    try:
        _info_dict = EXTRA_INFO_DICT[addr]
        major_device = _info_dict.get("major_device", "XXXX")
        minor_device = _info_dict.get("minor_device", "XXXX")
        services = _info_dict.get("services", "XXXX")
        return [major_device, minor_device, services]
    except:
        EXTRA_INFO_DICT[addr] = {
                    "major_device": "",
                    "minor_device": "",
                    "services": "",
                }
        return ["XXXX", "XXXX", "XXXX"]

def populate_info_dict():
    """
    call to populate the global info dictionary
    """

    # extract hex value dictionary
    hex_dict = dict()
    for i in CLASS_DICT:
        hex_dict[i] = "%X" %CLASS_DICT[i]
    # check against odd length hex values
    for i in hex_dict:
        if len(hex_dict[i]) % 2 != 0:
            hex_dict[i] = f"0{hex_dict[i]}"

    # initialize entries in EXTRA_INFO_DICT using vars
    for i in hex_dict:
        if i not in EXTRA_INFO_DICT:
            EXTRA_INFO_DICT[i] = {
                "major_device": "",
                "minor_device": "",
                "services": "",
            }
    # extract byte dictionary
    byte_dict = {i: binascii.unhexlify(hex_dict[i]) for i in hex_dict}
    # extract bit dictionary using big byte-decode
    bit_dict = {i: bin(int.from_bytes(byte_dict[i], 'big')) for i in byte_dict}

    # service bits 
    serv_numbers = [13, 16, 17, 18, 19, 20, 21, 22, 23]
    services = ""
    for i in bit_dict:
        bit_stream = bit_dict[i]
        major_stream = bit_stream[-13:-8]
        major_class = MAJOR_CLASSES.get(major_stream, "XXXX")
        minor_class = "XXXX"
        if major_class in ("Miscellaneous", "Device code not specified"):
            minor_class = "XXXX"
            services = "XXXX"
        elif major_class == "Computer":
            minor_class = MINOR_CLASSES[major_class].get(bit_stream[-8:-2], "XXXX")
        elif major_class == "Phone":
            minor_class = MINOR_CLASSES[major_class].get(bit_stream[-8:-2], "XXXX")
        elif major_class == "LAN/Network Access Point":
            minor_class = MINOR_CLASSES[major_class].get(bit_stream[-8:-5], "XXXX")
        elif major_class == "Audio/Video":
            minor_class = MINOR_CLASSES[major_class].get(bit_stream[-8:-2], "XXXX")
        elif major_class == "Peripheral":
            minor_class = MINOR_CLASSES[major_class].get(bit_stream[-8:-6], "XXXX")
        elif major_class == "Imaging":
            minor_class = MINOR_CLASSES[major_class].get(bit_stream[-8:-4], "XXXX")
        elif major_class == "Wearable":
            minor_class = MINOR_CLASSES[major_class].get(bit_stream[-8:-2], "XXXX")
        elif major_class == "Toy":
            minor_class = MINOR_CLASSES[major_class].get(bit_stream[-8:-2], "XXXX")
        elif major_class == "Health":
            minor_class = MINOR_CLASSES[major_class].get(bit_stream[-8:-2], "XXXX")

        # parse services logic, appending each available service
        serv = ""
        if services != "XXXX":
            # run from 13 to 23 excluding (14, 15)
            for x in serv_numbers:
                # appending 0 before odd-numbered hex values sometimes causes
                # the bit_stream[-x] query to hit the 'b' flag of the bit stream
                try:
                    # if bit at position -x is 1, append service
                    if bool(int(bit_stream[-x])):
                        serv += f"{SERVICES[str(x)]}|"
                except:
                    pass
            services = serv

        EXTRA_INFO_DICT[i] = {
            "major_device": major_class,
            "minor_device": minor_class,
            "services": services,            
        }


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

    try:
        # first read the current inquiry mode.
        bluez.hci_send_cmd(sock, bluez.OGF_HOST_CTL, bluez.OCF_READ_INQUIRY_MODE )
    except bluez.error as e:
        raise AdapterUnaccessibleError("Are you sure this a bluetooth 1.2 device? \nTurn On Your Bluetooth")

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

def device_inquiry_with_with_rssi(sock, show_name=False, show_extra_info=False, color=True, ret_table=False):
    global LOADING_HANDLER
    
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
    headers =["Name", "MAC Address", "RSSI"]
    data = []
    results = []
    if show_extra_info or show_name:
        devices = bluetooth.discover_devices(lookup_names=True, lookup_class=True)
        if show_name:
            update_dict = {i[0]: i[1] for i in devices}
            NAME_DICT.update(update_dict)
        if show_extra_info:
            update_dict = {i[0]: i[2] for i in devices}
            CLASS_DICT.update(update_dict)
            headers.extend(["Major Dev Class", "Minor Dev Class", "Services"])
            populate_info_dict()
    bluez.hci_send_cmd(sock, bluez.OGF_LINK_CTL, bluez.OCF_INQUIRY, cmd_pkt)
            


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
                if color:
                    data.append([name, addr, rssi_to_colour_str(rssi)])
                else:
                    data.append([name, addr, rssi])
                if show_extra_info:
                    extra_info = get_device_extra(addr)
                    # extend last data list with extra info
                    data[-1].extend(extra_info)
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
    # if ordered to return a table by analyze_all, ignore other sequence
    if ret_table:
        if len(results) < 1:
            return ( (None, headers ))
        return( (data, headers) )
    else:
        # print all the data at once since blessings clears the screen just before
        if len(results)>= 1:
            # terminate concurrent loading handler
            if bool(LOADING_HANDLER):
                LOADING_HANDLER.terminate()
            show_header("BLUETOOTH")
            print(tabulate(data, headers=headers, disable_numparse=True))
        else:
            # LOADING_HANDLER = spin(before="Searching",
            #                    after="\nNo devices found in nearby range")
            LOADING_HANDLER.terminate()
            LOADING_HANDLER = spin(before="No BT devices in nearby range")
        return results

def animate(i, ax, plt, val_dict, xs, sock, show_name=False, show_extra_info=False):
    """
    Instance function to create matplotlib graph
    
    """
    # TODO Hide/cutout devices with rssi < -200
    results = device_inquiry_with_with_rssi(sock, show_name=show_name)
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
        device_name = NAME_DICT.get(i, "XXXX")
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
    # display legend, attempt to supress warnings
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        ax.legend()
            
    plt.xticks([])
    plt.ylim(-100, 0)
    plt.title("Bluetooth Devices RSSI against time")
    plt.ylabel("BT RSSI")
    plt.xlabel("Time")

def bluelyze(**kwargs):
    global LOADING_HANDLER
    show_graph = kwargs.pop("graph")
    show_name = kwargs.pop("show_name")
    show_extra_info = kwargs.pop("show_extra_info")
    analyze_all = kwargs.pop("analyze_all")
    _color = kwargs.get("color", True)
    
    try:
        sock = bluez.hci_open_dev(DEVICE_ID)
    except:
        print("Error accessing bluetooth device...\n"
              "Confirm if your bluetooth device is correctly installed and try again")
        sys.exit(1)

    try:
        mode = read_inquiry_mode(sock)
        logging.debug("current inquiry mode is %d" % mode)
        
        if mode != 1:
            logging.debug("writing inquiry mode...")
            try:
                result = write_inquiry_mode(sock, 1)
            except Exception as e:
                print("error writing inquiry mode.  Are you sure you're root?")
                print(e)
                sys.exit(1)
            if result != 0:
                print("error while setting inquiry mode")
            logging.debug("result: %d" % result)

        if analyze_all:
            return device_inquiry_with_with_rssi(sock, show_name, show_extra_info, _color, ret_table=True)
        else: 
            print(term.clear())
            show_header("BLUETOOTH")
            LOADING_HANDLER = spin(before="Initializing...")
                
            if show_graph:
                # create general figure object 
                xs = []
                results = device_inquiry_with_with_rssi(sock, show_name, show_extra_info, _color) 
                # initialize dictionary to store real time values of devices
                val_dict = {key: list() for key,value,name in results}
                realtimeplot = RealTimePlot(
                                func=animate, 
                                func_args=(val_dict, xs, sock, show_name, show_extra_info, _color),
                                )
                realtimeplot.animate()
        
            else:
                while True:
                    device_inquiry_with_with_rssi(sock, show_name, show_extra_info, _color)
        
    except (Exception, bluez.error) as e:
        if LOADING_HANDLER:
            LOADING_HANDLER.terminate()
        # Analyze implements its own error handler
        if analyze_all:
            raise(e)
        else:
            logging.debug("error reading inquiry mode.  ")
            show_header("BLUETOOTH")
            print("Are you sure this a bluetooth 1.2 device? \nTurn On Your Bluetooth")
            logging.debug(e)
            sys.exit(1)
