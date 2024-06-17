from Ui import Ui
from Ski_resorts import ski_resorts #HOW AM I IMPORTING THIS
    
class Terminal(Ui):
    
    def run(self):
        length = int(input("How long do you want to ski for (hours.mins): ")) #VALIDATE
        print("Possible ski resorts: ")
