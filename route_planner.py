from queue import PriorityQueue
from math import inf
import random
from ski_resorts import Ski_resorts, Ski_resort, Node, Ski_node, Run

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
    
    def compare_greater_or_equal(self,t1,t2):
        #Is time t1 greater than or equal to time t2
        h1, m1 = t1.split(":")
        h2, m2 = t2.split(":")
        if int(h1) > int(h2):
            return True
        elif int(h1) == int(h2) and int(m1) >= int(m2):
            return True
        else:
            return False

    def _dijkstras_traversal(self,start,time_independent):
        node_number = self._ski_resort_object.node_number()
        queue = Priority_queue(node_number)
        keys = (self._ski_resort.keys())
        values = (inf for i in range(len(self._ski_resort)))
        distances = dict(zip(keys,values))
        visited = set()
        previous_node = dict()

        distances[start] = 0
        queue.enQueue((0,start))

        while not queue.isEmpty():
            #BFS algorithm with priority queue of (distance,node) tuple
            dist, v = queue.deQueue()

            if v in visited:
                continue
            visited.add(v)
            self._ski_resort_object.increment_time(dist)

            for edge in self._ski_resort[v].runs:
                if edge.name not in visited:
                    if time_independent:
                        edge.length = edge.open_length
                    distances[edge.name] = min(edge.length+dist,distances[edge.name])
                    if edge.length+dist <= distances[edge.name]:
                        previous_node[edge.name] = v
                    queue.enQueue((distances[edge.name],edge.name))
                    if time_independent:
                        self._ski_resort_object.check_open()  
            self._ski_resort_object.decrement_time(dist)

        return distances, previous_node
    
    def two_move_route(self,adjacent_nodes,time_elapsed,route):
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
                times,prev = self._dijkstras_traversal(node_1.name, True)
                time_from_start = times[self._start]
                time_value = 0
                time_value = self._length - temp_time_elapsed1 - time_from_start
                if time_value < 0:
                    single_priorities.append(time_value)
                else:
                    single_priorities.append(value1)

            priorities_for_double.append(single_priorities)
            self._ski_resort_object.decrement_time(node.length)

        maximum = -inf
        index = []
        for count,single in enumerate(priorities_for_double):
            single_maximum = -inf
            single_maximum_index = []
            for i,priority in enumerate(single):
                if priority > single_maximum or i == 0:
                    single_maximum = priority
                    single_maximum_index = [i]
                elif priority == single_maximum:
                    single_maximum_index.append(i)

            if single_maximum > maximum or count == 0:
                maximum = single_maximum
                index = []
                for single_index in single_maximum_index:
                    index.append([count,single_index])
            elif single_maximum == maximum:
                for single_index in single_maximum_index:
                    index.append([count,single_index])
        number_of_maximums = len(index)

        choice = random.randint(0,number_of_maximums-1)
        index_1 = index[choice][0]
        index_2 = index[choice][1]

        chosen_node_1 = adjacent_nodes[index_1]
        adjacent_nodes_double = self._ski_resort[chosen_node_1.name].runs
        chosen_node_2 = adjacent_nodes_double[index_2]

        if maximum >= 0 and chosen_node_2.name == self._start: #if the two moves are viable add them to the route
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
            times,prev = self._dijkstras_traversal(node.name, True)
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
    
    def fastest_route_back(self, chosen_node,time_elapsed,route):
        times,previous_node = self._dijkstras_traversal(chosen_node.name, False)
                
        route_to_finish = []
        current = self._start
        route_to_finish.insert(0,current)
        while current != chosen_node.name:
            current = previous_node[current]
            route_to_finish.insert(0,current)
                
        for i in range(len(route_to_finish)-1):
            run_length = (self._ski_resort[route_to_finish[i]].runs[[run.name for run in self._ski_resort[route_to_finish[i]].runs].index(route_to_finish[i+1])]).length
            if run_length != inf:
                time_elapsed += run_length
                self._ski_resort_object.increment_time(run_length)
                route.append({"start":route_to_finish[i+1],"time_elapsed":time_elapsed,"pause":False})
            else:
                break

        return route

    def _find_values(self,adjacent_nodes,count,temp_time_elapsed, priorities, value, values, ignore_way_home):
        if count >= 2:
            for node_1 in adjacent_nodes:
                temp_time_elapsed += node_1.length
                if ignore_way_home:
                    times, prev = self._dijkstras_traversal(node_1.name, True)
                else:
                    times, prev = self._dijkstras_traversal(node_1.name, False)
                time_from_start = times[self._start]
                time_value = 0
                time_value = self._length - temp_time_elapsed - time_from_start
                node_value = 0 #generate value
                value += node_value
                if time_value < 0:
                    values.append(time_value)
                else:
                    values.append(value)
                temp_time_elapsed -= node_1.length
                value -= 0 #generate value
            count -= 1
            return priorities, values, count
        for node in adjacent_nodes:
            if count == 0:
                values = []
            count += 1
            temp_time_elapsed += node.length
            self._ski_resort_object.increment_time(node.length)
            node_value = 0 #generate value
            value += node_value
            priorities,values,count = self._find_values(self._ski_resort[node.name].runs, count, temp_time_elapsed, priorities, value, values, ignore_way_home)
            value -= node_value
            self._ski_resort_object.decrement_time(node.length)
            temp_time_elapsed -= node.length
            if count == 0:
                priorities.append(max(values))

        count -= 1
        return priorities, values, count
    
    def get_route(self, as_close_to_time):
        time_elapsed = 0
        complete = False
        route = [{"start":self._start,"time_elapsed":0,"pause":False}]
        chosen_node = self._ski_resort[self._start]
        returned_to_start = True
        previous_route_length = self._length

        while complete == False:

            find_priorities = []
            adjacent_nodes = self._ski_resort[chosen_node.name].runs
            count = 0
            temp_time_elapsed = time_elapsed
            value = 0
            values = []
            priorities, values, count = self._find_values(adjacent_nodes,count,temp_time_elapsed, find_priorities, value, values, False)

            if max(priorities) == -inf:
                continue_route = False
                for run in adjacent_nodes: #Determines if there is a 3 move route that will be able to be taken in the future
                    if self.compare_greater(run.opening, self._ski_resort_object.time) or (self.compare_greater_or_equal(self._ski_resort_object.time, run.opening) and self.compare_greater(run.closing, self._ski_resort_object.time)):
                        adjacent_nodes_1 = self._ski_resort[run.name].runs
                        for run_1 in adjacent_nodes_1:
                            if self.compare_greater(run_1.opening, self._ski_resort_object.time) or (self.compare_greater_or_equal(self._ski_resort_object.time, run_1.opening) and self.compare_greater(run_1.closing, self._ski_resort_object.time)):
                                adjacent_nodes_2 = self._ski_resort[run_1.name].runs
                                for run_2 in adjacent_nodes_2:
                                    if self.compare_greater(run_2.opening, self._ski_resort_object.time) or (self.compare_greater_or_equal(self._ski_resort_object.time, run_2.opening) and self.compare_greater(run_2.closing, self._ski_resort_object.time)):
                                        continue_route = True
                                        break
                                if continue_route == True:
                                    break
                        if continue_route == True:
                            break         

                find_priorities = []
                count = 0
                temp_time_elapsed = time_elapsed
                value = 0
                values = []
                priorities, values, count = self._find_values(adjacent_nodes,count,temp_time_elapsed, find_priorities, value, values, True)
                
                times, prev = self._dijkstras_traversal(chosen_node.name, True)
                time_from_start = times[self._start]
                time_value = self._length - time_elapsed - time_from_start

                if max(priorities) >= 0: #do 3 move route
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
                    
                elif max(priorities) != -inf and chosen_node.name == self._start: #try two move route
                    route = self.two_move_route(adjacent_nodes,time_elapsed,route)
                    complete = True #end the route generation

                elif max(priorities) != -inf: #get as far back to the starting node as possible
                    #delete last move in route
                    route_without_delete = self.fastest_route_back(chosen_node,time_elapsed,route)

                    if len(route) > 1:
                        if route[-1]["pause"] == True:
                            route[-1]["time_elapsed"] = route[-1]["time_elapsed"] - 1
                        else:
                            route.pop()
                            time_elapsed = route[-1]["time_elapsed"]
                            chosen_node = self._ski_resort[route[-1]["start"]]
                    route_with_delete = self.fastest_route_back(chosen_node,time_elapsed,route)

                    if as_close_to_time:
                        route_without_delete_time_away = abs(route_without_delete[-1]["time_elapsed"] - self._length)
                        route_with_delete_time_away = abs(route_with_delete[-1]["time_elapsed"] - self._length)
                        if route_without_delete_time_away <= route_with_delete_time_away:
                            route = route_without_delete
                        elif route_without_delete_time_away > route_with_delete_time_away:
                            route = route_with_delete
                    else:
                        route = route_with_delete

                    complete = True
                    if route[-1]["start"] != self._start:
                        returned_to_start = False

                elif (len(route) == 1 or previous_route_length + 1 == self._length) and continue_route == True and time_value >= 0: #If the route hasn't started yet
                    time_elapsed += 1
                    self._ski_resort_object.increment_time(1)
                    if route[-1]["pause"] == False:
                        route.append({"start":chosen_node.name,"time_elapsed":time_elapsed,"pause":True})
                    else:
                        route[-1]["time_elapsed"] = route[-1]["time_elapsed"] + 1
                    previous_route_length = self._length
                    self._length += 1 #Length of the route is increased by 1 minute to account for the time spent waiting for the ski lifts to open
                
                #If the route is stopped by reaching unopened runs               
                elif continue_route == True and time_value >= 0: #If the route can continue since the surrounding runs are yet to open
                    time_elapsed += 1
                    self._ski_resort_object.increment_time(1)
                    if route[-1]["pause"] == False:
                        route.append({"start":chosen_node.name,"time_elapsed":time_elapsed,"pause":True})
                    else:
                        route[-1]["time_elapsed"] = route[-1]["time_elapsed"] + 1

                else: #If the route cannot continue
                    #Delete last move in route
                    route_without_delete = self.fastest_route_back(chosen_node,time_elapsed,route)

                    if len(route) > 1:
                        if route[-1]["pause"] == True:
                            route[-1]["time_elapsed"] = route[-1]["time_elapsed"] - 1
                        else:
                            route.pop()
                            time_elapsed = route[-1]["time_elapsed"]
                            chosen_node = self._ski_resort[route[-1]["start"]]
                    route_with_delete = self.fastest_route_back(chosen_node,time_elapsed,route)

                    if as_close_to_time:
                        route_without_delete_time_away = abs(route_without_delete[-1]["time_elapsed"] - self._length)
                        route_with_delete_time_away = abs(route_with_delete[-1]["time_elapsed"] - self._length)
                        if route_without_delete_time_away <= route_with_delete_time_away:
                            route = route_without_delete
                        elif route_without_delete_time_away > route_with_delete_time_away:
                            route = route_with_delete
                    else:
                        route = route_with_delete

                    complete = True #end the route generation
                    if route[-1]["start"] != self._start:
                        returned_to_start = False

            elif max(priorities) < 0 and chosen_node.name == self._start:
                
                #No set of three moves is viable however this checks if a set of two moves is still viable
                route = self.two_move_route(adjacent_nodes,time_elapsed,route)
                complete = True #end the route generation

            elif max(priorities) < 0: #If no set of three moves is viable but the route has not returned to the start node
                #Delete last move in route
                route_without_delete = self.fastest_route_back(chosen_node,time_elapsed,route)

                if len(route) > 1:
                    if route[-1]["pause"] == True:
                        route[-1]["time_elapsed"] = route[-1]["time_elapsed"] - 1
                    else:
                        route.pop()
                        time_elapsed = route[-1]["time_elapsed"]
                        chosen_node = self._ski_resort[route[-1]["start"]]
                route_with_delete = self.fastest_route_back(chosen_node,time_elapsed,route)

                if as_close_to_time:
                    route_without_delete_time_away = abs(route_without_delete[-1]["time_elapsed"] - self._length)
                    route_with_delete_time_away = abs(route_with_delete[-1]["time_elapsed"] - self._length)
                    if route_without_delete_time_away <= route_with_delete_time_away:
                        route = route_without_delete
                    elif route_without_delete_time_away > route_with_delete_time_away:
                        route = route_with_delete
                else:
                    route = route_with_delete

                complete = True
                if route[-1]["start"] != self._start:
                    returned_to_start = False
            
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


class Priority_queue():
    def __init__(self,n):
        self._max_length = int((0.5*n**2)-(1.5*n)+2)
        self._queue = [(0,"") for i in range(int(self._max_length))]
        self._front = 0
        self._rear = -1
        self._size = 0

    def enQueue(self,item): #item is a tuple of (distance,node name)
        if self.isFull():
            print("Queue is full")
        self._rear = int((self._rear + 1) % self._max_length)
        self._queue[self._rear] = item
        self._size += 1
        #priority shift
        counter = self._rear
        while self._queue[counter][0] < self._queue[int((counter-1)%self._max_length)][0] and counter != self._front:
            self._queue[counter],self._queue[counter-1] = self._queue[counter-1],self._queue[counter]
            counter = int((counter-1)%self._max_length)

    def deQueue(self):
        if self.isEmpty():
            print("Queue is empty")
            return None
        data_item = self._queue[self._front]
        self._front = int((self._front + 1) % self._max_length)
        self._size -= 1
        return data_item
    
    def isEmpty(self):
        return self._size == 0
    
    def isFull(self):
        return self._size == self._max_length

if __name__ == "__main__":
    example = Ski_resorts()
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

    print(Plan_route(example.resorts["Val Thorens"],"Plein Sud bottom","01:09","10:00").get_route(True))
    #print(Plan_route(example.resorts["Val Thorens"],"Plein Sud top","01:00","07:00").get_route())
    #print(Plan_route(example.resorts["Val Thorens"],"Plein Sud bottom","00:50","8:15")._dijkstras_traversal("Plein Sud bottom",False))

