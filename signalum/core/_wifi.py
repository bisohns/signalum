import subprocess
import re
from tabulate import tabulate
import textwrap

from ._exceptions import InterfaceError
from .utils import db2dbm
from ._base import show_header, term


cells_re = re.compile(r'Cell \d+ - ')
quality_re_dict = {
        'dBm': re.compile(r'Quality[=:](?P<quality>\d+/\d+).*Signal level[=:](?P<siglevel>-\d+) dBm?(.*Noise level[=:](?P<noiselevel>-\d+) dBm)?'),
        'relative': re.compile(r'Quality[=:](?P<quality>\d+/\d+).*Signal level[=:](?P<siglevel>\d+/\d+)'),
        'absolute': re.compile(r'Quality[=:](?P<quality>\d+).*Signal level[=:](?P<siglevel>\d+)')
        }
frequency_re = re.compile(r'^(?P<frequency>[\d\.]+ .Hz)(?:[\s\(]+Channel\s+(?P<channel>\d+)[\s\)]+)?$')


identity = lambda x: x

key_translations = {
    'encryption key': 'encrypted',
    'essid': 'ssid',
}


class Cell:
    """
    Presents a Python interface to the output of iwlist.
    """

    def __init__(self):
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

    def __repr__(self):
        return 'Cell(ssid={ssid})'.format(**vars(self))

    def __getitem__(self, index):
        ls = [self.ssid, self.address, self.signal]
        return ls[index]



def scan():
    """
    Returns a list of all cells extracted from the output of iwlist.
    """
    try:
        iwlist_scan = subprocess.check_output(['iwlist', 'scan'],
                                              stderr=subprocess.STDOUT)
    except subprocess.CalledProcessError as e:
        raise InterfaceError(e.output.strip())
    else:
        iwlist_scan = iwlist_scan.decode('utf-8')
    _normalize = lambda cell_string: normalize(cell_string)
    cells = [_normalize(i) for i in cells_re.split(iwlist_scan)[1:]]

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


def normalize(cell_block):
    # The cell blocks come in with every line except the first indented at
    # least 20 spaces.  This removes the first 20 spaces off of those lines.
    lines = textwrap.dedent(' ' * 20 + cell_block).splitlines()
    cell = Cell()

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

def wifilyze(**kwargs):
    """ Display wifi analyzed details"""
    _show_graph = kwargs.pop("show_graph")

    headers =["Name", "MAC Address", "RSSI"]
    while True:
        _signals = scan()
        show_header()
        print(tabulate(_signals, headers=headers))




