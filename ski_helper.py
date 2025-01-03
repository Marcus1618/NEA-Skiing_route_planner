from Terminal import Terminal
from GUI import Gui
from sys import argv

def usage(): #Prints the instructions on how to use the program to the terminal 
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