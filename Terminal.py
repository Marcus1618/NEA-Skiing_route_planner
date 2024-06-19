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
}

class Terminal(Ui):
    
    def __init__(self):
        length = "0.00"
        ski_resort = ""
        start = ""
        valid = None

    def run(self):
        while valid == None:
            length = input("How long do you want to ski for (hours.mins): ")
            valid = re.match(r'^\d{1,2}.\d{2}$', length)
            if length[0] > "2":
                valid = None
            elif length[0] == "2" and length[1] > "4": #THIS IS CURRENTLY WRONG - WHAT IF ONLY 1 DIGIT
                valid = None

        while ski_resort not in ski_resorts.keys():
            ski_resort = input(f"Which ski resort are you in: {ski_resorts.values()}\n")
        print(ski_resorts[ski_resort]) #MAKE THIS BETTER
        while start not in ski_resorts[ski_resort].keys():
            start = input("From what lift do you want to start your route: ")

        route = Plan_route(ski_resorts[ski_resort], start, length)
        print(route)

        save = input("Do you want to save this route? (y/n): ") #ADD THIS TO OBJECTIVES
        option = input("Enter 'm' to return to the main menu or 'q' to quit: ")
        #DO SOMETHING WITH OPTION


