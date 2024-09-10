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
    
    def compare_greater(self,t1,t2):
        #Is time t1 greater than time t2
        h1, m1 = t1.split(":")
        h2, m2 = t2.split(":")
        if int(h1) > int(h2):
            return True
        elif int(h1) == int(h2) and int(m1) > int(m2):
            return True
        else:
            return False

    def _djikstras_traversal(self,start,time_update=False):
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
            if time_update:
                self._ski_resort_object.increment_time(dist)

            for edge in self._ski_resort[v].runs:
                if edge.name not in visited:
                    distances[edge.name] = min(edge.length+dist,distances[edge.name])
                    if edge.length+dist <= distances[edge.name]:
                        previous_node[edge.name] = v
                    queue.put((distances[edge.name],edge.name))
            if time_update:
                self._ski_resort_object.decrement_time(dist)

        return distances, previous_node
    
    def two_move_route(self,adjacent_nodes,time_elapsed,route, due_to_closing=False):
        priorities_for_double = []
        for node in adjacent_nodes:
            value = 0
            temp_time_elapsed = time_elapsed + node.length
            adjacent_nodes_1 = self._ski_resort[node.name].runs
            self._ski_resort_object.increment_time(node.length)

            single_priorities = []
            for node_1 in adjacent_nodes_1:
                value1 = value + 0
                temp_time_elapsed1 = temp_time_elapsed + node_1.length
                times,prev = self._djikstras_traversal(node_1.name)
                time_from_start = times[self._start]
                time_value = 0
                time_value = self._length - temp_time_elapsed1 - time_from_start
                if due_to_closing:
                    single_priorities.append(time_value)
                else:
                    if time_value < 0:
                        single_priorities.append(time_value)
                    else:
                        single_priorities.append(value1)

            priorities_for_double.append(single_priorities)
            self._ski_resort_object.decrement_time(node.length)

        if priorities_for_double.count(max(max(priorities_for_double))) == 1:
            chosen_node_1 = adjacent_nodes[priorities_for_double.index(max(priorities_for_double))]
            adjacent_nodes_double = self._ski_resort[chosen_node_1.name].runs
            chosen_node_2 = adjacent_nodes_double[priorities_for_double[priorities_for_double.index(max(priorities_for_double))].index(max(priorities_for_double))]

        else: #randomly choose between the nodes with the same priority
            number_of_maximums = 0
            for item in priorities_for_double:
                if max(max(priorities_for_double)) in item:
                    number_of_maximums += 1
            choice = random.randint(1,number_of_maximums)
            count = 0
            for i,item in enumerate(priorities_for_double):
                for o,num in enumerate(item):
                    if num == max(max(priorities_for_double)):
                        count += 1
                        if count == choice:
                            index_1 = i
                            index_2 = o
                            break

            chosen_node_1 = adjacent_nodes[index_1]
            adjacent_nodes_double = self._ski_resort[chosen_node_1.name].runs
            chosen_node_2 = adjacent_nodes_double[index_2]

        if max(max(priorities_for_double)) >= 0: #if the two moves are viable add them to the route
            time_elapsed += chosen_node_1.length
            route.append({"start":chosen_node_1.name,"time_elapsed":time_elapsed,"pause":False})
            self._ski_resort_object.increment_time(chosen_node_1.length)
            time_elapsed += chosen_node_2.length
            route.append({"start":chosen_node_2.name,"time_elapsed":time_elapsed,"pause":False})
            self._ski_resort_object.increment_time(chosen_node_2.length)

        return route
    
    def one_move_route(self,adjacent_nodes,time_elapsed,route):
        priorities = []
        for node in adjacent_nodes:
            temp_time_elapsed = time_elapsed + node.length
            times,prev = self._djikstras_traversal(node.name)
            time_from_start = times[self._start]
            time_value = 0
            time_value = self._length - temp_time_elapsed - time_from_start
            priorities.append(time_value)

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

        if max(priorities) >= 0:
            time_elapsed += chosen_node.length
            route.append({"start":chosen_node.name,"time_elapsed":time_elapsed,"pause":False})
            self._ski_resort_object.increment_time(chosen_node.length)

        return route

    def get_route(self):
        time_elapsed = 0
        complete = False
        route = [{"start":self._start,"time_elapsed":0,"pause":False}]
        chosen_node = self._ski_resort[self._start]
        returned_to_start = True
        previous_route_length = self._length

        while complete == False:
            
            adjacent_nodes = self._ski_resort[chosen_node.name].runs
            priorities = []
            values = []

            for node in adjacent_nodes:
                value = 0
                temp_time_elapsed = time_elapsed + node.length
                adjacent_nodes_1 = self._ski_resort[node.name].runs
                self._ski_resort_object.increment_time(node.length)

                for node_1 in adjacent_nodes_1:
                    value1 = value + 0
                    temp_time_elapsed1 = temp_time_elapsed + node_1.length
                    adjacent_nodes_2 = self._ski_resort[node_1.name].runs
                    self._ski_resort_object.increment_time(node_1.length)

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
                        print(node_2.name)
                    self._ski_resort_object.decrement_time(node_1.length)
                self._ski_resort_object.decrement_time(node.length)
                priorities.append(max(values))
                print(node.name,values,max(values))


            if max(priorities) == -inf:
                continue_route = False
                for run in adjacent_nodes: #Determines if there is a 3 move route  that will be able to be taken in the future
                    if self.compare_greater(run.opening, self._ski_resort_object.time) or (self.compare_greater(self._ski_resort_object.time, run.opening) and self.compare_greater(run.closing, self._ski_resort_object.time)):
                        adjacent_nodes_1 = self._ski_resort[run.name].runs
                        for run_1 in adjacent_nodes_1:
                            if self.compare_greater(run_1.opening, self._ski_resort_object.time) or (self.compare_greater(self._ski_resort_object.time, run.opening) and self.compare_greater(run.closing, self._ski_resort_object.time)):
                                adjacent_nodes_2 = self._ski_resort[run_1.name].runs
                                for run_2 in adjacent_nodes_2:
                                    if self.compare_greater(run_2.opening, self._ski_resort_object.time) or (self.compare_greater(self._ski_resort_object.time, run.opening) and self.compare_greater(run.closing, self._ski_resort_object.time)):
                                        continue_route = True
                                        break
                                if continue_route == True:
                                    break
                        if continue_route == True:
                            break         

                if (len(route) == 1 or previous_route_length + 1 == self._length) and continue_route == True: #If the route hasn't started yet
                    time_elapsed += 1
                    self._ski_resort_object.increment_time(1)
                    if route[-1]["pause"] == False:
                        route.append({"start":chosen_node.name,"time_elapsed":1,"pause":True})
                    else:
                        route[-1]["time_elapsed"] = route[-1]["time_elapsed"] + 1
                    previous_route_length = self._length
                    self._length += 1 #Length of the route is increased by 1 minute to account for the time spent waiting for the ski lifts to open
                
                else: #If the route is stopped by reaching unopened runs
                    
                    if continue_route == True: #If the route can continue since the surrounding runs are yet to open
                        time_elapsed += 1
                        self._ski_resort_object.increment_time(1)
                        if route[-1]["pause"] == False:
                            route.append({"start":chosen_node.name,"time_elapsed":1,"pause":True})
                        else:
                            route[-1]["time_elapsed"] = route[-1]["time_elapsed"] + 1

                    else: #If the route cannot continue
                        due_to_closing = True
                        route = self.two_move_route(adjacent_nodes,time_elapsed,route,due_to_closing)
                        route = self.one_move_route(adjacent_nodes,time_elapsed,route)
                        complete = True #end the route generation
                        if route[-1]["start"] != self._start:
                            returned_to_start = False



            elif max(priorities) < 0 and chosen_node.name == self._start:
                
                #No set of three moves is viable however this checks if a set of two moves is still viable
                route = self.two_move_route(adjacent_nodes,time_elapsed,route)
                complete = True #end the route generation

            elif max(priorities) < 0: #If no set of three moves is viable but the route has not returned to the start node
                #find shortest way back
                times,previous_node = self._djikstras_traversal(chosen_node.name,True)
                
                route_to_finish = []
                current = self._start
                route_to_finish.insert(0,current)
                while current != chosen_node.name:
                    current = previous_node[current]
                    route_to_finish.insert(0,current)
                
                for i in range(len(route_to_finish)-1):
                    run_length = self._ski_resort[route_to_finish[i]].runs[[run.name for run in self._ski_resort[route_to_finish[i]].runs].index(route_to_finish[i+1])].length
                    if run_length != inf:
                        time_elapsed += run_length
                        route.append({"start":route_to_finish[i+1],"time_elapsed":time_elapsed,"pause":False})

                route = self.two_move_route(adjacent_nodes,time_elapsed,route)
                route = self.one_move_route(adjacent_nodes,time_elapsed,route)

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
                route.append({"start":chosen_node.name,"time_elapsed":time_elapsed,"pause":False})
                self._ski_resort_object.increment_time(chosen_node.length)


        return route, returned_to_start



if __name__ == "__main__":
    example = ski_resorts()
    example.add_resort("Val Thorens")
    example.resorts["Val Thorens"].add_lift("Plein Sud bottom")
    example.resorts["Val Thorens"].nodes["Plein Sud bottom"].add_run("Plein Sud top",10, "08:00", "17:00")
    example.resorts["Val Thorens"].add_lift("Plein Sud top")
    example.resorts["Val Thorens"].nodes["Plein Sud top"].add_run("Pionniers bottom",5, "00:00", "23:59")
    example.resorts["Val Thorens"].nodes["Plein Sud top"].add_run("Pionniers top",1, "00:00", "23:59")
    example.resorts["Val Thorens"].add_lift("3 Vallees bottom")
    example.resorts["Val Thorens"].nodes["3 Vallees bottom"].add_run("Plein Sud bottom",15, "00:00", "23:59")
    example.resorts["Val Thorens"].nodes["3 Vallees bottom"].add_run("3 Vallees top",6, "08:30", "16:00")
    example.resorts["Val Thorens"].add_lift("3 Vallees top")
    example.resorts["Val Thorens"].nodes["3 Vallees top"].add_run("3 Vallees bottom",5, "00:00", "23:59")
    example.resorts["Val Thorens"].nodes["3 Vallees top"].add_run("Plein Sud top",4, "00:00", "23:59")
    example.resorts["Val Thorens"].add_lift("Pionniers bottom")
    example.resorts["Val Thorens"].nodes["Pionniers bottom"].add_run("Plein Sud bottom",10, "00:00", "23:59")
    example.resorts["Val Thorens"].nodes["Pionniers bottom"].add_run("Pionniers top",4, "08:00", "16:30")
    example.resorts["Val Thorens"].add_lift("Pionniers top")
    example.resorts["Val Thorens"].nodes["Pionniers top"].add_run("3 Vallees bottom",1, "00:00", "23:59")

    print(Plan_route(example.resorts["Val Thorens"],"Plein Sud bottom","00:35","09:00").get_route())
    #print(Plan_route(example.resorts["Val Thorens"],"Plein Sud bottom","00:50")._djikstras_traversal("3 Vallees top"))








#Create my own priority queue class