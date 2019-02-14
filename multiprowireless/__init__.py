name = "multiprowireless"
import sys, os
# insert all modules here
sys.path.insert(0, os.path.dirname(os.path.realpath(__file__)))
from bluetooth import *
from wifi import *
from zigbee import *