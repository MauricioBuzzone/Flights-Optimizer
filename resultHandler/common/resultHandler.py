import csv
import io
import logging
import signal
from utils.flightQ1Serializer import FlightQ1Serializer
from utils.flightQ2Serializer import FlightQ2Serializer
from utils.resultQ4Serializer import ResultQ4Serializer
from utils.protocol import is_flight_eof

from common.resultHandlerMiddleware import ResultHandlerMiddleware

class ResultHandler():
    def __init__(self):
        self.flightQ1Serializer = FlightQ1Serializer()
        self.flightQ2Serializer = FlightQ2Serializer()
        self.resultQ4Serializer = ResultQ4Serializer()
        signal.signal(signal.SIGTERM, self.__handle_signal)

        # last thing to do:
        self.middleware = ResultHandlerMiddleware()

    def run(self):
        logging.info(f'action: listen_results | result: in_progress')
        self.middleware.listen_results(self.save_results)
        logging.info(f'action: listen_results | result: success')

        self.middleware.start()

        self.middleware.stop()
    
    def save_results(self, results_raw, results_type):
        reader = io.BytesIO(results_raw)
        if results_type == 'Q1':
            if is_flight_eof(results_raw):
                logging.info(f'action: recv EOF Query1| result: success ')
            results = self.flightQ1Serializer.from_chunk(reader)
        elif results_type == 'Q2':
            results = self.flightQ2Serializer.from_chunk(reader)
        elif results_type == 'Q3':
            results = [] # self.flightQ3Serializer.from_chunk(reader)
        elif results_type == 'Q4':
            results = self.resultQ4Serializer.from_chunk(reader)
        else:
            # unknown
            return

        # TODO: tomar lock result.csv?
        # PREG: un archivo por query? un mismo archivo? ???
        with open('results.csv', 'a', encoding='UTF8') as file:
            writer = csv.writer(file)

            for result in results:
                logging.info(f'action: receive_result | result: success | value: {result}')
                if results_type == 'Q1':
                    legs = '-'.join(result.legs) # 'AAA-BBB-CCC'
                    writer.writerow(['Q1', result.id, result.origin, result.destiny, result.total_fare, legs])
                elif results_type == 'Q2':
                    writer.writerow(['Q2', result.id, result.origin, result.destiny, result.total_distance])
                elif results_type == 'Q4':
                    journey = '-'.join([result.origin, result.destiny])
                    writer.writerow(['Q4', journey, result.fare_avg, result.fare_max])
                else: 
                    continue

    def __handle_signal(self, signum, frame):
        logging.info(f'action: stop_handler | result: in_progress | signal {signum}')
        self.middleware.stop()
        logging.info(f'action: stop_handler | result: success')
