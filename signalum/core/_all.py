import datetime as dt

from tabulate import tabulate
from .utils import db2dbm, RealTimePlot, spin, rssi_to_colour_str                                     
from ._base import show_header, term
from ._bluetooth import bluelyze
from ._wifi import wifilyze
from ._exceptions import AdapterUnaccessibleError 


def spin_terminator(spinners):
    """
    terminate all spinner objects in the tuple of spinners

    Args:
        spinners: (iterable) iterable of spinner objects
    """
    for i in spinners:
        if i:
            i.terminate()

def display(data, tab_name):
    """
    checks if devices are available and then displays

    Args:
        data: (tuple) tuple where data[0] is the table iterable \
                and data[1] is the table header
        tab_name: (str) name of the table to be displayed

    Returns:
       None if there are devices in data[0], spinner object\
            when there are no available devices yet 
    """
    if bool(data[0]):
        print(f"TABLE: {tab_name}")
        print(tabulate(data[0], headers=data[1], disable_numparse=True ,tablefmt="rst"), "\n\n")
        return None
    else:
        print(f"No {tab_name} Device in range.. \n\n")
        return None
        #return spin(before=f"No {tab_name} Device in range.. \n\n")        

def allyze(**kwargs):
    """
    analyze all devices
    
    .. todo:
        Add Graph implementations for this functionality
    """ 
    LOADING = spin(before="Initializing", 
                after="\nLocating WF and BT Devices")
    kwargs["graph"] = False
    while True:
        try:
            wifi_devices = wifilyze(**kwargs)
            bluetooth_devices = bluelyze(**kwargs)
            if LOADING:
                LOADING.terminate()
            show_header()
            print("Showing BT and WIFI Devices\n\n")
            display(bluetooth_devices, "BT")
            display(wifi_devices, "WIFI")
        except AdapterUnaccessibleError as e:
            # Wifi and Bluetooth might be running of different threads, so we want to kill those
            # Processes so that the terminal can be blocked
            LOADING.terminate()
            spin_terminator((LOADING, ))
            show_header()
            print(e)
            break
