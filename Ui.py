from abc import ABC, abstractmethod

class Ui(ABC):

    @abstractmethod
    def menu(self):
        raise NotImplementedError