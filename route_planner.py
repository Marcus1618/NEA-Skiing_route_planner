from math import inf
import random
import requests
from ski_resorts import Ski_resorts, Ski_resort, Node, Ski_node, Run
#Deals with the generation of a route through a ski resort.

class Plan_route(): #Plan_route class is used to create a viable route through a ski resort
    DIFFICULTY_MULTIPLIER = 10000
    ALTITUDE_MULTIPLIER = 1000
    REPETITION_MULTIPLIER = 100
    LIFT_TYPE_MULTIPLIER = 1
    def __init__(self,ski_resort,start,length,start_time, max_difficulty, snow_conditions, lift_type_preference, weather, latitude, longitude): 
        #Initialises the attributes setting the time attribute for the ski resort to the starting time of the route and creating a suitable URL for the API call. Parameters: None. Return values: None.
        self.__ski_resort_object = ski_resort
        self.__ski_resort = ski_resort.nodes
        self.__start = start
        self.__max_difficulty = max_difficulty
        self.__snow_conditions = snow_conditions
        self.__weather = weather
        self.__repeated_runs = {}
        self.__lift_type_preference = lift_type_preference
        self.__length = length
        self.__ski_resort_object.time = start_time
        self.__ski_resort_object.check_open()
        if latitude == "N/A" and longitude == "N/A":
            self.__previous_snow = "N/A"
            self.__current_snow = "N/A"
            self.__temperature = "N/A"
        elif latitude == "default" and longitude == "default":
            self.__url_weather = "https://api.tomorrow.io/v4/weather/forecast?location=45.1753%2C%206.3448&timesteps=1d&units=metric&apikey=tXd5I8WP449Un0EQqtPzXgJUfhJTVZos"
            self.__previous_snow, self.__current_snow, self.__temperature = self.__get_weather(self.__weather)
        else:
            self.__url_weather = f"https://api.tomorrow.io/v4/weather/forecast?location={latitude}%2C%20{longitude}&timesteps=1d&units=metric&apikey=tXd5I8WP449Un0EQqtPzXgJUfhJTVZos"
            self.__previous_snow, self.__current_snow, self.__temperature = self.__get_weather(self.__weather)
    
    def __compare_greater(self,t1,t2): #Compares if time t1 is greater than time t2 where both times are in hh:mm format. Parameters: t1 – String, t2 – String. Return values: Boolean.
        h1, m1 = t1.split(":")
        h2, m2 = t2.split(":")
        if int(h1) > int(h2):
            return True
        elif int(h1) == int(h2) and int(m1) > int(m2):
            return True
        else:
            return False
    
    def __compare_greater_or_equal(self,t1,t2): #Compares if time t1 is greater than or equal to time t2 where both times are in hh:mm format. Parameters: t1 – String, t2 – String. Return values: Boolean.
        h1, m1 = t1.split(":")
        h2, m2 = t2.split(":")
        if int(h1) > int(h2):
            return True
        elif int(h1) == int(h2) and int(m1) >= int(m2):
            return True
        else:
            return False
    
    def __add_times(self, t1, t2): #Adds a time t1 in hh:mm format to an integer number of minutes t2. Parameters: t1 – String, t2 – Integer. Return values: time - String.
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

    #######################################################
    # GROUP A Skill: Graph traversal (Dijkstra’s algorithm)
    #######################################################
    def __dijkstras_traversal(self,start,time_independent): #Dijkstra's algorithm to find the shortest path from a node in the graph to all of the other nodes.
        #Parameters: start (the node at which the traversal begins) - String, time_independent – Boolean. Return values: distances – list, previous_node - list.
        node_number = self.__ski_resort_object.node_number()
        queue = Priority_queue(node_number)
        keys = (self.__ski_resort.keys())
        values = (inf for i in range(len(self.__ski_resort)))
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
            self.__ski_resort_object.increment_time(dist)

            for edge in self.__ski_resort[v].runs: #Iterates through the nodes adjacent to the node
                if edge.name not in visited:
                    if time_independent: #Allows closed runs not to affect the distances to a node
                        edge.length = edge.open_length
                    distances[edge.name] = min(edge.length+dist,distances[edge.name])
                    if edge.length+dist <= distances[edge.name]:
                        previous_node[edge.name] = v
                    queue.enQueue((distances[edge.name],edge.name))
                    if time_independent:
                        self.__ski_resort_object.check_open()  
            self.__ski_resort_object.decrement_time(dist)

        return distances, previous_node
    
    def __min_and_max_altitudes(self): #Finds the minimum and maximum altitude of all the nodes in the ski resort. Parameters: None. Return values: min_altitdue – integer, max_altitude – integer.
        min_altitude = inf
        max_altitude = -inf
        for node in self.__ski_resort.values():
            if node.altitude < min_altitude:
                min_altitude = node.altitude
            if node.altitude > max_altitude:
                max_altitude = node.altitude
        return min_altitude, max_altitude

    def __generate_values(self, start_node, end_node): #Generates the value of a run based on its difficulty, altitude depending on weather, number of repetitions and lift type preference.
        #Their importance is weighted in the same order which they are previously given with the difficulty the most important feature. Parameters: start_node – Object, end_node – Object. Return values: value – integer.
        value = 0
        #difficulty score
        if self.__max_difficulty == "black":
            if end_node.difficulty == "black" or end_node.difficulty == "red" or end_node.difficulty == "blue" or end_node.difficulty == "green":
                value += 9*Plan_route.DIFFICULTY_MULTIPLIER
        elif self.__max_difficulty == "red":
            if end_node.difficulty == "red" or end_node.difficulty == "blue" or end_node.difficulty == "green":
                value += 9*Plan_route.DIFFICULTY_MULTIPLIER
            elif end_node.difficulty == "black":
                value += 1*Plan_route.DIFFICULTY_MULTIPLIER
        elif self.__max_difficulty == "blue":
            if end_node.difficulty == "blue" or end_node.difficulty == "green":
                value += 9*Plan_route.DIFFICULTY_MULTIPLIER
            elif end_node.difficulty == "red":
                value += 2*Plan_route.DIFFICULTY_MULTIPLIER
            elif end_node.difficulty == "black":
                value += 1*Plan_route.DIFFICULTY_MULTIPLIER
        elif self.__max_difficulty == "green":
            if end_node.difficulty == "green":
                value += 9*Plan_route.DIFFICULTY_MULTIPLIER
            elif end_node.difficulty == "blue":
                value += 3*Plan_route.DIFFICULTY_MULTIPLIER
            elif end_node.difficulty == "red":
                value += 2*Plan_route.DIFFICULTY_MULTIPLIER
            elif self.__max_difficulty == "black":
                value += 1*Plan_route.DIFFICULTY_MULTIPLIER
        
        #altitude score depending on snow conditions and weather
        min_altitude_fraction = 0.25
        max_altitude_fraction = 1
        min_altitude, max_altitude = self.__min_and_max_altitudes()
        if self.__weather != "unknown":
            if not(self.__previous_snow == "N/A" or self.__current_snow == "N/A" or self.__temperature == "N/A"):
                if self.__current_snow > 0:
                    max_altitude_fraction = max_altitude_fraction*0.75
                if self.__temperature < 3:
                    min_altitude_fraction = min_altitude_fraction*0.5
                else:
                    min_altitude_fraction = min_altitude_fraction*1.3
                if self.__previous_snow > 0:
                    min_altitude_fraction = min_altitude_fraction*0.5
        if self.__snow_conditions != "unknown":
            if self.__snow_conditions == "good":
               min_altitude_fraction = min_altitude_fraction*0.5                
            elif self.__snow_conditions == "bad":
                min_altitude_fraction = min_altitude_fraction*1.3
        min_alititude_boundary = min_altitude + (max_altitude-min_altitude)*min_altitude_fraction
        max_alititude_boundary = min_altitude + (max_altitude-min_altitude)*max_altitude_fraction
        self.__ski_resort[end_node.name].altitude
        if self.__ski_resort[end_node.name].altitude < min_alititude_boundary or self.__ski_resort[end_node.name].altitude > max_alititude_boundary:
            value += 1*Plan_route.ALTITUDE_MULTIPLIER
        else:
            value += 9*Plan_route.ALTITUDE_MULTIPLIER

        #repetition of runs
        num_repetitions = 0
        if (start_node.name,end_node.name) in self.__repeated_runs.keys():
            num_repetitions = self.__repeated_runs[(start_node.name,end_node.name)]
        if num_repetitions < 90:
            value += 990-(num_repetitions*0.1*Plan_route.REPETITION_MULTIPLIER)
        else:
            value += 990-(89*0.1*Plan_route.REPETITION_MULTIPLIER)

        #lift type preference
        if end_node.lift == 1:
            if self.__lift_type_preference == "gondola":
                if end_node.lift_type == "gondola":
                    value += 9*Plan_route.LIFT_TYPE_MULTIPLIER
                else:
                    value += 1*Plan_route.LIFT_TYPE_MULTIPLIER
            elif self.__lift_type_preference == "chairlift":
                if end_node.lift_type == "chairlift":
                    value += 9*Plan_route.LIFT_TYPE_MULTIPLIER
                else:
                    value += 1*Plan_route.LIFT_TYPE_MULTIPLIER
            elif self.__lift_type_preference == "draglift":
                if end_node.lift_type == "draglift":
                    value += 9*Plan_route.LIFT_TYPE_MULTIPLIER
                else:
                    value += 1*Plan_route.LIFT_TYPE_MULTIPLIER
        return value

    ######################################################################################################
    # GROUP B Skill: Calling web service APIs and parsing JSON/XML to service a simple client-server model
    ######################################################################################################
    def __get_weather(self, date): #Gets the weather for the ski resort from the API ‘www.tomorrow.io/weather-api/’  using the input coordinates of the ski resort.
        #Parameters: date – string. Return values: previous_snow – float, current_snow – float, temperature – float.
        day_index = 0
        if date == "today":
            day_index = 1
        elif date == "tomorrow":
            day_index = 2
        elif date == "2 days time":
            day_index = 3
        elif date == "3 days time":
            day_index = 4
        headers = {"accept": "application/json"}
        response = requests.get(self.__url_weather, headers=headers)
        if response.status_code == 200: #If the API data request is successful, the weather data is extracted
            weather_data = response.json()
            previous_snow = weather_data["timelines"]["daily"][day_index-1]["values"]["snowIntensityMax"] #parsing the JSON data
            current_snow = weather_data["timelines"]["daily"][day_index]["values"]["snowIntensityMax"]
            temperature = weather_data["timelines"]["daily"][day_index]["values"]["temperatureAvg"]
            print(f"The temperature is {temperature} degrees and the maximum snow intensity from today is {current_snow}.")
        else:
            previous_snow = "N/A"
            current_snow = "N/A"
            temperature = "N/A"
        return previous_snow, current_snow, temperature
    
    ################################################
    # GROUP A Skill: Complex user-defined algorithms
    ################################################
    def __two_move_route(self,original_chosen_node,adjacent_nodes,time_elapsed,route,as_close_to_time): #Finds the highest value sequence of two moves and completes them if the value is greater than or equal to 0.
        #Parameters: original_chosen_node – Object, adjacent_nodes - List, time_elapsed - Integer, route – List of dictionaries, as_close_to_time – Boolean. Return values: route – List of dictionaries, change - Boolean, time_elapsed - Integer, original_chosen_node – Object.
        change = False
        priorities_for_double = []
        for node in adjacent_nodes: #Iterate throught the adjacent nodes to calculate the values for each possible two move sequence
            value = self.__generate_values(original_chosen_node, node)
            temp_time_elapsed = time_elapsed + node.length
            adjacent_nodes_1 = self.__ski_resort[node.name].runs
            self.__ski_resort_object.increment_time(node.length)

            single_priorities = []
            for node_1 in adjacent_nodes_1:
                value1 = value + self.__generate_values(self.__ski_resort[node.name], node_1)
                temp_time_elapsed1 = temp_time_elapsed + node_1.length
                times,prev = self.__dijkstras_traversal(node_1.name, True)
                time_from_start = times[self.__start]
                time_value = 0
                time_value = self.__length - temp_time_elapsed1 - time_from_start
                if time_value < 0:
                    single_priorities.append(time_value)
                else:
                    single_priorities.append(value1)

            priorities_for_double.append(single_priorities)
            self.__ski_resort_object.decrement_time(node.length)

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
        adjacent_nodes_double = self.__ski_resort[chosen_node_1.name].runs
        chosen_node_2 = adjacent_nodes_double[index_2]
        dist_home_from_chosen = self.__dijkstras_traversal(original_chosen_node.name, False)[0][self.__start]
        if (maximum >= 0 and chosen_node_2.name == self.__start) or (as_close_to_time == True and abs(maximum) <= self.__length-(time_elapsed+dist_home_from_chosen)): #if the two moves are viable, add them to the route
            change = True
            time_elapsed += chosen_node_1.length
            if chosen_node_1.lift:
                lift_or_run = "lift"
            else:
                lift_or_run = "run"
            route.append({"start":chosen_node_1.name,"time_elapsed":time_elapsed,"pause":False, "lift":lift_or_run, "break":False})
            if (original_chosen_node.name,chosen_node_1.name) in self.__repeated_runs.keys():
                self.__repeated_runs[(original_chosen_node.name,chosen_node_1.name)] += 1
            else:
                self.__repeated_runs[(original_chosen_node.name,chosen_node_1.name)] = 1
            self.__ski_resort_object.increment_time(chosen_node_1.length)
            time_elapsed += chosen_node_2.length
            if chosen_node_2.lift:
                lift_or_run = "lift"
            else:
                lift_or_run = "run"
            route.append({"start":chosen_node_2.name,"time_elapsed":time_elapsed,"pause":False, "lift":lift_or_run, "break":False})
            if (chosen_node_1.name,chosen_node_2.name) in self.__repeated_runs.keys():
                self.__repeated_runs[(chosen_node_1.name,chosen_node_2.name)] += 1
            else:
                self.__repeated_runs[(chosen_node_1.name,chosen_node_2.name)] = 1
            self.__ski_resort_object.increment_time(chosen_node_2.length)
            original_chosen_node = chosen_node_2

        return route, change, time_elapsed, original_chosen_node
    
    def __one_move_route(self,original_chosen_node,adjacent_nodes,time_elapsed,route,as_close_to_time): #Finds the highest value single move and completes it if its value is greater than or equal to 0.
        #Parameters: original_chosen_node – Object, adjacent_nodes - List, time_elapsed - Integer, route – List of dictionaries, as_close_to_time – Boolean. Return values: route – List of dictionaries, change - Boolean, time_elapsed - Integer, original_chosen_node – Object.
        change = False
        priorities = []
        for node in adjacent_nodes: #Iterate through the adjacent nodes to calculate the values for each possible move
            temp_time_elapsed = time_elapsed + node.length
            times,prev = self.__dijkstras_traversal(node.name, True)
            time_from_start = times[self.__start]
            time_value = 0
            time_value = self.__length - temp_time_elapsed - time_from_start
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
        dist_home_from_chosen = self.__dijkstras_traversal(original_chosen_node.name, False)[0][self.__start]

        if max(priorities) >= 0 or (as_close_to_time == True and abs(max(priorities)) <= self.__length-(time_elapsed+dist_home_from_chosen)): #if the one move is viable add it to the route
            change = True
            time_elapsed += chosen_node.length
            if chosen_node.lift:
                lift_or_run = "lift"
            else:
                lift_or_run = "run"
            route.append({"start":chosen_node.name,"time_elapsed":time_elapsed,"pause":False, "lift":lift_or_run, "break":False})
            if (original_chosen_node.name,chosen_node.name) in self.__repeated_runs.keys():
                self.__repeated_runs[(original_chosen_node.name,chosen_node.name)] += 1
            else:
                self.__repeated_runs[(original_chosen_node.name,chosen_node.name)] = 1
            self.__ski_resort_object.increment_time(chosen_node.length)
            original_chosen_node = chosen_node

        return route, change, time_elapsed, original_chosen_node
    
    def __pause_route(self,time_elapsed,route,chosen_node): #Pauses the route for one minute. Parameters: time_elapsed - Integer, route - List, chosen_node – Object. Return Values: time_elapsed - Integer, route – List.
        time_elapsed += 1
        self.__ski_resort_object.increment_time(1)
        if route[-1]["pause"] == False:
            route.append({"start":chosen_node.name,"time_elapsed":time_elapsed,"pause":True, "lift":None, "break":False})
        else: #If the route was already paused, increment the time of the pause
            route[-1]["time_elapsed"] = route[-1]["time_elapsed"] + 1
        return time_elapsed, route
    
    ################################################
    # GROUP A Skill: Complex user-defined algorithms
    ################################################
    def __best_way_back(self,route,time_elapsed,chosen_node,as_close_to_time,adjacent_nodes): #Used when there are no viable sequences of three moves through the ski resort. Determines a route which tries to return as far back to the starting node as possible.
        #Parameters: route – List, time_elapsed - Integer, chosen_node - object, as_close_to_time - Boolean, adjacent_nodes – List. Return values: route – List.
        #If as_close_to_time is False, the route will return to the starting node ensuring it reaches it before the specified length of route is reached
        #If as_close_to_time is True, the route will return to the starting node but will try to end the route at a time close to the specified length of route meaning it could be longer than the specified length
        route, change_two, time_elapsed, chosen_node = self.__two_move_route(chosen_node,adjacent_nodes,time_elapsed,route,as_close_to_time)
        adjacent_nodes = self.__ski_resort[chosen_node.name].runs
        route, change_one, time_elapsed, chosen_node = self.__one_move_route(chosen_node,adjacent_nodes,time_elapsed,route,as_close_to_time)
        adjacent_nodes = self.__ski_resort[chosen_node.name].runs
        if not(change_two or change_one): #If the node that the route is currently at is greater than 3 edges away from the starting node
            route_without_delete = self.__fastest_route_back(chosen_node,time_elapsed,route) #Determines the fastest route back to the starting node from the current node

            if len(route) > 1:
                if route[-1]["pause"] == True:
                    route[-1]["time_elapsed"] = route[-1]["time_elapsed"] - 1
                else:
                    route.pop()
                    time_elapsed = route[-1]["time_elapsed"]
                    chosen_node = self.__ski_resort[route[-1]["start"]]
            route_with_delete = self.__fastest_route_back(chosen_node,time_elapsed,route) #Deletes the last move in the route then determines the fastest route back to the starting node to ensure that the route finishses before the specified length of time

            if as_close_to_time:
                route_without_delete_time_away = abs(route_without_delete[-1]["time_elapsed"] - self.__length)
                route_with_delete_time_away = abs(route_with_delete[-1]["time_elapsed"] - self.__length)
                if route_without_delete_time_away <= route_with_delete_time_away:
                    route = route_without_delete
                elif route_without_delete_time_away > route_with_delete_time_away:
                    route = route_with_delete
            else:
                route = route_with_delete
        else:
            route = self.__fastest_route_back(chosen_node,time_elapsed,route)
        return route

    ################################################
    # GROUP A Skill: Complex user-defined algorithms
    ################################################
    def __should_route_continue(self,adjacent_nodes): #Determines if there is a 3 move route that will be able to be taken in the future when there is not currently one possible. Parameters: adjacent_nodes – List. Return values: continue_route – Boolean.
        continue_route = False
        for run in adjacent_nodes: #Iterating through the adjacent nodes to see if there are three nodes in a sequence that are all either open or will be open in the future
            if self.__compare_greater(run.opening, self.__ski_resort_object.time) or (self.__compare_greater_or_equal(self.__ski_resort_object.time, run.opening) and self.__compare_greater(run.closing, self.__ski_resort_object.time)):
                min_time = self.__add_times(run.opening, run.open_length)
                max_time = run.closing
                adjacent_nodes_1 = self.__ski_resort[run.name].runs
                for run_1 in adjacent_nodes_1:
                    if (self.__compare_greater(run_1.opening, min_time) and self.__compare_greater(max_time, run_1.opening)) or (self.__compare_greater_or_equal(min_time, run_1.opening) and self.__compare_greater(run_1.closing, min_time)):
                        min_time_1 = self.__add_times(min_time, run_1.open_length)
                        max_time_1 = max_time
                        if self.__compare_greater(self.__add_times(run_1.opening, run_1.open_length), min_time_1):
                            min_time_1 = self.__add_times(run_1.opening, run_1.open_length)
                        if self.__compare_greater_or_equal(max_time_1, run_1.closing):
                            max_time_1 = run_1.closing
                        adjacent_nodes_2 = self.__ski_resort[run_1.name].runs
                        for run_2 in adjacent_nodes_2:
                            if (self.__compare_greater(run_2.opening, min_time_1) and self.__compare_greater(max_time_1, run_2.opening)) or (self.__compare_greater_or_equal(min_time_1, run_2.opening) and self.__compare_greater(run_2.closing, min_time_1)):
                                continue_route = True
                                break
                        if continue_route == True:
                            break
                if continue_route == True:
                    break
        return continue_route

    ###############################################
    # GROUP B Skill: Simple user defined algorithms
    ###############################################
    def __complete_move(self,priorities,adjacent_nodes,time_elapsed,route,original_chosen_node): #A procedure which completes the first move of the sequence of three moves which was determined to have the highest value.
        #Parameters: priorities - List, adjacent_nodes - List, time_elapsed - Integer, route – List. Return values: chosen_node - Object, time_elapsed - Integer, route – List.
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
        if chosen_node.lift:
            lift_or_run = "lift"
        else:
            lift_or_run = "run"
        route.append({"start":chosen_node.name,"time_elapsed":time_elapsed,"pause":False, "lift":lift_or_run, "break":False})
        if (original_chosen_node.name,chosen_node.name) in self.__repeated_runs.keys():
            self.__repeated_runs[(original_chosen_node.name,chosen_node.name)] += 1
        else:
            self.__repeated_runs[(original_chosen_node.name,chosen_node.name)] = 1
        self.__ski_resort_object.increment_time(chosen_node.length)
        return chosen_node, time_elapsed, route

    ###############################################
    # GROUP B Skill: Simple user defined algorithms
    ###############################################
    def __fastest_route_back(self, chosen_node,time_elapsed,route): #Determines the fastest route back to the starting node from the current node using a Dijkstra’s graph traversal.
        #Parameters: chosen_node – Object ,time_elapsed - Integer, route – List. Return values: temp_route – List.
        temp_route = route.copy()
        times,previous_node = self.__dijkstras_traversal(chosen_node.name, False)
                
        route_to_finish = []
        current = self.__start
        route_to_finish.insert(0,current)
        while current != chosen_node.name:
            current = previous_node[current]
            route_to_finish.insert(0,current)
                
        for i in range(len(route_to_finish)-1):
            run_length = (self.__ski_resort[route_to_finish[i]].runs[[run.name for run in self.__ski_resort[route_to_finish[i]].runs].index(route_to_finish[i+1])]).length
            if run_length != inf: #Ensures that the run is only added to the route if it is open
                time_elapsed += run_length
                self.__ski_resort_object.increment_time(run_length)
                chosen_node = self.__ski_resort[route_to_finish[i]].runs[[run.name for run in self.__ski_resort[route_to_finish[i]].runs].index(route_to_finish[i+1])]
                if chosen_node.lift:
                    lift_or_run = "lift"
                else:
                    lift_or_run = "run"
                temp_route.append({"start":chosen_node.name,"time_elapsed":time_elapsed,"pause":False, "lift":lift_or_run, "break":False})
            else:
                break
        return temp_route

    #####################################
    # GROUP A Skill: Recursive algorithms
    #####################################
    def __find_values(self,adjacent_nodes,count,temp_time_elapsed, priorities, value, values, ignore_way_home, previous_node): #A recursive function to find the values of all of the possible sequences of three moves from the current node and determine which one has the maximum value. 
        #Parameters: adjacent_nodes - List, count - Integer, temp_time_elapsed - Integer, priorities - List, value - Integer, values - List, ignore_way_home – Boolean. Return values: priorities - List, values - List, count – Integer.
        if count >= 2: #base case determining the search depth through the graph
            for node_1 in adjacent_nodes:
                temp_time_elapsed += node_1.length
                if ignore_way_home:
                    times, prev = self.__dijkstras_traversal(node_1.name, True)
                else:
                    times, prev = self.__dijkstras_traversal(node_1.name, False)
                time_from_start = times[self.__start]
                time_value = 0
                time_value = self.__length - temp_time_elapsed - time_from_start
                node_value = self.__generate_values(self.__ski_resort[previous_node.name], node_1)
                value += node_value
                if time_value < 0: #If the time to get back to the starting node is greater than the time left in the route, the value is the time to get back to the starting node
                    values.append(time_value)
                else: #If the time to get back to the starting node is less than the time left in the route, the value is the desirability of the runs in the route
                    values.append(value)
                temp_time_elapsed -= node_1.length
                value -= node_value
            count -= 1
            return priorities, values, count
        for node in adjacent_nodes: #Iterate through the adjacent nodes to calculate the values for each possible move
            if count == 0:
                values = []
            count += 1
            temp_time_elapsed += node.length
            self.__ski_resort_object.increment_time(node.length)
            node_value = self.__generate_values(self.__ski_resort[previous_node.name], node) #continue
            value += node_value
            priorities,values,count = self.__find_values(self.__ski_resort[node.name].runs, count, temp_time_elapsed, priorities, value, values, ignore_way_home, node) #Call the function recursively
            value -= node_value
            self.__ski_resort_object.decrement_time(node.length)
            temp_time_elapsed -= node.length
            if count == 0:
                priorities.append(max(values))

        count -= 1
        return priorities, values, count
    
    ################################################
    # GROUP A Skill: Complex user-defined algorithms
    ################################################
    def get_route(self, as_close_to_time, route, start, time_elapsed): #Generates the complete route through the ski resort returing the route as a list of dictionaries and a boolean indicating if the route returned to the starting node.
        #Parameters: as_close_to_time – Boolean. Return values: route – List of dictionaries, returned_to_start – Boolean.
        complete = False
        chosen_node = self.__ski_resort[start]
        returned_to_start = True
        previous_route_length = self.__length

        while complete == False: #The route generation continues until it has to end due to the time limit being reached or closure of lifts forcing it to stop

            find_priorities = []
            adjacent_nodes = self.__ski_resort[chosen_node.name].runs
            count = 0
            temp_time_elapsed = time_elapsed
            value = 0
            values = []
            priorities, values, count = self.__find_values(adjacent_nodes,count,temp_time_elapsed, find_priorities, value, values, False, chosen_node)

            if max(priorities) == -inf: #If all sequences of three moves have to pass through a closed lift or there is no route to the starting node without passing through a closed lift
                continue_route = self.__should_route_continue(adjacent_nodes)     

                find_priorities = []
                count = 0
                temp_time_elapsed = time_elapsed
                value = 0
                values = []
                priorities, values, count = self.__find_values(adjacent_nodes,count,temp_time_elapsed, find_priorities, value, values, True, chosen_node) #Finds the values of the possible routes but ignoring if there is no route to the starting node without passing through a closed lift
                
                times, prev = self.__dijkstras_traversal(chosen_node.name, True)
                time_from_start = times[self.__start]
                time_value = self.__length - time_elapsed - time_from_start

                if max(priorities) >= 0: #If a sequence of three moves is still viable (the algorithm has entered this edge case since there is no longer a route to the starting node without passing through a closed lift)
                    chosen_node, time_elapsed, route = self.__complete_move(priorities,adjacent_nodes,time_elapsed,route, chosen_node)
                    
                elif max(priorities) != -inf and chosen_node.name == self.__start: #If there is not time left for a sequence of three moves and the route has returned to the starting node
                    route, change, time_elapsed, chosen_node = self.__two_move_route(chosen_node,adjacent_nodes,time_elapsed,route,as_close_to_time)
                    complete = True #end the route generation

                elif max(priorities) != -inf: #If there is not time left for a sequence of three moves and the route has not returned to the starting node
                    route = self.__best_way_back(route,time_elapsed,chosen_node,as_close_to_time,adjacent_nodes) #Get as far back to the starting node as possible
                    complete = True

                #The remaining edge cases are when the route is stopped by reaching unopened runs
                elif (len(route) == 1 or previous_route_length + 1 == self.__length) and continue_route == True and time_value >= 0: #If the route hasn't started yet and there will be possible sequences of moves in the future
                    time_elapsed, route = self.__pause_route(time_elapsed,route,chosen_node)
                    previous_route_length = self.__length
                    self.__length += 1 #Length of the route is increased by 1 minute to account for the time spent waiting for the ski lifts to open
                               
                elif continue_route == True and time_value >= 0: #If the route can continue since the surrounding runs are yet to open
                    time_elapsed, route = self.__pause_route(time_elapsed,route,chosen_node)

                else: #If the route cannot continue
                    route = self.__best_way_back(route,time_elapsed,chosen_node,as_close_to_time,adjacent_nodes) #Get as far back to the starting node as possible
                    complete = True #End the route generation

            elif max(priorities) < 0 and chosen_node.name == self.__start: #If no sequence of three moves is viable within the time and the route has returned to the start node
                route, change, time_elapsed, chosen_node = self.__two_move_route(chosen_node,adjacent_nodes,time_elapsed,route,as_close_to_time)
                complete = True #End the route generation

            elif max(priorities) < 0: #If no sequence of three moves is viable within the time and the route has not returned to the start node
                route = self.__best_way_back(route,time_elapsed,chosen_node,as_close_to_time,adjacent_nodes)
                complete = True
            
            else: #If a sequence of three moves is viable within the time
                chosen_node, time_elapsed, route = self.__complete_move(priorities,adjacent_nodes,time_elapsed,route,chosen_node)

        if route[-1]["start"] != self.__start: #Check if the route ends at the starting node
            returned_to_start = False
        return route, returned_to_start, self.__length

###############################
# GROUP A Skill: Priority queue
###############################
class Priority_queue(): #Implementation of a circular, priority queue using a static array
    def __init__(self,n): #Initialises the length of the queue in memory. Parameters: n – integer. Return values: None.
        self.__max_length = int((0.5*n**2)-(1.5*n)+2) #The maximum length of the queue that the Dijkstra's algorithm could require if the graph is fully connected 
        self.__queue = [(0,"") for i in range(int(self.__max_length))] #The memory used to store the queue is allocated when the priority queue is initialised
        self.__front = 0
        self.__rear = -1
        self.__size = 0

    #################################
    # GROUP A Skill: Queue operations
    #################################
    def enQueue(self,item): #Adds an item to the rear of the queue where an item is a tuple of (distance, node name). Parameters: item – Tuple. Return values: None
        if self.isFull():
            print("Queue is full")
        self.__rear = int((self.__rear + 1) % self.__max_length)
        self.__queue[self.__rear] = item
        self.__size += 1
        #priority shift
        counter = self.__rear
        while self.__queue[counter][0] < self.__queue[int((counter-1)%self.__max_length)][0] and counter != self.__front:
            self.__queue[counter],self.__queue[counter-1] = self.__queue[counter-1],self.__queue[counter]
            counter = int((counter-1)%self.__max_length)

    def deQueue(self): #Pops the front of the queue. Parameters: None. Return values: None.
        if self.isEmpty():
            print("Queue is empty")
            return None
        data_item = self.__queue[self.__front]
        self.__front = int((self.__front + 1) % self.__max_length)
        self.__size -= 1
        return data_item
    
    def isEmpty(self): #Checks if the queue is empty. Parameters: None. Return values: None.
        return self.__size == 0
    
    def isFull(self): #Checks if the queue is full. Parameters: None. Return values: None.
        return self.__size == self.__max_length