import networkx as nx 
import matplotlib.pyplot as plt
 
class Display_graph():
   
    def __init__(self):
        self.__edges = []

    def __add_edge(self, x, y, z): #adds edge between nodes x and y
        edge = (x, y, z)
        self.__edges.append(edge)

    def __visualise(self, ski_resort_object): #Creates a visual graph from a set of edges
        G = nx.DiGraph()
        G.add_edges_from(self.__edges)
        colours_list = []
        nodes = list(G.nodes())
        for node in nodes:
            node_object = ski_resort_object.nodes[node]
            if node_object.__class__.__name__ == "Ski_node":
                colours_list.append("blue")
            elif node_object.__class__.__name__ == "Amenity":
                colours_list.append("green")
            elif node_object.__class__.__name__ == "Ski_park":
                colours_list.append("red")
                
        options = {
            "edge_color": [G[u][v]["color"] for u, v in G.edges()],
            "style": [G[u][v]["style"] for u, v in G.edges()],
            "width": [G[u][v]["width"] for u, v in G.edges()],
            "node_color": colours_list,
        }
        nx.draw_networkx(G, **options)
        for _, _, data in G.edges(data=True):
            data["alpha"] = 0.5
        plt.show()

    def display_ski_resort(self,ski_resort_object): #Formats the ski resort object into a set of edges that can be displayed
        for node in ski_resort_object.nodes.values():
            for run in node.runs:
                if run.lift:
                    self.__add_edge(node.name, run.name, {"color": "black", "style": "dashed", "width": 2, "alpha": 0.5})
                else:
                    self.__add_edge(node.name, run.name, {"color": run.difficulty.lower(), "style": "solid", "width": 1, "alpha": 1})
        self.__visualise(ski_resort_object)