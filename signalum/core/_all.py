from .utils import db2dbm, RealTimePlot, spin, rssi_to_colour_str                                     
from ._base import show_header, term
from ._bluetooth import bluelyze
from ._wifi import wifilyze


def allyze(**kwargs):
    LOADING = spin(before="Initializing.. ",
                    after="\nlocating BT and WIFI devices")
    while True:
        bluetooth_devices = bluelyze(**kwargs)
        wifi_devices = wifilyze(**kwargs)
        if LOADING:
            LOADING.terminate()
        show_header()
        print("Showing BT and WIFI Devices\n\n")
        print("TABLE: BT")
        print(bluetooth_devices, "\n\n")
        print("TABLE: WIFI")
        print(wifi_devices)

    
