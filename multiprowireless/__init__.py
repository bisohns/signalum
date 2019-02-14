name = "multiprowireless"
import sys, os
# insert all modules here
sys.path.insert(0, os.path.dirname(os.path.realpath(__file__)))
from _bluetooth import *
from _wifi import *
from _zigbee import *