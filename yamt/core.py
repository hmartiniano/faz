# -*- coding: utf-8 -*-
import os
import tempfile
import subprocess
from .utils import expand_filenames, files_exist, dependencies_are_newer


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
        print out
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
                "There is a file called %s in this directory!!!" % self.dirname)
        self.fd, self.fname = tempfile.mkstemp(dir=self.dirname, text=True)

    def __repr__(self):
        return "Interpreter: %s; Inputs: %s; Outputs: %s;" % (self.interpreter, ", ".join(self.inputs), ", ".join(self.outputs))


def execute(graph, tasks):
    """ Given a dependency graph check inputs and outputs and execute tasks. """
    for node in nx.topological_sort(graph):
        task = tasks[node]
        print node, task
        print task.inputs
        print task.outputs
        if files_exist(task.inputs) or len(task.inputs) == 0:
            if files_exist(task.outputs):
                if dependencies_are_newer(task.outputs, task.inputs):
                    print "Dependencies are newer than outputs. Running task."
                    task.execute()
                else:
                    print "Ouputs exist and are older than inputs."
            else:
                print "No ouputs. Running task."
                task.execute()
        else:
            print "Not executing task. Input files do not exist."
