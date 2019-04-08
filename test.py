# simple inquiry example
import os
import bluetooth

try:
    nearby_devices = bluetooth.discover_devices(lookup_names=True, lookup_class=True)
    print("found %d devices" % len(nearby_devices))
    for addr, name, class_ in nearby_devices:
        print("  %s - %s (class - %s)" % (addr, name, class_))
    
except OSError:
    print("turn on bluetooth device")
