from queue import PriorityQueue
from math import inf
import random

class Plan_route():
    def __init__(self,ski_resort,start,length):
        self._ski_resort = ski_resort
        self._start = start
        self._length = self._hours_to_minutes(length)

    def _hours_to_minutes(self,time):
        h,m = time.split(":")
        return int(h)*60 + int(m)

    def _djikstras_traversal(self,start):
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
        time_elapsed = 0
        complete = False
        route = [[self._start,{"length":0}]]
        chosen_node = [self._start,{"length":0}]

        while complete == False:

            adjacent_nodes = self._ski_resort[chosen_node[0]]
            priorities = []
            values = []

            for node in adjacent_nodes:
                value = 0
                temp_time_elapsed = time_elapsed + node[1]["length"]
                adjacent_nodes_1 = self._ski_resort[node[0]]

                for node_1 in adjacent_nodes_1:
                    value1 = 0
                    temp_time_elapsed += node_1[1]["length"]
                    value1 = value + 0
                    adjacent_nodes_2 = self._ski_resort[node_1[0]]

                    for node_2 in adjacent_nodes_2:
                        value2 = 0
                        temp_time_elapsed += node_2[1]["length"]
                        temp = 0
                        times = self._djikstras_traversal(node_2[0])
                        time_from_start = times[self._start]
                        if time_from_start > self._length - temp_time_elapsed:
                            temp = self._length - temp_time_elapsed - time_from_start
                        value2 = value1 + temp
                        values.append(value2)

                priorities.append(max(values))

            #MEED TO PUT THIS TO THE END
            if priorities.count(max(priorities)) == 1:
                chosen_node = adjacent_nodes[priorities.index(max(priorities))]
            else: #randomly choose between the nodes with the same priority
                number_of_maximums = priorities.count(max(priorities))
                choice = random.randint(1,number_of_maximums)
                count = 0
                for i,item in enumerate(priorities):
                    if item == max(priorities):
                        count += 1
                        if count == choice:
                            index_choice = i
                            break
                chosen_node = adjacent_nodes[index_choice]
            #THIS WHOLE BLOCK


            time_elapsed += chosen_node[1]["length"]
            route.append(chosen_node)

            if max(priorities) < 0 and chosen_node[0] == self._start:
                
                #No set of three moves is viable however this checks if a set of two moves is still viable
                adjacent_nodes = self._ski_resort[chosen_node[0]]
                priorities = []
                values = []
                for node in adjacent_nodes:
                    value = 0
                    temp_time_elapsed = time_elapsed + node[1]["length"]
                    adjacent_nodes_1 = self._ski_resort[node[0]]

                    for node_1 in adjacent_nodes_1:
                        value1 = 0
                        temp_time_elapsed += node_1[1]["length"]
                        temp = 0
                        times = self._djikstras_traversal(node_1[0])
                        time_from_start = times[self._start]
                        if time_from_start > self._length - temp_time_elapsed:
                            temp = self._length - temp_time_elapsed - time_from_start
                        value1 = value + temp
                        priorities.append(value1)

                    priorities.append(-inf)

                if priorities.count(max(priorities)) == 1:
                    index_choice = priorities.index(max(priorities))
                    inf_num = 0
                    count = 0
                    divides = []
                    while count < index_choice:
                        value = priorities[count]
                        if value == -inf:
                            divides.append(count)
                            inf_num += 1
                        count += 1
                    chosen_node_1 = adjacent_nodes[inf_num]
                    adjacent_nodes = self._ski_resort[chosen_node_1[0]]
                    if len(divides) == 0:
                        chosen_node_2 = index_choice
                    else:
                        chosen_node_2 = adjacent_nodes[index_choice - divides[-1] - 1]

                else: #randomly choose between the nodes with the same priority
                    number_of_maximums = priorities.count(max(priorities))
                    choice = random.randint(1,number_of_maximums)
                    count = 0
                    for i,item in enumerate(priorities):
                        if item == max(priorities):
                            count += 1
                            if count == choice:
                                index_choice = i
                                break
                    
                    inf_num = 0
                    count = 0
                    divides = []
                    while count < index_choice:
                        value = priorities[count]
                        if value == -inf:
                            divides.append(count)
                            inf_num += 1
                        count += 1
                    chosen_node_1 = adjacent_nodes[inf_num]
                    adjacent_nodes = self._ski_resort[chosen_node_1[0]]
                    if len(divides) == 0:
                        chosen_node_2 = index_choice
                    else:
                        chosen_node_2 = adjacent_nodes[index_choice - divides[-1] - 1]

                if max(priorities) >= 0: #if the two moves are viable add them to the route
                    time_elapsed += chosen_node_1[1]["length"]
                    time_elapsed += chosen_node_2[1]["length"]
                    route.append(chosen_node_1)
                    route.append(chosen_node_2)     

                complete = True #end the route generation
        
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

    print(Plan_route(ski_resorts["Val Thorens"],"3 Vallees top","00:11").get_route())







#Create my own priority queue class