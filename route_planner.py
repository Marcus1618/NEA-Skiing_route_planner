from queue import PriorityQueue
from math import inf

class Plan_route():
    def __init__(self,ski_resort,start,length):
        self._ski_resort = ski_resort
        self._start = start
        self._length = length

    def djikstras_traversal(self):
        queue = PriorityQueue()
        distances = set()
        visited = set()

        distances.add((0,self._start))
        queue.put((0,self._start))

        while not queue.empty():
            #BFS algorithm with priority queue of (distance,node) tuple
            dist, v = queue.get()

            if v in visited:
                continue
            visited.add(v)

            for w, edge in enumerate(self._ski_resort[v]):
                if edge[0] not in visited:
                    queue.put((dist + edge[1]["length"],w)) #Checked up to here
                    distances.add((dist + edge[1]["length"],w))







#Create my own priority queue class