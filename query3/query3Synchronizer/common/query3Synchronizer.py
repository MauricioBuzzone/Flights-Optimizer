from utils.worker import Worker
from middleware.middlewareQE import MiddlewareQE
from utils.resultQ3Serializer import ResultQ3Serializer

class Query3Synchronizer(Worker):
    def __init__(self, chunk_size):
        in_serializer = ResultQ3Serializer()
        out_serializer = ResultQ3Serializer()
        middleware = MiddlewareQE(in_queue_name='Q3-sync',
                                  exchange='results',
                                  tag='Q3')
        super().__init__(middleware=middleware,
                         in_serializer=in_serializer,
                         out_serializer=out_serializer,
                         peers=1,
                         chunk_size=chunk_size)

    def work(self, input):
        result = input
        journey = (result.fastest_flight.origin, result.fastest_flight.destiny)
        if journey in self.results:
            self.results[journey].merge(result)
        else:
            self.results[journey] = result