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

class ski_resorts():
    def __init__(self):
        self.__resorts = [ski_resort("Val Thorens")]

class ski_resort():
    def __init__(self,name):
        self.__name = name
        self.__lifts = []
        self.__parks = []
        self.__amenities = []
    

class node():
    def __init__(self,name):
        self.__name = name

    def add(self):
        pass

    def remove(self):
        pass

class ski_lift(node):
    def __init__(self,name):
        super().__init__(name)
    
    def add_adjacent(self):
        pass

class ski_park(node):
    pass

class amenity(node):
    pass