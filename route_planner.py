from queue import PriorityQueue
from math import inf
import random

class Plan_route():
    def __init__(self,ski_resort,start,length):
        self._ski_resort = ski_resort
        self._start = start
        self._length = length #FORMAT

    def djikstras_traversal(self,start):
        queue = PriorityQueue()
        keys = (self._ski_resort.keys())
        values = (inf for i in range(len(self._ski_resort)))
        distances = dict(zip(keys,values))
        visited = set()

        distances[start] = 0
        queue.put((0,start))

        while not queue.empty():
            #BFS algorithm with priority queue of (distance,node) tuple
            dist, v = queue.get()

            if v in visited:
                continue
            visited.add(v)

            for edge in self._ski_resort[v]:
                if edge[0] not in visited:
                    distances[edge[0]] = min(edge[1]["length"]+dist,distances[edge[0]])
                    queue.put((distances[edge[0]],edge[0]))

        return distances
    
    def get_route(self):
        total_time = 0
        complete = False
        route = [[self._start,{"length":0}]]
        chosen_node = [self._start,{"length":0}]

        while complete == False:
            times = self.djikstras_traversal(chosen_node[0])
            time_from_start = times[self._start]


            adjacent_nodes = self._ski_resort[self._start]
            priorities = []
            for i in range(len(adjacent_nodes)):
                priorities.append(random.randint(1,10000)) #There is a possibility of same priority here!!!

            chosen_node = adjacent_nodes[priorities.index(max(priorities))]
            previos_total_time = total_time
            total_time += chosen_node[1]["length"]
            route.append(chosen_node)

            if total_time > self._length:
                if total_time - self._length > self._length - previos_total_time:
                    route.pop()
                complete = True
        
        return route



if __name__ == "__main__":
    ski_resorts = {
        "Val Thorens" : {
            "Plein Sud bottom": [["Plein Sud top",{"length":10}]],
            "Plein Sud top": [["Pionniers bottom",{"length":5}],["Pionniers top",{"length":1}]],
            "3 Vallees bottom": [["Plein Sud bottom",{"length":15}],["3 Vallees top",{"length":6}]],
            "3 Vallees top": [["3 Vallees bottom",{"length":5}],["Plein Sud top",{"length":4}]],
            "Pionniers bottom": [["Plein Sud bottom",{"length":10}],["Pionniers top",{"length":4}]],
            "Pionniers top": [["3 Vallees bottom",{"length":1}]]
            }
    }

    print(Plan_route(ski_resorts["Val Thorens"],"Plein Sud top",10).get_route())







#Create my own priority queue class