# -*- coding: utf-8 -*-
import os
import glob
import logging
import tempfile
import subprocess
from datetime import datetime as dt
from string import Template
import networkx as nx


class TaskFailedException(Exception):
    pass


class TemDirIsFileException(Exception):
    pass


class Task(object):

    __dirname = ".yamt"

    def __init__(self, inputs, outputs, code, options, environment):
        self.inputs = inputs
        self.outputs = outputs
        self.code = code
        self.options = options
        self.environment = environment
        self.order = 0
        self.force = False
        self.check_options()

    def check_options(self):
        interpreter = "bash"
        for option in self.options:
            if "python" in option.lower():
                interpreter = "python"
            elif "ruby" in option.lower():
                interpreter = "ruby"
            elif "force" in option.lower():
                self.force = True
        self.interpreter = interpreter

    def check_filenames(self, filenames):
        result = []
        for n, filename in enumerate(filenames):
            if "$" in filename:
                s = Template(filename)
                result.append(s.substitute(**self.environment))
                logging.debug(
                    "Expanding {} to {}.".format(filename, result[-1]))
            else:
                result.append(filename)
        return result

    def check_inputs(self):
        """ Check for the existence of input files """
        self.inputs = self.expand_filenames(self.check_filenames(self.inputs))
        result = False
        if len(self.inputs) == 0 or self.files_exist(self.inputs):
            result = True
        else:
            print("Not executing task. Input file(s) do not exist.")
        return result

    def check_outputs(self):
        """ Check for the existence of output files """
        self.outputs = self.expand_filenames(self.check_filenames(self.outputs))
        result = False
        if self.files_exist(self.outputs):
            if self.dependencies_are_newer(self.outputs, self.inputs):
                result = True
                print("Dependencies are newer than outputs. Running task.")
            else:
                print("Ouput file(s) exist and are older than inputs.")
        else:
            print("No ouput file(s). Running task.")
            result = True
        return result

    def expand_filenames(self, filenames):
        """
        Expand a list of filenames using shell expansion.
        """
        results = []
        for filename in filenames:
            if any([pattern in filename for pattern in "*[]?"]):
                expanded = glob.glob(filename)
                if len(expanded) > 0:
                    results.extend(expanded)
                else:
                    results.append("NONEXISTENT")
            else:
                results.append(filename)
        return sorted(list(set(results)))

    def files_exist(self, filenames):
        """ Check if all files in a given list exist. """
        return all([os.path.exists(filename) and os.path.isfile(filename)
                    for filename in filenames])

    def dependencies_are_newer(self, files, dependencies):
        """
        For two lists of files, check if any file in the
        second list is newer than any file of the first.
        """
        dependency_mtimes = [
            os.path.getmtime(filename) for filename in dependencies]
        file_mtimes = [os.path.getmtime(filename) for filename in files]
        results = []
        for file_mtime in file_mtimes:
            for dependency_mtime in dependency_mtimes:
                if dependency_mtime > file_mtime:
                    print(dependency_mtime, file_mtime)
                    results.append(True)
                else:
                    print(dependency_mtime, file_mtime)
                    results.append(False)
        return any(results)

    def __call__(self):
        """ Invoque an interpreter to execute the code of a given task. """
        self.mktemp_file()
        os.write(self.fd, "\n".join(self.code) + "\n")
        logging.debug("Environment before task:\n{}".format(self.environment))
        start = dt.now()
        out = subprocess.check_output([self.interpreter, self.fname],
                                      env=self.environment)
        end = dt.now()
        logging.debug("Environment after task:\n{}".format(self.environment))
        print("***** execution time {}".format(str(end - start)))
        print("***** Output:\n{}".format(out))
        os.close(self.fd)
        os.unlink(self.fname)
        if not(self.files_exist(self.outputs)):
            print("Output files:")
            for filename in self.outputs:
                print("{}: {}".format(filename, os.path.exists(filename)))
            raise TaskFailedException("Output files not created for Task %s" % self)

    def mktemp_file(self):
        """ Create a temporary file in the '.yamt' directory for
            the code to feed to the interpreter. """
        if not(os.path.exists(self.__dirname)):
            logging.debug("Creating directory {}".format(self.__dirname))
            os.mkdir(self.__dirname)
        elif not(os.path.isdir(self.__dirname)):
            raise TempDirIsFileException(
                "There is a file called %s in this directory!!!" %
                self.__dirname)
        self.fd, self.fname = tempfile.mkstemp(dir=self.__dirname, text=True)
        logging.debug("Creating file {}".format(self.fname))

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
        if task.check_inputs():
            if task.check_outputs():
                task()
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
        print("Environment: {0}".format(task.interpreter))
        print("Inputs: {0}".format(task.inputs))
        print("Outputs: {0}".format(task.outputs))
        print("Code:")
        for line in task.code:
            print("{0}".format(line))
    print("**************************************")
