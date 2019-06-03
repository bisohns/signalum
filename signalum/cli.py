import argparse
from curses import wrapper
import logging
import sys
import pprint
from _version import __version__, name

try:
    from .core import bluelyze, term, get_logo, wifilyze, allyze
except:
    from core import bluelyze, term, get_logo, wifilyze, allyze


def main(args):
    """
        Executes logic from parsed arguments
    """
    logging.debug(args)
    if args['wifi']:
        wifilyze(show_extra_info=args["show_extra_info"],
                 graph=args["show_graph"],
                 analyze_all=False)
    elif args['bluetooth']:
        bluelyze(
            graph=args["show_graph"], 
            show_name=args["show_name"],
            show_extra_info=args["show_extra_info"],
            analyze_all=False)
    elif args['analyze_all']:
        allyze(
            show_name=args["show_name"],
            show_extra_info=args["show_extra_info"],
            analyze_all=True
        )
    else:
        sys.exit('Protocol does not exist. It can only be one of bluetooth or wifi')

def cli_usage(name=None):
    """
    custom usage message to override `cli.py`
    """
    return f"""
    {get_logo()}
    usage: signalyze [-h] [-o OUTPUT] [--show-name] [-b | -w | -all] [--show-graph | --show-extra-info] 
    """

def runner():
    """
    runner that handles parsing logic
    """
    parser = argparse.ArgumentParser(description='Signalyze', usage=cli_usage())
    graph_or_verbose = parser.add_mutually_exclusive_group()
    parser.add_argument('--version', action='version',
                        version='{package} -  {version}'.format(package=name, version=__version__))
    parser.add_argument('-o', '--output', help='save to an output csv file')
    parser.add_argument('--show-name', action="store_true", help='Show Device name and mac address')
    protocol = parser.add_mutually_exclusive_group()
    protocol.add_argument('-b','--bluetooth', action="store_true", help='Analyze only bluetooth')
    protocol.add_argument('-w','--wifi', action="store_true", help='Analyze only wifi')
    protocol.add_argument('-all','--analyze-all', action="store_true", help='Analyze both wifi and bluetooth')
    graph_or_verbose.add_argument('--show-graph', action="store_true", help='Show Realtime graph of nearby devices')
    graph_or_verbose.add_argument('--show-extra-info', action="store_true", help='Show extra information like services and device classification')

    args = vars(parser.parse_args())
    main(args)

if __name__ == '__main__':
    logging.basicConfig(stream=sys.stderr, level=logging.INFO)
    runner()
