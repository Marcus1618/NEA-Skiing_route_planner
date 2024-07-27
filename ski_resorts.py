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

class ski_resorts():
    def __init__(self):
        self.__resorts = [ski_resort("Val Thorens")]
    
    def add_resort(self,name):
        self.__resorts.append(ski_resort(name))
    
    @property
    def resorts(self):
        return self.__resorts

class ski_resort():
    def __init__(self,name):
        self.__name = name
        self.__nodes = []
    
    def add_lift(self,name):
        self.__nodes.append(ski_lift(name))
    
    @property
    def nodes(self):
        return self.__nodes
    

class node(): #Make abstract methods
    def __init__(self,name):
        self._runs = []

    def add(self):
        pass

    def remove(self):
        pass

class ski_lift(node):
    def __init__(self,name,runs):
        self._name = name
        super().__init__(runs)
    
    def add_run(self,end_node,length):
        self._runs.append(run(end_node,length))
    
    @property
    def runs(self):
        return self._runs
    
class run():
    def __init__(self,end_node,length):
        self._end_node = end_node
        self._length = length
    
    @property
    def end_node(self):
        return self._end_node
    
    @property
    def length(self):
        return self._length



#Do these later
class ski_park(node):
    pass

class amenity(node):
    pass