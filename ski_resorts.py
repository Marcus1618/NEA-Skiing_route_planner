class ski_resorts():
    def __init__(self):
        self.__resorts = {}
    
    def add_resort(self,name):
        self.__resorts[name] = ski_resort(name)
    
    @property
    def resorts(self):
        return self.__resorts


class ski_resort():
    def __init__(self,name):
        self.__name = name
        self.__nodes = {}
    
    def add_lift(self,name):
        self.__nodes[name] = ski_lift(name)
    
    @property
    def nodes(self):
        return self.__nodes
    

class node(): #Make abstract methods
    def __init__(self):
        pass

    def add(self):
        pass

    def remove(self):
        pass

class ski_lift(node):
    def __init__(self,name):
        self._name = name
        self._runs = []
    
    def add_run(self,name,length):
        self._runs.append(run(name,length))
    
    @property
    def runs(self):
        return self._runs
    
    @property
    def name(self):
        return self._name
    
class run():
    def __init__(self,name,length):
        self._name = name
        self._length = length
    
    @property
    def name(self):
        return self._name
    
    @property
    def length(self):
        return self._length



#Do these later
class ski_park(node):
    pass

class amenity(node):
    pass