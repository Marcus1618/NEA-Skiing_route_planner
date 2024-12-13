import networkx as nx 
import matplotlib.pyplot as plt
 
class Display_graph():
   
    def __init__(self):
        self.__edges = []

    def __add_edge(self, x, y): #adds edge between nodes x and y
        edge = [x, y]
        self.__edges.append(edge) 

    def __visualise(self): #Creates a visual graph from a set of edges
        G = nx.DiGraph()
        G.add_edges_from(self.__edges,arrowstyle='->') #need to know direction of run
        nx.draw_networkx(G)
        plt.show()

    def display_ski_resort(self,ski_resort_object): #Formats the ski resort object into a set of edges that can be displayed
        for node in ski_resort_object.nodes.values():
            for run in node.runs:
                self.__add_edge(node.name, run.name) #add colour of run to edge!!!
        self.__visualise()