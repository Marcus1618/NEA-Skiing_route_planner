from Ui import Ui
from route_planner import Plan_route
import re

ski_resorts = {
    "Val_thorens" : {
        "Plein Sud bottom": [],
        "Plein Sud top": [["Pionniers bottom",{"length":5}],["Pionniers top",{"length":1}]],
        "3 Vallees bottom": [["Plein Sud bottom",{"length":15}]],
        "3 Vallees top": [["3 Vallees bottom",{"length":5}],["Plein Sud top",{"length":4}]],
        "Pionniers bottom": [["Plein Sud bottom",{"length":10}]],
        "Pionniers top": [["3 Vallees top",{"length":1}]]
        }
} #Outsource to a file

class Terminal(Ui):
    
    def __init__(self):
        length = "0.00"
        ski_resort = ""
        start = ""
        valid = None
    
    def menu(self):
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
            self.make_route()
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

    def make_route(self):
        
        while valid == None:
            length = input("How long do you want to ski for (Hours:Mins): ")
            valid = re.match(r'^\d{1,2}:\d{2}$', length)
            if valid[:valid.index(":")] == 2:
                if length[0] > "2":
                    valid = None
                elif length[0] == "2" and length[1] > "4":
                    valid = None
                elif int(length[3:]) > 59:
                    valid = None
            else:
                if int(length[2:]) > 59:
                    valid = None

        while ski_resort not in ski_resorts.keys():
            ski_resort = input(f"Which ski resort are you in: {ski_resorts.values()}\n")
        print(ski_resorts[ski_resort]) #MAKE THIS BETTER
        while start not in ski_resorts[ski_resort].keys():
            start = input("From what lift do you want to start your route: ")

        route = Plan_route(ski_resorts[ski_resort], start, length)
        print(route)

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