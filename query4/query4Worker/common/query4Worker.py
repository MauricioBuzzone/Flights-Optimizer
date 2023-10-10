from utils.queryWorker.queryWorker import QueryWorker
from utils.flightQ4Serializer import FlightQ4Serializer
from utils.resultQ4Serializer import ResultQ4Serializer
from utils.resultQ4 import ResultQ4

class Query4Worker(QueryWorker):
    def __init__(self, peers, chunk_size):
        in_queue_name = 'Q4-workers'
        in_serializer = FlightQ4Serializer()
        out_queue_name = 'Q4-sync'
        out_serializer = ResultQ4Serializer()
        super().__init__(peers, chunk_size, in_queue_name, in_serializer, out_queue_name, out_serializer)

    def work(self, input):
        flight = input
        journey = (flight.origin, flight.destiny)
        if journey in self.results:
            self.results[journey].update(flight.total_fare)
        else:
            self.results[journey] = ResultQ4(origin=flight.origin,
                                                destiny=flight.destiny,
                                                fare_avg=flight.total_fare,
                                                fare_max=flight.total_fare,
                                                n=1)