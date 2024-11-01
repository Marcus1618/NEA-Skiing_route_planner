from math import inf
import math

class Ski_resorts():
    def __init__(self):
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
        self._time = "00:00"
    
    def add_lift(self,name):
        self.__nodes[name] = Ski_node(name)
    
    @property
    def nodes(self):
        return self.__nodes
    
    @property
    def time(self):
        return self._time
    
    @time.setter
    def time(self,time):
        self._time = time
    
    def node_number(self):
        return len(self.__nodes)

    def increment_time(self,mins):
        if mins > 0 and mins != inf:
            h1, m1 = self._time.split(":")
            mins = int(m1) + mins
            hours = int(h1) + mins // 60
            mins = mins % 60
            if hours > 23:
                hours %= 24
            if len(str(hours)) == 1:
                hours = f"0{hours}"
            if len(str(mins)) == 1:
                mins = f"0{mins}"
            self._time = f"{hours}:{mins}"
            self.check_open()

    
    def decrement_time(self,mins):
        if mins > 0 and mins != inf:
            h1, m1 = self._time.split(":")
            mins = int(m1) - mins
            hours = math.ceil(int(h1) - mins / 60)
            while mins < 0:
                mins += 60
            while hours < 0:
                hours += 24
            if len(str(hours)) == 1:
                hours = f"0{hours}"
            if len(str(mins)) == 1:
                mins = f"0{mins}"
            self._time = f"{hours}:{mins}"
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
                if self.compare_greater(run.opening, self._time) or self.compare_greater_or_equal(self._time, run.closing):
                    run.length = inf
                else:
                    run.length = run.open_length

    
class Node(): #Make abstract methods
    def __init__(self):
        pass

    def add(self):
        pass

    def remove(self):
        pass

class Ski_node(Node):
    def __init__(self,name):
        self._name = name
        self._runs = []
    
    def add_run(self,name,length,opening,closing):
        self._runs.append(Run(name,length,opening,closing))
    
    @property
    def runs(self):
        return self._runs
    
    @property
    def name(self):
        return self._name
    
class Run():
    def __init__(self,name,length,opening,closing):
        self._name = name
        self._length = length
        self._open_length = length
        self._opening = opening
        self._closing = closing
    
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



#Do these later
class Ski_park(Node):
    pass

class Amenity(Node):
    pass