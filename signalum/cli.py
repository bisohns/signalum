#! /bin/bash
import argparse
from curses import wrapper
import logging
import sys
import pprint

try:
    from .core import bluelyze, term, get_logo, wifilyze
except:
    from core import bluelyze, term, get_logo, wifilyze


def main(args):
    """
        Executes logic from parsed arguments
    """
    logging.debug(args)
    if args['protocol'] == 'wifi':
        wifilyze(show_graph=args["show_graph"])
        # TODO Add wifi integration
    elif args['protocol'] == 'bluetooth':
        bluelyze(graph=args["show_graph"], show_name=args["show_name"])
    elif args['protocol'] == 'all':
        print("Procedure for all protocol not yet implemented, select bluetooth")
       # TODO Add all implementation
    else:
        sys.exit('Protocol does not exist. It can only be one of bluetooth or wifi')

def cli_usage(name=None):
    """
    custom usage message to override `cli.py`
    """
    return f"""
    {get_logo()}
    usage: signalyze [-h] [-p PROTOCOL] [-o OUTPUT] [--show-graph] [--show-name]
    """

def runner():
    """
    runner that handles parsing logic
    """
    parser = argparse.ArgumentParser(description='Signalyze', usage=cli_usage())
    parser.add_argument('-p','--protocol', help='A protocol to analyze (default: all)', default='all')
    parser.add_argument('--show-graph', action="store_true", help='Show Realtime graph of nearby devices')
    parser.add_argument('-o', '--output', help='path to store output csv file', default=False)
    parser.add_argument('--show-name', action="store_true", help='Show Device name and mac address')

    args = vars(parser.parse_args())
    main(args)

if __name__ == '__main__':
    logging.basicConfig(stream=sys.stderr, level=logging.INFO)
    runner()
