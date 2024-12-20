from math import inf
import math
from abc import ABC, abstractmethod

######################################################################################################################################################
# GROUP A Skill: Complex user-defined use of a object-orientated programming model e.g. classes, inheritance, composition, polymorphism and interfaces
######################################################################################################################################################
class Ski_resorts():
    def __init__(self):
        #############################
        # GROUP B Skill: Dictionaries
        #############################
        self.__resorts = {}
    
    def add_resort(self,name):
        self.__resorts[name] = Ski_resort(name)
    
    @property
    def resorts(self):
        return self.__resorts

class Ski_resort():
    def __init__(self,name):
        self.__name = name
        self.__nodes = {}
        self.__time = "00:00"
        self.__amenity_names = []
        self.__ski_park_names = []
    
    def add_ski_node(self,name,altitude):
        self.__nodes[name] = Ski_node(name,altitude)
    
    def add_ski_park(self,name,altitude,length):
        self.__nodes[name] = Ski_park(name,altitude,length)
        self.__ski_park_names.append(name)
    
    def add_amenity(self,name,altitude,amenity_type):
        self.__nodes[name] = Amenity(name,altitude,amenity_type)
        self.__amenity_names.append(name)
    
    @property
    def name(self):
        return self.__name
    
    @property
    def amenity_names(self):
        return self.__amenity_names
    
    @property
    def ski_park_names(self):
        return self.__ski_park_names
    
    @property
    def nodes(self):
        return self.__nodes
    
    @property
    def time(self):
        return self.__time
    
    @time.setter
    def time(self,time):
        self.__time = time
    
    def node_number(self):
        return len(self.__nodes)

    ###############################################
    # GROUP B Skill: Simple user defined algorithms
    ###############################################
    def increment_time(self,mins):
        if mins > 0 and mins != inf:
            h1, m1 = self.__time.split(":")
            mins = int(m1) + mins
            hours = int(h1) + mins // 60
            mins = mins % 60
            if hours > 23:
                hours %= 24
            if len(str(hours)) == 1:
                hours = f"0{hours}"
            if len(str(mins)) == 1:
                mins = f"0{mins}"
            self.__time = f"{hours}:{mins}"
            self.check_open()

    ###############################################
    # GROUP B Skill: Simple user defined algorithms
    ###############################################
    def decrement_time(self,mins):
        if mins > 0 and mins != inf:
            h1, m1 = self.__time.split(":")
            hours = int(h1) - math.ceil((mins-int(m1)) / 60)
            mins = int(m1) - mins % 60
            if mins < 0:
                mins += 60
            if hours < 0:
                hours += 24
            if len(str(hours)) == 1:
                hours = f"0{hours}"
            if len(str(mins)) == 1:
                mins = f"0{mins}"
            self.__time = f"{hours}:{mins}"
            self.check_open()
    
    def compare_greater(self,t1,t2):
        #Is time t1 greater than time t2
        h1, m1 = t1.split(":")
        h2, m2 = t2.split(":")
        if int(h1) > int(h2):
            return True
        elif int(h1) == int(h2) and int(m1) > int(m2):
            return True
        else:
            return False
    
    def compare_greater_or_equal(self,t1,t2):
        #Is time t1 greater than or equal to time t2
        h1, m1 = t1.split(":")
        h2, m2 = t2.split(":")
        if int(h1) > int(h2):
            return True
        elif int(h1) == int(h2) and int(m1) >= int(m2):
            return True
        else:
            return False
    
    def check_open(self):
        for lift in self.__nodes.values():
            for run in lift.runs:
                if self.compare_greater(run.opening, self.__time) or self.compare_greater_or_equal(self.__time, run.closing):
                    run.length = inf
                else:
                    run.length = run.open_length
  
class Node():
    def __init__(self,name, altitude):
        self._name = name
        self._altitude = altitude
        self.__runs = []
        self.__node_type = "Node"
        self.__length = 0
        self.__amenity_type = "None"

    def add_run(self,name,length,opening,closing,lift,difficulty,lift_type):
        self.__runs.append(Run(name,length,opening,closing,lift,difficulty,lift_type))
    
    @property
    def runs(self):
        return self.__runs
    
    @property
    def name(self):
        return self._name

    @property
    def altitude(self):
        return self._altitude
    
    @altitude.setter
    def altitude(self,altitude):
        self._altitude = altitude
    
    @abstractmethod
    def __repr__(self):
        raise NotImplementedError
    
    @property
    def node_type(self):
        return self.__node_type
    
    @property
    def length(self):
        return self.__length
    
    @property
    def amenity_type(self):
        return self.__amenity_type

class Ski_node(Node):
    def __init__(self,name,altitude):
        super().__init__(name,altitude)
        self.__node_type = "Ski lift station"
    
    def __repr__(self):
        return f"Ski node '{self._name}' - Altitude: {self._altitude}m"
    
    @property
    def node_type(self):
        return self.__node_type
    
class Run():
    def __init__(self,name,length,opening,closing,lift,difficulty,lift_type):
        self._name = name
        self._length = length
        self._open_length = length
        self._opening = opening
        self._closing = closing
        self._lift = lift
        self._difficulty = difficulty
        self._lift_type = lift_type
    
    @property
    def name(self):
        return self._name
    
    @property
    def length(self):
        return self._length
    
    @length.setter
    def length(self,length):
        self._length = length
    
    @property
    def open_length(self):
        return self._open_length
    
    @property
    def opening(self):
        return self._opening
    
    @property
    def closing(self):
        return self._closing
    
    @property
    def lift(self):
        return self._lift
    
    @property
    def difficulty(self):
        return self._difficulty
    
    @property
    def lift_type(self):
        return self._lift_type

#Do these later
class Ski_park(Node):
    def __init__(self,name,altitude, length):
        super().__init__(name,altitude)
        self.__length = length
        self.__node_type = "Ski park"
    
    def __repr__(self):
        return f"Ski park of length {self.__length}m"
    
    @property
    def length(self):
        return self.__length

    @property
    def node_type(self):
        return self.__node_type

class Amenity(Node):
    def __init__(self,name,altitude, amenity_type):
        super().__init__(name,altitude)
        self.__amenity_type = amenity_type
        self.__node_type = "Amenity"
    
    def __repr__(self):
        return f"{self.__amenity_type}"
    
    @property
    def amenity_type(self):
        return self.__amenity_type
    
    @property
    def node_type(self):
        return self.__node_type