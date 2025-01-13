from Terminal import Terminal
from GUI import Gui
from sys import argv
#Determines if the program will run in the terminal or in a GUI and begins the program

def usage(): #Prints the instructions of how to start the program into the terminal. Parameters: None. Return values: None.
    print(f"""
Usage: {argv[0]} [g | t]
g : run in the GUI
t : run in the Terminal""")
    quit()

if __name__ == "__main__":
    if len(argv) != 2:
        usage()
    elif argv[1] == 'g':
        #Run in GUI
        ui = Gui()
    elif argv[1] == 't':
        #Run in Terminal
        ui = Terminal()
    else:
        usage()

    ui.menu()