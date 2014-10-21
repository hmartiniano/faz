# -*- coding: utf-8 -*-
import os
import logging
import tempfile
import subprocess
import networkx as nx
from yamt.utils import expand_filenames, files_exist, dependencies_are_newer


class FubarException(Exception):
    pass


class Task(object):

    dirname = ".yamt"

    def __init__(self, interpreter, inputs, outputs, code, comments=None):
        self.interpreter = interpreter
        self.inputs = expand_filenames(inputs)
        self.outputs = expand_filenames(outputs)
        self.code = code
        self.comments = comments

    def execute(self):
        """ Invoque an interpreter to execute the code of a given task. """
        self.mktemp_file()
        os.write(self.fd, "\n".join(self.code) + "\n")
        out = subprocess.check_output([self.interpreter, self.fname])
        logging.info("{0}".format(out))
        os.close(self.fd)
        os.unlink(self.fname)
        if not(files_exist(self.outputs)):
            raise FubarException("Output files not created for Task %s" % self)

    def mktemp_file(self):
        """ Create a temporary file in the '.yamt' directory for
            the code to feed to the interpreter. """
        if not(os.path.exists(self.dirname)):
            os.mkdir(self.dirname)
        elif not(os.path.isdir(self.dirname)):
            raise FubarException(
                "There is a file called %s in this directory!!!" %
                self.dirname)
        self.fd, self.fname = tempfile.mkstemp(dir=self.dirname, text=True)

    def __repr__(self):
        return "%s <- %s [%s]" % (
            ", ".join(self.outputs), ", ".join(self.inputs), self.interpreter)


def execute(graph, tasks):
    """ Given a dependency graph check inputs
        and outputs and execute tasks if needed.
    """
    for node in nx.topological_sort(graph):
        task = tasks[node]
        logging.info("Task {0}: {1}".format(task.order, task))
        if files_exist(task.inputs) or len(task.inputs) == 0:
            if files_exist(task.outputs):
                if dependencies_are_newer(task.outputs, task.inputs):
                    logging.info(
                        "Dependencies are newer than outputs. Running task.")
                    task.execute()
                else:
                    logging.info(
                        "Ouput file(s) exist and are older than inputs.")
            else:
                logging.info("No ouput file(s). Running task.")
                task.execute()
        else:
            logging.info("Not executing task. Input file(s) do not exist.")


def dependency_graph(tasks):
    """ Produce a dependency graph based on a list
        of tasks produced by the parser.
    """
    graph = nx.MultiDiGraph()
    for i in range(len(tasks)):
        graph.add_node(i)
    for node1 in graph.nodes():
        for node2 in graph.nodes():
            for input in tasks[node1].inputs:
                for output in tasks[node2].outputs:
                    if output == input:
                        graph.add_edge(node2, node1)
    return graph


def show_tasks(graph, tasks):
    for n, node in enumerate(nx.topological_sort(graph)):
        task = tasks[node]
        task.predecessors = graph.predecessors(node)
        task.order = n
        logging.info("Task {0}  ******************************".format(n))
        logging.info("Predecessors: {0}".format(task.predecessors))
        logging.info("Comments: {0}".format(task.comments))
        logging.info("Interpreter: {0}".format(task.interpreter))
        logging.info("Inputs: {0}".format(task.inputs))
        logging.info("Outputs: {0}".format(task.outputs))
        logging.info("Code:")
        for line in task.code:
            logging.info("{0}".format(line))
