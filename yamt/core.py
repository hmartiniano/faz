import os
import glob
import shlex
import tempfile
import subprocess
import networkx as nx


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


def parser(text):
    """ Very crude parser for a file with syntax somewhat similar to Drake."""
    tasks = []
    code = []
    comments = []
    task_found = False
    for line in text.splitlines():
        if line.startswith("#"):
            if task_found:
                tasks.append(
                    Task(interpreter, inputs, outputs, code, comments))
                comments = []
            if "<-" in line:
                interpreter = "bash"
                inputs = []
                outputs = []
                code = []
                lexer = shlex.shlex(line[1:])
                tokens = [token for token in lexer]
                print tokens
                found = False
                found_interpreter = False
                for token in tokens:
                    if "]" in token:
                        break
                    elif found_interpreter:
                        interpreter = token
                        found_interpreter = False
                    elif "[" in token:
                        found_interpreter = True
                    elif "<" in token or "-" in token:
                        found = True
                    elif "," in token:
                        continue
                    elif found:
                        inputs.append(token)
                    else:
                        outputs.append(token)
                task_found = True
            else:
                comments.append(line[1:])
                task_found = False
        else:
            code.append(line)
    if task_found:
        tasks.append(Task(interpreter, inputs, outputs, code, comments))
    return tasks


def parser(text):
    """ Very crude parser for a file with syntax somewhat similar to Drake."""
    tasks = []
    code = []
    comments = []
    task_found = False
    for line in text.splitlines():
        line = line.strip()
        if line.startswith("#"):
            if task_found:
                tasks.append(
                    Task(interpreter, inputs, outputs, code, comments))
                comments = []
            if "<-" in line:
                if "[python]" in line:
                    interpreter = "python"
                elif "[ruby]" in line:
                    interpreter = "ruby"
                else:
                    interpreter = "bash"
                line = line.replace("[" + interpreter + "]", "")
                outputs, inputs = line[1:].split("<-")
                print inputs, outputs
                inputs = [item.strip() for item in inputs.split(",")]
                outputs = [item.strip() for item in outputs.split(",")]
                inputs = [item for item in inputs if not(item == "")]
                outputs = [item for item in outputs if not(item == "")]
                print inputs, outputs
                task_found = True
                code = []
            else:
                comments.append(line[1:])
                task_found = False
        else:
            code.append(line)
    if task_found:
        tasks.append(Task(interpreter, inputs, outputs, code, comments))
    return tasks


def expand_filenames(filenames):
    results = []
    for filename in filenames:
        if "*" in filename:
            results.extend(glob.glob(filename))
        else:
            results.append(filename)
    results.sort()
    return results


def dependency_graph(tasks):
    """ Produce a dependency graph based on a list of tasks produced by the parser."""
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


def show_graph(graph, tasks):
    for node in nx.topological_sort(graph):
        print node, tasks[node]
        print "Predecessors:", graph.predecessors(node)


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


def files_exist(filenames):
    """ Check if all files in a given list exist. """
    return all([os.path.exists(filename) and os.path.isfile(filename) for filename in filenames])


def dependencies_are_newer(files, dependencies):
    """ For two lists of files, check if any file in the second list is newer than any file of the first. """
    dependency_mtimes = [
        os.path.getmtime(filename) for filename in dependencies]
    file_mtimes = [os.path.getmtime(filename) for filename in files]
    results = []
    for file_mtime in file_mtimes:
        for dependency_mtime in dependency_mtimes:
            if dependency_mtime > file_mtime:
                results.append(True)
            else:
                results.append(False)
    return any(results)


def main(filename):
    tasks = parser(open(filename).read())
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
    import sys
    main(sys.argv[1])
