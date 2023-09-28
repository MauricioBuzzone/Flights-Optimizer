import socket
import logging
import csv

class Client:
    def __init__(self, port, ip, airport_path):
        # Initialize server socket
        # self._server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        # self._server_socket.bind((ip, port))
        self.airport_path = airport_path


    def run(self):
        # Read airports.csv and send to the system.
        self.send_airports()

    def send_airports(self):
        # opening the CSV file
        with open(self.airport_path, mode ='r') as file:
            csvFile = csv.reader(file,delimiter=';')
            for line in csvFile:
                cod = line[0]
                latitud = line[5]
                longitud = line[6]
                logging.info(f'action: read | airport: {cod,latitud,longitud}')

