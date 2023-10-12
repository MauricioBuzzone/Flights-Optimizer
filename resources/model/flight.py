from model.duration import Duration

class Flight:
    def __init__(self, id:int, origin:str, destiny:str, total_distance: int,
                       total_fare:float, legs:list, flight_duration: Duration):
        self.id = id
        self.origin = origin
        self.destiny = destiny
        self.total_distance = total_distance
        self.total_fare = total_fare
        self.legs = legs
        self.flight_duration = flight_duration

    def is_fastest_than(self, other):
        my_duration = self.flight_duration.hours*60 + self.flight_duration.minutes
        other_duration = other.flight_duration.hours*60 + other.flight_duration.minutes
        return my_duration < other_duration

    def __repr__(self):
        return f'Flight(id: {self.id}, origin: {self.origin}, destiny: {self.destiny})'
    def __str__(self):
        return f'Flight(id: {self.id}, origin: {self.origin}, destiny: {self.destiny})'