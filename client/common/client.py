import socket
import logging
import csv
from ProtocolHandler import ProtocolHandler
from airport import Airport

LEG_ID = 0; DURATION = 6; TOTAL_FARE = 12; DISTANCE = 14;
STARTING_AIRPORT = 3; DESTINATION_AIRPORT = 4;
SEGMENTS_DEPARTURE_COD = 20;

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
#        self.send_flights()
        self.protocolHandler.close()
        # poll results

    def get_legs(self, line):
        return line[SEGMENTS_DEPARTURE_COD].split('||')[1:]

    def send_flights(self):
        with open(self.flights_path, mode = 'r') as file:
            csvFile = csv.reader(file, delimiter=';')
            next(csvFile, None) # skip the headers
            flights = []
            for line in csvFile:
                flight = Flight(id= line[LEG_ID],
                    origin=line[STARTING_AIRPORT],destiny=line[DESTINATION_AIRPORT],
                    total_distance=line[DISTANCE], total_fare=line[TOTAL_FARE],
                    legs=self.get_legs(line), flight_duration=line[DURATION])

                flights.append(flight)
                if len(flights) == self.config["chunk_size"]:
                    self.protocolHandler.send_flight(flights)
                    flights = []
            if flights:
                self.protocolHandler.send_flight(flights)

            self.protocolHandler.eof()
            self.protocolHandler.wait_confimation()


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
            
            self.protocolHandler.eof()
            self.protocolHandler.wait_confimation()