import networkx as nx 
import matplotlib.pyplot as plt
 
class Display_graph():
   
    def __init__(self):
        self._edges = []

    def add_edge(self, x, y): #adds edge between nodes a and b
        edge = [x, y]
        self._edges.append(edge) 

    def visualise(self): #Creates a visual graph from a set of edges
        G = nx.DiGraph()
        G.add_edges_from(self._edges,arrowstyle='->') #need to know direction of run
        nx.draw_networkx(G) 
        plt.show()

    def display_ski_resort(self,ski_resort_object): #Displays a chosen ski resort in a graph format
        for node in ski_resort_object.nodes.values():
            for run in node.runs:
                self.add_edge(node.name, run.name) #add colour of run to edge!!!
        self.visualise()