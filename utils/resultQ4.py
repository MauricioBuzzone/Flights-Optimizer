class ResultQ4:
    def __init__(self, origin: str, destiny: str, fare_avg: float, fare_max: float, n: int):
        self.origin = origin
        self.destiny = destiny
        self.fare_avg = fare_avg
        self.fare_max = fare_max
        self.n = n

    def update_fare(self, new_fare: float):
        self.fare_avg = (self.fare_avg*self.n + new_fare) / (self.n + 1)
        self.fare_max = max(self.fare_max, new_fare)
        self.n += 1

    def merge(self, other):
        self.fare_avg = (self.fare_avg * self.n + other.fare_avg * other.n) / (self.n + other.n)
        self.fare_max = max(self.fare_max, other.fare_max)
        self.n += other.n

    def __str__(self):
        return f'ResultQ4(journey: {self.origin}-{self.destiny}, avg: {self.fare_avg}, max:{self.fare_max}, n:{self.n})'

    def __repr__(self):
        return self.__str__()