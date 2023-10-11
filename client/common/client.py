import socket
import logging
import csv
import re

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

        # TODO: quitar
        time.sleep(5)

        # Read flights.csv and send to the system.
        self.send_flights()
        self.disconnect()

        # poll results
        self.connect(self.config["results_ip"], self.config["results_port"])
        self.poll_results()
        self.disconnect()

    def connect(self, ip, port):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.connect((ip, port))
        self.protocolHandler = ProtocolHandler(self.socket)

    def disconnect(self):
        self.socket.close()

    """
    def poll_results(self):
        keep_running = True
        while keep_running:
            results = self.protocolHandler.poll_results()
            if self.protocolHandler.is_wait(results):
            elif self.protocolHandler.is_eof(results):
            elif self.protocolHandler:
            else:
    """

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
            i = 0
            with open(path, mode ='r') as file:
                csvFile = csv.reader(file,delimiter=delimiter)
                next(csvFile, None)  # skip the headers
                batch = []
                for line in csvFile:
                    element = parser(line)

                    batch.append(element)
                    if len(batch) == chunk_size:
                        logging.info(f'lines sended: {100*i/2e6}%')
                        i += chunk_size                    
                        send_message(batch)
                        batch = []

                if batch:
                    logging.info(f'lines sended: {100*i/2e6}%')
                    i += len(batch)   
                    send_message(batch)
                send_eof()
        except (SocketBroken,OSError) as e:
            logging.error(f'action: send file | result: fail | error: {e}')
        else: 
            logging.info(f'action: send file | result: sucesfull | path: {path}')


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