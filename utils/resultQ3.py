from model.duration import Duration
from model.flight import Flight

class ResultQ3:
    def __init__(self, flight1, flight2 = None):
        assert flight1, 'first flight must not be None'

        if flight1 and flight2:
            if flight1.is_fastest_than(flight2):
                self.fastest_flight = flight1
                self.second_fastest_flight = flight2
            else:
                self.fastest_flight = flight2
                self.second_fastest_flight = flight1
        else:
            self.fastest_flight = flight1
            self.second_fastest_flight = None

    def update(self, new_flight):
        if new_flight.is_fastest_than(self.fastest_flight):
            self.second_fastest_flight = self.fastest_flight
            self.fastest_flight = new_flight
        elif not self.second_fastest_flight or new_flight.is_fastest_than(self.second_fastest_flight):
            self.second_fastest_flight = new_flight


    def merge(self, other):
        self.update(other.fastest_flight)
        if other.second_fastest_flight:
            self.update(other.second_fastest_flight)
        return

    def __str__(self):
        return f'ResultQ3(flight1: {self.fastest_flight}, flight2: {self.second_fastest_flight})'

    def __repr__(self):
        return self.__str__()