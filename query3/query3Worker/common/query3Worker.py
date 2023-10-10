from utils.queryWorker.queryWorker import QueryWorker
from utils.flightQ1Serializer import FlightQ1Serializer
from utils.resultQ3Serializer import ResultQ3Serializer
from utils.resultQ3 import ResultQ3

class Query3Worker(QueryWorker):
    def __init__(self, peers, chunk_size):
        in_queue_name = 'Q3-workers'
        in_serializer = FlightQ1Serializer()
        out_queue_name = 'Q3-sync'
        out_serializer = ResultQ3Serializer()
        super().__init__(peers, chunk_size, in_queue_name, in_serializer, out_queue_name, out_serializer)

    def work(self, input):
        flight = input
        journey = (flight.origin, flight.destiny)
        if journey in self.results:
            self.results[journey].update(flight)
        else:
            self.results[journey] = ResultQ3(flight)