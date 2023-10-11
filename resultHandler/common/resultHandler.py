import csv
import io
import logging
import signal
from utils.flightQ1Serializer import FlightQ1Serializer
from utils.flightQ2Serializer import FlightQ2Serializer
from utils.resultQ3Serializer import ResultQ3Serializer
from utils.resultQ4Serializer import ResultQ4Serializer
from utils.protocol import is_eof

from common.resultHandlerMiddleware import ResultHandlerMiddleware

class ResultHandler():
    def __init__(self):
        signal.signal(signal.SIGTERM, self.__handle_signal)
        self.serializers = {'Q1': FlightQ1Serializer(),
                            'Q2': FlightQ2Serializer(),
                            'Q3': ResultQ3Serializer(),
                            'Q4': ResultQ4Serializer(),}
        
        # last thing to do:
        self.middleware = ResultHandlerMiddleware()

    def run(self):
        logging.info(f'action: listen_results | result: in_progress')
        self.middleware.listen_results(self.save_results)
        logging.info(f'action: listen_results | result: success')

        self.middleware.start()
        self.middleware.stop()

    def save_results(self, results_raw, results_type):
        results = self.deserialize_result(results_raw, results_type)

        # TODO: tomar lock result.csv?
        with open(f'results{results_type}.csv', 'a', encoding='UTF8') as file:
            writer = csv.writer(file)

            for result in results:
                logging.info(f'action: receive_result | result: success | value: {result}')
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

    def deserialize_result(self, bytes_raw, type):
        reader = io.BytesIO(bytes_raw)
        results = self.serializers[type].from_chunk(reader)        
        if is_eof(bytes_raw):
            logging.info(f'action: recv EOF {type}| result: success')
        return results       
        
    def __handle_signal(self, signum, frame):
        logging.info(f'action: stop_handler | result: in_progress | signal {signum}')
        self.middleware.stop()
        logging.info(f'action: stop_handler | result: success')
