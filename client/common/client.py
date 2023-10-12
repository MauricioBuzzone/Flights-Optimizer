import socket
import logging
import csv
import re
import os

import time

from model.flight import Flight
from model.airport import Airport
from model.duration import Duration

from utils.TCPHandler import SocketBroken
from utils.protocolHandler import ProtocolHandler

LEG_ID = 0; DURATION = 6; TOTAL_FARE = 12; DISTANCE = 14;
STARTING_AIRPORT = 3; DESTINATION_AIRPORT = 4;
SEGMENTS_DEPARTURE_COD = 20;

AIRPORT_COD = 0;AIRPORT_LAT = 5;AIRPORT_LON = 6

MAX_TIME_SLEEP = 8      # seconds
MIN_TIME_SLEEP = 1    # seconds
TIME_SLEEP_SCALE = 2    # 2 * t

class Client:
    def __init__(self, config_params):
        # Initialize server socket
        self.config = config_params
        self.airport_path = config_params["airport_path"]
        self.flight_path = config_params["flight_path"]

    def run(self):
        # Read airports.csv and send to the system.
        self.connect(self.config["ip"], self.config["port"])
        self.send_airports()

        # Read flights.csv and send to the system.
        self.send_flights()
        self.disconnect()

        # poll results
        self.connect(self.config["results_ip"], self.config["results_port"])
        self.poll_results()
        self.disconnect()

        logging.info(f'action: closing client')

    def connect(self, ip, port):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.connect((ip, port))
        self.protocolHandler = ProtocolHandler(self.socket)

    def disconnect(self):
        self.socket.close()

    def save_results(self, results):
        for result in results:
            logging.info(f'result: {result}')

    def poll_results(self):
        keep_running = True
        t_sleep = MIN_TIME_SLEEP
        while keep_running:
            logging.debug('action: polling | result: in_progress')
            t, value = self.protocolHandler.poll_results()
            if self.protocolHandler.is_result_wait(t):
                logging.debug(f'action: polling | result: wait')
                time.sleep(t_sleep)
                t_sleep = min(TIME_SLEEP_SCALE*t_sleep, MAX_TIME_SLEEP)
            elif self.protocolHandler.is_result_eof(t):
                logging.debug(f'action: polling | result: eof')
                keep_running = False
            elif self.protocolHandler.is_results(t):
                logging.debug(f'action: polling | result: succes | len(results): {len(value)}')
                t_sleep = max(t_sleep/TIME_SLEEP_SCALE, MIN_TIME_SLEEP)
                self.save_results(value)
            else:
                logging.error(f'action: polling | result: fail | unknown_type: {t}')

    def send_flights(self):
        self.send_file(self.flight_path,
                       ',',
                       parser_flight,
                       self.config["chunk_size_flight"],
                       self.protocolHandler.send_flight,
                       self.protocolHandler.send_flight_eof
                       )
        
    def send_airports(self):
        self.send_file(self.airport_path,
                       ';',
                       parser_airport,
                       self.config["chunk_size_airport"],
                       self.protocolHandler.send_airport,
                       self.protocolHandler.send_airport_eof
                       )

    def send_file(self, path, delimiter, parser, chunk_size, send_message, send_eof):
        logging.info(f'action: send file | result: in_progress | path: {path}')
        try:
            file_size = os.path.getsize(path)
            cursor = 0
            with open(path, mode ='r') as file:
                file.readline()  # skip the headers
                batch = []
                while line := file.readline():
                    element = parser(line.split(delimiter))

                    batch.append(element)
                    if len(batch) == chunk_size:
                        send_message(batch)
                        batch = []
                        logging.info('action: read {} | progress: {:.2f}%'.format(
                            path, 100*(file.tell())/(file_size)
                        ))

                if batch:
                    send_message(batch)
                    logging.info('action: read {} | progress: {:.2f}%'.format(
                        path, 100*(file.tell())/(file_size)
                    ))
                send_eof()
        except (SocketBroken,OSError) as e:
            logging.error(f'action: send file | result: fail | error: {e}')
        else: 
            logging.info(f'action: send file | result: success | path: {path}')


def parser_airport(line):
    return Airport(cod=line[AIRPORT_COD], 
                   latitude=float(line[AIRPORT_LAT]), 
                   longitude=float(line[AIRPORT_LON]))

def parser_flight(line):
    hours, minutes = get_duration(line[DURATION])
    
    total_distance = 0
    if line[DISTANCE] != '':
        total_distance=int(line[DISTANCE])

    return Flight(id= line[LEG_ID],
                  origin=line[STARTING_AIRPORT],
                  destiny=line[DESTINATION_AIRPORT],
                  total_distance=total_distance, 
                  total_fare=float(line[TOTAL_FARE]),
                  legs=get_legs(line), 
                  flight_duration= Duration(hours,minutes))

def get_legs(line):
    return line[SEGMENTS_DEPARTURE_COD].split('||')[1:]

def get_duration(s):
    match = re.match(r'P(?:([0-9]+)D)?(?:T(?:([0-9]+)H)?(?:([0-9]+)M)?)?', s)
    
    if match:
        dias = int(match.group(1)) if match.group(1) else 0
        horas = int(match.group(2)) if match.group(2) else 0
        minutos = int(match.group(3)) if match.group(3) else 0
    
        return horas + dias*24, minutos
    else:
        return None
    
    ## Revisar si agregamos el dia a Duration
    if match:
        horas = int(match.group(1)) if match.group(1) else 0
        minutos = int(match.group(2)) if match.group(2) else 0
        return horas, minutos
    else:
        return None