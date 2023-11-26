import csv
import io
import logging
import signal
from utils.serializer.flightQ1Serializer import FlightQ1Serializer
from utils.serializer.flightQ2Serializer import FlightQ2Serializer
from utils.serializer.resultQ3Serializer import ResultQ3Serializer
from utils.serializer.resultQ4Serializer import ResultQ4Serializer
from utils.protocol import is_eof

from common.resultHandlerMiddleware import ResultHandlerMiddleware

class ResultReceiver():
    def __init__(self, file_name, file_lock):
        signal.signal(signal.SIGTERM, self.__handle_signal)
        self.serializers = {'Q1': FlightQ1Serializer(),
                            'Q2': FlightQ2Serializer(),
                            'Q3': ResultQ3Serializer(),
                            'Q4': ResultQ4Serializer(),}
        self.eofs = {'Q1': False, 'Q2': False, 'Q3': False, 'Q4': False}
        self.middleware = ResultHandlerMiddleware()
        self.file_lock = file_lock
        self.file_name = file_name

    def run(self):
        logging.debug(f'action: listen_results | result: in_progress')
        self.middleware.listen_results(self.save_results)
        logging.debug(f'action: listen_results | result: success')

        self.middleware.start()

    def save_results(self, results_raw, results_type):
        results = self.deserialize_result(results_raw, results_type)

        with self.file_lock, open(self.file_name, 'a', encoding='UTF8') as file:
            writer = csv.writer(file)

            for result in results:
                logging.debug(f'action: receive_result | result: success | value: {result}')
                if results_type == 'Q1':
                    legs = '-'.join(result.legs) # 'AAA-BBB-CCC'
                    writer.writerow(['Q1', result.id, result.origin, result.destiny, result.total_fare, legs])
                elif results_type == 'Q2':
                    writer.writerow(['Q2', result.id, result.origin, result.destiny, result.total_distance])
                elif results_type == 'Q3':
                    flight1 = result.fastest_flight
                    legs = '-'.join(flight1.legs) # 'AAA-BBB-CCC'
                    writer.writerow(['Q3', flight1.origin, flight1.destiny, flight1.id, legs, str(flight1.flight_duration)])
                    if result.second_fastest_flight:
                        flight2 = result.second_fastest_flight
                        legs = '-'.join(flight2.legs) # 'AAA-BBB-CCC'
                        writer.writerow(['Q3', flight2.origin, flight2.destiny, flight2.id, legs, str(flight2.flight_duration)])
                elif results_type == 'Q4':
                    journey = '-'.join([result.origin, result.destiny])
                    writer.writerow(['Q4', journey, result.fare_avg, result.fare_max])
                else:
                    continue

    def write_eof(self):
        with self.file_lock, open(self.file_name, 'a', encoding='UTF8') as file:
            writer = csv.writer(file)
            writer.writerow(['EOF'])
    
    def deserialize_result(self, bytes_raw, type):
        if is_eof(bytes_raw):
            self.eofs[type] = True
            logging.debug(f'action: recv EOF {type}| result: success')
            if all(self.eofs.values()):
                self.write_eof()
            return []

        reader = io.BytesIO(bytes_raw)
        idempotency_key, results = self.serializers[type].from_chunk(reader)

        return results

    def __handle_signal(self, signum, frame):
        logging.debug(f'action: stop_handler | result: in_progress | signal {signum}')
        self.middleware.stop()
        logging.debug(f'action: stop_handler | result: success')
