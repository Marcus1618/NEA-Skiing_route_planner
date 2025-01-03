from ski_resorts import Ski_resorts, Ski_resort, Ski_node, Run
FILE_NAME = "saved_routes.txt"

def add_times(t1, t2): #Adds two times together where t1 is in the format hh:mm and t2 is just an integer number of minutes
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

###########################
# GROUP B Skill: Text files
###########################
def get_route_names(): #Returns a list of all the route names that have been saved
    route_names = []
    try:
        with open(FILE_NAME, "r") as f:
            route_data = f.read().split("\n\n")
            route_data.pop()
            for route in route_data:
                route_lines = route.split("\n")
                route_names.append(route_lines[0])
    except FileNotFoundError:
        pass
    return route_names

###############################################
# GROUP B Skill: Writing and reading from files
###############################################
def view_previous_route(route_name): #Fetches the route data and ski resort of the route for a specific route name
    output_route = []
    with open(FILE_NAME, "r") as f:
        route_data = f.read().split("\n\n")
        route_data.pop()
        for route in route_data:
            route_lines = route.split("\n")
            if route_lines[0] == route_name:
                for line in route_lines[2:]:
                    output_route.append(line)
    return output_route, route_lines[1] #Returns the route data as a list and the ski resort which the route is in

###############################################
# GROUP B Skill: Writing and reading from files
###############################################
def save_route(route_name, route, route_start_time, returned_to_start, ski_resort, ski_resort_object): #Saves the route data to a file in the format which it is displayed
    with open(FILE_NAME, "a") as f:
        f.write(f"{route_name}\n")
        f.write(f"{ski_resort}\n")        
        for i in range(len(route)-1):
                if route[i+1]["pause"] == True:
                    if i != 0:
                        f.write(f"{i+1}. Break for {route[i+1]["time_elapsed"]-route[i]["time_elapsed"]} minutes due to ski lifts not yet being open - {add_times(route_start_time,route[i+1]["time_elapsed"])}")
                    else:
                        f.write(f"{i+1}. Break for {route[i+1]["time_elapsed"]-route[i]["time_elapsed"]} minutes due to ski lifts not yet being open (route length increased by {route[i+1]["time_elapsed"]-route[i]["time_elapsed"]} minutes) - {add_times(route_start_time,route[i+1]["time_elapsed"])}")
                elif route[i+1]["break"] == True:
                    f.write(f"{i+1}. Break for {route[i+1]["time_elapsed"]-route[i]["time_elapsed"]} minutes at {route[i+1]["start"]} ({ski_resort_object.resorts[ski_resort].nodes[route[i+1]["start"]]}) - {add_times(route_start_time,route[i+1]["time_elapsed"])}")
                else: #add lift/run from x to y
                    f.write(f"{i+1}. {route[i+1]["lift"].title()} from {route[i]['start']} to {route[i+1]['start']} taking {route[i+1]['time_elapsed']-route[i]['time_elapsed']} minutes - {add_times(route_start_time,route[i+1]['time_elapsed'])}")

        if not returned_to_start:
            print(f"Your route could not return to the starting point in the time that you wanted to ski for due to ski lift closing times.\n")

        f.write("\n")