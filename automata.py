import numpy as np
import networkx as nx
import matplotlib.pyplot as plt
from itertools import product
from random import randint
import os

import my_networkx as my_nx
from giftools import render

class Automaton:
    def __init__(self, initial = 1, accept = [1], symbols = None, graph = None, state_count = 1, state_table = None):
        self.initial = initial #vector
        self.state = initial
        self.accept = accept #states where the outcome is accepted
        self.symbols = symbols #alphabet that the language is constructed from

        if (graph is None) and (state_table is None): #constructs a random graph on state_count many vertices if none is supplied
            graph = nx.DiGraph()
            graph.add_nodes_from([x+1 for x in range(state_count)])
            for node in graph.nodes:
                for letter in symbols:
                    graph.add_edges_from([(node, randint(1,state_count),{'w':letter})])
            self.graph = graph
        elif (graph is None): #constructor from state table
            self.state_count = len(state_table)
            self.symbols = [chr(ord('a') + x) for x in range(len(state_table[0]))]
            graph = nx.DiGraph()
            graph.add_nodes_from([(x+1) for x in range(self.state_count)])
            for source in graph.nodes:
                for letter in range(len(self.symbols)):
                    graph.add_edges_from([(source, state_table[source-1][letter], {'w':chr(ord('a') + letter)})])
            self.graph = graph
        else:
            self.state_count = len(graph.nodes)
            self.graph = graph #underlying graph of the automata, nodes integers, edges already weighted with symbols

    def decide(self, word, show_trace = False): #returns true when the automata accepts the word after iterating
        self.state = self.initial
        count = 0
        for letter in word:
            if show_trace:
                print(self.state)
                if count == 0:
                    self.plot(str(count),[self.state], color = 'white')
                    count += 1
                    self.plot(str(count),[self.state])
                else:
                    self.plot(str(count),[self.state], color = 'white')
                    count += 1
                    self.plot(str(count),[self.state], color = 'blue')
            for node in self.graph.succ[self.state]:
                if self.graph[self.state][node]['w'] == letter:
                    self.state = node
                    break
                else:
                    pass
            count += 1
        if show_trace:
            print(self.state)
            self.plot(str(count),[self.state], color = 'white')
            count += 1
            self.plot(str(count),[self.state], color = 'red')
            count += 1
            self.plot(str(count),[self.state], color = 'white')

            directory = 'frames/'
            frames = []

            for filename in os.listdir(directory):
                frames.append((int(filename[:-4]),'frames/' + filename))

            frames = sorted(frames)
            print(frames)

            render([y for (x,y) in frames], "test", frame_duration = 0.5)

        if self.state in self.accept:
            return True
        else:
            return False

    def enumerate_words(self, length):
        free_set = [''.join(x) for x in product(''.join(self.symbols), repeat=length)]

        language = []

        for word in free_set:
            if self.decide(word) == True:
                language.append(word)

        return language

    def enumerate_language(self, max_length):
        language = []

        for n in range(max_length):
            language = language + self.enumerate_words(n+1)

        return language

    def linearize(self): #returns dictionary of linear maps indexed by the alphabet which acts as the automata on the standard basis vectors
        system = {}
        edge_weights = nx.get_edge_attributes(self.graph,'w')

        for letter in self.symbols:
            system[letter] = np.zeros((self.state_count,self.state_count), dtype=int)

        for edge in self.graph.edges:
            elem = np.zeros((self.state_count,self.state_count), dtype=int)
            elem[edge[1]-1][edge[0]-1] = 1
            system[edge_weights[edge]] += elem

        return system

    def state_transition_table(self):
        edge_weights = nx.get_edge_attributes(self.graph,'w')
        table = np.zeros((self.state_count,len(self.symbols)), dtype=int)
        for edge in self.graph.edges:
            table[edge[0]-1][self.symbols.index(edge_weights[edge])] = edge[1]
        return table

    def plot(self, label, distinguished = [], show = False, color = 'green'):
        figure = my_nx.plot_graph(self.graph, label, distinguished, color)
        if show:
            plt.show()
        figure.savefig("frames/" + label + ".png", bbox_inches='tight',pad_inches=0)
        plt.close()
