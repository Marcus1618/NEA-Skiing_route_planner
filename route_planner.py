from queue import PriorityQueue
from math import inf

class Plan_route():
    def __init__(self,ski_resort,start,length):
        self._ski_resort = ski_resort
        self._start = start
        self._length = length

    def djikstras_traversal(self):
        queue = PriorityQueue()
        dim = len(self._ski_resort.keys())
        visited = [False] * dim #Needs to be a dictionary not a list
        distances = [inf] * dim

        distances[self._start] = 0
        queue.put(0,self._start)

        while not queue.empty():
            #BFS algorithm with priority queue of (distance,node) tuple
            dist, v = queue.get()

            if visited[v]:
                continue
            visited[v] = True







#Create my own priority queue class