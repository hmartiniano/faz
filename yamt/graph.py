# -*- coding: utf-8 -*-
import networkx as nx


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
