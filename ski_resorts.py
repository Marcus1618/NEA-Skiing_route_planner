from math import inf
import math
from abc import ABC, abstractmethod
#Defines the classes that make up the ski resort graph structure.

######################################################################################################################################################
# GROUP A Skill: Complex user-defined use of a object-orientated programming model e.g. classes, inheritance, composition, polymorphism and interfaces
######################################################################################################################################################
##################################################################
#Excellent coding style: Grouping of modules with a common purpose
##################################################################
class Ski_resorts(): #The object at the top of the graph hierarchy which stores a dictionary of key resort name and value the corresponding resort object.
    def __init__(self): #Initialises the resorts dictionary. Parameters: None. Return values: None.
        #############################
        # GROUP B Skill: Dictionaries
        #############################
        self.__resorts = {}
    
    def add_resort(self,name): #Adds a resort with a given name to the resorts dictionary. Parameters: name – String. Return values: None
        self.__resorts[name] = Ski_resort(name)
    
    @property
    def resorts(self): #The resorts dictionary getter method. Parameters: None. Return values: nodes – Dictionary
        return self.__resorts

class Ski_resort(): #A ski resort object with a collection of nodes
    def __init__(self,name): #Initialises the attributes required including a nodes dictionary with keys of node names and values of the corresponding node object. Parameters: None. Return values: None.
        self.__name = name
        self.__nodes = {}
        self.__time = "00:00"
        self.__amenity_names = []
        self.__ski_park_names = []
    
    def add_ski_node(self,name,altitude): #Adds a ski node to the ski resort
        self.__nodes[name] = Ski_node(name,altitude)
    
    def add_ski_park(self,name,altitude,length): #Adds a ski park to the ski resort
        self.__nodes[name] = Ski_park(name,altitude,length)
        self.__ski_park_names.append(name)
    
    def add_amenity(self,name,altitude,amenity_type): #Adds an amenity to the ski resort
        self.__nodes[name] = Amenity(name,altitude,amenity_type)
        self.__amenity_names.append(name)
    
    @property
    def name(self): #Getter for name
        return self.__name
    
    @property
    def amenity_names(self): #Getter for amenity names
        return self.__amenity_names
    
    @property
    def ski_park_names(self): #Getter for ski park names
        return self.__ski_park_names
    
    @property
    def nodes(self): #Getter for nodes
        return self.__nodes
    
    @property
    def time(self): #Getter for time
        return self.__time
    
    @time.setter
    def time(self,time): #Setter for time
        self.__time = time
    
    def node_number(self): #Returns the number of nodes in the ski resort
        return len(self.__nodes)

    ###############################################
    # GROUP B Skill: Simple user defined algorithms
    ###############################################
    def increment_time(self,mins): #Adds a time in minutes to the time attribute of ‘Ski_resort’ in ‘hh:mm’ format. 
        #Since the time has changed, ‘check_open’ is called to check if any runs have closed. Parameters: mins – Integer. Return values: None.
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
    def decrement_time(self,mins): #Minuses a time in minutes from the time attribute of ‘Ski_resort’ in ‘hh:mm’ format.
        #Since the time has changed, ‘check_open’ is called to check if any runs have closed. Parameters: mins – Integer. Return values: None.
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
    
    def compare_greater(self,t1,t2): #Compares if time t1 is greater than time t2 where both times are in ‘hh:mm’ format. Parameters: t1 – String, t2 – String. Return values: Boolean.
        #Is time t1 greater than time t2
        h1, m1 = t1.split(":")
        h2, m2 = t2.split(":")
        if int(h1) > int(h2):
            return True
        elif int(h1) == int(h2) and int(m1) > int(m2):
            return True
        else:
            return False
    
    def compare_greater_or_equal(self,t1,t2): #Compares if time t1 is greater than or equal to time t2 where both times are in ‘hh:mm’ format. Parameters: t1 – String, t2 – String. Return values: Boolean.
        #Is time t1 greater than or equal to time t2
        h1, m1 = t1.split(":")
        h2, m2 = t2.split(":")
        if int(h1) > int(h2):
            return True
        elif int(h1) == int(h2) and int(m1) >= int(m2):
            return True
        else:
            return False
    
    def check_open(self): #Determines if any of the runs would be closed at the time given by the attribute ‘time’ and changes their run length to infinity if they are closed.
        #If they aren’t closed, their length is returned to its open length. Parameters: None. Return values: None.
        for lift in self.__nodes.values():
            for run in lift.runs:
                if self.compare_greater(run.opening, self.__time) or self.compare_greater_or_equal(self.__time, run.closing):
                    run.length = inf
                else:
                    run.length = run.open_length
  
class Node(): #The general node class from which ‘Ski_node’, ‘Ski_park’ and ‘Amenity’ are inherited.
    def __init__(self,name, altitude): #Initialises the attributes including the list ‘runs’ which stores all of the run objects for the node. Parameters: name – String, altitude – Integer. Return values: None.
        self._name = name
        self._altitude = altitude
        self.__runs = []
        self.__node_type = "Node"
        self.__length = 0
        self.__amenity_type = "None"

    ################################################
    #Excellent coding style: Loosely coupled modules
    ################################################
    def add_run(self,name,length,opening,closing,lift,difficulty,lift_type): #Appends a run object to the list ‘runs’. Parameters: name – String, length – Integer, opening – String, closing – String, lift – Boolean, difficulty – String, lift_type – String. Return values: None.
        self.__runs.append(Run(name,length,opening,closing,lift,difficulty,lift_type))
    
    @property
    def runs(self): #Getter for runs
        return self.__runs
    
    @property
    def name(self): #Getter for name
        return self._name

    @property
    def altitude(self): #Getter for altitude
        return self._altitude
    
    @altitude.setter
    def altitude(self,altitude): #Setter for altitude
        self._altitude = altitude
    
    @abstractmethod
    def __repr__(self): #Abstract method requiring all inherited classes to be able to print a description of the class
        raise NotImplementedError
    
    @property
    def node_type(self): #Getter for node type
        return self.__node_type
    
    @property
    def length(self): #Length getter method. Allows the polymorphism of objects where this getter is only called if the inherited class does not have a length getter method itself. Parameters: None. Return values: length – Integer.
        return self.__length
    
    @property
    def amenity_type(self): #Getter for amenity type
        return self.__amenity_type

class Ski_node(Node): #A ski lift station node inherited from the node class
    def __init__(self,name,altitude): #Initialises the attributes from the parent class. Parameters: name – String, altitude – Integer. Return values: None.
        super().__init__(name,altitude)
        self.__node_type = "Ski lift station"
    
    def __repr__(self): #Prints a description of the ski lift station. Parameters: None. Return values: None.
        return f"Ski node '{self._name}' - Altitude: {self._altitude}m"
    
    @property
    def node_type(self): #Node_type getter method. This method is used instead of the inherited one of the same name if it is called by a ski_node. Parameters: None. Return values: node_type – String.
        return self.__node_type

################################################################################################################
#Excellent coding style: Modules with appropriate interfaces including suitable public and private method access
################################################################################################################
class Run(): #The lowest object in the graph data structure hierarchy.
    def __init__(self,name,length,opening,closing,lift,difficulty,lift_type): #Initialises the attributes. Parameters: name – String, length – Integer, opening – String, closing – String, lift – Boolean, difficulty – String, lift_type – String. Return values: None.
        #########################################################
        #Basic coding style: Meaningful variable identifier names
        #########################################################
        self._name = name
        self._length = length
        self._open_length = length
        self._opening = opening
        self._closing = closing
        self._lift = lift
        self._difficulty = difficulty
        self._lift_type = lift_type
    
    @property
    def name(self): #Getter for name
        return self._name
    
    @property
    def length(self): #Getter for length
        return self._length
    
    @length.setter
    def length(self,length): #Setter for length
        self._length = length
    
    @property
    def open_length(self): #Getter for open length
        return self._open_length
    
    @property
    def opening(self): #Getter for opening time
        return self._opening
    
    @property
    def closing(self): #Getter for closing time
        return self._closing
    
    @property
    def lift(self): #Getter for lift
        return self._lift
    
    @property
    def difficulty(self): #Getter for difficulty
        return self._difficulty
    
    @property
    def lift_type(self): #Getter for lift type
        return self._lift_type

class Ski_park(Node): #A ski park node inherited from the node class
    def __init__(self,name,altitude, length): #Initialises the attributes from the parent class. Parameters: name – String, altitude – Integer. Return values: None.
        super().__init__(name,altitude)
        self.__length = length
        self.__node_type = "Ski park"
    
    def __repr__(self): #Prints a description of the ski park
        return f"Ski park of length {self.__length}m"
    
    @property
    def length(self): #Getter for length
        return self.__length

    @property
    def node_type(self): #Getter for node type
        return self.__node_type

class Amenity(Node): #An amenity node inherited from the node class
    def __init__(self,name,altitude, amenity_type): #Initialises the attributes from the parent class. Parameters: name – String, altitude – Integer. Return values: None.
        super().__init__(name,altitude)
        self.__amenity_type = amenity_type
        self.__node_type = "Amenity"
    
    def __repr__(self): #Prints a description of the amenity. Parameters: None. Return values: None.
        return f"{self.__amenity_type}"
    
    @property
    def amenity_type(self): #Getter for amenity type
        return self.__amenity_type
    
    @property
    def node_type(self): #Getter for node type
        return self.__node_type