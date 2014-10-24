# -*- coding: utf-8 -*-
import os
import logging
import tempfile
import subprocess
from datetime import datetime as dt
import networkx as nx
from yamt.utils import (expand_filenames, files_exist,
                        dependencies_are_newer)


class FubarException(Exception):
    pass


class Task(object):

    __dirname = ".yamt"

    def __init__(self, inputs, outputs, code, options, environment):
        self.inputs = expand_filenames(inputs)
        self.outputs = expand_filenames(outputs)
        self.code = code
        self.options = options
        self.environment = environment
        self.order = 0
        self.force = False
        self.check_options()

    def check_options(self):
        interpreter = "bash"
        for option in self.options:
            if "python" in option:
                interpreter = "python"
            elif "ruby" in option:
                interpreter = "ruby"
            elif "force" in option:
                self.force = True
        self.interpreter = interpreter

    def __call__(self):
        """ Invoque an interpreter to execute the code of a given task. """
        self.mktemp_file()
        os.write(self.fd, "\n".join(self.code) + "\n")
        start = dt.now()
        out = subprocess.check_output([self.interpreter, self.fname],
                                      env=self.environment)
        end = dt.now()
        print("***** execution time {}".format(str(end - start)))
        print("***** Output:\n{}".format(out))
        os.close(self.fd)
        os.unlink(self.fname)
        if not(files_exist(self.outputs)):
            raise FubarException("Output files not created for Task %s" % self)

    def mktemp_file(self):
        """ Create a temporary file in the '.yamt' directory for
            the code to feed to the interpreter. """
        if not(os.path.exists(self.__dirname)):
            logging.debug("Creating directory {}".format(self.__dirname))
            os.mkdir(self.__dirname)
        elif not(os.path.isdir(self.__dirname)):
            raise FubarException(
                "There is a file called %s in this directory!!!" %
                self.__dirname)
        logging.debug("Creating file {}".format(self.fname))
        self.fd, self.fname = tempfile.mkstemp(dir=self.__dirname, text=True)

    def __repr__(self):
        return "%s <- %s :%s" % (
            ", ".join(self.outputs),
            ", ".join(self.inputs),
            ", ".join(self.options))


def execute(graph, tasks):
    """
    Given a dependency graph check inputs
    and outputs and execute tasks if needed.
    """
    for node in nx.topological_sort(graph):
        task = tasks[node]
        print(80 * "*")
        print("\n ********** Task {0}: {1}\n".format(task.order, task))
        if files_exist(task.inputs) or len(task.inputs) == 0:
            if files_exist(task.outputs):
                if dependencies_are_newer(task.outputs, task.inputs):
                    print(
                        "Dependencies are newer than outputs. Running task.")
                    task()
                else:
                    print(
                        "Ouput file(s) exist and are older than inputs.")
            else:
                print("No ouput file(s). Running task.")
                task()
        else:
            print("Not executing task. Input file(s) do not exist.")
        print(80 * "*")


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
        print("Task {0}  ******************************".format(n))
        print("Predecessors: {0}".format(task.predecessors))
        print("options: {0}".format(task.options))
        print("Interpreter: {0}".format(task.interpreter))
        print("Inputs: {0}".format(task.inputs))
        print("Outputs: {0}".format(task.outputs))
        print("Code:")
        for line in task.code:
            print("{0}".format(line))
    print("**************************************")
