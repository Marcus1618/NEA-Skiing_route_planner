from queue import PriorityQueue
from math import inf

class Plan_route():
    def __init__(self,ski_resort,start,length):
        self._ski_resort = ski_resort
        self._start = start
        self._length = length

    def djikstras_traversal(self):
        queue = PriorityQueue()
        keys = (self._ski_resort.keys())
        values = (inf for i in range(len(self._ski_resort)))
        distances = dict(zip(keys,values))
        visited = set()

        distances[self._start] = 0
        queue.put((0,self._start))

        while not queue.empty():
            #BFS algorithm with priority queue of (distance,node) tuple
            dist, v = queue.get()

            if v in visited:
                continue
            visited.add(v)

            for edge in self._ski_resort[v]:
                if edge[0] not in visited:
                    distances[edge[0]] = min(edge[1]["length"]+dist,distances[edge[0]])
                    queue.put((edge[1]["length"],edge[0]))

        return distances


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

    print(Plan_route(ski_resorts["Val Thorens"],"Plein Sud top",3).djikstras_traversal())







#Create my own priority queue class