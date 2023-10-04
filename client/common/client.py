import socket
import logging
import csv
import re

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
        self.connect()
        self.send_airports()

        # Read flights.csv and send to the system.
        self.send_flights()
        self.disconnect()

        # poll results

    def connect(self):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.connect((self.config["ip"], self.config["port"]))
        self.protocolHandler = ProtocolHandler(self.socket)

    def disconnect(self):
        self.socket.close()

    def send_flights(self):
        self.send_file(self.flight_path,
                       ',',
                       parser_flight,
                       self.protocolHandler.send_flight,
                       self.protocolHandler.send_flight_eof
                       )
        
    def send_airports(self):
        self.send_file(self.airport_path,
                       ';',
                       parser_airport,
                       self.protocolHandler.send_airport,
                       self.protocolHandler.send_airport_eof
                       )

    def send_file(self, path, delimiter, parser, send_message, send_eof):
        logging.info(f'action: send file | result: in_progress | path: {path}')
        try:
            with open(path, mode ='r') as file:
                csvFile = csv.reader(file,delimiter=delimiter)
                next(csvFile, None)  # skip the headers
                batch = []
                for line in csvFile:
                    element = parser(line)
                    batch.append(element)
                    if len(batch) == self.config["chunk_size"]: 
                        send_message(batch)
                        batch = []

                if batch:
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
    return Flight(id= line[LEG_ID],
                  origin=line[STARTING_AIRPORT],
                  destiny=line[DESTINATION_AIRPORT],
                  total_distance=int(line[DISTANCE]), 
                  total_fare=float(line[TOTAL_FARE]),
                  legs=get_legs(line), 
                  flight_duration= Duration(hours,minutes))

def get_legs(line):
    return line[SEGMENTS_DEPARTURE_COD].split('||')[1:]

def get_duration(s):
    match = re.match(r'PT(\d+)H(\d+)M', s)
    if match:
        horas = int(match.group(1))
        minutos = int(match.group(2))
        return horas, minutos
    else:
        return None