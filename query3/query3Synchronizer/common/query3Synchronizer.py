from utils.querySynchronizer.querySynchronizer import QuerySynchronizer
from utils.resultQ3Serializer import ResultQ3Serializer

class Query3Synchronizer(QuerySynchronizer):
    def __init__(self, chunk_size):
        in_queue_name = 'Q3-sync'
        in_serializer = ResultQ3Serializer()
        tag_out = 'Q3'
        out_serializer = ResultQ3Serializer()
        super().__init__(chunk_size, in_queue_name, in_serializer, tag_out, out_serializer)

    def work(self, input):
        result = input
        journey = (result.fastest_flight.origin, result.fastest_flight.destiny)
        if journey in self.results:
            self.results[journey].merge(result)
        else:
            self.results[journey] = result