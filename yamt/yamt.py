# -*- coding: utf-8 -*-
import argparse
from .parser import parser
from .graph import dependency_graph, show_graph
from .core import execute


def create_parser():
    parser = argparse.ArgumentParser()
    parser.create_argument('input_file', type=str, default="yamtfile")
    return parser


def main():
    cmdline_parser = create_parser()
    args = cmdline_parser.parse_arguments()
    tasks = parser(open(args.input_file).read())
    for task in tasks:
        print 80 * "*"
        print task.interpreter
        print task.inputs
        print task.outputs
        print task.code
        print task.comments
        print 80 * "*"
    graph = dependency_graph(tasks)
    for node in graph.nodes():
        print node
        print tasks[node]
    show_graph(graph, tasks)
    execute(graph, tasks)


if __name__ == '__main__':
    main()
