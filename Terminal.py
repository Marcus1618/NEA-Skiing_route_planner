from Ui import Ui
from route_planner import Plan_route
import re
import sqlite3
from ski_resorts import Ski_resorts, Ski_resort, Ski_node, Run
from display_graph import Display_graph

class Terminal(Ui):
    def __init__(self):
        self.saved_ski_resorts = Ski_resorts() #change this so that it load from database
        self._construct_example_ski_resort()
        DATABASE_NAME = "ski_resorts.db"
        try:
            with sqlite3.connect(self.DATABASE_NAME) as conn:
                cursor = conn.cursor()
                create_table = """CREATE TABLE IF NOT EXISTS ski_resorts (
                                    ski_resort_name VARCHAR PRIMARY KEY
                                );"""
                cursor.execute(create_table)
                conn.commit()
        except sqlite3.OperationalError as e:
            print("Failed to open database: ", e)

    def menu(self): #Allows one of seven options that the program allows to be selected
        option = "-1"
        print("""
        Menu:
        1. Generate your route
        2. Add a ski resort
        3. Modify an existing ski resort
        4. Display a ski resort
        5. Delete a ski resort
        6. View previous routes
        7. Exit\n""")
        while option not in ["1","2","3","4","5","6","7"]:
            option = input("Enter the number of the option you want to select: ")

        if option == "1":
            self.generate_route()
        elif option == "2":
            self.create_ski_resort()
        elif option == "3":
            self.modify_ski_resort()
        elif option == "4":
            ski_resort_name = ""
            while ski_resort_name not in self.saved_ski_resorts.resorts.keys():
                ski_resort_name = input("Enter the name of the ski resort that you want to display: ")
            Display_graph().display_ski_resort(self.saved_ski_resorts.resorts[ski_resort_name])
        elif option == "5":
            self.delete_ski_resort()
        elif option == "6":
            self.view_previous_routes()
        elif option == "7":
            quit()

    def _add_times(self, t1, t2): #Adds two times together where t1 is in the format hh:mm and t2 is just an integer number of minutes
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
    
    def _construct_example_ski_resort(self): #Creates an example ski resort with ski lift stations and runs
        self.saved_ski_resorts.add_resort("Val Thorens")
        self.saved_ski_resorts.resorts["Val Thorens"].add_ski_node("Plein Sud bottom")
        self.saved_ski_resorts.resorts["Val Thorens"].nodes["Plein Sud bottom"].add_run("Plein Sud top",10, "08:00", "17:00")
        self.saved_ski_resorts.resorts["Val Thorens"].add_ski_node("Plein Sud top")
        self.saved_ski_resorts.resorts["Val Thorens"].nodes["Plein Sud top"].add_run("Pionniers bottom",5, "00:00", "23:59")
        self.saved_ski_resorts.resorts["Val Thorens"].nodes["Plein Sud top"].add_run("Pionniers top",1, "00:00", "23:59")
        self.saved_ski_resorts.resorts["Val Thorens"].add_ski_node("3 Vallees bottom")
        self.saved_ski_resorts.resorts["Val Thorens"].nodes["3 Vallees bottom"].add_run("Plein Sud bottom",15, "00:00", "23:59")
        self.saved_ski_resorts.resorts["Val Thorens"].nodes["3 Vallees bottom"].add_run("3 Vallees top",6, "08:30", "16:00")
        self.saved_ski_resorts.resorts["Val Thorens"].add_ski_node("3 Vallees top")
        self.saved_ski_resorts.resorts["Val Thorens"].nodes["3 Vallees top"].add_run("3 Vallees bottom",5, "00:00", "23:59")
        self.saved_ski_resorts.resorts["Val Thorens"].nodes["3 Vallees top"].add_run("Plein Sud top",4, "00:00", "23:59")
        self.saved_ski_resorts.resorts["Val Thorens"].add_ski_node("Pionniers bottom")
        self.saved_ski_resorts.resorts["Val Thorens"].nodes["Pionniers bottom"].add_run("Plein Sud bottom",10, "00:00", "23:59")
        self.saved_ski_resorts.resorts["Val Thorens"].nodes["Pionniers bottom"].add_run("Pionniers top",4, "08:00", "16:30")
        self.saved_ski_resorts.resorts["Val Thorens"].add_ski_node("Pionniers top")
        self.saved_ski_resorts.resorts["Val Thorens"].nodes["Pionniers top"].add_run("3 Vallees bottom",1, "00:00", "23:59")

    def generate_route(self): #Creates a route through a ski resort dependent on various user parameters
        length = "0.00"
        valid = None
        while valid == None:
            length = input("How long do you want to ski for (hh:mm): ")

            if int(length[length.index(":")+1:]) < 60 and re.match(r'^\d{2}:\d{2}$', length):
                valid = True

        ski_resort = ""
        while ski_resort not in self.saved_ski_resorts.resorts.keys():
            ski_resort = input(f"Which ski resort are you in: ({', '.join(self.saved_ski_resorts.resorts.keys())})\n")

        start = ""
        while start not in self.saved_ski_resorts.resorts[ski_resort].nodes.keys():
            start = input(f"From which ski lift station do you want to start your route: ({', '.join(self.saved_ski_resorts.resorts[ski_resort].nodes.keys())})\n")

        start_time = "00:00"
        start_time = input("At what time do you want to start your route (hh:mm): ") #ADD VALIDATION - between opening and closing times + right format

        #Advanced options
        as_close_to_time = False #get a user input for this

        route_planning = Plan_route(self.saved_ski_resorts.resorts[ski_resort], start, length, start_time)
        route, returned_to_start = route_planning.get_route(as_close_to_time) #Returns a list of dictionaries containing the node moved to and the time elapsed

        for i in range(len(route)-1):
            if route[i+1]["pause"] == True:
                print(f"{i+1}. Break for {route[i+1]["time_elapsed"]} minutes due to ski lifts not yet being open - {self._add_times(start_time,route[i+1]["time_elapsed"])}")
            else:
                print(f"{i+1}. {route[i]['start']} to {route[i+1]['start']} taking {route[i+1]['time_elapsed']-route[i]['time_elapsed']} minutes - {self._add_times(start_time,route[i+1]['time_elapsed'])}")

        if not returned_to_start:
            print(f"Your route could not return to the starting point in the time that you wanted to ski for due to ski lift closing times.")

        save = input("Do you want to save this route? (y/n): ") #ADD THIS TO OBJECTIVES + ADD FUNCTIONAILTY
        option = input("Enter 'm' to return to the main menu or 'q' to quit: ") #validate
        if option == "m":
            self.menu()
        elif option == "q":
            quit()

    def create_ski_resort(self): #Allows the user to create a ski resort through terminal inputs and displays it once created
        ski_resort_name = ""
        while ski_resort_name in self.saved_ski_resorts.resorts or not(re.match('(^[a-z]|[A-Z]).*$',ski_resort_name)):
            ski_resort_name = input("Enter the name of the ski resort which you want to create: ")
        self.saved_ski_resorts.add_resort(ski_resort_name)

        creating = True
        while creating: #Allow any number of ski lift stations to be created
            create_node = input("Do you want to create a new ski lift station? (y/n): ") #Validation
            if create_node == "y":
                node_name = ""
                while node_name in self.saved_ski_resorts.resorts[ski_resort_name].nodes or not(re.match('(^[a-z]|[A-Z]).*$',node_name)):
                    if len(self.saved_ski_resorts.resorts[ski_resort_name].nodes) == 0:
                        node_name = input(f"Enter the name of the ski lift station: (No previously created stations)\n")
                    else:
                        node_name = input(f"Enter the name of the ski lift station: (Previously created ski lift stations: {', '.join(self.saved_ski_resorts.resorts[ski_resort_name].nodes.keys())})\n")
                self.saved_ski_resorts.resorts[ski_resort_name].add_ski_node(node_name)
                creating_run = "y"
                while creating_run == "y": #Allow at least one run to be created from each ski lift station
                    run_name = ""
                    while run_name in self.saved_ski_resorts.resorts[ski_resort_name].nodes[node_name].runs or run_name == node_name or not(re.match('(^[a-z]|[A-Z]).*$',run_name)):
                        run_names_excluding_node = list(self.saved_ski_resorts.resorts[ski_resort_name].nodes.keys())
                        run_names_excluding_node.remove(node_name)
                        if len(run_names_excluding_node) == 0:
                            run_name = input(f"Enter an end ski lift station of this run: (No previously created ski lift stations)\n")   
                        else:
                            run_name = input(f"Enter an end ski lift station of this run: (Previously created ski lift stations: {', '.join(run_names_excluding_node)})\n")
                    length = input("Enter the length of the run (minutes): ") #Validation
                    opening = input("Enter the opening time of the run (hh:mm): ") #Validation
                    closing = input("Enter the closing time of the run (hh:mm): ") #Validation - has to be after opening time
                    self.saved_ski_resorts.resorts[ski_resort_name].nodes[node_name].add_run(run_name,length,opening,closing)
                    creating_run = input("Do you want to create another run from this ski lift station? (y/n): ") #Validation #Post loop repetition test to ensure that at least one run is added tjo each ski lift station
            elif create_node == "n":
                creating = False
        
        #Check if any ski lift stations have been used as the end of a run but have not been created
        incomplete_nodes = True
        break_loop = False
        while incomplete_nodes:
            for node in self.saved_ski_resorts.resorts[ski_resort_name].nodes: #node is a string of the name of the ski lift station
                for run in self.saved_ski_resorts.resorts[ski_resort_name].nodes[node].runs: #run is the run object
                    if run.name not in self.saved_ski_resorts.resorts[ski_resort_name].nodes:
                        self.saved_ski_resorts.resorts[ski_resort_name].add_ski_node(run.name)
                        print(f"Node {run.name} has been created as it was used as the end of a run but had not been created.")
                        creating_run = "y"
                        while creating_run == "y":
                            run_name = ""
                            while run_name in self.saved_ski_resorts.resorts[ski_resort_name].nodes[node].runs or run_name == node_name or not(re.match('(^[a-z]|[A-Z]).*$',run_name)):
                                run_names_excluding_node = list(self.saved_ski_resorts.resorts[ski_resort_name].nodes.keys())
                                run_names_excluding_node.remove(node)
                                if len(run_names_excluding_node) == 0:
                                    run_name = input(f"Enter an end ski lift station of this run: (No previously created ski lift stations)\n")   
                                else:
                                    run_name = input(f"Enter an end ski lift station of this run: (Previously created ski lift stations: {', '.join(run_names_excluding_node)})\n")
                            length = input("Enter the length of the run (minutes): ") #Validation
                            opening = input("Enter the opening time of the run (hh:mm): ") #Validation
                            closing = input("Enter the closing time of the run (hh:mm): ") #Validation
                            self.saved_ski_resorts.resorts[ski_resort_name].nodes[node].add_run(run_name,length,opening,closing)
                            creating_run = input("Do you want to create another run from this ski lift station? (y/n): ") #Validation #Post loop repetition test to ensure that at least one run is added tjo each ski lift station
                        break_loop = True #The loop will break if a new ski lift station is created since the dictionary being iterated over has changed
                    if break_loop:
                        break
                if break_loop:
                    break
            
            incomplete_nodes = False
            for node in self.saved_ski_resorts.resorts[ski_resort_name].nodes: #Checks if there are any more ski lift stations that have not been created left
                for run in self.saved_ski_resorts.resorts[ski_resort_name].nodes[node].runs:
                    if run.name not in self.saved_ski_resorts.resorts[ski_resort_name].nodes:
                        incomplete_nodes = True

        #display ski resort

        option = input("Enter 'm' to return to the main menu or 'q' to quit: ") #validate
        if option == "m":
            self.menu()
        elif option == "q":
            quit()

    def modify_ski_resort(self):
        try:
            with sqlite3.connect(self.DATABASE_NAME) as conn:
                cursor = conn.cursor()
                #add options with code

                conn.commit()
        except sqlite3.OperationalError as e:
            print("Failed to open database: ", e)

    def delete_ski_resort(self):
        try:
            with sqlite3.connect(self.DATABASE_NAME) as conn:
                cursor = conn.cursor()

                ski_resorts_list = ()
                while ski_resort_to_delete not in ski_resorts_list:
                    ski_resort_to_delete = input("Enter the name of the ski resort you want to delete: ") #need to check if the ski resort exists in the database before it can be deleted
                    select_resorts = "SELECT ski_resort_name FROM ski_resorts;"
                    cursor.execute(select_resorts)
                    ski_resorts_list = cursor.fetchall()

                delete_table = "DROP TABLE ?;"
                cursor.execute(delete_table, ski_resort_to_delete)

                conn.commit()
        except sqlite3.OperationalError as e:
            print("Failed to open database: ", e)

    def view_previous_routes(self):
        pass

#TESTING
if __name__ == "__main__":
    ui = Terminal()
    #ui.generate_route()
    ui.menu()