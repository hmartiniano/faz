import os
import shlex
import tempfile
import subprocess
import networkx as nx


class FubarException(Exception):
    pass


def parser(text):
    """ Very crude parser for afile with syntax similar to Drake."""
    tasks = []
    code = []
    task_found = False
    for line in text.splitlines():
        if line.startswith("#"):
            interpreter = "bash"
            if task_found:
                tasks.append((interpreter, inputs, outputs, code))
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
            code.append(line)
    if task_found:
        tasks.append((interpreter, inputs, outputs, code))
    return tasks


def dependency_graph(tasks):
    """ Produce a dependency graph based on a list of tasks produced by the parser."""
    graph = nx.MultiDiGraph()
    for i in range(len(tasks)):
        graph.add_node(i)
    for node1 in graph.nodes():
        for node2 in graph.nodes():
            for input in tasks[node1][1]:
                for output in tasks[node2][2]:
                    if output == input:
                        graph.add_edge(node2, node1)
#    for interpreter, inputs, outputs, code in tasks:
#        node_name = ", ".join(outputs) + " <- " + ", ".join(inputs)
#        graph.add_node(node_name, interpreter=interpreter, inputs=inputs, outputs=outputs, code=code)
#        graph[node_name]["interpreter"] = interpreter
#        graph[node_name]["inputs"] = inputs
#        graph[node_name]["outputs"] = outputs
#        graph[node_name]["code"] = code
#    for node1 in graph.nodes():
#        for node2 in graph.nodes():
#            for input in graph[node1]["inputs"]:
#                for output in graph[node2]["outputs"]:
#                    if output == input:
#                        graph.add_edge(node2, node1)
    return graph


def show_graph(graph, tasks):
    for node in nx.topological_sort(graph):
        print node, tasks[node]
        print "Predecessors:", graph.predecessors(node)
        #print "Antecesssors:", graph.antecessors(node)
        #print dir(graph[node])


def mktemp_dir():
    """ Check if the '.yamt' directory exists and create it if necessary.
        If a file exists with the same name raise an exception. """
    if not(os.path.exists(".yamt")):
        os.mkdir("./yamt")
    elif not(os.path.isdir(".yamt")):
        raise FubarException("there is a file called .yamt in this directory!!!")


def mktemp_file(dirname=".yamt"):
    """ Create a temporary file in the '.yamt' directory for the code to feed to the interpreter. """
    if not(os.path.exists(dirname)):
        os.mkdir(dirname)
    elif not(os.path.isdir(dirname)):
        raise FubarException("There is a file called %s in this directory!!!" % dirname)
    fd, fname = tempfile.mkstemp(dir=dirname, text=True)
    return fd, fname


def execute_task(interpreter, inputs, outputs, code):
    """ Invoque an interpreter to execute the code of a given task. """
    fd, fname = mktemp_file()
    os.write(fd, "\n".join(code) + "\n")
    out = subprocess.check_output([interpreter, fname])
    print out
    os.close(fd)
    os.unlink(fname)


def execute(graph, tasks):
    """ Given a dependency graph check inputs and outputs and execute tasks. """
    for node in nx.topological_sort(graph):
        print node, tasks[node]
        interpreter = tasks[node][0]
        inputs = tasks[node][1]
        outputs = tasks[node][2]
        code = tasks[node][3]
        if files_exist(inputs):
            if files_exist(outputs):
                if dependencies_are_newer(outputs, inputs):
                    print "Dependencies are newer than outputs. Running task"
                    execute_task(interpreter, inputs, outputs, code)
                else:
                    print "Ouputs exist and are older than inputs."
            else:
                print "No ouputs. Running task."
                execute_task(interpreter, inputs, outputs, code)
        else:
            print "Not executing task. Input files do not exist."


def files_exist(filenames):
    """ Check if all files in a given list exist. """
    return all([os.path.exists(filename) and os.path.isfile(filename) for filename in filenames])


def dependencies_are_newer(files, dependencies):
    """ For two lists of files, check if any file in the second list is newer than any file o the first. """
    dependency_mtimes = [os.path.getmtime(filename) for filename in dependencies]
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
        print task
    graph = dependency_graph(tasks)
    for node in graph.nodes():
        print node
        print tasks[node]
    show_graph(graph, tasks)
    execute(graph, tasks)


if __name__ == '__main__':
    import sys
    main(sys.argv[1])
