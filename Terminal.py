from Ui import Ui
from route_planner import Plan_route
import re

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

class Terminal(Ui):
    
    def __init__(self):
        length = "0.00"
        ski_resort = ""
        start = ""
        valid = None
    
    def menu(self):
        option = "-1"
        print("""
        Menu:
        1. Make a route
        2. Create a ski resort
        3. Modify an existing ski resort
        4. Display a ski resort
        5. Delete a ski resort
        6. View previous routes
        7. Exit              
              \n""")
        while option not in ["1","2","3","4","5","6","7"]:
            option = input("Enter the number of the option you want to select: ")

        if option == "1":
            self.generate_route()
        elif option == "2":
            self.create_ski_resort()
        elif option == "3":
            self.modify_ski_resort()
        elif option == "4":
            self.display_ski_resort()
        elif option == "5":
            self.delete_ski_resort()
        elif option == "6":
            self.view_previous_routes()
        elif option == "7":
            quit()

    def _add_times(self, t1, t2):
        h1, m1 = t1.split(":")
        h1, m1 = int(h1), int(m1)
        h2 = t2 // 60
        m2 = t2 % 60
        h = h1 + h2
        m = m1 + m2
        if m > 59:
            h += 1
            m -= 60
        if h > 23:
            h -= 24

        h = str(h)
        m = str(m)
        if len(h) == 1:
            h = "0" + h
        if len(m) == 1:
            m = "0" + m
        
        return f"{h}:{m}"

    def generate_route(self):

        valid = None
        while valid == None:
            length = input("How long do you want to ski for (hh:mm): ")

            if int(length[length.index(":")+1:]) < 60 and re.match(r'^\d{2}:\d{2}$', length):
                valid = True

        ski_resort = ""
        while ski_resort not in ski_resorts.keys():
            ski_resort = input(f"Which ski resort are you in: ({', '.join(ski_resorts.keys())})\n")

        start = ""
        while start not in ski_resorts[ski_resort].keys():
            start = input(f"From what lift do you want to start your route: ({', '.join(ski_resorts[ski_resort].keys())})\n")

        start_time = "00:00"
        start_time = input("At what time do you want to start your route (hh:mm): ") #ADD VALIDATION - between opening and closing times + right format

        route = Plan_route(ski_resorts[ski_resort], start, length).get_route()
        old_time = start_time
        for i in range(len(route)-1):
            new_time = self._add_times(old_time,route[i+1][1]["length"])
            print(f"{i+1}. {route[i][0]} to {route[i+1][0]} taking {route[i+1][1]['length']} minutes - {new_time}")
            old_time = new_time

        save = input("Do you want to save this route? (y/n): ") #ADD THIS TO OBJECTIVES + ADD FUNCTIONAILTY
        option = input("Enter 'm' to return to the main menu or 'q' to quit: ")
        if option == "m":
            self.menu()
        elif option == "q":
            quit()

    def create_ski_resort(self):
        pass

    def modify_ski_resort(self):
        pass

    def display_ski_resort(self):
        pass

    def delete_ski_resort(self):
        pass

    def view_previous_routes(self):
        pass