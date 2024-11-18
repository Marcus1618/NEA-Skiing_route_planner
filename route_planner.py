from math import inf
import random
from ski_resorts import Ski_resorts, Ski_resort, Node, Ski_node, Run

class Plan_route(): #Plan_route class is used to create a viable route through a ski resort
    def __init__(self,ski_resort,start,length,start_time): #Initialisation
        self._ski_resort_object = ski_resort
        self._ski_resort = ski_resort.nodes
        self._start = start
        self._length = self._hours_to_minutes(length)
        self._ski_resort_object.time = start_time
        self._ski_resort_object.check_open()

    def _hours_to_minutes(self,time): #Converts time from hh:mm format to minutes
        h,m = time.split(":")
        return int(h)*60 + int(m)
    
    def compare_greater(self,t1,t2): #Compares if time t1 is greater than time t2
        h1, m1 = t1.split(":")
        h2, m2 = t2.split(":")
        if int(h1) > int(h2):
            return True
        elif int(h1) == int(h2) and int(m1) > int(m2):
            return True
        else:
            return False
    
    def compare_greater_or_equal(self,t1,t2): #Compares if time t1 is greater than or equal to time t2
        h1, m1 = t1.split(":")
        h2, m2 = t2.split(":")
        if int(h1) > int(h2):
            return True
        elif int(h1) == int(h2) and int(m1) >= int(m2):
            return True
        else:
            return False
    
    def _add_times(self, t1, t2):
        h1, m1 = t1.split(":")
        m2 = t2
        mins = int(m1) + int(m2)
        hours = int(h1) + mins // 60
        mins = mins % 60
        if hours > 23:
            hours %= 24
        if len(str(hours)) == 1:
            hours = f"0{hours}"
        if len(str(mins)) == 1:
            mins = f"0{mins}"
        return f"{hours}:{mins}"

    def _dijkstras_traversal(self,start,time_independent): #Dijkstra's algorithm to find the shortest path from a node in the graph to all of the other nodes
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
                continue #If the node has already been visited, skip it
            visited.add(v)
            self._ski_resort_object.increment_time(dist)

            for edge in self._ski_resort[v].runs: #Iterates through the nodes adjacent to the node
                if edge.name not in visited:
                    if time_independent: #Allows closed runs not to affect the distances to a node
                        edge.length = edge.open_length
                    distances[edge.name] = min(edge.length+dist,distances[edge.name])
                    if edge.length+dist <= distances[edge.name]:
                        previous_node[edge.name] = v
                    queue.enQueue((distances[edge.name],edge.name))
                    if time_independent:
                        self._ski_resort_object.check_open()  
            self._ski_resort_object.decrement_time(dist)

        return distances, previous_node
    
    def _two_move_route(self,original_chosen_node,adjacent_nodes,time_elapsed,route,as_close_to_time): #Finds the highest value sequence of two moves and completes them
        change = False
        priorities_for_double = []
        for node in adjacent_nodes: #Iterate throught the adjacent nodes to calculate the values for each possible two move sequence
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
        for count,single in enumerate(priorities_for_double): #Determines the indices of the move seqeunces with the highest value (there could be multiple with equal value)
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
        dist_home_from_chosen = self._dijkstras_traversal(original_chosen_node.name, False)[0][self._start]
        if (maximum >= 0 and chosen_node_2.name == self._start) or (as_close_to_time == True and abs(maximum) <= self._length-(time_elapsed+dist_home_from_chosen)): #if the two moves are viable, add them to the route
            change = True
            time_elapsed += chosen_node_1.length
            route.append({"start":chosen_node_1.name,"time_elapsed":time_elapsed,"pause":False})
            self._ski_resort_object.increment_time(chosen_node_1.length)
            time_elapsed += chosen_node_2.length
            route.append({"start":chosen_node_2.name,"time_elapsed":time_elapsed,"pause":False})
            self._ski_resort_object.increment_time(chosen_node_2.length)
            original_chosen_node = chosen_node_2

        return route, change, time_elapsed, original_chosen_node
    
    def _one_move_route(self,original_chosen_node,adjacent_nodes,time_elapsed,route,as_close_to_time): #Finds the highest value move and completes it
        change = False
        priorities = []
        for node in adjacent_nodes: #Iterate through the adjacent nodes to calculate the values for each possible move
            temp_time_elapsed = time_elapsed + node.length
            times,prev = self._dijkstras_traversal(node.name, True)
            time_from_start = times[self._start]
            time_value = 0
            time_value = self._length - temp_time_elapsed - time_from_start
            priorities.append(time_value)

        if priorities.count(max(priorities)) == 1:
            chosen_node = adjacent_nodes[priorities.index(max(priorities))]
        else: #randomly choose between the nodes with the same value
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
        dist_home_from_chosen = self._dijkstras_traversal(original_chosen_node.name, False)[0][self._start]

        if max(priorities) >= 0 or (as_close_to_time == True and abs(max(priorities)) <= self._length-(time_elapsed+dist_home_from_chosen)): #if the one move is viable add it to the route
            change = True
            time_elapsed += chosen_node.length
            route.append({"start":chosen_node.name,"time_elapsed":time_elapsed,"pause":False})
            self._ski_resort_object.increment_time(chosen_node.length)
            original_chosen_node = chosen_node

        return route, change, time_elapsed, original_chosen_node
    
    def _pause_route(self,time_elapsed,route,chosen_node): #Pauses the route for 1 minute
        time_elapsed += 1
        self._ski_resort_object.increment_time(1)
        if route[-1]["pause"] == False:
            route.append({"start":chosen_node.name,"time_elapsed":time_elapsed,"pause":True})
        else: #If the route was already paused, increment the time of the pause
            route[-1]["time_elapsed"] = route[-1]["time_elapsed"] + 1
        return time_elapsed, route
    
    def _best_way_back(self,route,time_elapsed,chosen_node,as_close_to_time,adjacent_nodes): #Runs when there are no viable sequences of three moves. Determines a route which tries to return to the starting node
        #If as_close_to_time is False, the route will return to the starting node ensuring it reaches it before the specified length of route is reached
        #If as_close_to_time is True, the route will return to the starting node but will try to end the route at a time close to the specified length of route meaning it could be longer than the specified length
        route, change_two, time_elapsed, chosen_node = self._two_move_route(chosen_node,adjacent_nodes,time_elapsed,route,as_close_to_time)
        adjacent_nodes = self._ski_resort[chosen_node.name].runs
        route, change_one, time_elapsed, chosen_node = self._one_move_route(chosen_node,adjacent_nodes,time_elapsed,route,as_close_to_time)
        adjacent_nodes = self._ski_resort[chosen_node.name].runs
        if not(change_two or change_one): #If the node that the route is currently at is greater than 3 edges away from the starting node
            route_without_delete = self.fastest_route_back(chosen_node,time_elapsed,route) #Determines the fastest route back to the starting node from the current node

            if len(route) > 1:
                if route[-1]["pause"] == True:
                    route[-1]["time_elapsed"] = route[-1]["time_elapsed"] - 1
                else:
                    route.pop()
                    time_elapsed = route[-1]["time_elapsed"]
                    chosen_node = self._ski_resort[route[-1]["start"]]
            route_with_delete = self.fastest_route_back(chosen_node,time_elapsed,route) #Deletes the last move in the route then determines the fastest route back to the starting node to ensure that the route finishses before the specified length of time

            if as_close_to_time:
                route_without_delete_time_away = abs(route_without_delete[-1]["time_elapsed"] - self._length)
                route_with_delete_time_away = abs(route_with_delete[-1]["time_elapsed"] - self._length)
                if route_without_delete_time_away <= route_with_delete_time_away:
                    route = route_without_delete
                elif route_without_delete_time_away > route_with_delete_time_away:
                    route = route_with_delete
            else:
                route = route_with_delete
        else:
            route = self.fastest_route_back(chosen_node,time_elapsed,route)
        return route

    def _should_route_continue(self,adjacent_nodes): #Determines if there is a 3 move route that will be able to be taken in the future
        continue_route = False
        for run in adjacent_nodes: #Iterating through the adjacent nodes to see if there are three nodes in a sequence that are all either open or will be open in the future
            if self.compare_greater(run.opening, self._ski_resort_object.time) or (self.compare_greater_or_equal(self._ski_resort_object.time, run.opening) and self.compare_greater(run.closing, self._ski_resort_object.time)):
                min_time = self._add_times(run.opening, run.open_length)
                max_time = run.closing
                adjacent_nodes_1 = self._ski_resort[run.name].runs
                for run_1 in adjacent_nodes_1:
                    if (self.compare_greater(run_1.opening, min_time) and self.compare_greater(max_time, run_1.opening)) or (self.compare_greater_or_equal(min_time, run_1.opening) and self.compare_greater(run_1.closing, min_time)):
                        min_time_1 = self._add_times(min_time, run_1.open_length)
                        max_time_1 = max_time
                        if self.compare_greater(self._add_times(run_1.opening, run_1.open_length), min_time_1):
                            min_time_1 = self._add_times(run_1.opening, run_1.open_length)
                        if self.compare_greater_or_equal(max_time_1, run_1.closing):
                            max_time_1 = run_1.closing
                        adjacent_nodes_2 = self._ski_resort[run_1.name].runs
                        for run_2 in adjacent_nodes_2:
                            if (self.compare_greater(run_2.opening, min_time_1) and self.compare_greater(max_time_1, run_2.opening)) or (self.compare_greater_or_equal(min_time_1, run_2.opening) and self.compare_greater(run_2.closing, min_time_1)):
                                continue_route = True
                                break
                        if continue_route == True:
                            break
                if continue_route == True:
                    break
        return continue_route

    def _complete_move(self,priorities,adjacent_nodes,time_elapsed,route): #Completes the first move of the sequence of three moves which had the highest value
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
        return chosen_node, time_elapsed, route

    def fastest_route_back(self, chosen_node,time_elapsed,route): #Determines the fastest route back to the starting node from the current node
        temp_route = route.copy()
        times,previous_node = self._dijkstras_traversal(chosen_node.name, False)
                
        route_to_finish = []
        current = self._start
        route_to_finish.insert(0,current)
        while current != chosen_node.name:
            current = previous_node[current]
            route_to_finish.insert(0,current)
                
        for i in range(len(route_to_finish)-1):
            run_length = (self._ski_resort[route_to_finish[i]].runs[[run.name for run in self._ski_resort[route_to_finish[i]].runs].index(route_to_finish[i+1])]).length
            if run_length != inf: #Ensures that the run is only added to the route if it is open
                time_elapsed += run_length
                self._ski_resort_object.increment_time(run_length)
                temp_route.append({"start":route_to_finish[i+1],"time_elapsed":time_elapsed,"pause":False})
            else:
                break
        return temp_route

    def _find_values(self,adjacent_nodes,count,temp_time_elapsed, priorities, value, values, ignore_way_home): #A recursive function to find the values of the possible routes from the current node
        if count >= 2: #base case determining the search depth through the graph
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
                if time_value < 0: #If the time to get back to the starting node is greater than the time left in the route, the value is the time to get back to the starting node
                    values.append(time_value)
                else: #If the time to get back to the starting node is less than the time left in the route, the value is the desirability of the runs in the route
                    values.append(value)
                temp_time_elapsed -= node_1.length
                value -= 0 #generate value
            count -= 1
            return priorities, values, count
        for node in adjacent_nodes: #Iterate through the adjacent nodes to calculate the values for each possible move
            if count == 0:
                values = []
            count += 1
            temp_time_elapsed += node.length
            self._ski_resort_object.increment_time(node.length)
            node_value = 0 #generate value
            value += node_value
            priorities,values,count = self._find_values(self._ski_resort[node.name].runs, count, temp_time_elapsed, priorities, value, values, ignore_way_home) #Call the function recursively
            value -= node_value
            self._ski_resort_object.decrement_time(node.length)
            temp_time_elapsed -= node.length
            if count == 0:
                priorities.append(max(values))

        count -= 1
        return priorities, values, count
    
    def get_route(self, as_close_to_time): #Generates the complete route through the ski resort returing the route as a list of dictionaries and a boolean indicating if the route returned to the starting node
        time_elapsed = 0
        complete = False
        route = [{"start":self._start,"time_elapsed":0,"pause":False}]
        chosen_node = self._ski_resort[self._start]
        returned_to_start = True
        previous_route_length = self._length

        while complete == False: #The route generation continues until it has to end due to the time limit being reached or closure of lifts forcing it to stop

            find_priorities = []
            adjacent_nodes = self._ski_resort[chosen_node.name].runs
            count = 0
            temp_time_elapsed = time_elapsed
            value = 0
            values = []
            priorities, values, count = self._find_values(adjacent_nodes,count,temp_time_elapsed, find_priorities, value, values, False)

            if max(priorities) == -inf: #If all sequences of three moves have to pass through a closed lift or there is no route to the starting node without passing through a closed lift
                continue_route = self._should_route_continue(adjacent_nodes)     

                find_priorities = []
                count = 0
                temp_time_elapsed = time_elapsed
                value = 0
                values = []
                priorities, values, count = self._find_values(adjacent_nodes,count,temp_time_elapsed, find_priorities, value, values, True) #Finds the values of the possible routes but ignoring if there is no route to the starting node without passing through a closed lift
                
                times, prev = self._dijkstras_traversal(chosen_node.name, True)
                time_from_start = times[self._start]
                time_value = self._length - time_elapsed - time_from_start

                if max(priorities) >= 0: #If a sequence of three moves is still viable (the algorithm has entered this edge case since there is no longer a route to the starting node without passing through a closed lift)
                    chosen_node, time_elapsed, route = self._complete_move(priorities,adjacent_nodes,time_elapsed,route)
                    
                elif max(priorities) != -inf and chosen_node.name == self._start: #If there is not time left for a sequence of three moves and the route has returned to the starting node
                    route, change, time_elapsed, chosen_node = self._two_move_route(chosen_node,adjacent_nodes,time_elapsed,route,as_close_to_time)
                    complete = True #end the route generation

                elif max(priorities) != -inf: #If there is not time left for a sequence of three moves and the route has not returned to the starting node
                    route = self._best_way_back(route,time_elapsed,chosen_node,as_close_to_time,adjacent_nodes) #Get as far back to the starting node as possible
                    complete = True

                #The remaining edge cases are when the route is stopped by reaching unopened runs
                elif (len(route) == 1 or previous_route_length + 1 == self._length) and continue_route == True and time_value >= 0: #If the route hasn't started yet and there will be possible sequences of moves in the future
                    time_elapsed, route = self._pause_route(time_elapsed,route,chosen_node)
                    previous_route_length = self._length
                    self._length += 1 #Length of the route is increased by 1 minute to account for the time spent waiting for the ski lifts to open
                               
                elif continue_route == True and time_value >= 0: #If the route can continue since the surrounding runs are yet to open
                    time_elapsed, route = self._pause_route(time_elapsed,route,chosen_node)

                else: #If the route cannot continue
                    route = self._best_way_back(route,time_elapsed,chosen_node,as_close_to_time,adjacent_nodes) #Get as far back to the starting node as possible
                    complete = True #End the route generation

            elif max(priorities) < 0 and chosen_node.name == self._start: #If no sequence of three moves is viable within the time and the route has returned to the start node
                route, change, time_elapsed, chosen_node = self._two_move_route(chosen_node,adjacent_nodes,time_elapsed,route,as_close_to_time)
                complete = True #End the route generation

            elif max(priorities) < 0: #If no sequence of three moves is viable within the time and the route has not returned to the start node
                route = self._best_way_back(route,time_elapsed,chosen_node,as_close_to_time,adjacent_nodes)
                complete = True
            
            else: #If a sequence of three moves is viable within the time
                chosen_node, time_elapsed, route = self._complete_move(priorities,adjacent_nodes,time_elapsed,route)

        if route[-1]["start"] != self._start: #Check if the route ends at the starting node
            returned_to_start = False
        return route, returned_to_start


class Priority_queue(): #Implementation of a circular, priority queue using a static array
    def __init__(self,n):
        self._max_length = int((0.5*n**2)-(1.5*n)+2) #The maximum length of the queue that the Dijkstra's algorithm could require if the graph is fully connected 
        self._queue = [(0,"") for i in range(int(self._max_length))] #The memory used to store the queue is allocated when the priority queue is initialised
        self._front = 0
        self._rear = -1
        self._size = 0

    def enQueue(self,item): #Adds an item to the rear of the queue where an item is a tuple of (distance,node name)
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

    def deQueue(self): #Pops the front of the queue
        if self.isEmpty():
            print("Queue is empty")
            return None
        data_item = self._queue[self._front]
        self._front = int((self._front + 1) % self._max_length)
        self._size -= 1
        return data_item
    
    def isEmpty(self): #Checks if the queue is empty
        return self._size == 0
    
    def isFull(self): #Checks if the queue is full
        return self._size == self._max_length

if __name__ == "__main__":
    example = Ski_resorts()
    example.add_resort("Val Thorens")
    example.resorts["Val Thorens"].add_ski_node("Plein Sud bottom")
    example.resorts["Val Thorens"].nodes["Plein Sud bottom"].add_run("Plein Sud top",10, "08:00", "17:00")
    example.resorts["Val Thorens"].add_ski_node("Plein Sud top")
    example.resorts["Val Thorens"].nodes["Plein Sud top"].add_run("Pionniers bottom",5, "00:00", "23:59")
    example.resorts["Val Thorens"].nodes["Plein Sud top"].add_run("Pionniers top",1, "00:00", "23:59")
    example.resorts["Val Thorens"].add_ski_node("3 Vallees bottom")
    example.resorts["Val Thorens"].nodes["3 Vallees bottom"].add_run("Plein Sud bottom",15, "00:00", "23:59")
    example.resorts["Val Thorens"].nodes["3 Vallees bottom"].add_run("3 Vallees top",6, "08:30", "16:00")
    example.resorts["Val Thorens"].add_ski_node("3 Vallees top")
    example.resorts["Val Thorens"].nodes["3 Vallees top"].add_run("3 Vallees bottom",5, "00:00", "23:59")
    example.resorts["Val Thorens"].nodes["3 Vallees top"].add_run("Plein Sud top",4, "00:00", "23:59")
    example.resorts["Val Thorens"].add_ski_node("Pionniers bottom")
    example.resorts["Val Thorens"].nodes["Pionniers bottom"].add_run("Plein Sud bottom",10, "00:00", "23:59")
    example.resorts["Val Thorens"].nodes["Pionniers bottom"].add_run("Pionniers top",4, "08:00", "16:30")
    example.resorts["Val Thorens"].add_ski_node("Pionniers top")
    example.resorts["Val Thorens"].nodes["Pionniers top"].add_run("3 Vallees bottom",1, "00:00", "23:59")

    print(Plan_route(example.resorts["Val Thorens"],"Plein Sud top","00:53","07:00").get_route(False))
    #print(Plan_route(example.resorts["Val Thorens"],"Plein Sud top","01:00","07:00").get_route())
    #print(Plan_route(example.resorts["Val Thorens"],"Plein Sud bottom","00:50","8:15")._dijkstras_traversal("Plein Sud bottom",False))