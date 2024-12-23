from Ui import Ui
import PySimpleGUI as sg
from route_planner import Plan_route
import re
import sqlite3
from math import inf
from ski_resorts import Ski_resorts, Ski_resort, Ski_node, Run
from display_graph import Display_graph
from database_changes import sync_from_database, add_resort_to_database
from file_changes import view_previous_route, save_route, get_route_names

class Gui(Ui):
    DATABASE_NAME = "ski_resorts.db"
    def __init__(self):
        self.__saved_ski_resorts = Ski_resorts()
        self.__construct_example_ski_resort()
        self.__window = None
        self.__window_display = None
        self.__window_view = None
        self.__window_view_output = None
        self.__window_delete = None
        self.__window_generate = None
        self.__window_advanced_options = None
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

    def menu(self): #Allows one of seven options that the program allows to be selected - the algorithm for all the functions are the same as in the terminal except the input is taken from the GUI
        while True:
            menu_layout = [
            [sg.Text("Menu")],
            [sg.Button("Generate your route", key = "-Generate-")],
            [sg.Button("Create a ski resort", key = "-Create-")],
            [sg.Button("Modify an existing ski resort", key = "-Modify-")],
            [sg.Button("Display an existing ski resort", key = "-Display-")],
            [sg.Button("Delete an existing ski resort", key = "-Delete-")],
            [sg.Button("View previous routes", key = "-View-")],
            [sg.Button("Exit", key = "-Exit-")]
            ]
            self.__window = sg.Window("Skiing Route Planner", menu_layout)
            event, values = self.__window.read()
            if event == "-Exit-" or event == sg.WIN_CLOSED:
                break
            elif event == "-Generate-":
                self.__window.close()
                self.__generate_route()            
            elif event == "-Create-":
                self.__window.close()
                self.__create_ski_resort()
            elif event == "-Modify-":
                self.__window.close()
                self.__modify_ski_resort()
            elif event == "-Display-":
                self.__saved_ski_resorts = Ski_resorts() #overwrite the locally stored ski resorts
                self.__saved_ski_resorts = sync_from_database(self.__saved_ski_resorts) #Sync the ski resorts stored in the database with the ski resorts stored in the program
                self.__construct_example_ski_resort()
                self.__window.close()
                display_layout = [
                    [sg.Text("Enter the name of the ski resort that you want to display:")],
                    [sg.InputText(key="-ski_resort_name-")],
                    [sg.Text(f"Existing ski resorts:\n{'\n'.join(self.__saved_ski_resorts.resorts.keys())}")],
                    [sg.Button("Submit", key="-Submit-")],
                    [sg.Button("Cancel", key="-Cancel-")],
                    [sg.Button("Return to main menu", key="-Return-")]
                ]
                self.__window_display = sg.Window("Display ski resort", display_layout)
                while True:
                    event, values = self.__window_display.read()
                    if event == "-Return-" or event == sg.WIN_CLOSED:
                        break
                    elif event == "-Submit-":
                        ski_resort_name = values["-ski_resort_name-"]
                        if ski_resort_name in self.__saved_ski_resorts.resorts.keys():
                            Display_graph().display_ski_resort(self.__saved_ski_resorts.resorts[ski_resort_name])
                            break
                        else:
                            sg.popup("The ski resort does not exist.")
                    elif event == "-Cancel-":
                        self.__window_display["-ski_resort_name-"].update("")
                self.__window_display.close()
            elif event == "-Delete-":
                self.__window.close()
                self.__delete_ski_resort()
            elif event == "-View-":
                self.__window.close()
                previous_route_names = get_route_names()
                view_layout_input = [
                    [sg.Text("Enter the name of the route that you want to display:")],
                    [sg.InputText(key="-route_name-")],
                    [sg.Text(f"Existing routes:\n{'\n'.join(previous_route_names)}")],
                    [sg.Button("Submit", key="-Submit-")],
                    [sg.Button("Cancel", key="-Cancel-")],
                    [sg.Button("Return to main menu", key="-Return-")]
                ]
                self.__window_view = sg.Window("View previous routes", view_layout_input)
                if len(previous_route_names) != 0:
                    loop = True
                    while loop:
                        event, values = self.__window_view.read()
                        if event == "-Return-" or event == sg.WIN_CLOSED:
                            loop = False
                        elif event == "-Submit-":
                            route_name = values["-route_name-"]
                            if route_name in previous_route_names:
                                route_to_display, resort_name = view_previous_route(route_name)
                                self.__window_view.close()
                                view_layout_output = [
                                    [sg.Text(f"Route '{route_name}' in {resort_name}:")],
                                    [sg.Text(f"{"\n".join(route_to_display)}")],
                                    [sg.Button("Return to main menu", key="-Return-")]
                                ]
                                self.__window_view_output = sg.Window("View previous routes", view_layout_output)
                                output_loop = True
                                while output_loop:
                                    event, values = self.__window_view_output.read()
                                    if event == "-Return-" or event == sg.WIN_CLOSED:
                                        self.__window_view_output.close()
                                        output_loop = False
                                        loop = False
                            else:
                                sg.popup("The route does not exist.")
                        elif event == "-Cancel-":
                            self.__window_view["route_name"].update("")
                else:
                    sg.popup("There are no routes saved.")
                self.__window_view.close()
        self.__window.close()

    def __add_times(self, t1, t2): #Adds two times together where t1 is in the format hh:mm and t2 is just an integer number of minutes
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
    
    def __compare_greater(self,t1,t2): #Compares if time t1 is greater than time t2
        h1, m1 = t1.split(":")
        h2, m2 = t2.split(":")
        if int(h1) > int(h2):
            return True
        elif int(h1) == int(h2) and int(m1) > int(m2):
            return True
        else:
            return False
    
    def __time_difference(self, t1, t2): #Returns the difference between two times where t1 and t2 are in the format hh:mm
        h1, m1 = t1.split(":")
        h2, m2 = t2.split(":")
        return (int(h2)*60 + int(m2)) - (int(h1)*60 + int(m1))
    
    def __construct_example_ski_resort(self): #Creates an example ski resort with ski lift stations and runs - only stored locally in the program
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

    def __advanced_options(self): #Allows the user to input advanced options for the route generation
        quit_generate = False
        weather = ""
        as_close_to_time = ""
        snow_conditions = ""
        lift_type_preference = ""
        altitude = ""
        latitude = ""
        longitude = ""
        as_close_to_time_input = ""

        generate_layout = [
            [sg.Text("Do you want to return to the starting point as close to the time you specified as possible rather than always before it? (y/n):", key = "-text-")],
            [sg.InputText(key="-text_input-")],
            [sg.Button("Submit", key="-submit-")],
            [sg.Button("Cancel", key="-cancel-")],
            [sg.Button("Return to menu", key="-return-")]
        ]
        self.__window_advanced_options = sg.Window("Advanced route requirements", generate_layout)

        quit_options = False
        while not quit_options and not quit_generate:
            event, values = self.__window_advanced_options.read()
            if event == "-return-" or event == sg.WIN_CLOSED:
                quit_options = True
                quit_generate = True
            elif event == "-cancel-":
                self.__window_advanced_options["-text_input-"].update("")
            elif event == "-submit-":
                if values["-text_input-"] in ["y","n"]:
                    quit_options = True
                    as_close_to_time = values["-text_input-"]
                    if as_close_to_time_input == "y":
                        as_close_to_time = True
                    else:
                        as_close_to_time = False
                else:
                    sg.popup("Error. The input must be 'y' or 'n'.")
                    self.__window_advanced_options["-text_input-"].update("")
        
        quit_options = True
        self.__window_advanced_options["-text_input-"].update("")
        self.__window_advanced_options["-text-"].update(f"Do you want to consider the snow conditions and weather at your resort? (y/n):")
        while quit_options and not quit_generate:
            event, values = self.__window_advanced_options.read()
            if event == "-return-" or event == sg.WIN_CLOSED:
                quit_options = False
                quit_generate = True
            elif event == "-cancel-":
                self.__window_advanced_options["-text_input-"].update("")
            elif event == "-submit-":
                if values["-text_input-"] in ["y","n"]:
                    quit_options = False
                    altitude = values["-text_input-"]
                else:
                    sg.popup("Error. The input must be 'y' or 'n'.")
                    self.__window_advanced_options["-text_input-"].update("")

        if altitude == "y":
            quit_options = True
            self.__window_advanced_options["-text_input-"].update("")
            self.__window_advanced_options["-text-"].update(f"What are the snow conditions like ('good', 'average', 'poor' or 'unknown):")
            while quit_options and not quit_generate:
                event, values = self.__window_advanced_options.read()
                if event == "-return-" or event == sg.WIN_CLOSED:
                    quit_options = False
                    quit_generate = True
                elif event == "-cancel-":
                    self.__window_advanced_options["-text_input-"].update("")
                elif event == "-submit-":
                    if values["-text_input-"] in ["good","average","poor","unknown"]:
                        quit_options = False
                        snow_conditions = values["-text_input-"]
                    else:
                        sg.popup("Error. The input must be 'good', 'average', 'poor' or 'unknown'.")
                        self.__window_advanced_options["-text_input-"].update("")
            quit_options = True
            self.__window_advanced_options["-text_input-"].update("")
            self.__window_advanced_options["-text-"].update(f"On what day are you skiing? ('today', 'tomorrow', '2 days time', '3 days time' or 'unknown'):")
            while quit_options and not quit_generate:
                event, values = self.__window_advanced_options.read()
                if event == "-return-" or event == sg.WIN_CLOSED:
                    quit_options = False
                    quit_generate = True
                elif event == "-cancel-":
                    self.__window_advanced_options["-text_input-"].update("")
                elif event == "-submit-":
                    if values["-text_input-"] in ["today","tomorrow","2 days time","3 days time","unknown"]:
                        quit_options = False
                        weather = values["-text_input-"]
                    else:
                        sg.popup("Error. The input must be 'today', 'tomorrow', '2 days time', '3 days time' or 'unknown'.")
                        self.__window_advanced_options["-text_input-"].update("")
            quit_options = True
            self.__window_advanced_options["-text_input-"].update("")
            self.__window_advanced_options["-text-"].update(f"Enter the latitude of the resort (enter N/A if unknown):")
            while quit_options and not quit_generate:
                event, values = self.__window_advanced_options.read()
                if event == "-return-" or event == sg.WIN_CLOSED:
                    quit_options = False
                    quit_generate = True
                elif event == "-cancel-":
                    self.__window_advanced_options["-text_input-"].update("")
                elif event == "-submit-":
                    if re.match(r'^-?\d{1,2}\.\d{4}$', values["-text_input-"]) or values["-text_input-"] == "N/A":
                        quit_options = False
                        latitude = values["-text_input-"]
                    else:
                        sg.popup("Error. The latitude must be in the format xx.xxxx.")
                        self.__window_advanced_options["-text_input-"].update("")
            quit_options = True
            self.__window_advanced_options["-text_input-"].update("")
            self.__window_advanced_options["-text-"].update(f"Enter the longitude of the resort (enter N/A if unknown):")
            while quit_options and not quit_generate:
                event, values = self.__window_advanced_options.read()
                if event == "-return-" or event == sg.WIN_CLOSED:
                    quit_options = False
                    quit_generate = True
                elif event == "-cancel-":
                    self.__window_advanced_options["-text_input-"].update("")
                elif event == "-submit-":
                    if re.match(r'^-?\d{1,3}\.\d{4}$', values["-text_input-"]) or values["-text_input-"] == "N/A":
                        quit_options = False
                        longitude = values["-text_input-"]
                    else:
                        sg.popup("Error. The longitude must be in the format xx.xxxx.")
                        self.__window_advanced_options["-text_input-"].update("")
        else:
            snow_conditions = "unknown"
            weather = "unknown"
            latitude = "N/A"
            longitude = "N/A"

        quit_options = True
        self.__window_advanced_options["-text_input-"].update("")
        self.__window_advanced_options["-text-"].update(f"Do you want to use more of one type of ski lift than the others ('gondola', 'chairlift', 'draglift' or 'no preference'):")
        while quit_options and not quit_generate:
            event, values = self.__window_advanced_options.read()
            if event == "-return-" or event == sg.WIN_CLOSED:
                quit_options = False
                quit_generate = True
            elif event == "-cancel-":
                self.__window_advanced_options["-text_input-"].update("")
            elif event == "-submit-":
                if values["-text_input-"] in ["gondola","chairlift","draglift","no preference"]:
                    quit_options = False
                    lift_type_preference = values["-text_input-"]
                else:
                    sg.popup("Error. The input must be 'gondola', 'chairlift', 'draglift' or 'no preference'.")
                    self.__window_advanced_options["-text_input-"].update("")

        self.__window_advanced_options.close()
        return as_close_to_time, snow_conditions, lift_type_preference, weather, latitude, longitude, quit_generate

    def __generate_route(self): #Creates a route through a ski resort dependent on various user parameters
        self.__saved_ski_resorts = Ski_resorts() #overwrite the locally stored ski resorts
        self.__saved_ski_resorts = sync_from_database(self.__saved_ski_resorts) #Sync the ski resorts stored in the database with the ski resorts stored in the program
        self.__construct_example_ski_resort()
        generate_layout = [
            [sg.Text("How long do you want to ski for (hh:mm):", key = "-text-")],
            [sg.InputText(key="-text_input-")],
            [sg.Button("Submit", key="-submit-")],
            [sg.Button("Cancel", key="-cancel-")],
            [sg.Button("Return to menu", key="-return-")]
        ]
        self.__window_generate = sg.Window("Route requirements", generate_layout)
        #The window will be re-used for all of the user inputs within this function with the text prompt being updated each time to request the different input

        quit_generate = False
        generate_loop = True
        while generate_loop:
            event, values = self.__window_generate.read()
            if event == "-return-" or event == sg.WIN_CLOSED:
                generate_loop = False
                quit_generate = True
            elif event == "-cancel-":
                self.__window_generate["-text_input-"].update("")
            elif event == "-submit-":
                try:
                    if int(values["-text_input-"][values["-text_input-"].index(":")+1:]) < 60 and re.match(r'^\d{2}:\d{2}$', values["-text_input-"]):
                        generate_loop = False
                        length = values["-text_input-"]
                        h,m = length.split(":")
                        length = int(h)*60 + int(m)
                    else:
                        sg.popup("Error. The time entered must be in the format hh:mm.")
                        self.__window_generate["-text_input-"].update("")
                except:
                    sg.popup("Error. The time entered must be in the format hh:mm.")
                    self.__window_generate["-text_input-"].update("")

        if not quit_generate:
            generate_loop = True
            self.__window_generate["-text_input-"].update("")
            self.__window_generate["-text-"].update(f"Which ski resort are you in:\n({'\n'.join(self.__saved_ski_resorts.resorts.keys())})")
        while generate_loop and not quit_generate:
            event, values = self.__window_generate.read()
            if event == "-return-" or event == sg.WIN_CLOSED:
                generate_loop = False
                quit_generate = True
            elif event == "-cancel-":
                self.__window_generate["-text_input-"].update("")
            elif event == "-submit-":
                if values["-text_input-"] in self.__saved_ski_resorts.resorts.keys():
                    generate_loop = False
                    ski_resort = values["-text_input-"]
                else:
                    sg.popup("Error. The ski resort entered does not exist.")
                    self.__window_generate["-text_input-"].update("")

        if not quit_generate:
            generate_loop = True
            self.__window_generate["-text_input-"].update("")
            self.__window_generate["-text-"].update(f"From which ski lift station do you want to start your route:\n({'\n'.join(self.__saved_ski_resorts.resorts[ski_resort].nodes.keys())})")
        while generate_loop and not quit_generate:
            event, values = self.__window_generate.read()
            if event == "-return-" or event == sg.WIN_CLOSED:
                generate_loop = False
                quit_generate = True
            elif event == "-cancel-":
                self.__window_generate["-text_input-"].update("")
            elif event == "-submit-":
                if values["-text_input-"] in self.__saved_ski_resorts.resorts[ski_resort].nodes.keys():
                    generate_loop = False
                    start = values["-text_input-"]
                    original_start = start
                else:
                    sg.popup("Error. The ski lift station entered does not exist.")
                    self.__window_generate["-text_input-"].update("")
        
        if not quit_generate:
            generate_loop = True
            self.__window_generate["-text_input-"].update("")
            self.__window_generate["-text-"].update(f"At what time do you want to start your route (hh:mm):")
        while generate_loop and not quit_generate:
            event, values = self.__window_generate.read()
            if event == "-return-" or event == sg.WIN_CLOSED:
                generate_loop = False
                quit_generate = True
            elif event == "-cancel-":
                self.__window_generate["-text_input-"].update("")
            elif event == "-submit-":
                if int(values["-text_input-"][values["-text_input-"].index(":")+1:]) < 60 and re.match(r'^\d{2}:\d{2}$', values["-text_input-"]):
                    generate_loop = False
                    start_time = values["-text_input-"]
                    route_start_time = start_time
                    route_stop_time = self.__add_times(start_time, length)
                else:
                    sg.popup("Error. The time entered must be in the format hh:mm.")
                    self.__window_generate["-text_input-"].update("")

        if not quit_generate:
            generate_loop = True
            self.__window_generate["-text_input-"].update("")
            self.__window_generate["-text-"].update(f"What is the maximum difficulty of run that you want to ski on ('green', 'blue', 'red', 'black' or 'unknown'):")
        while generate_loop and not quit_generate:
            event, values = self.__window_generate.read()
            if event == "-return-" or event == sg.WIN_CLOSED:
                generate_loop = False
                quit_generate = True
            elif event == "-cancel-":
                self.__window_generate["-text_input-"].update("")
            elif event == "-submit-":
                if values["-text_input-"] in ["green","blue","red","black","unknown"]:
                    generate_loop = False
                    max_difficulty = values["-text_input-"]
                else:
                    sg.popup("Error. The difficulty entered must be 'green', 'blue', 'red', 'black' or 'unknown'.")
                    self.__window_generate["-text_input-"].update("")

        generate_loop = True
        breaks_data = []
        if not quit_generate:
            self.__window_generate["-text_input-"].update("")
            self.__window_generate["-text-"].update(f"Do you want to take breaks during your skiing time e.g. for lunch or at ski parks? (y/n):")
        while generate_loop and not quit_generate:
            event, values = self.__window_generate.read()
            if event == "-return-" or event == sg.WIN_CLOSED:
                generate_loop = False
                quit_generate = True
            elif event == "-cancel-":
                self.__window_generate["-text_input-"].update("")
            elif event == "-submit-":
                if values["-text_input-"] in ["y","n"]:
                    generate_loop = False
                    breaks = values["-text_input-"]
                    previous_time = "00:00"
                    while breaks == "y":
                        generate_loop = True
                        break_type = ""
                        self.__window_generate["-text_input-"].update("")
                        self.__window_generate["-text-"].update(f"What type of break do you want to take ('restaurant/amenity' or 'ski park'):")
                        while generate_loop and not quit_generate:
                            event, values = self.__window_generate.read()
                            if event == "-return-" or event == sg.WIN_CLOSED:
                                generate_loop = False
                                quit_generate = True
                            elif event == "-cancel-":
                                self.__window_generate["-text_input-"].update("")
                            elif event == "-submit-":
                                if values["-text_input-"] in ["restaurant/amenity","ski park"]:
                                    generate_loop = False
                                    break_type = values["-text_input-"]
                                else:
                                    sg.popup("Error. The break type must be 'restaurant/amenity' or 'ski park'.")
                                    self.__window_generate["-text_input-"].update("")
                        if break_type == "restaurant/amenity" and not quit_generate:
                            generate_loop = True
                            self.__window_generate["-text_input-"].update("")
                            self.__window_generate["-text-"].update(f"Enter the name of the restaurant/amenity that you want to stop at:\n({"\n".join(self.__saved_ski_resorts.resorts[ski_resort].amenity_names)}):")
                            while generate_loop and not quit_generate:
                                event, values = self.__window_generate.read()
                                if event == "-return-" or event == sg.WIN_CLOSED:
                                    generate_loop = False
                                    quit_generate = True
                                elif event == "-cancel-":
                                    self.__window_generate["-text_input-"].update("")
                                elif event == "-submit-":
                                    if values["-text_input-"] in self.__saved_ski_resorts.resorts[ski_resort].amenity_names:
                                        generate_loop = False
                                        amenity_name = values["-text_input-"]
                                    else:
                                        sg.popup("Error. The amenity name must be one of the following:", ", ".join(self.__saved_ski_resorts.resorts[ski_resort].amenity_names))
                                        self.__window_generate["-text_input-"].update("")
                        elif break_type == "ski park" and not quit_generate:
                            generate_loop = True
                            self.__window_generate["-text_input-"].update("")
                            self.__window_generate["-text-"].update(f"Enter the name of the ski park that you want to stop at:\n({"\n".join(self.__saved_ski_resorts.resorts[ski_resort].ski_park_names)}):")
                            while generate_loop and not quit_generate:
                                event, values = self.__window_generate.read()
                                if event == "-return-" or event == sg.WIN_CLOSED:
                                    generate_loop = False
                                    quit_generate = True
                                elif event == "-cancel-":
                                    self.__window_generate["-text_input-"].update("")
                                elif event == "-submit-":
                                    if values["-text_input-"] in self.__saved_ski_resorts.resorts[ski_resort].ski_park_names:
                                        generate_loop = False
                                        amenity_name = values["-text_input-"]
                                    else:
                                        sg.popup("Error. The ski park name must be one of the following:", ", ".join(self.__saved_ski_resorts.resorts[ski_resort].ski_park_names))
                                        self.__window_generate["-text_input-"].update("")
                        
                        if not quit_generate:
                            generate_loop = True
                            self.__window_generate["-text_input-"].update("")
                            self.__window_generate["-text-"].update(f"At what time do you want to visit this amenity (hh:mm):")
                        while generate_loop and not quit_generate:
                            event, values = self.__window_generate.read()
                            if event == "-return-" or event == sg.WIN_CLOSED:
                                generate_loop = False
                                quit_generate = True
                            elif event == "-cancel-":
                                self.__window_generate["-text_input-"].update("")
                            elif event == "-submit-":
                                if int(values["-text_input-"][values["-text_input-"].index(":")+1:]) < 60 and re.match(r'^\d{2}:\d{2}$', values["-text_input-"]):
                                    break_time = values["-text_input-"]
                                    if self.__compare_greater(break_time, start_time) and self.__compare_greater(route_stop_time, break_time):
                                        if self.__compare_greater(break_time, previous_time):
                                            previous_time = break_time
                                            generate_loop = False
                                        else:
                                            sg.popup("Error. The time that you want to visit this amenity at must be after the previous break.")
                                            self.__window_generate["-text_input-"].update("")
                                    else:
                                        sg.popup("Error. The time that you want to visit this amenity at must be after the start time of the route and before the end time.")
                                        self.__window_generate["-text_input-"].update("")
                                else:
                                    sg.popup("Error. The time entered must be in the format hh:mm.")
                                    self.__window_generate["-text_input-"].update("")
                        
                        if break_type == "restaurant/amenity":
                            park_repetitions = 0
                            generate_loop = True
                            self.__window_generate["-text_input-"].update("")
                            self.__window_generate["-text-"].update(f"How long do you want to spend at this restaurant/amenity (minutes):")
                            while generate_loop and not quit_generate:
                                event, values = self.__window_generate.read()
                                if event == "-return-" or event == sg.WIN_CLOSED:
                                    generate_loop = False
                                    quit_generate = True
                                elif event == "-cancel-":
                                    self.__window_generate["-text_input-"].update("")
                                elif event == "-submit-":
                                    if int(values["-text_input-"]) > 0:
                                        try:
                                            break_length = int(values["-text_input-"])
                                            allowed_time = self.__time_difference(break_time, route_stop_time)
                                            if break_length <= allowed_time:
                                                generate_loop = False
                                            else:
                                                sg.popup("Error. The break cannot extend past the desired end time of this route.")
                                                self.__window_generate["-text_input-"].update("")
                                        except ValueError:
                                            sg.popup("Error. The break length must be an integer.")
                                            self.__window_generate["-text_input-"].update("")
                                    else:
                                        sg.popup("Error. The break length must be greater than 0.")
                                        self.__window_generate["-text_input-"].update("")
                        elif break_type == "ski park":
                            break_length = 0
                            generate_loop = True
                            self.__window_generate["-text_input-"].update("")
                            self.__window_generate["-text-"].update(f"How many times do you want to ski the ski park:")
                            while generate_loop and not quit_generate:
                                event, values = self.__window_generate.read()
                                if event == "-return-" or event == sg.WIN_CLOSED:
                                    generate_loop = False
                                    quit_generate = True
                                elif event == "-cancel-":
                                    self.__window_generate["-text_input-"].update("")
                                elif event == "-submit-":
                                    if int(values["-text_input-"]) > 0:
                                        park_repetitions = int(values["-text_input-"])
                                        generate_loop = False
                                    else:
                                        sg.popup("Error. The number of times must be greater than 0.")
                                        self.__window_generate["-text_input-"].update("")
                        
                        breaks = "n"
                        if not quit_generate:
                            generate_loop = True
                            self.__window_generate["-text_input-"].update("")
                            self.__window_generate["-text-"].update(f"Do you want to take another break during your skiing time? (y/n):")
                        while generate_loop and not quit_generate:
                            event, values = self.__window_generate.read()
                            if event == "-return-" or event == sg.WIN_CLOSED:
                                generate_loop = False
                                quit_generate = True
                            elif event == "-cancel-":
                                self.__window_generate["-text_input-"].update("")
                            elif event == "-submit-":
                                if values["-text_input-"] in ["y","n"]:
                                    generate_loop = False
                                    breaks = values["-text_input-"]
                                else:
                                    sg.popup("Error. The input must be 'y' or 'n'.")
                                    self.__window_generate["-text_input-"].update("")
                        if not quit_generate:
                            breaks_data.append([break_type, amenity_name, break_time, break_length, park_repetitions])
                else:
                    sg.popup("Error. The input must be 'y' or 'n'.")
                    self.__window_generate["-text_input-"].update("")
        
        advanced_options = ""
        if not quit_generate:
            generate_loop = True
            self.__window_generate["-text_input-"].update("")
            self.__window_generate["-text-"].update(f"Do you want to enter further advanced options? (y/n):")
        while generate_loop and not quit_generate:
            event, values = self.__window_generate.read()
            if event == "-return-" or event == sg.WIN_CLOSED:
                generate_loop = False
                quit_generate = True
            elif event == "-cancel-":
                self.__window_generate["-text_input-"].update("")
            elif event == "-submit-":
                if values["-text_input-"] in ["y","n"]:
                    generate_loop = False
                    advanced_options = values["-text_input-"]
                else:
                    sg.popup("Error. The input must be 'y' or 'n'.")
                    self.__window_generate["-text_input-"].update("")
        
        self.__window_generate.close()

        if advanced_options == "y" and not quit_generate:
            as_close_to_time, snow_conditions, lift_type_preference, weather, latitude, longitude, quit_generate = self.__advanced_options()
        else:
            weather = "unknown"
            as_close_to_time = False
            snow_conditions = "unknown"
            lift_type_preference = "no preference"
            latitude = "N/A"
            longitude = "N/A"

        if not quit_generate:
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
            
            route_output = []
            for i in range(len(route)-1):
                if route[i+1]["pause"] == True:
                    if i != 0:
                        route_output.append(f"{i+1}. Break for {route[i+1]["time_elapsed"]-route[i]["time_elapsed"]} minutes due to ski lifts not yet being open - {self.__add_times(route_start_time,route[i+1]["time_elapsed"])}")
                    else:
                        route_output.append(f"{i+1}. Break for {route[i+1]["time_elapsed"]-route[i]["time_elapsed"]} minutes due to ski lifts not yet being open (route length increased by {route[i+1]["time_elapsed"]-route[i]["time_elapsed"]} minutes) - {self.__add_times(route_start_time,route[i+1]["time_elapsed"])}")
                elif route[i+1]["break"] == True:
                    route_output.append(f"{i+1}. Break for {route[i+1]["time_elapsed"]-route[i]["time_elapsed"]} minutes at {route[i+1]["start"]} ({self.__saved_ski_resorts.resorts[ski_resort].nodes[route[i+1]["start"]]}) - {self.__add_times(route_start_time,route[i+1]["time_elapsed"])}")
                else: #add lift/run from x to y
                    route_output.append(f"{i+1}. {route[i+1]["lift"].title()} from {route[i]['start']} to {route[i+1]['start']} taking {route[i+1]['time_elapsed']-route[i]['time_elapsed']} minutes - {self.__add_times(route_start_time,route[i+1]['time_elapsed'])}")

            if not returned_to_start:
                route_output.append(f"Your route could not return to the starting point in the time that you wanted to ski for due to ski lift closing times.")
            
            route_ouput_layout = [
                [sg.Text(f"Instructions:\n{'\n'.join(route_output)}")], #Displays the route generated
                [sg.Text("Enter the name of the route before saving:")],
                [sg.InputText(key="-route_name-")],
                [sg.Button("Save route", key="-Save-")],
                [sg.Button("Return to main menu", key="-Return-")]
            ]
            self.__window_route_output = sg.Window("Route", route_ouput_layout)
            generate_loop = True
            while generate_loop:
                event, values = self.__window_route_output.read()
                if event == "-Return-" or event == sg.WIN_CLOSED:
                    generate_loop = False
                    quit_generate = True
                elif event == "-Save-":
                    previous_route_names = get_route_names()
                    if values["-route_name-"] not in previous_route_names and re.match('(^[a-z]|[A-Z]).*$',values["-route_name-"]):
                        generate_loop = False
                        route_name = values["-route_name-"]
                        save_route(route_name, route, route_start_time, returned_to_start, ski_resort, self.__saved_ski_resorts)
                    else:
                        sg.popup("Error. The route name must start with a letter and not already exist.")
                        self.__window_route_output["-route_name-"].update("")
            self.__window_route_output.close()

    ################################################################################################
    # GROUP A Skill: Dynamic generation of objects based on complex user-defined use of an OOP model
    ################################################################################################
    def __create_ski_resort(self): #Allows the user to create a ski resort through terminal inputs and displays it once created - the algorithm is exactly the same as that when run in the terminal except inputs must be entered through the GUI
        self.__saved_ski_resorts = Ski_resorts() #overwrite the locally stored ski resorts
        self.__saved_ski_resorts = sync_from_database(self.__saved_ski_resorts) #Sync the ski resorts stored in the database with the ski resorts stored in the program
        self.__construct_example_ski_resort()

        create_layout = [
            [sg.Text(f"Enter the name of the ski resort which you want to create (It cannot be the same as one of the previously created resorts shown):\n({"\n".join(self.__saved_ski_resorts.resorts)})", key = "-text-")],
            [sg.InputText(key="-text_input-")],
            [sg.Button("Submit", key="-submit-")],
            [sg.Button("Cancel", key="-cancel-")],
            [sg.Button("Return to menu", key="-return-")]
        ]
        self.__window_create = sg.Window("Creating ski resort", create_layout)

        creating_loop = True
        quit_creating = False
        while creating_loop and not quit_creating:
            event, values = self.__window_create.read()
            if event == "-return-" or event == sg.WIN_CLOSED:
                creating_loop = False
                quit_creating = True
            elif event == "-cancel-":
                self.__window_create["-text_input-"].update("")
            elif event == "-submit-":
                if values["-text_input-"] not in self.__saved_ski_resorts.resorts and re.match('(^[a-z]|[A-Z]).*$',values["-text_input-"]):
                    creating_loop = False
                    ski_resort_name = values["-text_input-"]
                    self.__saved_ski_resorts.add_resort(ski_resort_name)
                else:
                    sg.popup("Error. The ski resort name must start with a letter and not already exist.")
                    self.__window_create["-text_input-"].update("")

        if not quit_creating:
            creating = True
            while creating:
                create_node = ""
                creating = False
                if not quit_creating:
                    creating_loop = True
                    self.__window_create["-text_input-"].update("")
                    self.__window_create["-text-"].update(f"Do you want to create a new ski lift station? (y/n):")
                while creating_loop and not quit_creating:
                    event, values = self.__window_create.read()
                    if event == "-return-" or event == sg.WIN_CLOSED:
                        creating_loop = False
                        quit_creating = True
                    elif event == "-cancel-":
                        self.__window_create["-text_input-"].update("")
                    elif event == "-submit-":
                        if values["-text_input-"] in ["y","n"]:
                            creating_loop = False
                            create_node = values["-text_input-"]
                        else:
                            sg.popup("Error. The input must be 'y' or 'n'.")
                            self.__window_create["-text_input-"].update("")
                
                if create_node == "y" and not quit_creating:
                    creating = True
                    creating_loop = True
                    self.__window_create["-text_input-"].update("")
                    if len(self.__saved_ski_resorts.resorts[ski_resort_name].nodes) == 0:
                        self.__window_create["-text-"].update(f"Enter the name of the new ski lift station: (No previously created stations)")
                    else:
                        self.__window_create["-text-"].update(f"Enter the name of the new ski lift station:\n({'\n'.join(self.__saved_ski_resorts.resorts[ski_resort_name].nodes.keys())})")
                    while creating_loop and not quit_creating:
                        event, values = self.__window_create.read()
                        if event == "-return-" or event == sg.WIN_CLOSED:
                            creating_loop = False
                            quit_creating = True
                        elif event == "-cancel-":
                            self.__window_create["-text_input-"].update("")
                        elif event == "-submit-":
                            if values["-text_input-"] not in self.__saved_ski_resorts.resorts[ski_resort_name].nodes and re.match('(^[a-z]|[A-Z]).*$',values["-text_input-"]):
                                creating_loop = False
                                node_name = values["-text_input-"]
                            else:
                                sg.popup("Error. The ski lift station name must start with a letter and not already exist.")
                                self.__window_create["-text_input-"].update("")
                    
                    node_type = ""
                    if not quit_creating:
                        creating_loop = True
                        self.__window_create["-text_input-"].update("")
                        self.__window_create["-text-"].update(f"Do you want to create a ski lift station, a ski park or an amenity ('s', 'p' or 'a'):")
                    while creating_loop and not quit_creating:
                        event, values = self.__window_create.read()
                        if event == "-return-" or event == sg.WIN_CLOSED:
                            creating_loop = False
                            quit_creating = True
                        elif event == "-cancel-":
                            self.__window_create["-text_input-"].update("")
                        elif event == "-submit-":
                            if values["-text_input-"] in ["s","p","a"]:
                                creating_loop = False
                                node_type = values["-text_input-"]
                            else:
                                sg.popup("Error. The input must be 's', 'p' or 'a'.")
                                self.__window_create["-text_input-"].update("")
                    
                    if not quit_creating:
                        creating_loop = True
                        self.__window_create["-text_input-"].update("")
                        self.__window_create["-text-"].update(f"Enter the altitude of the ski lift station:")
                    while creating_loop and not quit_creating:
                        event, values = self.__window_create.read()
                        if event == "-return-" or event == sg.WIN_CLOSED:
                            creating_loop = False
                            quit_creating = True
                        elif event == "-cancel-":
                            self.__window_create["-text_input-"].update("")
                        elif event == "-submit-":
                            if values["-text_input-"].isnumeric():
                                creating_loop = False
                                altitude = int(values["-text_input-"])
                            else:
                                sg.popup("Error. The altitude must be a number.")
                                self.__window_create["-text_input-"].update("")
                    
                    if node_type == "p":
                        creating_loop = True
                        self.__window_create["-text_input-"].update("")
                        self.__window_create["-text-"].update(f"Enter the length of the ski park (minutes):")
                        while creating_loop and not quit_creating:
                            event, values = self.__window_create.read()
                            if event == "-return-" or event == sg.WIN_CLOSED:
                                creating_loop = False
                                quit_creating = True
                            elif event == "-cancel-":
                                self.__window_create["-text_input-"].update("")
                            elif event == "-submit-":
                                if values["-text_input-"].isnumeric():
                                    if int(values["-text_input-"]) > 0:
                                        creating_loop = False
                                        ski_park_length = int(values["-text_input-"])
                                    else:
                                        sg.popup("Error. The ski park length must be greater than 0.")
                                        self.__window_create["-text_input-"].update("")
                                else:
                                    sg.popup("Error. The ski park length must be a number.")
                                    self.__window_create["-text_input-"].update("")
                        self.__saved_ski_resorts.resorts[ski_resort_name].add_ski_park(node_name,altitude,ski_park_length)

                    elif node_type == "a":
                        creating_loop = True
                        self.__window_create["-text_input-"].update("")
                        self.__window_create["-text-"].update(f"Enter a description of the type of amenity e.g. restaurant:")
                        while creating_loop and not quit_creating:
                            event, values = self.__window_create.read()
                            if event == "-return-" or event == sg.WIN_CLOSED:
                                creating_loop = False
                                quit_creating = True
                            elif event == "-cancel-":
                                self.__window_create["-text_input-"].update("")
                            elif event == "-submit-":
                                if re.match('(^[a-z]|[A-Z]).*$',values["-text_input-"]):
                                    creating_loop = False
                                    amenity_type = values["-text_input-"]
                                else:
                                    sg.popup("Error. The amenity type must start with a letter.")
                                    self.__window_create["-text_input-"].update("")
                        self.__saved_ski_resorts.resorts[ski_resort_name].add_amenity(node_name,altitude,amenity_type)
                    
                    elif node_type == "s":
                        self.__saved_ski_resorts.resorts[ski_resort_name].add_ski_node(node_name,altitude)
                    
                    creating_run = "y"
                    while creating_run == "y" and not quit_creating: #Allow at least one run to be created from each ski lift station
                        creating_loop = True
                        self.__window_create["-text_input-"].update("")
                        run_names_excluding_node = list(self.__saved_ski_resorts.resorts[ski_resort_name].nodes.keys())
                        run_names_excluding_node.remove(node_name)
                        if len(run_names_excluding_node) == 0:
                            self.__window_create["-text-"].update(f"Enter an end ski lift station of this run: (No previously created ski lift stations)")
                        else:
                            self.__window_create["-text-"].update(f"Enter an end ski lift station of this run:\n({'\n'.join(run_names_excluding_node)})")
                        while creating_loop and not quit_creating:
                            event, values = self.__window_create.read()
                            if event == "-return-" or event == sg.WIN_CLOSED:
                                creating_loop = False
                                quit_creating = True
                            elif event == "-cancel-":
                                self.__window_create["-text_input-"].update("")
                            elif event == "-submit-":
                                if values["-text_input-"] not in self.__saved_ski_resorts.resorts[ski_resort_name].nodes[node_name].runs and values["-text_input-"] != node_name and re.match('(^[a-z]|[A-Z]).*$',values["-text_input-"]):
                                    creating_loop = False
                                    run_name = values["-text_input-"]
                                else:
                                    sg.popup("Error.  The name entered cannot already be a run or be the same as the node name. It must also start with a letter.")
                                    self.__window_create["-text_input-"].update("")
                        
                        if not quit_creating:
                            creating_loop = True
                            self.__window_create["-text_input-"].update("")
                            self.__window_create["-text-"].update(f"Enter the length of the run (minutes):")
                        while creating_loop and not quit_creating:
                            event, values = self.__window_create.read()
                            if event == "-return-" or event == sg.WIN_CLOSED:
                                creating_loop = False
                                quit_creating = True
                            elif event == "-cancel-":
                                self.__window_create["-text_input-"].update("")
                            elif event == "-submit-":
                                if values["-text_input-"].isnumeric():
                                    creating_loop = False
                                    length = int(values["-text_input-"])
                                else:
                                    sg.popup("Error. The length must be a number.")
                                    self.__window_create["-text_input-"].update("")
                        
                        if not quit_creating:
                            creating_loop = True
                            self.__window_create["-text_input-"].update("")
                            self.__window_create["-text-"].update(f"Enter the opening time of the run (hh:mm):")
                        while creating_loop and not quit_creating:
                            event, values = self.__window_create.read()
                            if event == "-return-" or event == sg.WIN_CLOSED:
                                creating_loop = False
                                quit_creating = True
                            elif event == "-cancel-":
                                self.__window_create["-text_input-"].update("")
                            elif event == "-submit-":
                                if int(values["-text_input-"][values["-text_input-"].index(":")+1:]) < 60 and re.match(r'^\d{2}:\d{2}$', values["-text_input-"]):
                                    creating_loop = False
                                    opening = values["-text_input-"]
                                else:
                                    sg.popup("Error. The time entered must be in the format hh:mm.")
                                    self.__window_create["-text_input-"].update("")
                        
                        if not quit_creating:
                            creating_loop = True
                            self.__window_create["-text_input-"].update("")
                            self.__window_create["-text-"].update(f"Enter the closing time of the run (hh:mm):")
                        while creating_loop and not quit_creating:
                            event, values = self.__window_create.read()
                            if event == "-return-" or event == sg.WIN_CLOSED:
                                creating_loop = False
                                quit_creating = True
                            elif event == "-cancel-":
                                self.__window_create["-text_input-"].update("")
                            elif event == "-submit-":
                                if int(values["-text_input-"][values["-text_input-"].index(":")+1:]) < 60 and re.match(r'^\d{2}:\d{2}$', values["-text_input-"]):
                                    if self.__compare_greater(values["-text_input-"], opening):
                                        creating_loop = False
                                        closing = values["-text_input-"]
                                    else:
                                        sg.popup("Error. The closing time must be after the opening time.")
                                        self.__window_create["-text_input-"].update("")
                                else:
                                    sg.popup("Error. The time entered must be in the format hh:mm.")
                                    self.__window_create["-text_input-"].update("")
                        
                        lift = ""
                        if not quit_creating:
                            creating_loop = True
                            self.__window_create["-text_input-"].update("")
                            self.__window_create["-text-"].update(f"Is this a lift or a run ('l' or 'r'):")
                        while creating_loop and not quit_creating:
                            event, values = self.__window_create.read()
                            if event == "-return-" or event == sg.WIN_CLOSED:
                                creating_loop = False
                                quit_creating = True
                            elif event == "-cancel-":
                                self.__window_create["-text_input-"].update("")
                            elif event == "-submit-":
                                if values["-text_input-"] in ["l","r"]:
                                    creating_loop = False
                                    lift = values["-text_input-"]
                                else:
                                    sg.popup("Error. The input must be 'l' or 'r'.")
                                    self.__window_create["-text_input-"].update("")
                        
                        if lift == "l":
                            lift = 1
                            difficulty = "none"

                            creating_loop = True
                            self.__window_create["-text_input-"].update("")
                            self.__window_create["-text-"].update(f"Enter the type of lift ('gondola', 'chairlift', 'draglift'):")
                            while creating_loop and not quit_creating:
                                event, values = self.__window_create.read()
                                if event == "-return-" or event == sg.WIN_CLOSED:
                                    creating_loop = False
                                    quit_creating = True
                                elif event == "-cancel-":
                                    self.__window_create["-text_input-"].update("")
                                elif event == "-submit-":
                                    if values["-text_input-"] in ["gondola","chairlift","draglift"]:
                                        creating_loop = False
                                        lift_type = values["-text_input-"]
                                    else:
                                        sg.popup("Error. The input must be 'gondola', 'chairlift' or 'draglift'.")
                                        self.__window_create["-text_input-"].update("")
                        
                        elif lift == "r":
                            lift = 0
                            lift_type = "none"

                            creating_loop = True
                            self.__window_create["-text_input-"].update("")
                            self.__window_create["-text-"].update(f"Enter the difficulty of the run ('green', 'blue', 'red', 'black'):")
                            while creating_loop and not quit_creating:
                                event, values = self.__window_create.read()
                                if event == "-return-" or event == sg.WIN_CLOSED:
                                    creating_loop = False
                                    quit_creating = True
                                elif event == "-cancel-":
                                    self.__window_create["-text_input-"].update("")
                                elif event == "-submit-":
                                    if values["-text_input-"] in ["green","blue","red","black"]:
                                        creating_loop = False
                                        difficulty = values["-text_input-"]
                                    else:
                                        sg.popup("Error. The input must be 'green', 'blue', 'red' or 'black'.")
                                        self.__window_create["-text_input-"].update("")
                        
                        if not quit_creating:
                            self.__saved_ski_resorts.resorts[ski_resort_name].nodes[node_name].add_run(run_name,length,opening,closing,lift,difficulty,lift_type)

                        if not quit_creating:
                            creating_loop = True
                            self.__window_create["-text_input-"].update("")
                            self.__window_create["-text-"].update(f"Do you want to create another run from this ski lift station? (y/n):")
                        while creating_loop and not quit_creating:
                            event, values = self.__window_create.read()
                            if event == "-return-" or event == sg.WIN_CLOSED:
                                creating_loop = False
                                quit_creating = True
                            elif event == "-cancel-":
                                self.__window_create["-text_input-"].update("")
                            elif event == "-submit-":
                                if values["-text_input-"] in ["y","n"]:
                                    creating_run = values["-text_input-"]
                                    creating_loop = False
                                else:
                                    sg.popup("Error. The input must be 'y' or 'n'.")
                                    self.__window_create["-text_input-"].update("")

                elif create_node == "n" and not quit_creating:
                    creating = False

        incomplete_nodes = True
        break_loop = False
        while incomplete_nodes and not quit_creating:
            for node in self.__saved_ski_resorts.resorts[ski_resort_name].nodes: #node is a string of the name of the ski lift station
                for run in self.__saved_ski_resorts.resorts[ski_resort_name].nodes[node].runs: #run is the run object
                    if run.name not in self.__saved_ski_resorts.resorts[ski_resort_name].nodes:
                        creating_loop = True
                        self.__window_create["-text_input-"].update("")
                        self.__window_create["-text-"].update(f"Node {run.name} must be created since it was used as the end of a run but has not been created.\nEnter the altitude of the ski lift station:")
                        while creating_loop and not quit_creating:
                            event, values = self.__window_create.read()
                            if event == "-return-" or event == sg.WIN_CLOSED:
                                creating_loop = False
                                quit_creating = True
                            elif event == "-cancel-":
                                self.__window_create["-text_input-"].update("")
                            elif event == "-submit-":
                                if values["-text_input-"].isnumeric():
                                    creating_loop = False
                                    altitude = int(values["-text_input-"])
                                else:
                                    sg.popup("Error. The altitude must be a number.")
                                    self.__window_create["-text_input-"].update("")
                        self.__saved_ski_resorts.resorts[ski_resort_name].add_ski_node(run.name,altitude)

                        creating_run = "y"
                        while creating_run == "y" and not quit_creating:
                            creating_loop = True
                            self.__window_create["-text_input-"].update("")
                            run_names_excluding_node = list(self.__saved_ski_resorts.resorts[ski_resort_name].nodes.keys())
                            run_names_excluding_node.remove(node_name)
                            if len(run_names_excluding_node) == 0:
                                self.__window_create["-text-"].update(f"Enter an end ski lift station of this run: (No previously created ski lift stations)")
                            else:
                                self.__window_create["-text-"].update(f"Enter an end ski lift station of this run:\n({'\n'.join(run_names_excluding_node)})")
                            while creating_loop and not quit_creating:
                                event, values = self.__window_create.read()
                                if event == "-return-" or event == sg.WIN_CLOSED:
                                    creating_loop = False
                                    quit_creating = True
                                elif event == "-cancel-":
                                    self.__window_create["-text_input-"].update("")
                                elif event == "-submit-":
                                    if values["-text_input-"] not in self.__saved_ski_resorts.resorts[ski_resort_name].nodes[node_name].runs and values["-text_input-"] != node_name and re.match('(^[a-z]|[A-Z]).*$',values["-text_input-"]):
                                        creating_loop = False
                                        run_name = values["-text_input-"]
                                    else:
                                        sg.popup("Error. The name entered cannot already be a run or be the same as the node name. It must also start with a letter.")
                                        self.__window_create["-text_input-"].update("")

                            if not quit_creating:
                                creating_loop = True
                                self.__window_create["-text_input-"].update("")
                                self.__window_create["-text-"].update(f"Enter the length of the run (minutes):")
                            while creating_loop and not quit_creating:
                                event, values = self.__window_create.read()
                                if event == "-return-" or event == sg.WIN_CLOSED:
                                    creating_loop = False
                                    quit_creating = True
                                elif event == "-cancel-":
                                    self.__window_create["-text_input-"].update("")
                                elif event == "-submit-":
                                    if values["-text_input-"].isnumeric():
                                        creating_loop = False
                                        length = int(values["-text_input-"])
                                    else:
                                        sg.popup("Error. The length must be a number.")
                                        self.__window_create["-text_input-"].update("")
                            
                            if not quit_creating:
                                creating_loop = True
                                self.__window_create["-text_input-"].update("")
                                self.__window_create["-text-"].update(f"Enter the opening time of the run (hh:mm):")
                            while creating_loop and not quit_creating:
                                event, values = self.__window_create.read()
                                if event == "-return-" or event == sg.WIN_CLOSED:
                                    creating_loop = False
                                    quit_creating = True
                                elif event == "-cancel-":
                                    self.__window_create["-text_input-"].update("")
                                elif event == "-submit-":
                                    if int(values["-text_input-"][values["-text_input-"].index(":")+1:]) < 60 and re.match(r'^\d{2}:\d{2}$', values["-text_input-"]):
                                        creating_loop = False
                                        opening = values["-text_input-"]
                                    else:
                                        sg.popup("Error. The time entered must be in the format hh:mm.")
                                        self.__window_create["-text_input-"].update("")
                            
                            if not quit_creating:
                                creating_loop = True
                                self.__window_create["-text_input-"].update("")
                                self.__window_create["-text-"].update(f"Enter the closing time of the run (hh:mm):")
                            while creating_loop and not quit_creating:
                                event, values = self.__window_create.read()
                                if event == "-return-" or event == sg.WIN_CLOSED:
                                    creating_loop = False
                                    quit_creating = True
                                elif event == "-cancel-":
                                    self.__window_create["-text_input-"].update("")
                                elif event == "-submit-":
                                    if int(values["-text_input-"][values["-text_input-"].index(":")+1:]) < 60 and re.match(r'^\d{2}:\d{2}$', values["-text_input-"]):
                                        if self.__compare_greater(values["-text_input-"], opening):
                                            creating_loop = False
                                            closing = values["-text_input-"]
                                        else:
                                            sg.popup("Error. The closing time must be after the opening time.")
                                            self.__window_create["-text_input-"].update("")
                                    else:
                                        sg.popup("Error. The time entered must be in the format hh:mm.")
                                        self.__window_create["-text_input-"].update("")
                            
                            lift = ""
                            if not quit_creating:
                                creating_loop = True
                                self.__window_create["-text_input-"].update("")
                                self.__window_create["-text-"].update(f"Is this a lift or a run ('l' or 'r'):")
                            while creating_loop and not quit_creating:
                                event, values = self.__window_create.read()
                                if event == "-return-" or event == sg.WIN_CLOSED:
                                    creating_loop = False
                                    quit_creating = True
                                elif event == "-cancel-":
                                    self.__window_create["-text_input-"].update("")
                                elif event == "-submit-":
                                    if values["-text_input-"] in ["l","r"]:
                                        creating_loop = False
                                        lift = values["-text_input-"]
                                    else:
                                        sg.popup("Error. The input must be 'l' or 'r'.")
                                        self.__window_create["-text_input-"].update("")
                            
                            if lift == "l":
                                lift = 1
                                difficulty = "none"

                                creating_loop = True
                                self.__window_create["-text_input-"].update("")
                                self.__window_create["-text-"].update(f"Enter the type of lift ('gondola', 'chairlift', 'draglift'):")
                                while creating_loop and not quit_creating:
                                    event, values = self.__window_create.read()
                                    if event == "-return-" or event == sg.WIN_CLOSED:
                                        creating_loop = False
                                        quit_creating = True
                                    elif event == "-cancel-":
                                        self.__window_create["-text_input-"].update("")
                                    elif event == "-submit-":
                                        if values["-text_input-"] in ["gondola","chairlift","draglift"]:
                                            creating_loop = False
                                            lift_type = values["-text_input-"]
                                        else:
                                            sg.popup("Error. The input must be 'gondola', 'chairlift' or 'draglift'.")
                                            self.__window_create["-text_input-"].update("")
                            
                            elif lift == "r":
                                lift = 0
                                lift_type = "none"

                                creating_loop = True
                                self.__window_create["-text_input-"].update("")
                                self.__window_create["-text-"].update(f"Enter the difficulty of the run ('green', 'blue', 'red', 'black'):")
                                while creating_loop and not quit_creating:
                                    event, values = self.__window_create.read()
                                    if event == "-return-" or event == sg.WIN_CLOSED:
                                        creating_loop = False
                                        quit_creating = True
                                    elif event == "-cancel-":
                                        self.__window_create["-text_input-"].update("")
                                    elif event == "-submit-":
                                        if values["-text_input-"] in ["green","blue","red","black"]:
                                            creating_loop = False
                                            difficulty = values["-text_input-"]
                                        else:
                                            sg.popup("Error. The input must be 'green', 'blue', 'red' or 'black'.")
                                            self.__window_create["-text_input-"].update("")
                            
                            if not quit_creating:
                                self.__saved_ski_resorts.resorts[ski_resort_name].nodes[node_name].add_run(run_name,length,opening,closing,lift,difficulty,lift_type)

                                creating_loop = True
                                self.__window_create["-text_input-"].update("")
                                self.__window_create["-text-"].update(f"Do you want to create another run from this ski lift station? (y/n):")
                            while creating_loop and not quit_creating:
                                event, values = self.__window_create.read()
                                if event == "-return-" or event == sg.WIN_CLOSED:
                                    creating_loop = False
                                    quit_creating = True
                                elif event == "-cancel-":
                                    self.__window_create["-text_input-"].update("")
                                elif event == "-submit-":
                                    if values["-text_input-"] in ["y","n"]:
                                        creating_run = values["-text_input-"]
                                        creating_loop = False
                                    else:
                                        sg.popup("Error. The input must be 'y' or 'n'.")
                                        self.__window_create["-text_input-"].update("")
                        break_loop = True #The loop will break if a new ski lift station is created since the dictionary being iterated over has changed
                    if break_loop:
                        break
                if break_loop:
                    break
            if not quit_creating:
                incomplete_nodes = False
                for node in self.__saved_ski_resorts.resorts[ski_resort_name].nodes: #Checks if there are any more ski lift stations that have not been created left
                    for run in self.__saved_ski_resorts.resorts[ski_resort_name].nodes[node].runs:
                        if run.name not in self.__saved_ski_resorts.resorts[ski_resort_name].nodes:
                            incomplete_nodes = True
        if not quit_creating:     
            if self.__saved_ski_resorts.resorts[ski_resort_name].nodes == {}:
                sg.popup("There are no ski lift stations in this ski resort so it has not been created.")
            self.__window_create.close()
            add_resort_to_database(self.__saved_ski_resorts, ski_resort_name) #Add the ski resorts created in the program to the database
            Display_graph().display_ski_resort(self.__saved_ski_resorts.resorts[ski_resort_name]) #display ski resort

    ##############################################
    # GROUP A Skill: Cross-table parameterised SQL
    ##############################################
    def __modify_ski_resort(self): #Allows the user to modify an existing run, add a new run or lift or add a new node
        self.__saved_ski_resorts = Ski_resorts()
        self.__saved_ski_resorts = sync_from_database(self.__saved_ski_resorts)
        self.__construct_example_ski_resort()

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

                modify_layout = [
                    [sg.Text(f"Enter the name of the ski resort which you want to modify (It cannot be the same as one of the previously created resorts shown):\n({"\n".join(ski_resorts_list)})", key = "-text-")],
                    [sg.InputText(key="-text_input-")],
                    [sg.Button("Submit", key="-submit-")],
                    [sg.Button("Cancel", key="-cancel-")],
                    [sg.Button("Return to menu", key="-return-")]
                ]
                self.__window_modify = sg.Window("Modifying ski resort", modify_layout)

                modify_loop = True
                quit_modifying = False
                while modify_loop and not quit_modifying:
                    event, values = self.__window_modify.read()
                    if event == "-return-" or event == sg.WIN_CLOSED:
                        modify_loop = False
                        quit_modifying = True
                    elif event == "-cancel-":
                        self.__window_modify["-text_input-"].update("")
                    elif event == "-submit-":
                        if values["-text_input-"] in ski_resorts_list:
                            modify_loop = False
                            ski_resort_to_modify = values["-text_input-"]
                        else:
                            sg.popup("Error. The ski resort name must be one of the previously created ski resorts shown.")
                            self.__window_modify["-text_input-"].update("")

                modify = ""
                if not quit_modifying:
                    modify_loop = True
                    self.__window_modify["-text_input-"].update("")
                    self.__window_modify["-text-"].update(f"What do you want to modify?\n1. Add a new ski lift station\n2. Add a new run or lift\n3. Modify an existing run\n")
                while modify_loop and not quit_modifying:
                    event, values = self.__window_modify.read()
                    if event == "-return-" or event == sg.WIN_CLOSED:
                        modify_loop = False
                        quit_modifying = True
                    elif event == "-cancel-":
                        self.__window_modify["-text_input-"].update("")
                    elif event == "-submit-":
                        if values["-text_input-"] in ["1","2","3"]:
                            modify_loop = False
                            modify = values["-text_input-"]
                        else:
                            sg.popup("Error. The input must be '1', '2' or '3'.")
                            self.__window_modify["-text_input-"].update("")
                
                if modify == "1" and not quit_modifying: #add a new ski lift station
                    select_nodes = "SELECT node_name FROM nodes WHERE resort_name=?;"
                    cursor.execute(select_nodes, [ski_resort_to_modify])
                    node_names_unpacked = cursor.fetchall()
                    node_names =[]
                    for item in node_names_unpacked:
                        node_names.append(item[0])
                    node_name = ""

                    if not quit_modifying:
                        modify_loop = True
                        self.__window_modify["-text_input-"].update("")
                        if len(node_names) == 0:
                            self.__window_modify["-text-"].update(f"Enter the name of the ski lift station that you want to create: (No previously created stations)")
                        else:
                            self.__window_modify["-text-"].update(f"Enter the name of the ski lift station that you want to create:\n({", ".join(node_names)})")
                    while modify_loop and not quit_modifying:
                        event, values = self.__window_modify.read()
                        if event == "-return-" or event == sg.WIN_CLOSED:
                            modify_loop = False
                            quit_modifying = True
                        elif event == "-cancel-":
                            self.__window_modify["-text_input-"].update("")
                        elif event == "-submit-":
                            if values["-text_input-"] not in node_names and re.match('(^[a-z]|[A-Z]).*$',values["-text_input-"]):
                                modify_loop = False
                                node_name = values["-text_input-"]
                            else:
                                sg.popup("Error. The ski lift station name must start with a letter and not already exist.")
                                self.__window_modify["-text_input-"].update("")

                    node_type = ""
                    if not quit_modifying:
                        modify_loop = True
                        self.__window_modify["-text_input-"].update("")
                        self.__window_modify["-text-"].update(f"Is this a ski lift station, a ski park or an amenity ('s', 'p' or 'a'):")
                    while modify_loop and not quit_modifying:
                        event, values = self.__window_modify.read()
                        if event == "-return-" or event == sg.WIN_CLOSED:
                            modify_loop = False
                            quit_modifying = True
                        elif event == "-cancel-":
                            self.__window_modify["-text_input-"].update("")
                        elif event == "-submit-":
                            if values["-text_input-"] in ["s","p","a"]:
                                modify_loop = False
                                node_type = values["-text_input-"]
                            else:
                                sg.popup("Error. The input must be 's', 'p' or 'a'.")
                                self.__window_modify["-text_input-"].update("")

                    if not quit_modifying:
                        modify_loop = True
                        self.__window_modify["-text_input-"].update("")
                        self.__window_modify["-text-"].update(f"Enter the altitude of the ski lift station:")
                    while modify_loop and not quit_modifying:
                        event, values = self.__window_modify.read()
                        if event == "-return-" or event == sg.WIN_CLOSED:
                            modify_loop = False
                            quit_modifying = True
                        elif event == "-cancel-":
                            self.__window_modify["-text_input-"].update("")
                        elif event == "-submit-":
                            if values["-text_input-"].isnumeric():
                                modify_loop = False
                                altitude = int(values["-text_input-"])
                            else:
                                sg.popup("Error. The altitude must be a number.")
                                self.__window_modify["-text_input-"].update("")

                    if node_type == "p" and not quit_modifying:
                        modify_loop = True
                        self.__window_modify["-text_input-"].update("")
                        self.__window_modify["-text-"].update(f"Enter the length of the ski park (minutes):")
                        while modify_loop and not quit_modifying:
                            event, values = self.__window_modify.read()
                            if event == "-return-" or event == sg.WIN_CLOSED:
                                modify_loop = False
                                quit_modifying = True
                            elif event == "-cancel-":
                                self.__window_modify["-text_input-"].update("")
                            elif event == "-submit-":
                                if values["-text_input-"].isnumeric():
                                    modify_loop = False
                                    ski_park_length = int(values["-text_input-"])
                                else:
                                    sg.popup("Error. The ski park length must be a number.")
                                    self.__window_modify["-text_input-"].update("")
                        if not quit_modifying:
                            add_node = """INSERT INTO nodes (node_name, resort_name, altitude, node_type, ski_park_length, amenity_type)
                                        VALUES (?,?,?,?,?,?);"""
                            cursor.execute(add_node, [node_name, ski_resort_to_modify, altitude, "Ski park", ski_park_length, "None"])
                    elif node_type == "a" and not quit_modifying:
                        modify_loop = True
                        self.__window_modify["-text_input-"].update("")
                        self.__window_modify["-text-"].update(f"Enter a description of the type of amenity e.g. restaurant:")
                        while modify_loop and not quit_modifying:
                            event, values = self.__window_modify.read()
                            if event == "-return-" or event == sg.WIN_CLOSED:
                                modify_loop = False
                                quit_modifying = True
                            elif event == "-cancel-":
                                self.__window_modify["-text_input-"].update("")
                            elif event == "-submit-":
                                if re.match('(^[a-z]|[A-Z]).*$',values["-text_input-"]):
                                    modify_loop = False
                                    amenity_type = values["-text_input-"]
                                else:
                                    sg.popup("Error. The amenity type must start with a letter.")
                                    self.__window_modify["-text_input-"].update("")
                        if not quit_modifying:
                            add_node = """INSERT INTO nodes (node_name, resort_name, altitude, node_type, ski_park_length, amenity_type)
                                        VALUES (?,?,?,?,?,?);"""
                            cursor.execute(add_node, [node_name, ski_resort_to_modify, altitude, "Amenity", 0, amenity_type])
                    elif node_type == "s" and not quit_modifying:
                        add_node = """INSERT INTO nodes (node_name, resort_name, altitude, node_type, ski_park_length, amenity_type)
                                    VALUES (?,?,?,?,?,?);"""
                        cursor.execute(add_node, [node_name, ski_resort_to_modify, altitude, "Ski lift station", 0, "None"])

                    creating_run = "y"
                    while creating_run == "y" and not quit_modifying: #Allow at least one run to be created from each ski lift station
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
                            sg.popup("There is only one ski lift station in this ski resort so no runs can be created.")
                            break
                        if run_names == node_names:
                            sg.popup("There are runs from this ski lift station to all other ski lift stations in this ski resort so no more runs can be created.")
                            break
                        
                        if not quit_modifying:
                            modify_loop = True
                            self.__window_modify["-text_input-"].update("")
                            self.__window_modify["-text-"].update(f"Enter the end ski lift station of a run:\nSki lift stations that the run could end at:\n({"\n".join(node_names)})\nSki lift stations to which there is already a run:\n({"\n".join(run_names)})")
                        while modify_loop and not quit_modifying:
                            event, values = self.__window_modify.read()
                            if event == "-return-" or event == sg.WIN_CLOSED:
                                modify_loop = False
                                quit_modifying = True
                            elif event == "-cancel-":
                                self.__window_modify["-text_input-"].update("")
                            elif event == "-submit-":
                                if values["-text_input-"] in node_names and values["-text_input-"] not in run_names and values["-text_input-"] != node_name and re.match('(^[a-z]|[A-Z]).*$',values["-text_input-"]):
                                    modify_loop = False
                                    run_name = values["-text_input-"]
                                else:
                                    sg.popup("Error. The name entered must not already be a run, be the same as the node name and start with a letter.")
                                    self.__window_modify["-text_input-"].update("")

                        if not quit_modifying:
                            modify_loop = True
                            self.__window_modify["-text_input-"].update("")
                            self.__window_modify["-text-"].update(f"Enter the length of the run (minutes):")
                        while modify_loop and not quit_modifying:
                            event, values = self.__window_modify.read()
                            if event == "-return-" or event == sg.WIN_CLOSED:
                                modify_loop = False
                                quit_modifying = True
                            elif event == "-cancel-":
                                self.__window_modify["-text_input-"].update("")
                            elif event == "-submit-":
                                if values["-text_input-"].isnumeric():
                                    modify_loop = False
                                    length = int(values["-text_input-"])
                                else:
                                    sg.popup("Error. The length must be a number.")
                                    self.__window_modify["-text_input-"].update("")

                        if not quit_modifying:
                            modify_loop = True
                            self.__window_modify["-text_input-"].update("")
                            self.__window_modify["-text-"].update(f"Enter the opening time of the run (hh:mm):")
                        while modify_loop and not quit_modifying:
                            event, values = self.__window_modify.read()
                            if event == "-return-" or event == sg.WIN_CLOSED:
                                modify_loop = False
                                quit_modifying = True
                            elif event == "-cancel-":
                                self.__window_modify["-text_input-"].update("")
                            elif event == "-submit-":
                                if int(values["-text_input-"][values["-text_input-"].index(":")+1:]) < 60 and re.match(r'^\d{2}:\d{2}$', values["-text_input-"]):
                                    modify_loop = False
                                    opening = values["-text_input-"]
                                else:
                                    sg.popup("Error. The time entered must be in the format hh:mm.")
                                    self.__window_modify["-text_input-"].update("")

                        if not quit_modifying:
                            modify_loop = True
                            self.__window_modify["-text_input-"].update("")
                            self.__window_modify["-text-"].update(f"Enter the closing time of the run (hh:mm):")
                        while modify_loop and not quit_modifying:
                            event, values = self.__window_modify.read()
                            if event == "-return-" or event == sg.WIN_CLOSED:
                                modify_loop = False
                                quit_modifying = True
                            elif event == "-cancel-":
                                self.__window_modify["-text_input-"].update("")
                            elif event == "-submit-":
                                if int(values["-text_input-"][values["-text_input-"].index(":")+1:]) < 60 and re.match(r'^\d{2}:\d{2}$', values["-text_input-"]):
                                    if self.__compare_greater(values["-text_input-"], opening):
                                        modify_loop = False
                                        closing = values["-text_input-"]
                                    else:
                                        sg.popup("Error. The closing time must be after the opening time.")
                                        self.__window_modify["-text_input-"].update("")
                                else:
                                    sg.popup("Error. The time entered must be in the format hh:mm.")
                                    self.__window_modify["-text_input-"].update("")

                        lift = ""
                        if not quit_modifying:
                            modify_loop = True
                            self.__window_modify["-text_input-"].update("")
                            self.__window_modify["-text-"].update(f"Is this a lift or a run ('l' or 'r'):")
                        while modify_loop and not quit_modifying:
                            event, values = self.__window_modify.read()
                            if event == "-return-" or event == sg.WIN_CLOSED:
                                modify_loop = False
                                quit_modifying = True
                            elif event == "-cancel-":
                                self.__window_modify["-text_input-"].update("")
                            elif event == "-submit-":
                                if values["-text_input-"] in ["l","r"]:
                                    modify_loop = False
                                    lift = values["-text_input-"]
                                else:
                                    sg.popup("Error. The input must be 'l' or 'r'.")
                                    self.__window_modify["-text_input-"].update("")

                        if lift == "l" and not quit_modifying:
                            lift = 1

                            modify_loop = True
                            self.__window_modify["-text_input-"].update("")
                            self.__window_modify["-text-"].update(f"Enter the type of lift ('gondola', 'chairlift', 'draglift'):")
                            while modify_loop and not quit_modifying:
                                event, values = self.__window_modify.read()
                                if event == "-return-" or event == sg.WIN_CLOSED:
                                    modify_loop = False
                                    quit_modifying = True
                                elif event == "-cancel-":
                                    self.__window_modify["-text_input-"].update("")
                                elif event == "-submit-":
                                    if values["-text_input-"] in ["gondola","chairlift","draglift"]:
                                        modify_loop = False
                                        lift_type = values["-text_input-"]
                                    else:
                                        sg.popup("Error. The input must be 'gondola', 'chairlift' or 'draglift'.")
                                        self.__window_modify["-text_input-"].update("")
                            difficulty = "none"
                        elif lift == "r" and not quit_modifying:
                            lift = 0
                            lift_type = "none"

                            modify_loop = True
                            self.__window_modify["-text_input-"].update("")
                            self.__window_modify["-text-"].update(f"Enter the difficulty of the run ('green', 'blue', 'red', 'black'):")
                            while modify_loop and not quit_modifying:
                                event, values = self.__window_modify.read()
                                if event == "-return-" or event == sg.WIN_CLOSED:
                                    modify_loop = False
                                    quit_modifying = True
                                elif event == "-cancel-":
                                    self.__window_modify["-text_input-"].update("")
                                elif event == "-submit-":
                                    if values["-text_input-"] in ["green","blue","red","black"]:
                                        modify_loop = False
                                        difficulty = values["-text_input-"]
                                    else:
                                        sg.popup("Error. The input must be 'green', 'blue', 'red' or 'black'.")
                                        self.__window_modify["-text_input-"].update("")

                        creating_run = "n"
                        if not quit_modifying:
                            add_run = """INSERT INTO runs (node_id, end_node_id, run_length, opening, closing, lift, difficulty, lift_type)
                                        VALUES ((SELECT node_id FROM nodes WHERE node_name=? AND resort_name=?),(SELECT node_id FROM nodes WHERE node_name=? AND resort_name=?),?,?,?,?,?,?);"""
                            cursor.execute(add_run, [node_name, ski_resort_to_modify, run_name, ski_resort_to_modify, length, opening, closing, lift, difficulty, lift_type])

                            modify_loop = True
                            self.__window_modify["-text_input-"].update("")
                            self.__window_modify["-text-"].update(f"Do you want to create another run from this ski lift station? (y/n):")
                            while modify_loop and not quit_modifying:
                                event, values = self.__window_modify.read()
                                if event == "-return-" or event == sg.WIN_CLOSED:
                                    modify_loop = False
                                    quit_modifying = True
                                elif event == "-cancel-":
                                    self.__window_modify["-text_input-"].update("")
                                elif event == "-submit-":
                                    if values["-text_input-"] in ["y","n"]:
                                        creating_run = values["-text_input-"]
                                        modify_loop = False
                                    else:
                                        sg.popup("Error. The input must be 'y' or 'n'.")
                                        self.__window_modify["-text_input-"].update("")
                
                elif modify == "2" and not quit_modifying: #add a new run or lift
                    discontinue = False
                    select_nodes = "SELECT node_name FROM nodes WHERE resort_name=?;"
                    cursor.execute(select_nodes, [ski_resort_to_modify])
                    node_names_unpacked = cursor.fetchall()
                    node_names =[]
                    for item in node_names_unpacked:
                        node_names.append(item[0])
                    node_name = ""

                    if not quit_modifying:
                        modify_loop = True
                        self.__window_modify["-text_input-"].update("")
                        if len(node_names) == 0:
                            sg.popup("There are no nodes to which a run or lift can be added.")
                            discontinue = True
                        else:
                            self.__window_modify["-text-"].update(f"Enter the name of the ski lift station from which you want to add a run or lift:\n({"\n".join(node_names)})")
                    while modify_loop and not quit_modifying and not discontinue:
                        event, values = self.__window_modify.read()
                        if event == "-return-" or event == sg.WIN_CLOSED:
                            modify_loop = False
                            quit_modifying = True
                        elif event == "-cancel-":
                            self.__window_modify["-text_input-"].update("")
                        elif event == "-submit-":
                            if values["-text_input-"] in node_names and re.match('(^[a-z]|[A-Z]).*$',values["-text_input-"]):
                                modify_loop = False
                                node_name = values["-text_input-"]
                            else:
                                sg.popup("Error. The ski lift station name must start with a letter and already exist.")
                                self.__window_modify["-text_input-"].update("")

                    if not discontinue and not quit_modifying:
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
                            sg.popup("There is only one ski lift station in this ski resort so no runs can be created.")
                        elif run_names == node_names:
                            sg.popup("There are runs from this ski lift station to all other ski lift stations in this ski resort so no more runs can be created.")
                        else:
                            modify_loop = True
                            self.__window_modify["-text_input-"].update("")
                            self.__window_modify["-text-"].update(f"Enter the end ski lift station of a run:\nSki lift stations that the run could end at:\n({"\n".join(node_names)})\nSki lift stations to which there is already a run:\n({"\n".join(run_names)})")
                            while modify_loop and not quit_modifying:
                                event, values = self.__window_modify.read()
                                if event == "-return-" or event == sg.WIN_CLOSED:
                                    modify_loop = False
                                    quit_modifying = True
                                elif event == "-cancel-":
                                    self.__window_modify["-text_input-"].update("")
                                elif event == "-submit-":
                                    if values["-text_input-"] in node_names and values["-text_input-"] not in run_names and values["-text_input-"] != node_name and re.match('(^[a-z]|[A-Z]).*$',values["-text_input-"]):
                                        modify_loop = False
                                        run_name = values["-text_input-"]
                                    else:
                                        sg.popup("Error. The name entered must not already be a run, be the same as the node name and start with a letter.")
                                        self.__window_modify["-text_input-"].update("")

                            if not quit_modifying:
                                modify_loop = True
                                self.__window_modify["-text_input-"].update("")
                                self.__window_modify["-text-"].update(f"Enter the length of the run (minutes):")
                            while modify_loop and not quit_modifying:
                                event, values = self.__window_modify.read()
                                if event == "-return-" or event == sg.WIN_CLOSED:
                                    modify_loop = False
                                    quit_modifying = True
                                elif event == "-cancel-":
                                    self.__window_modify["-text_input-"].update("")
                                elif event == "-submit-":
                                    if values["-text_input-"].isnumeric():
                                        modify_loop = False
                                        length = int(values["-text_input-"])
                                    else:
                                        sg.popup("Error. The length must be a number.")
                                        self.__window_modify["-text_input-"].update("")

                            if not quit_modifying:
                                modify_loop = True
                                self.__window_modify["-text_input-"].update("")
                                self.__window_modify["-text-"].update(f"Enter the opening time of the run (hh:mm):")
                            while modify_loop and not quit_modifying:
                                event, values = self.__window_modify.read()
                                if event == "-return-" or event == sg.WIN_CLOSED:
                                    modify_loop = False
                                    quit_modifying = True
                                elif event == "-cancel-":
                                    self.__window_modify["-text_input-"].update("")
                                elif event == "-submit-":
                                    if int(values["-text_input-"][values["-text_input-"].index(":")+1:]) < 60 and re.match(r'^\d{2}:\d{2}$', values["-text_input-"]):
                                        modify_loop = False
                                        opening = values["-text_input-"]
                                    else:
                                        sg.popup("Error. The time entered must be in the format hh:mm.")
                                        self.__window_modify["-text_input-"].update("")

                            if not quit_modifying:
                                modify_loop = True
                                self.__window_modify["-text_input-"].update("")
                                self.__window_modify["-text-"].update(f"Enter the closing time of the run (hh:mm):")
                            while modify_loop and not quit_modifying:
                                event, values = self.__window_modify.read()
                                if event == "-return-" or event == sg.WIN_CLOSED:
                                    modify_loop = False
                                    quit_modifying = True
                                elif event == "-cancel-":
                                    self.__window_modify["-text_input-"].update("")
                                elif event == "-submit-":
                                    if int(values["-text_input-"][values["-text_input-"].index(":")+1:]) < 60 and re.match(r'^\d{2}:\d{2}$', values["-text_input-"]):
                                        if self.__compare_greater(values["-text_input-"], opening):
                                            modify_loop = False
                                            closing = values["-text_input-"]
                                        else:
                                            sg.popup("Error. The closing time must be after the opening time.")
                                            self.__window_modify["-text_input-"].update("")
                                    else:
                                        sg.popup("Error. The time entered must be in the format hh:mm.")
                                        self.__window_modify["-text_input-"].update("")

                            lift = ""
                            if not quit_modifying:
                                modify_loop = True
                                self.__window_modify["-text_input-"].update("")
                                self.__window_modify["-text-"].update(f"Is this a lift or a run ('l' or 'r'):")
                            while modify_loop and not quit_modifying:
                                event, values = self.__window_modify.read()
                                if event == "-return-" or event == sg.WIN_CLOSED:
                                    modify_loop = False
                                    quit_modifying = True
                                elif event == "-cancel-":
                                    self.__window_modify["-text_input-"].update("")
                                elif event == "-submit-":
                                    if values["-text_input-"] in ["l","r"]:
                                        modify_loop = False
                                        lift = values["-text_input-"]
                                    else:
                                        sg.popup("Error. The input must be 'l' or 'r'.")
                                        self.__window_modify["-text_input-"].update("")

                            if lift == "l" and not quit_modifying:
                                lift = 1

                                modify_loop = True
                                self.__window_modify["-text_input-"].update("")
                                self.__window_modify["-text-"].update(f"Enter the type of lift ('gondola', 'chairlift', 'draglift'):")
                                while modify_loop and not quit_modifying:
                                    event, values = self.__window_modify.read()
                                    if event == "-return-" or event == sg.WIN_CLOSED:
                                        modify_loop = False
                                        quit_modifying = True
                                    elif event == "-cancel-":
                                        self.__window_modify["-text_input-"].update("")
                                    elif event == "-submit-":
                                        if values["-text_input-"] in ["gondola","chairlift","draglift"]:
                                            modify_loop = False
                                            lift_type = values["-text_input-"]
                                        else:
                                            sg.popup("Error. The input must be 'gondola', 'chairlift' or 'draglift'.")
                                            self.__window_modify["-text_input-"].update("")
                                difficulty = "none"
                            elif lift == "r" and not quit_modifying:
                                lift = 0
                                lift_type = "none"

                                modify_loop = True
                                self.__window_modify["-text_input-"].update("")
                                self.__window_modify["-text-"].update(f"Enter the difficulty of the run ('green', 'blue', 'red', 'black'):")
                                while modify_loop and not quit_modifying:
                                    event, values = self.__window_modify.read()
                                    if event == "-return-" or event == sg.WIN_CLOSED:
                                        modify_loop = False
                                        quit_modifying = True
                                    elif event == "-cancel-":
                                        self.__window_modify["-text_input-"].update("")
                                    elif event == "-submit-":
                                        if values["-text_input-"] in ["green","blue","red","black"]:
                                            modify_loop = False
                                            difficulty = values["-text_input-"]
                                        else:
                                            sg.popup("Error. The input must be 'green', 'blue', 'red' or 'black'.")
                                            self.__window_modify["-text_input-"].update("")

                            if not quit_modifying:
                                add_run = """INSERT INTO runs (node_id, end_node_id, run_length, opening, closing, lift, difficulty, lift_type)
                                            VALUES ((SELECT node_id FROM nodes WHERE node_name=? AND resort_name=?),(SELECT node_id FROM nodes WHERE node_name=? AND resort_name=?),?,?,?,?,?,?);"""
                                cursor.execute(add_run, [node_name, ski_resort_to_modify, run_name, ski_resort_to_modify, length, opening, closing, lift, difficulty, lift_type])

                elif modify == "3" and not quit_modifying: #modify an existing run
                    discontinue = False
                    select_nodes = "SELECT node_name FROM nodes WHERE resort_name=?;"
                    cursor.execute(select_nodes, [ski_resort_to_modify])
                    node_names_unpacked = cursor.fetchall()
                    node_names =[]
                    for item in node_names_unpacked:
                        node_names.append(item[0])

                    if not quit_modifying:
                        modify_loop = True
                        self.__window_modify["-text_input-"].update("")
                        if len(node_names) == 0:
                            sg.popup(f"There are no nodes to which a run or lift can be added.\n")
                            discontinue = True
                        else:
                            self.__window_modify["-text-"].update(f"Enter the name of the ski lift station from which you want to modify a run or lift: (Possible ski lift station names)\n({"\n".join(node_names)})")                    
                    while modify_loop and not quit_modifying and not discontinue:
                        event, values = self.__window_modify.read()
                        if event == "-return-" or event == sg.WIN_CLOSED:
                            modify_loop = False
                            quit_modifying = True
                        elif event == "-cancel-":
                            self.__window_modify["-text_input-"].update("")
                        elif event == "-submit-":
                            if values["-text_input-"] in node_names and re.match('(^[a-z]|[A-Z]).*$',values["-text_input-"]):
                                modify_loop = False
                                node_name = values["-text_input-"]
                            else:
                                sg.popup("Error. The ski lift station name must start with a letter and already exist.")
                                self.__window_modify["-text_input-"].update("")
                    
                    if not discontinue and not quit_modifying:
                        select_runs = "SELECT * FROM runs WHERE node_id=(SELECT node_id FROM nodes WHERE node_name=? AND resort_name=?);"
                        cursor.execute(select_runs, [node_name, ski_resort_to_modify])
                        runs_unpacked = cursor.fetchall()
                        run_names = []
                        for i in range(len(runs_unpacked)):
                            select_end_node_name = "SELECT node_name FROM nodes WHERE node_id=?;"
                            cursor.execute(select_end_node_name, [runs_unpacked[i][2]])
                            end_node_name = cursor.fetchone()[0]
                            run_names.append(end_node_name)

                        if len(run_names) == 0:
                            sg.popup("There are no runs which can be modified.")
                        else:
                            modify_loop = True
                            self.__window_modify["-text_input-"].update("")
                            self.__window_modify["-text-"].update(f"Enter the end ski lift station of a run:\nSki lift stations that the run could end at:\n({"\n".join(node_names)})\nSki lift stations to which there is already a run:\n({"\n".join(run_names)})")
                            
                            while modify_loop and not quit_modifying:
                                event, values = self.__window_modify.read()
                                if event == "-return-" or event == sg.WIN_CLOSED:
                                    modify_loop = False
                                    quit_modifying = True
                                elif event == "-cancel-":
                                    self.__window_modify["-text_input-"].update("")
                                elif event == "-submit-":
                                    if values["-text_input-"] in run_names and values["-text_input-"] != node_name and re.match('(^[a-z]|[A-Z]).*$',values["-text_input-"]):
                                        modify_loop = False
                                        run_name = values["-text_input-"]
                                    else:
                                        sg.popup("Error. The name entered must be a run, not the same as the node name and start with a letter.")
                                        self.__window_modify["-text_input-"].update("")
                            
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
                            if lift_or_run == 0 and not quit_modifying:
                                modify_loop = True
                                self.__window_modify["-text_input-"].update("")
                                self.__window_modify["-text-"].update(f"What do you want to modify?\n1. Length\n2. Opening time\n3. Closing time\n4. Switch lift or run\n5. Close run\n6. Difficulty\n")
                                while modify_loop and not quit_modifying:
                                    event, values = self.__window_modify.read()
                                    if event == "-return-" or event == sg.WIN_CLOSED:
                                        modify_loop = False
                                        quit_modifying = True
                                    elif event == "-cancel-":
                                        self.__window_modify["-text_input-"].update("")
                                    elif event == "-submit-":
                                        if values["-text_input-"] in ["1","2","3","4","5","6"]:
                                            modify_loop = False
                                            modify3_option = values["-text_input-"]
                                        else:
                                            sg.popup("Error. The input must be '1', '2', '3', '4', '5' or '6'.")
                                            self.__window_modify["-text_input-"].update("")

                            elif lift_or_run == 1 and not quit_modifying:
                                modify_loop = True
                                self.__window_modify["-text_input-"].update("")
                                self.__window_modify["-text-"].update(f"What do you want to modify?\n1. Length\n2. Opening time\n3. Closing time\n4. Switch lift or run\n5. Close run\n6. Difficulty\n7. Lift type\n")
                                while modify_loop and not quit_modifying:
                                    event, values = self.__window_modify.read()
                                    if event == "-return-" or event == sg.WIN_CLOSED:
                                        modify_loop = False
                                        quit_modifying = True
                                    elif event == "-cancel-":
                                        self.__window_modify["-text_input-"].update("")
                                    elif event == "-submit-":
                                        if values["-text_input-"] in ["1","2","3","4","5","6","7"]:
                                            modify_loop = False
                                            modify3_option = values["-text_input-"]
                                        else:
                                            sg.popup("Error. The input must be '1', '2', '3', '4', '5', '6' or '7'.")
                                            self.__window_modify["-text_input-"].update("")

                            if modify3_option == "1" and not quit_modifying:
                                modify_loop = True
                                self.__window_modify["-text_input-"].update("")
                                self.__window_modify["-text-"].update(f"Enter the new length of the run (minutes):")
                                while modify_loop and not quit_modifying:
                                    event, values = self.__window_modify.read()
                                    if event == "-return-" or event == sg.WIN_CLOSED:
                                        modify_loop = False
                                        quit_modifying = True
                                    elif event == "-cancel-":
                                        self.__window_modify["-text_input-"].update("")
                                    elif event == "-submit-":
                                        if values["-text_input-"].isnumeric():
                                            modify_loop = False
                                            length = int(values["-text_input-"])
                                        else:
                                            sg.popup("Error. The length must be a number.")
                                            self.__window_modify["-text_input-"].update("")
                                if not quit_modifying:
                                    modify_run = "UPDATE runs SET run_length=? WHERE node_id=? AND end_node_id=?;"
                                    cursor.execute(modify_run, [length, node_id, end_node_id])

                            elif modify3_option == "2" and not quit_modifying:
                                modify_loop = True
                                self.__window_modify["-text_input-"].update("")
                                self.__window_modify["-text-"].update(f"Enter the new opening time of the run (hh:mm):")
                                while modify_loop and not quit_modifying:
                                    event, values = self.__window_modify.read()
                                    if event == "-return-" or event == sg.WIN_CLOSED:
                                        modify_loop = False
                                        quit_modifying = True
                                    elif event == "-cancel-":
                                        self.__window_modify["-text_input-"].update("")
                                    elif event == "-submit-":
                                        if int(values["-text_input-"][values["-text_input-"].index(":")+1:]) < 60 and re.match(r'^\d{2}:\d{2}$', values["-text_input-"]):
                                            modify_loop = False
                                            opening = values["-text_input-"]
                                        else:
                                            sg.popup("Error. The time entered must be in the format hh:mm.")
                                            self.__window_modify["-text_input-"].update("")
                                if not quit_modifying:
                                    modify_run = "UPDATE runs SET opening=? WHERE node_id=? AND end_node_id=?;"
                                    cursor.execute(modify_run, [opening, node_id, end_node_id])

                            elif modify3_option == "3" and not quit_modifying:
                                modify_loop = True
                                self.__window_modify["-text_input-"].update("")
                                self.__window_modify["-text-"].update(f"Enter the new closing time of the run (hh:mm):")
                                while modify_loop and not quit_modifying:
                                    event, values = self.__window_modify.read()
                                    if event == "-return-" or event == sg.WIN_CLOSED:
                                        modify_loop = False
                                        quit_modifying = True
                                    elif event == "-cancel-":
                                        self.__window_modify["-text_input-"].update("")
                                    elif event == "-submit-":
                                        if int(values["-text_input-"][values["-text_input-"].index(":")+1:]) < 60 and re.match(r'^\d{2}:\d{2}$', values["-text_input-"]):
                                            if self.__compare_greater(values["-text_input-"], opening):
                                                modify_loop = False
                                                closing = values["-text_input-"]
                                            else:
                                                sg.popup("Error. The closing time must be after the opening time.")
                                                self.__window_modify["-text_input-"].update("")
                                        else:
                                            sg.popup("Error. The time entered must be in the format hh:mm.")
                                            self.__window_modify["-text_input-"].update("")
                                if not quit_modifying:
                                    modify_run = "UPDATE runs SET closing=? WHERE node_id=? AND end_node_id=?;"
                                    cursor.execute(modify_run, [closing, node_id, end_node_id])
                            elif modify3_option == "4" and not quit_modifying:
                                if lift_or_run == 0:
                                    modify_run = "UPDATE runs SET lift=1 WHERE node_id=? AND end_node_id=?;"
                                    cursor.execute(modify_run, [node_id, end_node_id])
                                elif lift_or_run == 1:
                                    modify_run = "UPDATE runs SET lift=0 WHERE node_id=? AND end_node_id=?;"
                                    cursor.execute(modify_run, [node_id, end_node_id])
                            elif modify3_option == "5" and not quit_modifying:
                                close_run = "UPDATE runs SET run_length=? WHERE node_id=? AND end_node_id=?;"
                                cursor.execute(close_run, [inf, node_id, end_node_id])
                            elif modify3_option == "6" and not quit_modifying:
                                modify_loop = True
                                self.__window_modify["-text_input-"].update("")
                                self.__window_modify["-text-"].update(f"Enter the new difficulty of the run ('green', 'blue', 'red', 'black'):")
                                while modify_loop and not quit_modifying:
                                    event, values = self.__window_modify.read()
                                    if event == "-return-" or event == sg.WIN_CLOSED:
                                        modify_loop = False
                                        quit_modifying = True
                                    elif event == "-cancel-":
                                        self.__window_modify["-text_input-"].update("")
                                    elif event == "-submit-":
                                        if values["-text_input-"] in ["green","blue","red","black"]:
                                            modify_loop = False
                                            difficulty = values["-text_input-"]
                                        else:
                                            sg.popup("Error. The input must be 'green', 'blue', 'red' or 'black'.")
                                            self.__window_modify["-text_input-"].update("")
                                if not quit_modifying:
                                    modify_run = "UPDATE runs SET difficulty=? WHERE node_id=? AND end_node_id=?;"
                                    cursor.execute(modify_run, [difficulty, node_id, end_node_id])
                            elif modify3_option == "7" and not quit_modifying:
                                modify_loop = True
                                self.__window_modify["-text_input-"].update("")
                                self.__window_modify["-text-"].update(f"Enter the new type of lift ('gondola', 'chairlift', 'draglift'):")
                                while modify_loop and not quit_modifying:
                                    event, values = self.__window_modify.read()
                                    if event == "-return-" or event == sg.WIN_CLOSED:
                                        modify_loop = False
                                        quit_modifying = True
                                    elif event == "-cancel-":
                                        self.__window_modify["-text_input-"].update("")
                                    elif event == "-submit-":
                                        if values["-text_input-"] in ["gondola","chairlift","draglift"]:
                                            modify_loop = False
                                            lift_type = values["-text_input-"]
                                        else:
                                            sg.popup("Error. The input must be 'gondola', 'chairlift' or 'draglift'.")
                                            self.__window_modify["-text_input-"].update("")
                                if not quit_modifying:
                                    modify_run = "UPDATE runs SET lift_type=? WHERE node_id=? AND end_node_id=?;"
                                    cursor.execute(modify_run, [lift_type, node_id, end_node_id])

                self.__window_modify.close()
                conn.commit()
        except sqlite3.OperationalError as e:
            print("Failed to open database: ", e)
            
    ##############################################
    # GROUP A Skill: Cross-table parameterised SQL
    ##############################################
    def __delete_ski_resort(self): #Deletes a ski resort from the database
        self.__saved_ski_resorts = Ski_resorts()
        self.__saved_ski_resorts = sync_from_database(self.__saved_ski_resorts)
        self.__construct_example_ski_resort()
        delete_layout = [
            [sg.Text("Enter the name of the ski resort that you would like to delete: ")],
            [sg.InputText(key="-resort_name-")],
            [sg.Text(f"Existing ski resorts:\n{'\n'.join(self.__saved_ski_resorts.resorts.keys())}")],
            [sg.Button("Submit", key="-submit-")],
            [sg.Button("Cancel", key="-cancel-")],
            [sg.Button("Return to menu", key="-return-")]
        ]
        self.__window_delete = sg.Window("Delete a ski resort", delete_layout)
        delete_loop = True
        while delete_loop:
            event, values = self.__window_delete.read()
            if event == sg.WIN_CLOSED or event == "-return-":
                delete_loop = False
            elif event == "-submit-":
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
                        ski_resort_to_delete = values["-resort_name-"]
                        if ski_resort_to_delete in ski_resorts_list:
                            get_node_ids = "SELECT node_id FROM nodes WHERE resort_name=?;"
                            cursor.execute(get_node_ids, [ski_resort_to_delete])
                            node_ids = cursor.fetchall()

                            delete_records = "DELETE FROM nodes WHERE resort_name=?;"
                            cursor.execute(delete_records, [ski_resort_to_delete])

                            for node_id in node_ids:
                                delete_runs = "DELETE FROM runs WHERE node_id=?;"
                                cursor.execute(delete_runs, [node_id[0]])

                            conn.commit()
                            delete_loop = False
                        else:
                            sg.popup("The ski resort that you entered does not exist in the database.")
                except sqlite3.OperationalError as e:
                    sg.popup("Failed to open database: ", e)
            elif event == "-cancel-":
                self.__window_delete["-resort_name"].update("")
        self.__window_delete.close()

if __name__ == "__main__":
    ui = Gui()
    ui.menu()