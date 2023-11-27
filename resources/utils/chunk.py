import uuid

class Chunk:
    def __init__(self, id, values, retried=False, workers=[], id_client=0):
        self.id = id
        self.id_client = uuid.UUID('b7656279-bbe3-41a3-8326-7a5979febcea')
        self.values = values
        self.retried = retried
        self.workers = list(set(workers))

    def add_worker(self, worker):
        if worker not in self.workers:
            self.workers.append(worker)