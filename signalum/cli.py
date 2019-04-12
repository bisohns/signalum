import argparse
from curses import wrapper
import logging
import sys
import pprint

try:
    from .core import bluelyze, term, get_logo
except:
    from core import bluelyze, term, get_logo


def main(args):
    """
        Executes logic from parsed arguments
    """
    logging.debug(args)
    if args['protocol'] == 'wifi':
        pass
        # TODO Add wifi integration
    elif args['protocol'] == 'bluetooth':
        bluelyze(
            graph=args["show_graph"], 
            show_name=args["show_name"],
            show_extra_info=args["show_extra_info"])
    elif args['protocol'] == 'all':
        print("Procedure for all protocol not yet implemented, select bluetooth")
       # TODO Add all implementation
    else:
        sys.exit(f'Protocol <args["protocol"]> does not exist. It can only be one of bluetooth or wifi')

def custom_usage(name=None):
    """
    custom usage message to override `cli.py`
    """
    return f"""
    {get_logo()}
    usage: signalyze [-h] [-p PROTOCOL] [-o OUTPUT] ([--show-graph] OR [--show-extra-info]) [--show-name]
    """

def runner():
    """
    runner that handles parsing logic
    """
    parser = argparse.ArgumentParser(description='Signalyze', usage=custom_usage())
    parser.add_argument('-p','--protocol', help='A protocol to analyze (default: all)', default='all')
    parser.add_argument('-o', '--output', help='path to store output csv file', default=False)
    graph_or_verbose = parser.add_mutually_exclusive_group()
    parser.add_argument('--show-name', action="store_true", help='Show Device name and mac address')
    graph_or_verbose.add_argument('--show-graph', action="store_true", help='Show Realtime graph of nearby devices')
    graph_or_verbose.add_argument('--show-extra-info', action="store_true", help='Show extra information like services and device classification')

    args = vars(parser.parse_args())
    main(args)

if __name__ == '__main__':
    logging.basicConfig(stream=sys.stderr, level=logging.INFO)
    runner()
