import sys
import subprocess
import re
from tabulate import tabulate
import textwrap
import warnings
import datetime as dt

import numpy as np
from scipy.interpolate import interp1d
from ._exceptions import InterfaceError, AdapterUnaccessibleError
from .utils import db2dbm, RealTimePlot, spin, rssi_to_colour_str
from ._base import show_header, term


OUT_OF_RANGE = (-300, -200)
VALUES_PER_FRAME = 50
LOADING_HANDLER = None
NAME_DICT = dict()

cells_re = re.compile(r'Cell \d+ - ')
quality_re_dict = {
        'dBm': re.compile(r'Quality[=:](?P<quality>\d+/\d+).*Signal level[=:](?P<siglevel>-\d+) dBm?(.*Noise level[=:](?P<noiselevel>-\d+) dBm)?'),
        'relative': re.compile(r'Quality[=:](?P<quality>\d+/\d+).*Signal level[=:](?P<siglevel>\d+/\d+)'),
        'absolute': re.compile(r'Quality[=:](?P<quality>\d+).*Signal level[=:](?P<siglevel>\d+)')
        }
frequency_re = re.compile(r'^(?P<frequency>[\d\.]+ .Hz)(?:[\s\(]+Channel\s+(?P<channel>\d+)[\s\)]+)?$')
# Checks if wifi is off
network_down_re = re.compile(r'.*Network is down*.')


identity = lambda x: x

key_translations = {
    'encryption key': 'encrypted',
    'essid': 'ssid',
}


class Cell:
    """
    Presents a Python interface to the output of iwlist.
    """

    def __init__(self, show_extra_info=False ,color=True):
        self.ssid = None
        self.bitrates = []
        self.address = None
        self.channel = None
        self.encrypted = False
        self.encryption_type = None
        self.frequency = None
        self.mode = None
        self.quality = None
        self.signal = None
        self.noise = None
        self.show_extra_info = show_extra_info
        self.color = color

    @property
    def colour_coded_rssi(self):
        """
        returns the colour coded rssi value
        """
        return rssi_to_colour_str(self.signal)
    
    def __repr__(self):
        return 'Cell(ssid={ssid})'.format(**vars(self))

    def __getitem__(self, index):
        if self.color:
            rssi = self.colour_coded_rssi
        else:
            rssi = self.signal
        if self.show_extra_info:
            ls = [self.ssid, self.address, rssi, self.frequency, self.quality, \
                    self.encryption_type, self.mode, self.channel]
        else:
            ls = [self.ssid, self.address, rssi]
        return ls[index]



def scan(color=True, show_extra_info=False):
    """
    Returns a list of all cells extracted from the output of iwlist.
    """
    global LOADING_HANDLER, NAME_DICT

    try:
        iwlist_scan = subprocess.check_output(['iwlist', 'scan'],
                                              stderr=subprocess.STDOUT)
    except subprocess.CalledProcessError as e:
        raise InterfaceError(e.output.strip())
    else:
        iwlist_scan = iwlist_scan.decode('utf-8')
    _normalize = lambda cell_string: normalize(cell_string, color, show_extra_info)
    cells = [_normalize(i) for i in cells_re.split(iwlist_scan)[1:]]

    # If there are no wifi signals confirm, if it's because the wifi is not enabled
    if not len(cells):
        _no_card = network_down_re.search(iwlist_scan)
        if _no_card is not None:
            raise AdapterUnaccessibleError("Cannot access Network Adapter, is your Wifi off?")

    # terminate loader
    if LOADING_HANDLER:
        LOADING_HANDLER.terminate()
    # update NAME_DICT
    NAME_DICT.update({i.address: i.ssid for i in cells})
    return cells


def normalize_key(key):
    key = key.strip().lower()

    key = key_translations.get(key, key)

    return key.replace(' ', '')

normalize_value = {
    'ssid': lambda v: v.strip('"'),
    'encrypted': lambda v: v == 'on',
    'address': identity,
    'mode': identity,
    'channel': int,
}


def split_on_colon(string):
    key, _, value = map(lambda s: s.strip(), string.partition(':'))

    return key, value


def normalize(cell_block, color, show_extra_info=False):
    # The cell blocks come in with every line except the first indented at
    # least 20 spaces.  This removes the first 20 spaces off of those lines.
    lines = textwrap.dedent(' ' * 20 + cell_block).splitlines()
    cell = Cell(show_extra_info=show_extra_info, color=color)

    while lines:
        line = lines.pop(0)

        if line.startswith('Quality'):
            for re_name, quality_re in quality_re_dict.items():
                match_result = quality_re.search(line)
                if match_result is not None:
                    groups = match_result.groupdict()
                    cell.quality = groups['quality']
                    signal = groups['siglevel']
                    noise = groups.get('noiselevel')
                    if re_name == 'relative':
                        actual, total = map(int, signal.split('/'))
                        cell.signal = db2dbm(int((actual / total) * 100))
                    elif re_name == 'absolute':
                        cell.quality = cell.quality + '/100'
                        cell.signal = db2dbm(int(signal))
                    else:
                        cell.signal = int(signal)
                    if noise is not None:
                        cell.noise = int(noise)
                    break

        elif line.startswith('Bit Rates'):
            values = split_on_colon(line)[1].split('; ')

            # consume next line of bit rates, because they are split on
            # different lines, sometimes...
            if lines:
                while lines[0].startswith(' ' * 10):
                    values += lines.pop(0).strip().split('; ')

            cell.bitrates.extend(values)
        elif ':' in line:
            key, value = split_on_colon(line)
            key = normalize_key(key)

            if key == 'ie':
                if 'Unknown' in value:
                    continue

                # consume remaining block
                values = [value]
                while lines and lines[0].startswith(' ' * 4):
                    values.append(lines.pop(0).strip())

                if 'WPA2' in value:
                    cell.encryption_type = 'wpa2'
                elif 'WPA' in value:
                    cell.encryption_type = 'wpa'
                else:
                    cell.encryption_type = 'null'

            if key == 'frequency':
                matches = frequency_re.search(value)
                cell.frequency = matches.group('frequency')
                if matches.group('channel'):
                    cell.channel = int(matches.group('channel'))
            elif key in normalize_value:
                setattr(cell, key, normalize_value[key](value))

    # It seems that encryption types other than WEP need to specify their
        # existence.
        if cell.encrypted and not cell.encryption_type:
            cell.encryption_type = 'wep'

    return cell

def animate(i, ax, plt, xs, val_dict, _show_extra_info, headers):
    """
    animate a real time graph plot of RSSI against time
    """
    global NAME_DICT
    
    xs.append(float(dt.datetime.now().strftime("%H.%M%S")))
    _signals = scan(_show_extra_info)
    show_header("WIFI") 
    print(tabulate(_signals, headers=headers))
    print("\n\n")
    for i in _signals:
        # check for dict key if it exists and append
        try:
            #if signal is not None
            if i.signal:
                val_dict[i.address].append(i.signal)
            else:
                val_dict[i].append([np.random.random_integers(*OUT_OF_RANGE)])
        except: 
            # create new list with prior values out of range
            val_dict[i.address]= list()
            val_dict[i.address].extend([np.random.random_integers(*OUT_OF_RANGE) \
                 for i in range(len(xs))])
    ax.clear()
    # limit both axis to VALUES_PER_FRAME values at a time maximum
    xs = xs[-VALUES_PER_FRAME:]
    for i in val_dict:
        device_name = NAME_DICT[i]
        val_dict[i] = val_dict[i][-VALUES_PER_FRAME:]
        # if device has dissapeared, append OUT_OF_RANGE to make up length
        if len(val_dict[i]) < len(xs):
            val_dict[i].extend([np.random.random_integers(*OUT_OF_RANGE) \
                 for i in range(len(xs) - len(val_dict[i]))])
        # if y axis detects twice
        if len(xs) < len(val_dict[i]):
            val_dict[i] = val_dict[i][-len(xs):]
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
    plt.title("Wifi Devices RSSI against time")
    plt.ylabel("Wifi RSSI")
    plt.xlabel("Time")

def wifilyze(**kwargs):
    """ Display wifi analyzed details"""
    global LOADING_HANDLER
    
    _show_graph = kwargs.pop("graph")
    _show_extra_info = kwargs.pop("show_extra_info")
    _analyze_all = kwargs.pop("analyze_all")
    _color = kwargs.get("color", True)
    
    headers =["Name", "MAC Address", "RSSI"]
    if _show_extra_info:
        headers.extend(["Frequency", "Quality", "Encryption Type", "Mode of Device", "Channel"])
    if _analyze_all:
        # return _signals and headers of wifi tables if analyze all
        _signals = scan(_color, _show_extra_info)
        return ( (_signals, headers) )
    else:
        try:
            LOADING_HANDLER = spin(
                                before="Initializing ",
                                after="\nScanning for Wifi Devices")
            if _show_graph:
                _signals = scan(_show_extra_info)
                show_header("WIFI") 
                print(tabulate(_signals, headers=headers, disable_numparse=True))
                print("\n\n") 
                x = []
                val_dict = {i.address: list() for i in scan(_show_extra_info)}
                realtimehandler = RealTimePlot(
                                        func=animate, 
                                        func_args=(x, val_dict, _show_extra_info, headers)
                                        )
                realtimehandler.animate()
            else:
                while True:
                        _signals = scan(_show_extra_info)
                        if not bool(_signals):
                            LOADING_HANDLER = spin(before="No Devices found ")
                        else:
                            show_header("WIFI")
                            print(tabulate(_signals, headers=headers, disable_numparse=True))
                            print("\n\n")
        except AdapterUnaccessibleError as e:
            LOADING_HANDLER.terminate()
            show_header("WIFI")
            print(e)
            sys.exit(1)
