import numpy as np
import networkx as nx
import matplotlib.pyplot as plt
from itertools import product
from random import randint
import os

import my_networkx as my_nx
from giftools import render

class Automata:
    def __init__(self, initial, accept, symbols, graph = None, state_count = 5):
        self.initial = initial #vector
        self.state = initial
        self.accept = accept #states where the outcome is accepted
        self.symbols = symbols #alphabet that the language is constructed from

        if graph == None: #constructs a random graph if none is supplied
            graph = nx.DiGraph()
            graph.add_nodes_from([x+1 for x in range(state_count)])
            for node in graph.nodes:
                for letter in symbols:
                    graph.add_edges_from([(node, randint(1,state_count),{'w':letter})])
            self.graph = graph
        else:
            self.state_count = len(graph.nodes)
            self.graph = graph #underlying graph of the automata, nodes are unit vectors, edges already weighted with symbols

    def decide(self, word, show_trace = False):
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

        for n in range(max_length+1):
            language = language + self.enumerate_words(n)

        return language

    def linearize(self): #returns dictionary of linear maps indexed by the alphabet which acts as the automata on the standard basis vectors
        system = {}
        edge_weights = nx.get_edge_attributes(self.graph,'w')

        for letter in self.symbols:
            system[letter] = np.zeros((self.state_count,self.state_count))
        for edge in self.graph.edges:
            elem = np.zeros((self.state_count,self.state_count))
            elem[edge[1]-1][edge[0]-1] = 1
            system[edge_weights[edge]] += elem

        return system

    def plot(self, label, distinguished = [], show = False, color = 'green'):
        figure = my_nx.plot_graph(self.graph, label, distinguished, color)
        if show:
            plt.show()
        figure.savefig("frames/" + label + ".png", bbox_inches='tight',pad_inches=0)
        plt.close()


G = nx.DiGraph()
G.add_edges_from([(1,2,{'w':'a'}),(1,3,{'w':'b'}),(3,1,{'w':'a'}),(2, 2,{'w':'b'}),(3,3,{'w':'b'}),(2,3,{'w':'a'})])

test = Automata(1,[1],['a','b'],G)
#print(test.decide('baabaaa', True))
#print(test.enumerate_language(5))
test.plot("test")
print(test.linearize())

#test = Automata(1,[1],{'a','b','c'})
#test.plot('figure')
#test.decide('abcabcabc',True)
#print(test.enumerate_language(6))
