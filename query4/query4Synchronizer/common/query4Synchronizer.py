from utils.worker import Worker
from middleware.middlewareQE import MiddlewareQE
from utils.serializer.resultQ4Serializer import ResultQ4Serializer

class Query4Synchronizer(Worker):
    def __init__(self, chunk_size):
        in_serializer = ResultQ4Serializer()
        out_serializer = ResultQ4Serializer()
        middleware = MiddlewareQE(in_queue_name='Q4-sync',
                                  exchange='results',
                                  tag='Q4')
        super().__init__(middleware=middleware,
                         in_serializer=in_serializer,
                         out_serializer=out_serializer,
                         peers=1,
                         chunk_size=chunk_size)

    def work(self, input):
        result = input
        journey = (result.origin, result.destiny)
        if journey in self.results:
            self.results[journey].merge(result)
        else:
            self.results[journey] = result