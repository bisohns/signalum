import argparse
import logging
import sys
import pprint
from .core import bluelyze

logging.basicConfig(stream=sys.stderr, level=logging.INFO)

def main(args):
    """
        Executes logic from parsed arguments
    """
    logging.debug(args)
    if args['protocol'] == 'wifi':
        pass
        # TODO Add wifi integration
    elif args['protocol'] == 'bluetooth':
        bluelyze(graph=args["show_graph"], show_name=args["show_name"])
    elif args['protocol'] == 'all':
        print("Procedure for all protocol not yet implemented, select bluetooth")
        pass
       # TODO Add all implementation
    else:
        sys.exit(f'Protocol <args["protocol"]> does not exist. It can only be one of bluetooth or wifi')

def runner():
    """
    runner that handles parsing logic
    """
    parser = argparse.ArgumentParser(description='Signalyze')
    parser.add_argument('-p','--protocol', help='A protocol to analyze (default: all)', default='all')
    parser.add_argument('--show-graph', action="store_true", help='Show Realtime graph of nearby devices')
    parser.add_argument('-o', '--output', help='path to store output csv file', default=False)
    parser.add_argument('--show-name', action="store_true", help='Show Device name and mac address')

    args = vars(parser.parse_args())
    main(args)

if __name__ == '__main__':
    runner()
