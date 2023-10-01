import socket
import logging
import csv
from ProtocolHandler import ProtocolHandler
from airport import Airport

class Client:
    def __init__(self, config_params):
        # Initialize server socket
        self.config = config_params
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.connect((config_params["ip"], config_params["port"]))
        self.protocolHandler = ProtocolHandler(self.socket)
        self.airport_path = config_params["airport_path"]

    def run(self):
        # Read airports.csv and send to the system.
        self.send_airports()
        self.protocolHandler.close()

    def send_airports(self):
        # opening the CSV file
        with open(self.airport_path, mode ='r') as file:
            csvFile = csv.reader(file,delimiter=';')
            next(csvFile, None)  # skip the headers
            airports = []
            for line in csvFile:
                airport = Airport(cod=line[0], latitude=float(line[5]), longitude=float(line[6]))
                airports.append(airport)
                if len(airports) == self.config["chunk_size"]:
                    self.protocolHandler.send_airport(airports)
                    airports = []

            if airports:
                self.protocolHandler.send_airport(airports)

                
