#!/usr/bin/env python
# -*- coding: utf-8 -*-
import argparse
import logging
import sys


from yamt.parser import parse_input_file
from yamt.core import execute, dependency_graph, show_tasks


logger = logging.getLogger(__name__)


def yamt(input_file):
    """
    YAMT program entry point.
    """
    logging.debug("input file:\n {0}\n".format(input_file))
    tasks = parse_input_file(input_file)
    logging.info("Found {0} tasks.".format(len(tasks)))
    graph = dependency_graph(tasks)
    for node in graph.nodes():
        logging.info(node)
        logging.info(tasks[node])
    show_tasks(graph, tasks)
    execute(graph, tasks)


def _create_parser():
    parser = argparse.ArgumentParser()
    parser.add_argument('input_file',
                        type=str,
                        nargs="?",
                        default="yamtfile")
    parser.add_argument('-v',
                        '--verbose',
                        action="store_true",
                        default=False)
    parser.add_argument('-d',
                        '--debug',
                        action="store_true",
                        default=False)
    return parser


def main():
    parser = _create_parser()
    args = parser.parse_args(sys.argv[1:])
    if args.verbose:
        logging.basicConfig(
            format='%(levelname)s %(filename)s: %(message)s',
            level=logging.DEBUG)
    else:
        # Log info and above to console
        logging.basicConfig(
            # format='%(levelname)s: %(message)s',
            format='%(message)s',
            level=logging.INFO
        )
    logging.debug("Options:")
    for key, value in (vars(args)).iteritems():
        logging.debug("{0}: {1}".format(key, value))
    with open(args.input_file) as f:
        input_file = f.read()
    yamt(input_file)


if __name__ == '__main__':
    main()
