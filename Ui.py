from abc import ABC, abstractmethod
#Implements the general form of user interface from which the GUI and Terminal are inherited

class Ui(ABC):

    @abstractmethod
    def menu(self): #An abstract method since any type of user interface must begin by displaying the menu. An error is raised if it is not implemented. Parameters: None. Return values: None.
        raise NotImplementedError