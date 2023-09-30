import socket
import logging
import csv
from ProtocolHandler import ProtocolHandler
from airport import Airport

class Client:
    def __init__(self, port, ip, airport_path):
        # Initialize server socket
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.connect((ip, port))
        self.protocolHandler = ProtocolHandler(self.socket)
        self.airport_path = airport_path

    def run(self):
        # Read airports.csv and send to the system.
        self.send_airports()
        self.protocolHandler.close()

    def send_airports(self):
        # opening the CSV file
        with open(self.airport_path, mode ='r') as file:
            csvFile = csv.reader(file,delimiter=';')
            next(csvFile, None)  # skip the headers
            for line in csvFile:
                airport = Airport(cod=line[0], latitude=float(line[5]), longitude=float(line[6]))

                logging.info(f'action: send | airport: {airport} | result: in_progress')
                self.protocolHandler.send_airport(airport)
                logging.info(f'action: send | airport: {airport} | result: success')