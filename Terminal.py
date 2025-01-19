from Ui import Ui
from route_planner import Plan_route
import re
import sqlite3
from math import inf
from ski_resorts import Ski_resorts, Ski_resort, Ski_node, Run
from display_graph import Display_graph
from database_changes import sync_from_database, add_resort_to_database
from file_changes import view_previous_route, save_route, get_route_names
#Implements the terminal based user interface and  allows the user to interact with the program

class Terminal(Ui): #The object with which the user interacts with the program inherited from ‘Ui’
    DATABASE_NAME = "ski_resorts.db"
    def __init__(self): #Initialises the database creating the tables if they are not already created and creating the graph structure. Parameters: None. Return values: None.
        self.__saved_ski_resorts = Ski_resorts()
        self.__construct_example_ski_resort()
        ###############################################
        # GROUP A Skill: Complex data model in database
        ###############################################
        try:
            with sqlite3.connect(self.DATABASE_NAME) as conn:
                cursor = conn.cursor()
                create_nodes_table = """CREATE TABLE IF NOT EXISTS nodes (
                                    node_id INTEGER PRIMARY KEY AUTOINCREMENT,
                                    node_name TEXT NOT NULL,
                                    resort_name TEXT NOT NULL,
                                    altitude INTEGER,
                                    node_type TEXT,
                                    ski_park_length INTEGER,
                                    amenity_type TEXT
                                );"""
                cursor.execute(create_nodes_table)
                create_runs_table = """CREATE TABLE IF NOT EXISTS runs (
                                    run_id INTEGER PRIMARY KEY AUTOINCREMENT,
                                    node_id INTEGER NOT NULL,
                                    end_node_id INTEGER NOT NULL,
                                    run_length INTEGER NOT NULL,
                                    opening TEXT NOT NULL,
                                    closing TEXT NOT NULL,
                                    lift BOOLEAN,
                                    difficulty TEXT,
                                    lift_type TEXT
                                );"""
                cursor.execute(create_runs_table)
                conn.commit()
        except sqlite3.OperationalError as e:
            print("Failed to open database: ", e)

    def menu(self): #prints the options of different features which the program can run and receives an input for which one to proceed with. There is also the option to exit the program.
        #A ‘Display_graph’ object is also created if option 4 is selected allowing the graph to be displayed. Parameters: None. Return values: None.
        option = "-1"
        print("""
        Menu:
        1. Generate your route
        2. Create a ski resort
        3. Modify an existing ski resort
        4. Display a ski resort
        5. Delete a ski resort
        6. View previous routes
        7. Exit\n""")
        while option not in ["1","2","3","4","5","6","7"]:
            option = input("Enter the number of the option that you want to select: ")

        if option == "1":
            self.__generate_route()            
            while option not in ["m","q"]:
                option = input("Enter 'm' to return to the main menu or 'q' to quit: ")
            if option == "m":
                self.menu()
            elif option == "q":
                quit()
        elif option == "2":
            self.__create_ski_resort()
            while option not in ["m","q"]:
                option = input("Enter 'm' to return to the main menu or 'q' to quit: ")
            if option == "m":
                self.menu()
            elif option == "q":
                quit()
        elif option == "3":
            self.__modify_ski_resort()
            while option not in ["m","q"]:
                option = input("Enter 'm' to return to the main menu or 'q' to quit: ")
            if option == "m":
                self.menu()
            elif option == "q":
                quit()
        elif option == "4":
            self.__saved_ski_resorts = Ski_resorts() #overwrite the locally stored ski resorts
            self.__saved_ski_resorts = sync_from_database(self.__saved_ski_resorts) #Sync the ski resorts stored in the database with the ski resorts stored in the program
            self.__construct_example_ski_resort()
            ski_resort_name = ""
            while ski_resort_name not in self.__saved_ski_resorts.resorts.keys():
                ski_resort_name = input(f"Enter the name of the ski resort that you want to display: ({', '.join(self.__saved_ski_resorts.resorts.keys())})\n")
            Display_graph().display_ski_resort(self.__saved_ski_resorts.resorts[ski_resort_name])
            while option not in ["m","q"]:
                option = input("Enter 'm' to return to the main menu or 'q' to quit: ")
            if option == "m":
                self.menu()
            elif option == "q":
                quit()
        elif option == "5":
            self.__delete_ski_resort()
            while option not in ["m","q"]:
                option = input("Enter 'm' to return to the main menu or 'q' to quit: ")
            if option == "m":
                self.menu()
            elif option == "q":
                quit()
        elif option == "6":
            previous_route_names = get_route_names()
            if len(previous_route_names) != 0:
                route_name = ""
                while route_name not in previous_route_names:
                    route_name = input(f"Enter the name of the route that you want to view: ({", ".join(previous_route_names)})\n")
                route_to_display, resort_name = view_previous_route(route_name)
                print(f"\nRoute '{route_name}' in {resort_name}:")
                for line in route_to_display:
                    print(line)
            else:
                print("There are no routes saved.")
            while option not in ["m","q"]:
                option = input("Enter 'm' to return to the main menu or 'q' to quit: ")
            if option == "m":
                self.menu()
            elif option == "q":
                quit()
        elif option == "7":
            quit()

    def __add_times(self, t1, t2): #Adds two times together where t1 is in the format hh:mm and t2 is an integer number of minutes. Parameters: t1 - String, t2 – Integer. Return values: ‘hh:mm’ – String.
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
    
    def __compare_greater(self,t1,t2): #Compares if a time t1 is greater than the time t2. Parameters: t1 – String, t2 – Sting. Return values: Boolean.
        h1, m1 = t1.split(":")
        h2, m2 = t2.split(":")
        if int(h1) > int(h2):
            return True
        elif int(h1) == int(h2) and int(m1) > int(m2):
            return True
        else:
            return False
    
    def __time_difference(self, t1, t2): #Returns the difference between two times t1 and t2 where t1 and t2 are in the format hh:mm. Parameters: t1 – String, t2 – Sting. Return values: Integer.
        h1, m1 = t1.split(":")
        h2, m2 = t2.split(":")
        return (int(h2)*60 + int(m2)) - (int(h1)*60 + int(m1))
    
    def __construct_example_ski_resort(self): #Creates an example ski resort ‘Val Thorens’ with nodes and runs which can be used for testing. It is only stored locally within the graph data structure. Parameters: None. Return values: None.
        ######################
        # GROUP A Skill: Graph
        ######################
        self.__saved_ski_resorts.add_resort("Val Thorens")
        self.__saved_ski_resorts.resorts["Val Thorens"].add_ski_node("Plein Sud bottom", 2300)
        self.__saved_ski_resorts.resorts["Val Thorens"].nodes["Plein Sud bottom"].add_run("Plein Sud top",10, "08:00", "17:00", 1, "None", "chairlift")
        self.__saved_ski_resorts.resorts["Val Thorens"].add_ski_node("Plein Sud top",2600)
        self.__saved_ski_resorts.resorts["Val Thorens"].nodes["Plein Sud top"].add_run("La folie douce", 2, "00:00", "23:59", 0, "blue", "None")
        self.__saved_ski_resorts.resorts["Val Thorens"].nodes["Plein Sud top"].add_run("Pionniers top",1, "00:00", "23:59", 0, "blue", "None")
        self.__saved_ski_resorts.resorts["Val Thorens"].add_ski_node("3 Vallees bottom",2500)
        self.__saved_ski_resorts.resorts["Val Thorens"].nodes["3 Vallees bottom"].add_run("Snow park 1",5, "00:00", "23:59", 0, "blue", "None")
        self.__saved_ski_resorts.resorts["Val Thorens"].nodes["3 Vallees bottom"].add_run("3 Vallees top",6, "08:30", "16:00" , 1, "None", "gondola")
        self.__saved_ski_resorts.resorts["Val Thorens"].add_ski_node("3 Vallees top",3000)
        self.__saved_ski_resorts.resorts["Val Thorens"].nodes["3 Vallees top"].add_run("3 Vallees bottom",5, "00:00", "23:59", 0, "black", "None")
        self.__saved_ski_resorts.resorts["Val Thorens"].nodes["3 Vallees top"].add_run("Plein Sud top",4, "00:00", "23:59", 0, "red", "None")
        self.__saved_ski_resorts.resorts["Val Thorens"].add_ski_node("Pionniers bottom",2400)
        self.__saved_ski_resorts.resorts["Val Thorens"].nodes["Pionniers bottom"].add_run("Plein Sud bottom",10, "00:00", "23:59", 0, "blue", "None")
        self.__saved_ski_resorts.resorts["Val Thorens"].nodes["Pionniers bottom"].add_run("Pionniers top",4, "08:00", "16:30", 1, "None", "chairlift")
        self.__saved_ski_resorts.resorts["Val Thorens"].add_ski_node("Pionniers top",2550)
        self.__saved_ski_resorts.resorts["Val Thorens"].nodes["Pionniers top"].add_run("3 Vallees bottom",1, "00:00", "23:59", 0, "blue", "None")
        self.__saved_ski_resorts.resorts["Val Thorens"].add_amenity("La folie douce", 2550, "restaurant")
        self.__saved_ski_resorts.resorts["Val Thorens"].nodes["La folie douce"].add_run("Pionniers bottom", 3, "00:00", "23:59", 0, "blue", "None")
        self.__saved_ski_resorts.resorts["Val Thorens"].add_ski_park("Snow park 1", 2400, 4)
        self.__saved_ski_resorts.resorts["Val Thorens"].nodes["Snow park 1"].add_run("Plein Sud bottom", 10, "00:00", "23:59", 0, "blue", "None")

    def __advanced_options(self): #Allows the user to input advanced options for the route generation relating to the desired punctuality of the end time of the route, the snow conditions and weather and the ski lift type preference.
        #Parameters: None. Return values: as_close_to_time – Boolean, snow_conditions – String, lift_type_preference – String, weather – String, latitude – String, longitude – String.
        weather = ""
        as_close_to_time = ""
        snow_conditions = ""
        lift_type_preference = ""
        altitude = ""
        latitude = ""
        longitude = ""
        as_close_to_time_input = ""
        while as_close_to_time_input not in ["y","n"]:
            as_close_to_time_input = input("Do you want the end time to be finish as close to rather than finish before? (y/n): ")
        if as_close_to_time_input == "y":
            as_close_to_time = True
        else:
            as_close_to_time = False
        while altitude not in ["y","n"]:
            altitude = input("Do you want to consider the snow conditions and weather at your resort? (y/n): ")
        if altitude == "y":
            while snow_conditions not in ["good","average","poor", "unknown"]:
                snow_conditions = input("What are the snow conditions like ('good', 'average', 'poor' or 'unknown): ")
            while weather not in ["today","tomorrow","2 days time","3 days time","unknown"]:
                weather = input("On what day are you skiing? ('today', 'tomorrow', '2 days time', '3 days time' or 'unknown'): ")
            while not(re.match(r'^-?\d{1,2}\.\d{4}$', latitude)) and latitude != "N/A" and latitude != "default":
                latitude = input("Enter the latitude of the resort (enter 'N/A' if unknown or 'default' for the latitude of Val Thorens): ")
            while not(re.match(r'^-?\d{1,3}\.\d{4}$', longitude)) and longitude != "N/A" and longitude != "default":
                longitude = input("Enter the longitude of the resort (enter N/A if unknown or 'default' for the longitude of Val Thorens): ")
        else:
            snow_conditions = "unknown"
            weather = "unknown"
            latitude = "N/A"
            longitude = "N/A"
        while lift_type_preference not in ["gondola","chairlift","draglift","no preference"]:
            lift_type_preference = input("Do you want to use more of one type of ski lift than the others ('gondola', 'chairlift', 'draglift' or 'no preference'): ")

        return as_close_to_time, snow_conditions, lift_type_preference, weather, latitude, longitude

    def __generate_route(self): #Receives and validates the inputs required to create a route through a ski resort. This includes how long the user wants to ski for, what resort they are in and what lift station they want to start their route from. Parameters: None. Return values: None.
        self.__saved_ski_resorts = Ski_resorts() #overwrite the locally stored ski resorts
        self.__saved_ski_resorts = sync_from_database(self.__saved_ski_resorts) #Sync the ski resorts stored in the database with the ski resorts stored in the program
        self.__construct_example_ski_resort()
        length = "00:00"
        valid = None
        while valid == None:
            length = input("How long do you want to ski for (hh:mm): ")

            try:
                if int(length[length.index(":")+1:]) < 60 and re.match(r'^\d{2}:\d{2}$', length):
                    valid = True
            except:
                print("Error. The length of time that you want to ski for must be in the format hh:mm.")
        h,m = length.split(":")
        length = int(h)*60 + int(m)

        ski_resort = ""
        while ski_resort not in self.__saved_ski_resorts.resorts.keys():
            ski_resort = input(f"Which ski resort are you in: ({', '.join(self.__saved_ski_resorts.resorts.keys())})\n")

        start = ""
        while start not in self.__saved_ski_resorts.resorts[ski_resort].nodes.keys():
            start = input(f"From which ski lift station do you want to start and end your route: ({', '.join(self.__saved_ski_resorts.resorts[ski_resort].nodes.keys())})\n")
        original_start = start

        start_time = "00:00"
        valid = None
        while valid == None:
            start_time = input("At what time do you want to start your route (hh:mm): ")
            try:
                if int(start_time[start_time.index(":")+1:]) < 60 and re.match(r'^\d{2}:\d{2}$', start_time):
                    valid = True
            except:
                print("Error. The start time of the route must be in the format hh:mm.")
        route_start_time = start_time
        route_stop_time = self.__add_times(start_time, length)

        max_difficulty = ""
        while max_difficulty not in ["green","blue","red","black","unknown"]:
            max_difficulty = input("What is the maximum difficulty of run that you want to ski on ('green', 'blue', 'red', 'black' or 'unknown'): ")

        breaks_data = []
        breaks = ""
        while breaks not in ["y","n"]:
            breaks = input("Do you want to take breaks during your skiing time e.g. for lunch or at ski parks? (y/n): ")
        break_type = "None"
        amenity_name = "None"
        break_time = ""
        break_length = 0
        park_repetitions = 0
        previous_time = "00:00"
        if breaks == "y":
            while breaks == "y":
                break_type = ""
                while break_type not in ["restaurant/amenity","ski park"]:
                    break_type = input("What type of break do you want to take ('restaurant/amenity' or 'ski park'): ")
                if break_type == "restaurant/amenity":
                    amenity_name = ""
                    while amenity_name not in self.__saved_ski_resorts.resorts[ski_resort].amenity_names:
                        amenity_name = input(f"Enter the name of the restaurant/amenity that you want to stop at ({", ".join(self.__saved_ski_resorts.resorts[ski_resort].amenity_names)}): ")
                else:
                    amenity_name = ""
                    while amenity_name not in self.__saved_ski_resorts.resorts[ski_resort].ski_park_names:
                        amenity_name = input(f"Enter the name of the ski park that you want to stop at ({", ".join(self.__saved_ski_resorts.resorts[ski_resort].ski_park_names)}): ")

                valid = None
                while valid == None:
                    break_time = input("At what time do you want to visit this amenity (hh:mm): ")
                    try:
                        if int(break_time[break_time.index(":")+1:]) < 60 and re.match(r'^\d{2}:\d{2}$', break_time):
                            if self.__compare_greater(break_time, start_time) and self.__compare_greater(route_stop_time, break_time):
                                if self.__compare_greater(break_time, previous_time):
                                    previous_time = break_time
                                    valid = True
                                else:
                                    print("Error. The time that you want to visit this amenity at must be after the time that you visited the previous amenity at.")
                            else:
                                print("Error. The time that you want to visit this amenity at must be after the start time of the route and before the end time.")
                        else:
                            print("Error. The time that you want to visit this amenity at must be in the format hh:mm.")
                    except:
                        print("Error. The time that you want to visit this amenity at must be in the format hh:mm.")

                if break_type == "restaurant/amenity":
                    break_length = 0
                    allowed_time = self.__time_difference(break_time, route_stop_time)
                    valid = False
                    while valid == False:
                        try:
                            break_length = int(input("How long do you want to spend at this restaurant/amenity (minutes): "))
                        except ValueError:
                            print("Error. The break length must be a positive integer.")
                        if break_length > 0:
                            if break_length <= allowed_time:
                                valid = True
                            else:
                                print("Error. The break cannot extend past the desired end time of this route.")
                elif break_type == "ski park":
                    park_repetitions = 0
                    while park_repetitions < 1:
                        park_repetitions = int(input("How many times do you want to ski the ski park: "))
                breaks = ""
                while breaks not in ["y","n"]:
                    breaks = input("Do you want to take another break during your skiing time? (y/n): ")
                breaks_data.append([break_type, amenity_name, break_time, break_length, park_repetitions])

        advanced_options = ""
        while advanced_options not in ["y","n"]:
            advanced_options = input("Do you want to enter further advanced options? (y/n): ")
        if advanced_options == "y":
            as_close_to_time, snow_conditions, lift_type_preference, weather, latitude, longitude = self.__advanced_options()
        else:
            weather = "unknown"
            as_close_to_time = False
            snow_conditions = "unknown"
            lift_type_preference = "no preference"
            latitude = "N/A"
            longitude = "N/A"

        route = [{"start":start,"time_elapsed":0,"pause":False,"lift":None,"break":False}]
        time_elapsed = 0
        for plan_num in range(len(breaks_data)+1):
            if len(breaks_data) > 0:
                if plan_num > 0:
                    start_time = self.__add_times(route_start_time, time_elapsed)
                if plan_num < len(breaks_data):
                    end_time = breaks_data[plan_num][2]
                    length = self.__time_difference(route_start_time,end_time)
                    end_node = breaks_data[plan_num][1]
                else:
                    length = self.__time_difference(route_start_time,route_stop_time)
                    end_node = original_start
                route_planning = Plan_route(self.__saved_ski_resorts.resorts[ski_resort], end_node, length, start_time, max_difficulty, snow_conditions, lift_type_preference, weather, latitude, longitude)
                route, returned_to_start, new_length = route_planning.get_route(as_close_to_time, route, start, time_elapsed)

                if not returned_to_start:
                    break
                if new_length > length:
                    for break_num in range(len(breaks_data)):
                        breaks_data[break_num][2] = self.__add_times(breaks_data[break_num][2], new_length-length)
                    end_time = self.__add_times(end_time, new_length-length)
                    length = new_length
                if plan_num < len(breaks_data):
                    time_elapsed = route[-1]["time_elapsed"]
                    if breaks_data[plan_num][0] == "restaurant/amenity":
                        wait_length = breaks_data[plan_num][3]
                        route.append({"start":route[-1]["start"],"time_elapsed":time_elapsed+wait_length,"pause":False,"lift":None,"break":True})
                    elif breaks_data[plan_num][0] == "ski park":
                        ski_park_length = breaks_data[plan_num][4]*self.__saved_ski_resorts.resorts[ski_resort].nodes[breaks_data[plan_num][1]].length
                        route.append({"start":route[-1]["start"],"time_elapsed":time_elapsed+ski_park_length,"pause":False,"lift":None,"break":True})
                if plan_num < len(breaks_data):
                    start = breaks_data[plan_num][1]
                    time_elapsed = route[-1]["time_elapsed"]
            else:
                route_planning = Plan_route(self.__saved_ski_resorts.resorts[ski_resort], start, length, start_time, max_difficulty, snow_conditions, lift_type_preference, weather, latitude, longitude)
                route, returned_to_start, length = route_planning.get_route(as_close_to_time, route, start, time_elapsed) #Returns a list of dictionaries containing the node moved to and the time elapsed
        
        for i in range(len(route)-1):
            if route[i+1]["pause"] == True:
                if i != 0:
                    print(f"{i+1}. Break for {route[i+1]["time_elapsed"]-route[i]["time_elapsed"]} minutes due to ski lifts not yet being open - {self.__add_times(route_start_time,route[i+1]["time_elapsed"])}")
                else:
                    print(f"{i+1}. Break for {route[i+1]["time_elapsed"]-route[i]["time_elapsed"]} minutes due to ski lifts not yet being open (route length increased by {route[i+1]["time_elapsed"]-route[i]["time_elapsed"]} minutes) - {self.__add_times(route_start_time,route[i+1]["time_elapsed"])}")
            elif route[i+1]["break"] == True:
                print(f"{i+1}. Break for {route[i+1]["time_elapsed"]-route[i]["time_elapsed"]} minutes at {route[i+1]["start"]} ({self.__saved_ski_resorts.resorts[ski_resort].nodes[route[i+1]["start"]]}) - {self.__add_times(route_start_time,route[i+1]["time_elapsed"])}")
            else: #add lift/run from x to y
                print(f"{i+1}. {route[i+1]["lift"].title()} from {route[i]['start']} to {route[i+1]['start']} taking {route[i+1]['time_elapsed']-route[i]['time_elapsed']} minutes - {self.__add_times(route_start_time,route[i+1]['time_elapsed'])}")

        if not returned_to_start:
            print(f"Your route could not return to the starting point in the time that you wanted to ski for due to ski lift closing times.")

        save = input("Do you want to save this route? (y/n): ")
        if save == "y":
            previous_route_names = get_route_names()
            route_name = ""
            while route_name in previous_route_names or not(re.match('(^[a-z]|[A-Z]).*$',route_name)):
                route_name = input("Enter the name of the route: ")
            save_route(route_name, route, route_start_time, returned_to_start, ski_resort, self.__saved_ski_resorts)

    ################################################################################################
    # GROUP A Skill: Dynamic generation of objects based on complex user-defined use of an OOP model
    ################################################################################################
    def __create_ski_resort(self): #Receives and validates the inputs required to create a new ski resort. This includes receiving the name of the ski resort, the name of all nodes and the information required to create each run from each node. 
        #The subprogram must then check that no nodes were used as end points of runs without being defined as a node and if they were, the user should be forced to create them. The newly created ski resort is then displayed. Parameters: None. Return values: None.
        self.__saved_ski_resorts = Ski_resorts() #overwrite the locally stored ski resorts
        self.__saved_ski_resorts = sync_from_database(self.__saved_ski_resorts) #Sync the ski resorts stored in the database with the ski resorts stored in the program
        self.__construct_example_ski_resort()
        ski_resort_name = ""
        while ski_resort_name in self.__saved_ski_resorts.resorts or not(re.match('(^[a-z]|[A-Z]).*$',ski_resort_name)):
            ski_resort_name = input("Enter the name of the ski resort which you want to create: ")
        self.__saved_ski_resorts.add_resort(ski_resort_name)

        creating = True
        while creating: #Allow any number of ski lift stations to be created
            create_node = ""
            while create_node not in ["y","n"]:
                create_node = input("Do you want to create a new ski lift station? (y/n): ")
            if create_node == "y":
                node_name = ""
                while node_name in self.__saved_ski_resorts.resorts[ski_resort_name].nodes or not(re.match('(^[a-z]|[A-Z]).*$',node_name)):
                    if len(self.__saved_ski_resorts.resorts[ski_resort_name].nodes) == 0:
                        node_name = input(f"Enter the name of the ski lift station: (No previously created stations)\n")
                    else:
                        node_name = input(f"Enter the name of the ski lift station: (Previously created ski lift stations: {', '.join(self.__saved_ski_resorts.resorts[ski_resort_name].nodes.keys())})\n")
                node_type = ""
                while node_type not in ["s","p","a"]:
                    node_type = input("Is this a ski lift station, a ski park or an amenity ('s', 'p' or 'a'): ")
                altitude = ""
                while altitude.isnumeric() == False:
                    altitude = input("Enter the altitude of the ski lift station: ")
                altitude = int(altitude)
                if node_type == "p":
                    ski_park_length = 0
                    while ski_park_length < 1:
                        ski_park_length = int(input("Enter the length of the ski park (minutes): "))
                    self.__saved_ski_resorts.resorts[ski_resort_name].add_ski_park(node_name,altitude,ski_park_length)
                elif node_type == "a":
                    amenity_type = ""
                    amenity_type = input("Enter a description of the type of amenity e.g. restaurant: ")
                    self.__saved_ski_resorts.resorts[ski_resort_name].add_amenity(node_name,altitude,amenity_type)
                elif node_type == "s":
                    self.__saved_ski_resorts.resorts[ski_resort_name].add_ski_node(node_name,altitude)
                creating_run = "y"
                while creating_run == "y": #Allow at least one run to be created from each ski lift station
                    run_name = ""
                    while run_name in self.__saved_ski_resorts.resorts[ski_resort_name].nodes[node_name].runs or run_name == node_name or not(re.match('(^[a-z]|[A-Z]).*$',run_name)):
                        run_names_excluding_node = list(self.__saved_ski_resorts.resorts[ski_resort_name].nodes.keys())
                        run_names_excluding_node.remove(node_name)
                        if len(run_names_excluding_node) == 0:
                            run_name = input(f"Enter an end ski lift station of this run: (No previously created runs)\n")   
                        else:
                            run_name = input(f"Enter an end ski lift station of this run: (Previously created run end nodes: {', '.join(run_names_excluding_node)})\n")
                    length = ""
                    while length.isnumeric() == False:
                        length = input("Enter the length of the run (minutes): ")
                    length = int(length)
                    opening = ""
                    valid = False
                    while not valid:
                        opening = input("Enter the opening time of the run (hh:mm): ")
                        try:
                            if int(opening[opening.index(":")+1:]) < 60 and re.match(r'^\d{2}:\d{2}$', opening):
                                valid = True
                        except:
                            print("Error. The opening time must be in the format hh:mm.")
                    closing = ""
                    valid = False
                    while not valid:
                        closing = input("Enter the closing time of the run (hh:mm): ")
                        try:
                            if int(closing[closing.index(":")+1:]) < 60 and re.match(r'^\d{2}:\d{2}$', closing):
                                if self.__compare_greater(closing, opening):
                                    valid = True
                                else:
                                    print("Error. The closing time must be after the opening time.")
                        except:
                            print("Error. The closing time must be in the format hh:mm.")
                    lift = ""
                    while lift not in ["l","r"]:
                        lift = input("Is this a lift or a run ('l' or 'r'): ")
                    if lift == "l":
                        lift = 1
                        lift_type = ""
                        while lift_type not in ["gondola","chairlift","draglift"]:
                            lift_type = input("Enter the type of lift ('gondola', 'chairlift', 'draglift'): ")
                        difficulty = "none"
                    elif lift == "r":
                        lift = 0
                        lift_type = "none"
                        difficulty = ""
                        while difficulty not in ["green","blue","red","black"]:
                            difficulty = input("Enter the difficulty of the run ('green', 'blue', 'red', 'black'): ")
                    self.__saved_ski_resorts.resorts[ski_resort_name].nodes[node_name].add_run(run_name,length,opening,closing,lift,difficulty,lift_type)
                    creating_run = ""
                    while creating_run not in ["y","n"]:
                        creating_run = input("Do you want to create another run from this ski lift station? (y/n): ") #Post loop repetition test to ensure that at least one run is added to each ski lift station
            elif create_node == "n":
                creating = False
        
        #Check if any ski lift stations have been used as the end of a run but have not been created
        incomplete_nodes = True
        break_loop = False
        while incomplete_nodes:
            for node in self.__saved_ski_resorts.resorts[ski_resort_name].nodes: #node is a string of the name of the ski lift station
                for run in self.__saved_ski_resorts.resorts[ski_resort_name].nodes[node].runs: #run is the run object
                    if run.name not in self.__saved_ski_resorts.resorts[ski_resort_name].nodes:
                        print(f"Node {run.name} must be created since it was used as the end of a run but has not been created.")
                        node_type = ""
                        while node_type not in ["s","p","a"]:
                            node_type = input("Is this a ski lift station, a ski park or an amenity ('s', 'p' or 'a'): ")
                        altitude = ""
                        while altitude.isnumeric() == False:
                            altitude = input("Enter the altitude of the ski lift station: ")
                        altitude = int(altitude)
                        if node_type == "p":
                            ski_park_length = 0
                            while ski_park_length < 1:
                                ski_park_length = int(input("Enter the length of the ski park (minutes): "))
                            self.__saved_ski_resorts.resorts[ski_resort_name].add_ski_park(run.name,altitude,ski_park_length)
                        elif node_type == "a":
                            amenity_type = ""
                            amenity_type = input("Enter a description of the type of amenity e.g. restaurant: ")
                            self.__saved_ski_resorts.resorts[ski_resort_name].add_amenity(run.name,altitude,amenity_type)
                        elif node_type == "s":
                            self.__saved_ski_resorts.resorts[ski_resort_name].add_ski_node(run.name,altitude)
                        creating_run = "y"
                        while creating_run == "y":
                            run_name = ""
                            while run_name in self.__saved_ski_resorts.resorts[ski_resort_name].nodes[node].runs or run_name == run.name or not(re.match('(^[a-z]|[A-Z]).*$',run_name)):
                                run_names_excluding_node = list(self.__saved_ski_resorts.resorts[ski_resort_name].nodes.keys())
                                run_names_excluding_node.remove(node)
                                if len(run_names_excluding_node) == 0:
                                    run_name = input(f"Enter an end ski lift station of this run: (No previously created runs\n")
                                else:
                                    run_name = input(f"Enter an end ski lift station of this run: (Previously created run end nodes: {', '.join(run_names_excluding_node)})\n")
                            length = ""
                            while length.isnumeric() == False:
                                length = input("Enter the length of the run (minutes): ")
                            length = int(length)
                            opening = ""
                            valid = False
                            while not valid:
                                opening = input("Enter the opening time of the run (hh:mm): ")
                                try:
                                    if int(opening[opening.index(":")+1:]) < 60 and re.match(r'^\d{2}:\d{2}$', opening):
                                        valid = True
                                except:
                                    print("Error. The opening time must be in the format hh:mm.")
                            closing = ""
                            valid = False
                            while not valid:
                                closing = input("Enter the closing time of the run (hh:mm): ")
                                try:
                                    if int(closing[closing.index(":")+1:]) < 60 and re.match(r'^\d{2}:\d{2}$', closing):
                                        if self.__compare_greater(closing, opening):
                                            valid = True
                                        else:
                                            print("Error. The closing time must be after the opening time.")
                                except:
                                    print("Error. The closing time must be in the format hh:mm.")
                            lift = ""
                            while lift not in ["l","r"]:
                                lift = input("Is this a lift or a run ('l' or 'r'): ")
                            if lift == "l":
                                lift = 1
                                lift_type = ""
                                while lift_type not in ["gondola","chairlift","draglift"]:
                                    lift_type = input("Enter the type of lift ('gondola', 'chairlift', 'draglift'): ")
                                difficulty = "none"
                            elif lift == "r":
                                lift = 0
                                lift_type = "none"
                                difficulty = ""
                                while difficulty not in ["green","blue","red","black"]:
                                    difficulty = input("Enter the difficulty of the run ('green', 'blue', 'red', 'black'): ")
                            self.__saved_ski_resorts.resorts[ski_resort_name].nodes[run.name].add_run(run_name,length,opening,closing,lift,difficulty,lift_type)
                            creating_run = ""
                            while creating_run not in ["y","n"]:
                                creating_run = input("Do you want to create another run from this ski lift station? (y/n): ") #Post loop repetition test to ensure that at least one run is added to each ski lift station
                        break_loop = True #The loop will break if a new ski lift station is created since the dictionary being iterated over has changed
                    if break_loop:
                        break
                if break_loop:
                    break
            
            incomplete_nodes = False
            for node in self.__saved_ski_resorts.resorts[ski_resort_name].nodes: #Checks if there are any more ski lift stations that have not been created left
                for run in self.__saved_ski_resorts.resorts[ski_resort_name].nodes[node].runs:
                    if run.name not in self.__saved_ski_resorts.resorts[ski_resort_name].nodes:
                        incomplete_nodes = True
        if self.__saved_ski_resorts.resorts[ski_resort_name].nodes == {}:
            print("There are no ski lift stations in this ski resort so it has not been created.")
        add_resort_to_database(self.__saved_ski_resorts, ski_resort_name) #Add the ski resorts created in the program to the database
        Display_graph().display_ski_resort(self.__saved_ski_resorts.resorts[ski_resort_name]) #display ski resort

    ##############################################
    # GROUP A Skill: Cross-table parameterised SQL
    ##############################################
    def __modify_ski_resort(self): #This method allows a user to modify a pre-existing ski resort in the database through terminal inputs.
        #They are able to modify information about a pre-existing run, add a new node or add a new run. Parameters: None. Return values: None.
        try:
            with sqlite3.connect(self.DATABASE_NAME) as conn:
                cursor = conn.cursor()
                select_resorts = "SELECT resort_name FROM nodes;"
                cursor.execute(select_resorts)
                ski_resorts_list_unpacked = cursor.fetchall()
                ski_resorts_list =[]
                for item in ski_resorts_list_unpacked:
                    ski_resorts_list.append(item[0])
                ski_resorts_list = set(ski_resorts_list)
                ski_resort_to_modify = ""
                while ski_resort_to_modify not in ski_resorts_list:
                    ski_resort_to_modify = input(f"Enter the name of the ski resort you want to modify: ({", ".join(ski_resorts_list)})\n")

                #Choice of modification
                modify = ""
                while modify not in ["1","2","3"]:
                    modify = input("What do you want to modify?\n1. Add a new ski lift station\n2. Add a new run or lift\n3. Modify an existing run\n")
                
                if modify == "1": #add a new ski lift station
                    select_nodes = "SELECT node_name FROM nodes WHERE resort_name=?;"
                    cursor.execute(select_nodes, [ski_resort_to_modify])
                    node_names_unpacked = cursor.fetchall()
                    node_names =[]
                    for item in node_names_unpacked:
                        node_names.append(item[0])
                    node_name = ""
                    while node_name in node_names or not(re.match('(^[a-z]|[A-Z]).*$',node_name)):
                        if len(node_names) == 0:
                            node_name = input(f"Enter the name of the ski lift station that you want to create: (No previously created stations)\n")
                        else:
                            node_name = input(f"Enter the name of the ski lift station that you want to create: (Previously created ski lift stations: {', '.join(node_names)})\n")
                    node_type = ""
                    while node_type not in ["s","p","a"]:
                        node_type = input("Is this a ski lift station, a ski park or an amenity ('s', 'p' or 'a'): ")
                    altitude = ""
                    while altitude.isnumeric() == False:
                        altitude = input("Enter the altitude of the ski lift station: ")
                    altitude = int(altitude)
                    if node_type == "p":
                        ski_park_length = 0
                        while ski_park_length < 1:
                            ski_park_length = int(input("Enter the length of the ski park (minutes): "))
                        add_node = """INSERT INTO nodes (node_name, resort_name, altitude, node_type, ski_park_length, amenity_type)
                                    VALUES (?,?,?,?,?,?);"""
                        cursor.execute(add_node, [node_name, ski_resort_to_modify, altitude, "Ski park", ski_park_length, "None"])
                    elif node_type == "a":
                        amenity_type = ""
                        amenity_type = input("Enter a description of the type of amenity e.g. restaurant: ")
                        add_node = """INSERT INTO nodes (node_name, resort_name, altitude, node_type, ski_park_length, amenity_type)
                                    VALUES (?,?,?,?,?,?);"""
                        cursor.execute(add_node, [node_name, ski_resort_to_modify, altitude, "Amenity", 0, amenity_type])
                    elif node_type == "s":
                        add_node = """INSERT INTO nodes (node_name, resort_name, altitude, node_type, ski_park_length, amenity_type)
                                    VALUES (?,?,?,?,?,?);"""
                        cursor.execute(add_node, [node_name, ski_resort_to_modify, altitude, "Ski lift station", 0, "None"])
                    creating_run = "y"
                    while creating_run == "y": #Allow at least one run to be created from each ski lift station
                        select_runs = "SELECT * FROM runs WHERE node_id=(SELECT node_id FROM nodes WHERE node_name=? AND resort_name=?);"
                        cursor.execute(select_runs, [node_name, ski_resort_to_modify])
                        runs_unpacked = cursor.fetchall()
                        run_names = []
                        for i in range(len(runs_unpacked)):
                            select_end_node_name = "SELECT node_name FROM nodes WHERE node_id=?;"
                            cursor.execute(select_end_node_name, [runs_unpacked[i][2]])
                            end_node_name = cursor.fetchone()[0]
                            run_names.append(end_node_name)
                        run_name = ""
                        node_names.remove(node_name)
                        if len(node_names) == 1:
                            print("There is only one ski lift station in this ski resort so no runs can be created.")
                            break
                        if set(run_names) == set(node_names):
                            print("There are runs from this ski lift station to all other ski lift stations in this ski resort so no more runs can be created.")
                            break
                        while run_name in run_names or run_name == node_name or not(re.match('(^[a-z]|[A-Z]).*$',run_name)) or run_name not in node_names:
                            run_name = input(f"Enter the end ski lift station of a run:\nSki lift stations that the run could end at: ({', '.join(node_names)})\nSki lift stations to which there is already a run: ({', '.join(run_names)})\n")
                        length = ""
                        while length.isnumeric() == False:
                            length = input("Enter the length of the run (minutes): ")
                        length = int(length)
                        opening = ""
                        valid = False
                        while not valid:
                            opening = input("Enter the opening time of the run (hh:mm): ")
                            try:
                                if int(opening[opening.index(":")+1:]) < 60 and re.match(r'^\d{2}:\d{2}$', opening):
                                    valid = True
                            except:
                                print("Error. The opening time must be in the format hh:mm.")
                        closing = ""
                        valid = False
                        while not valid:
                            closing = input("Enter the closing time of the run (hh:mm): ")
                            try:
                                if int(closing[closing.index(":")+1:]) < 60 and re.match(r'^\d{2}:\d{2}$', closing):
                                    if self.__compare_greater(closing, opening):
                                        valid = True
                                    else:
                                        print("Error. The closing time must be after the opening time.")
                            except:
                                print("Error. The closing time must be in the format hh:mm.")
                        lift = ""
                        while lift not in ["l","r"]:
                            lift = input("Is this a lift or a run ('l' or 'r'): ")
                        if lift == "l":
                            lift = 1
                            lift_type = ""
                            while lift_type not in ["gondola","chairlift","draglift"]:
                                lift_type = input("Enter the type of lift ('gondola', 'chairlift', 'draglift'): ")
                            difficulty = "none"
                        elif lift == "r":
                            lift = 0
                            lift_type = "none"
                            difficulty = ""
                            while difficulty not in ["green","blue","red","black"]:
                                difficulty = input("Enter the difficulty of the run ('green', 'blue', 'red', 'black'): ")
                        add_run = """INSERT INTO runs (node_id, end_node_id, run_length, opening, closing, lift, difficulty, lift_type)
                                    VALUES ((SELECT node_id FROM nodes WHERE node_name=? AND resort_name=?),(SELECT node_id FROM nodes WHERE node_name=? AND resort_name=?),?,?,?,?,?,?);"""
                        cursor.execute(add_run, [node_name, ski_resort_to_modify, run_name, ski_resort_to_modify, length, opening, closing, lift, difficulty, lift_type])
                        creating_run = ""
                        while creating_run not in ["y","n"]:
                            creating_run = input("Do you want to create another run from this ski lift station? (y/n): ") #Post loop repetition test to ensure that at least one run is added to each ski lift station
                
                elif modify == "2": #add a new run or lift
                    discontinue = False
                    select_nodes = "SELECT node_name FROM nodes WHERE resort_name=?;"
                    cursor.execute(select_nodes, [ski_resort_to_modify])
                    node_names_unpacked = cursor.fetchall()
                    node_names =[]
                    for item in node_names_unpacked:
                        node_names.append(item[0])
                    node_name = ""
                    while node_name not in node_names or not(re.match('(^[a-z]|[A-Z]).*$',node_name)):
                        if len(node_names) == 1:
                            print(f"There are no nodes to which a run or lift can be added.\n")
                            discontinue = True
                        else:
                            node_name = input(f"Enter the name of the ski lift station from which you want to add a run or lift: (Previously created ski lift stations: {', '.join(node_names)})\n")
                    node_names.remove(node_name)
                    if not discontinue:
                        select_runs = "SELECT * FROM runs WHERE node_id=(SELECT node_id FROM nodes WHERE node_name=? AND resort_name=?);"
                        cursor.execute(select_runs, [node_name, ski_resort_to_modify])
                        runs_unpacked = cursor.fetchall()
                        run_names = []
                        for i in range(len(runs_unpacked)):
                            select_end_node_name = "SELECT node_name FROM nodes WHERE node_id=?;"
                            cursor.execute(select_end_node_name, [runs_unpacked[i][2]])
                            end_node_name = cursor.fetchone()[0]
                            run_names.append(end_node_name)
                        run_name = ""
                        if len(node_names) == 0:
                            print("There is only one ski lift station in this ski resort so no runs can be created.")
                        elif set(run_names) == set(node_names):
                            print("There are runs from this ski lift station to all other ski lift stations in this ski resort so no more runs can be created.")
                        else:
                            while run_name in run_names or run_name == node_name or not(re.match('(^[a-z]|[A-Z]).*$',run_name)) or run_name not in node_names:
                                run_name = input(f"Enter the end ski lift station of a run:\nSki lift stations that the run could end at: ({', '.join(node_names)})\nSki lift stations to which there is already a run: ({', '.join(run_names)})\n")
                            length = ""
                            while length.isnumeric() == False:
                                length = input("Enter the length of the run (minutes): ")
                            length = int(length)
                            opening = ""
                            valid = False
                            while not valid:
                                opening = input("Enter the opening time of the run (hh:mm): ")
                                try:
                                    if int(opening[opening.index(":")+1:]) < 60 and re.match(r'^\d{2}:\d{2}$', opening):
                                        valid = True
                                except:
                                    print("Error. The opening time must be in the format hh:mm.")
                            closing = ""
                            valid = False
                            while not valid:
                                closing = input("Enter the closing time of the run (hh:mm): ")
                                try:
                                    if int(closing[closing.index(":")+1:]) < 60 and re.match(r'^\d{2}:\d{2}$', closing):
                                        if self.__compare_greater(closing, opening):
                                            valid = True
                                        else:
                                            print("Error. The closing time must be after the opening time.")
                                except:
                                    print("Error. The closing time must be in the format hh:mm.")
                            lift = ""
                            while lift not in ["l","r"]:
                                lift = input("Is this a lift or a run ('l' or 'r'): ")
                            if lift == "l":
                                lift = 1
                                lift_type = ""
                                while lift_type not in ["gondola","chairlift","draglift"]:
                                    lift_type = input("Enter the type of lift ('gondola', 'chairlift', 'draglift'): ")
                                difficulty = "none"
                            elif lift == "r":
                                lift = 0
                                lift_type = "none"
                                difficulty = ""
                                while difficulty not in ["green","blue","red","black"]:
                                    difficulty = input("Enter the difficulty of the run ('green', 'blue', 'red', 'black'): ")
                            add_run = """INSERT INTO runs (node_id, end_node_id, run_length, opening, closing, lift, difficulty, lift_type)
                                        VALUES ((SELECT node_id FROM nodes WHERE node_name=? AND resort_name=?),(SELECT node_id FROM nodes WHERE node_name=? AND resort_name=?),?,?,?,?,?,?);"""
                            cursor.execute(add_run, [node_name, ski_resort_to_modify, run_name, ski_resort_to_modify, length, opening, closing, lift, difficulty, lift_type])

                elif modify == "3": #modify an existing run
                    discontinue = False
                    select_nodes = "SELECT node_name FROM nodes WHERE resort_name=?;"
                    cursor.execute(select_nodes, [ski_resort_to_modify])
                    node_names_unpacked = cursor.fetchall()
                    node_names =[]
                    for item in node_names_unpacked:
                        node_names.append(item[0])
                    node_name = ""
                    while node_name not in node_names or not(re.match('(^[a-z]|[A-Z]).*$',node_name)):
                        if len(node_names) == 1:
                            print(f"There are no nodes to which a run or lift can be added.\n")
                            discontinue = True
                        else:
                            node_name = input(f"Enter the name of the ski lift station from which you want to edit a run or lift: (Previously created ski lift stations: {', '.join(node_names)})\n")
                    
                    if not discontinue:
                        select_runs = "SELECT * FROM runs WHERE node_id=(SELECT node_id FROM nodes WHERE node_name=? AND resort_name=?);"
                        cursor.execute(select_runs, [node_name, ski_resort_to_modify])
                        runs_unpacked = cursor.fetchall()
                        run_names = []
                        for i in range(len(runs_unpacked)):
                            select_end_node_name = "SELECT node_name FROM nodes WHERE node_id=?;"
                            cursor.execute(select_end_node_name, [runs_unpacked[i][2]])
                            end_node_name = cursor.fetchone()[0]
                            run_names.append(end_node_name)
                        run_name = ""
                        if len(run_names) == 0:
                            print("There are no runs which can be modified.")
                        else:
                            while run_name not in run_names or run_name == node_name or not(re.match('(^[a-z]|[A-Z]).*$',run_name)):
                                run_name = input(f"Enter the end ski lift station of a run:\nPreviously created ski lift stations: ({', '.join(run_names)})\n")

                            select_node_id = "SELECT node_id FROM nodes WHERE node_name=? AND resort_name=?;"
                            cursor.execute(select_node_id, [node_name, ski_resort_to_modify])
                            node_id = cursor.fetchone()[0]
                            select_end_node_id = "SELECT node_id FROM nodes WHERE node_name=? AND resort_name=?;"
                            cursor.execute(select_end_node_id, [run_name, ski_resort_to_modify])
                            end_node_id = cursor.fetchone()[0]
                            select_lift_or_run = "SELECT lift FROM runs WHERE node_id=? AND end_node_id=?;"
                            cursor.execute(select_lift_or_run, [node_id, end_node_id])
                            lift_or_run = cursor.fetchone()[0]
                            modify3_option = ""
                            if lift_or_run == 0:
                                while modify3_option not in ["1","2","3","4","5","6"]:    
                                    modify3_option = input("What do you want to modify?\n1. Length\n2. Opening time\n3. Closing time\n4. Switch lift or run\n5. Close run\n6. Difficulty\n")
                            elif lift_or_run == 1:
                                while modify3_option not in ["1","2","3","4","5","7"]:
                                    modify3_option = input("What do you want to modify?\n1. Length\n2. Opening time\n3. Closing time\n4. Switch lift or run\n5. Close run\n7. Lift type\n")

                            if modify3_option == "1":
                                length = ""
                                while length.isnumeric() == False:
                                    length = input("Enter the new length of the run (minutes): ")
                                length = int(length)
                                modify_run = "UPDATE runs SET run_length=? WHERE node_id=? AND end_node_id=?;"
                                cursor.execute(modify_run, [length, node_id, end_node_id])
                            elif modify3_option == "2":
                                opening = ""
                                valid = False
                                while not valid:
                                    opening = input("Enter the opening time of the run (hh:mm): ")
                                    try:
                                        if int(opening[opening.index(":")+1:]) < 60 and re.match(r'^\d{2}:\d{2}$', opening):
                                            valid = True
                                    except:
                                        print("Error. The opening time must be in the format hh:mm.")
                                modify_run = "UPDATE runs SET opening=? WHERE node_id=? AND end_node_id=?;"
                                cursor.execute(modify_run, [opening, node_id, end_node_id])
                            elif modify3_option == "3":
                                closing = ""
                                valid = False
                                while not valid:
                                    closing = input("Enter the closing time of the run (hh:mm): ")
                                    try:
                                        if int(closing[closing.index(":")+1:]) < 60 and re.match(r'^\d{2}:\d{2}$', closing):
                                            if self.__compare_greater(closing, opening):
                                                valid = True
                                            else:
                                                print("Error. The closing time must be after the opening time.")
                                    except:
                                        print("Error. The closing time must be in the format hh:mm.")
                                modify_run = "UPDATE runs SET closing=? WHERE node_id=? AND end_node_id=?;"
                                cursor.execute(modify_run, [closing, node_id, end_node_id])
                            elif modify3_option == "4":
                                if lift_or_run == 0:
                                    modify_run = "UPDATE runs SET lift=1 WHERE node_id=? AND end_node_id=?;"
                                    cursor.execute(modify_run, [node_id, end_node_id])
                                elif lift_or_run == 1:
                                    modify_run = "UPDATE runs SET lift=0 WHERE node_id=? AND end_node_id=?;"
                                    cursor.execute(modify_run, [node_id, end_node_id])
                            elif modify3_option == "5":
                                close_run = "UPDATE runs SET run_length=? WHERE node_id=? AND end_node_id=?;"
                                cursor.execute(close_run, [inf, node_id, end_node_id])
                            elif modify3_option == "6":
                                difficulty = ""
                                while difficulty not in ["green","blue","red","black"]:
                                    difficulty = input("Enter the difficulty of the run ('green', 'blue', 'red', 'black'): ")
                                modify_run = "UPDATE runs SET difficulty=? WHERE node_id=? AND end_node_id=?;"
                                cursor.execute(modify_run, [difficulty, node_id, end_node_id])
                            elif modify3_option == "7":
                                lift_type = ""
                                while lift_type not in ["gondola","chairlift","draglift"]:
                                    lift_type = input("Enter the type of lift ('gondola', 'chairlift', 'draglift'): ")
                                modify_run = "UPDATE runs SET lift_type=? WHERE node_id=? AND end_node_id=?;"
                                cursor.execute(modify_run, [lift_type, node_id, end_node_id])

                conn.commit()
        except sqlite3.OperationalError as e:
            print("Failed to open database: ", e)

    ##############################################
    # GROUP A Skill: Cross-table parameterised SQL
    ##############################################
    def __delete_ski_resort(self): #This method allows a user to specify a ski resort to be deleted from the database. The input is first validated before the ski resort is deleted. Parameters: None. Return values: None.
        try:
            with sqlite3.connect(self.DATABASE_NAME) as conn:
                cursor = conn.cursor()

                select_resorts = "SELECT resort_name FROM nodes;"
                cursor.execute(select_resorts)
                ski_resorts_list_unpacked = cursor.fetchall()
                ski_resorts_list =[]
                for item in ski_resorts_list_unpacked:
                    ski_resorts_list.append(item[0])
                ski_resorts_list = set(ski_resorts_list)
                ski_resort_to_delete = ""
                while ski_resort_to_delete not in ski_resorts_list:
                    ski_resort_to_delete = input(f"Enter the name of the ski resort you want to delete: ({", ".join(ski_resorts_list)})\n") #need to check if the ski resort exists in the database before it can be deleted

                get_node_ids = "SELECT node_id FROM nodes WHERE resort_name=?;"
                cursor.execute(get_node_ids, [ski_resort_to_delete])
                node_ids = cursor.fetchall()

                delete_records = "DELETE FROM nodes WHERE resort_name=?;"
                cursor.execute(delete_records, [ski_resort_to_delete])

                for node_id in node_ids:
                    delete_runs = "DELETE FROM runs WHERE node_id=?;"
                    cursor.execute(delete_runs, [node_id[0]])

                conn.commit()
        except sqlite3.OperationalError as e:
            print("Failed to open database: ", e)

if __name__ == "__main__":
    ui = Terminal()
    ui.menu()