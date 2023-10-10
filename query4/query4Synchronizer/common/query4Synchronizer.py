from utils.querySynchronizer.querySynchronizer import QuerySynchronizer
from utils.resultQ4Serializer import ResultQ4Serializer

class Query4Synchronizer(QuerySynchronizer):
    def __init__(self, chunk_size):
        in_queue_name = 'Q4-sync'
        in_serializer = ResultQ4Serializer()
        tag_out = 'Q4'
        out_serializer = ResultQ4Serializer()
        super().__init__(chunk_size, in_queue_name, in_serializer, tag_out, out_serializer)

    def work(self, input):
        result = input
        journey = (result.origin, result.destiny)
        if journey in self.results:
            self.results[journey].merge(result)
        else:
            self.results[journey] = result