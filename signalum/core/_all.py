from tabulate import tabulate
from .utils import db2dbm, RealTimePlot, spin, rssi_to_colour_str                                     
from ._base import show_header, term
from ._bluetooth import bluelyze
from ._wifi import wifilyze



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
        print(tabulate(data[0], headers=data[1]))
        print("\n\n")
        for i in data[0]:
            print(data[0][i])
        return None
    else:
        print(f"No {tab_name} Device in range.. \n\n")
        return None
        #return spin(before=f"No {tab_name} Device in range.. \n\n")        

def allyze(**kwargs):
    """
    analyze all devices
    """
    LOADING = spin(before="Initializing.. ",
                    after="\nlocating BT and WIFI devices")
    BT_LOADING = None
    WF_LOADING = None
    while True:
        wifi_devices = wifilyze(**kwargs)
        bluetooth_devices = bluelyze(**kwargs)
        spin_terminator((BT_LOADING, WF_LOADING, LOADING))
        show_header()
        print("Showing BT and WIFI Devices\n\n")
        BT_LOADING = display(bluetooth_devices, "BT")
        WF_LOADING = display(wifi_devices, "WIFI")    
