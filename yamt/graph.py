# -*- coding: utf-8 -*-
import networkx as nx


class DependencyGraph(nx.MultiDiGraph):

    def __init__(self, tasks):
        super(DependencyGraph, self).__init__()
        self.tasks = tasks
        self._analyse_tasks()

    def _analyse_tasks(self):
        """ Produce a dependency graph based on a list
            of tasks produced by the parser.
        """
        for i in range(len(self.tasks)):
            self.add_node(i)
        for node1 in self.nodes():
            for node2 in self.nodes():
                for input_file in self.tasks[node1].inputs:
                    for output_file in self.tasks[node2].outputs:
                        if output_file == input_file:
                            self.add_edge(node2, node1)
        tasks = []
        for n, node in enumerate(nx.topological_sort(self)):
            task = self.tasks[node]
            task.predecessors = self.predecessors(node)
            task.order = n
            tasks.append(task)
        self.tasks = tasks

    def show_tasks(self):
        for task in self.tasks:
            print("Task {0}  ******************************".format(task.order))
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

    def execute(self):
        """
        Execute tasks in the graph (already in order).
        """
        for task in self.tasks:
            print(80 * "*")
            task()
            print(80 * "*")
