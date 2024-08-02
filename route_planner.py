from queue import PriorityQueue
from math import inf
import random
from ski_resorts import ski_resorts, ski_resort, node, ski_lift, run

class Plan_route():
    def __init__(self,ski_resort,start,length,start_time):
        self._ski_resort_object = ski_resort
        self._ski_resort = ski_resort.nodes
        self._start = start
        self._length = self._hours_to_minutes(length)
        self._ski_resort_object.time = start_time
        self._ski_resort_object.check_open()



    def _hours_to_minutes(self,time):
        h,m = time.split(":")
        return int(h)*60 + int(m)

    def _djikstras_traversal(self,start):
        queue = PriorityQueue()
        keys = (self._ski_resort.keys())
        values = (inf for i in range(len(self._ski_resort)))
        distances = dict(zip(keys,values))
        visited = set()
        previous_node = dict()

        distances[start] = 0
        queue.put((0,start))

        while not queue.empty():
            #BFS algorithm with priority queue of (distance,node) tuple
            dist, v = queue.get()

            if v in visited:
                continue
            visited.add(v)

            for edge in self._ski_resort[v].runs:
                if edge.name not in visited:
                    distances[edge.name] = min(edge.length+dist,distances[edge.name])
                    if edge.length+dist <= distances[edge.name]:
                        previous_node[edge.name] = v
                    queue.put((distances[edge.name],edge.name))

        return distances, previous_node
    

    def get_route(self):
        time_elapsed = 0
        complete = False
        route = [{"start":self._start,"time_elapsed":0}]
        chosen_node = self._ski_resort[self._start]

        while complete == False:
            
            adjacent_nodes = self._ski_resort[chosen_node.name].runs
            priorities = []
            values = []

            for node in adjacent_nodes:
                value = 0
                temp_time_elapsed = time_elapsed + node.length
                adjacent_nodes_1 = self._ski_resort[node.name].runs

                for node_1 in adjacent_nodes_1:
                    value1 = value + 0
                    temp_time_elapsed1 = temp_time_elapsed + node_1.length
                    adjacent_nodes_2 = self._ski_resort[node_1.name].runs

                    for node_2 in adjacent_nodes_2:
                        value2 = value1 + 0
                        temp_time_elapsed2 = temp_time_elapsed1 + node_2.length
                        times,prev = self._djikstras_traversal(node_2.name)
                        time_from_start = times[self._start]
                        time_value = 0
                        time_value = self._length - temp_time_elapsed2 - time_from_start
                        if time_value < 0:
                            values.append(time_value)
                        else:
                            values.append(value2)
                priorities.append(max(values))


            if max(priorities) < 0 and chosen_node.name == self._start:
                
                #No set of three moves is viable however this checks if a set of two moves is still viable
                priorities_for_double = []
                for node in adjacent_nodes:
                    value = 0
                    temp_time_elapsed = time_elapsed + node.length
                    adjacent_nodes_1 = self._ski_resort[node.name].runs

                    for node_1 in adjacent_nodes_1:
                        value1 = value + 0
                        temp_time_elapsed1 = temp_time_elapsed + node_1.length
                        times,prev = self._djikstras_traversal(node_1.name)
                        time_from_start = times[self._start]
                        time_value = 0
                        time_value = self._length - temp_time_elapsed1 - time_from_start
                        if time_value < 0:
                            priorities_for_double.append(time_value)
                        else:
                            priorities_for_double.append(value1)

                    priorities_for_double.append(-inf)

                if priorities_for_double.count(max(priorities_for_double)) == 1:
                    index_choice = priorities_for_double.index(max(priorities_for_double))

                    inf_num = 0
                    count = 0
                    divides = []
                    while count < index_choice:
                        value = priorities_for_double[count]
                        if value == -inf:
                            divides.append(count)
                            inf_num += 1
                        count += 1
                    chosen_node_1 = adjacent_nodes[inf_num]
                    adjacent_nodes_double = self._ski_resort[chosen_node_1.name].runs
                    if len(divides) == 0:
                        chosen_node_2 = adjacent_nodes_double[index_choice]
                    else:
                        chosen_node_2 = adjacent_nodes_double[index_choice - divides[-1] - 1]

                else: #randomly choose between the nodes with the same priority
                    number_of_maximums = priorities_for_double.count(max(priorities_for_double))
                    choice = random.randint(1,number_of_maximums)
                    count = 0
                    for i,item in enumerate(priorities_for_double):
                        if item == max(priorities_for_double):
                            count += 1
                            if count == choice:
                                index_choice = i
                                break
                    
                    inf_num = 0
                    count = 0
                    divides = []
                    while count < index_choice:
                        value = priorities_for_double[count]
                        if value == -inf:
                            divides.append(count)
                            inf_num += 1
                        count += 1
                    chosen_node_1 = adjacent_nodes[inf_num]
                    adjacent_nodes_double = self._ski_resort[chosen_node_1.name].runs
                    if len(divides) == 0:
                        chosen_node_2 = adjacent_nodes_double[index_choice]
                    else:
                        chosen_node_2 = adjacent_nodes_double[index_choice - divides[-1] - 1]

                if max(priorities_for_double) >= 0: #if the two moves are viable add them to the route
                    time_elapsed += chosen_node_1.length
                    route.append({"start":chosen_node_1.name,"time_elapsed":time_elapsed})
                    self._ski_resort_object.increment_time(chosen_node.length)
                    time_elapsed += chosen_node_2.length
                    route.append({"start":chosen_node_2.name,"time_elapsed":time_elapsed})
                    self._ski_resort_object.increment_time(chosen_node.length)   

                complete = True #end the route generation

            elif max(priorities) < 0: #If no set of three moves is viable but the route has not returned to the start node
                #find shortest way back
                times,previous_node = self._djikstras_traversal(chosen_node.name)
                
                route_to_finish = []
                current = self._start
                route_to_finish.insert(0,current)
                while current != chosen_node.name:
                    current = previous_node[current]
                    route_to_finish.insert(0,current)
                
                for i in range(len(route_to_finish)-1):
                    time_elapsed += self._ski_resort[route_to_finish[i]].runs[[run.name for run in self._ski_resort[route_to_finish[i]].runs].index(route_to_finish[i+1])].length
                    route.append({"start":route_to_finish[i+1],"time_elapsed":time_elapsed})

                complete = True
            

            else: #if a set of three moves is viable
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

                time_elapsed += chosen_node.length
                route.append({"start":chosen_node.name,"time_elapsed":time_elapsed})
                self._ski_resort_object.increment_time(chosen_node.length)


        return route



if __name__ == "__main__":
    example = ski_resorts()
    example.add_resort("Val Thorens")
    example.resorts["Val Thorens"].add_lift("Plein Sud bottom")
    example.resorts["Val Thorens"].nodes["Plein Sud bottom"].add_run("Plein Sud top",10)
    example.resorts["Val Thorens"].add_lift("Plein Sud top")
    example.resorts["Val Thorens"].nodes["Plein Sud top"].add_run("Pionniers bottom",5)
    example.resorts["Val Thorens"].nodes["Plein Sud top"].add_run("Pionniers top",1)
    example.resorts["Val Thorens"].add_lift("3 Vallees bottom")
    example.resorts["Val Thorens"].nodes["3 Vallees bottom"].add_run("Plein Sud bottom",15)
    example.resorts["Val Thorens"].nodes["3 Vallees bottom"].add_run("3 Vallees top",6)
    example.resorts["Val Thorens"].add_lift("3 Vallees top")
    example.resorts["Val Thorens"].nodes["3 Vallees top"].add_run("3 Vallees bottom",5)
    example.resorts["Val Thorens"].nodes["3 Vallees top"].add_run("Plein Sud top",4)
    example.resorts["Val Thorens"].add_lift("Pionniers bottom")
    example.resorts["Val Thorens"].nodes["Pionniers bottom"].add_run("Plein Sud bottom",10)
    example.resorts["Val Thorens"].nodes["Pionniers bottom"].add_run("Pionniers top",4)
    example.resorts["Val Thorens"].add_lift("Pionniers top")
    example.resorts["Val Thorens"].nodes["Pionniers top"].add_run("3 Vallees bottom",1)

    print(Plan_route(example.resorts["Val Thorens"],"Plein Sud bottom","00:35").get_route())
    #print(Plan_route(example.resorts["Val Thorens"],"Plein Sud bottom","00:50")._djikstras_traversal("3 Vallees top"))








#Create my own priority queue class