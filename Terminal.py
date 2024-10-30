from Ui import Ui
from route_planner import Plan_route
import re
from ski_resorts import Ski_resorts, Ski_resort, Ski_node, Run

"""ski_resorts = {
    "Val Thorens" : {
        "Plein Sud bottom": [["Plein Sud top",{"length":10}]],
        "Plein Sud top": [["Pionniers bottom",{"length":5}],["Pionniers top",{"length":1}]],
        "3 Vallees bottom": [["Plein Sud bottom",{"length":15}],["3 Vallees top",{"length":6}]],
        "3 Vallees top": [["3 Vallees bottom",{"length":5}],["Plein Sud top",{"length":4}]],
        "Pionniers bottom": [["Plein Sud bottom",{"length":10}],["Pionniers top",{"length":4}]],
        "Pionniers top": [["3 Vallees bottom",{"length":1}]]
        }
}"""

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
    
    def _construct_example_ski_resort(self):
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

        return example

    def generate_route(self):

        ski_resorts_data = self._construct_example_ski_resort()

        valid = None
        while valid == None:
            length = input("How long do you want to ski for (hh:mm): ")

            if int(length[length.index(":")+1:]) < 60 and re.match(r'^\d{2}:\d{2}$', length):
                valid = True

        ski_resort = ""
        while ski_resort not in ski_resorts_data.resorts.keys():
            ski_resort = input(f"Which ski resort are you in: ({', '.join(ski_resorts_data.resorts.keys())})\n")

        start = ""
        while start not in ski_resorts_data.resorts[ski_resort].nodes.keys():
            start = input(f"From what lift do you want to start your route: ({', '.join(ski_resorts_data.resorts[ski_resort].nodes.keys())})\n")

        start_time = "00:00"
        start_time = input("At what time do you want to start your route (hh:mm): ") #ADD VALIDATION - between opening and closing times + right format

        route, returned_to_start = Plan_route(ski_resorts_data.resorts[ski_resort], start, length, start_time).get_route() #Returns a list of dictionaries containing the node moved to and the time elapsed

        for i in range(len(route)-1):
            if route[i+1]["pause"] == True:
                print(f"{i+1}. Break for {route[i+1]["time_elapsed"]} minutes due to ski lifts not yet being open - {self._add_times(start_time,route[i+1]["time_elapsed"])}")
            else:
                print(f"{i+1}. {route[i]['start']} to {route[i+1]['start']} taking {route[i+1]['time_elapsed']-route[i]['time_elapsed']} minutes - {self._add_times(start_time,route[i+1]['time_elapsed'])}")

        if not returned_to_start:
            print(f"Your route could not return to the starting point in the time that you wanted to ski for due to ski lift closing times.")

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

#TESTING
if __name__ == "__main__":
    ui = Terminal()
    ui.generate_route()

