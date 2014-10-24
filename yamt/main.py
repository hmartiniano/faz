#!/usr/bin/env python
# -*- coding: utf-8 -*-
import argparse
import logging
import sys
from time import strftime


from yamt.parser import parse_input_file
from yamt.core import execute, dependency_graph, show_tasks


logger = logging.getLogger(__name__)


def yamt(input_file, variables=None):
    """
    YAMT program entry point.
    """
    logging.debug("input file:\n {0}\n".format(input_file))
    tasks = parse_input_file(input_file, variables=variables)
    print("Found {0} tasks.".format(len(tasks)))
    graph = dependency_graph(tasks)
    show_tasks(graph, tasks)
    execute(graph, tasks)


def _create_parser():
    parser = argparse.ArgumentParser()
    parser.add_argument('input_file',
                        type=str,
                        nargs="?",
                        default="yamtfile")
    parser.add_argument('-v',
                        '--variables',
                        type=str,
                        nargs="+",
                        default=[])
    parser.add_argument('-d',
                        '--debug',
                        action="store_true",
                        default=False)
    return parser


def main(arguments=sys.argv[1:]):
    print("\n*******************" +
          "  Program Started at: " +
          strftime("%Y-%m-%d %H:%M:%S") +
          "  ******************\n\n")
    parser = _create_parser()
    args = parser.parse_args(arguments)
    if args.debug:
        logging.basicConfig(
            format='%(levelname)s %(filename)s: %(message)s',
            level=logging.DEBUG)
    else:
        # Log info and above to console
        logging.basicConfig(
            # format='%(levelname)s: %(message)s',
            format='%(levelname)s %(filename)s: %(message)s',
            level=logging.INFO
        )
    logging.debug("Options:")
    for key, value in (vars(args)).iteritems():
        logging.debug("{0}: {1}".format(key, value))
    with open(args.input_file) as f:
        input_file = f.read()
    yamt(input_file, variables=args.variables)
    print("\n********************" +
          "  Program Ended at: " +
          strftime("%Y-%m-%d %H:%M:%S") +
          "  *******************\n\n")
