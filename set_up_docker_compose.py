# pip install yaml
import yaml
import argparse

from config import AMOUNT_OF_AIRPORT_HANDLER, AMOUNT_OF_QUERY1_HANDLER

def create_network():
    return {
        'external': 'true',
        'ipam': {
            'driver': 'default',
            'config': [{'subnet': '172.25.125.0/24'}],
        }
    }

def create_client():
    return {
        'container_name': 'client',
        'image': 'client:latest',
        'entrypoint': 'python3 /main.py',
        'environment': [
            'PYTHONUNBUFFERED=1',
            'LOGGING_LEVEL=INFO',
        ],
        'volumes': [
            './client/config.ini:/config.ini',
            './client/airports-codepublic.csv:/airports-codepublic.csv',
        ],
        'depends_on': [
            'clientHandler',
        ],
        'networks': [
            'middleware_testing_net',
        ],
        'restart': 'on-failure',
    }

def create_clientHandler():
    return {
        'container_name': 'clientHandler',
        'image': 'client_handler:latest',
        'entrypoint': 'python3 /main.py',
        'environment': [
            'PYTHONUNBUFFERED=1',
            'LOGGING_LEVEL=INFO',
        ],
        'volumes': [
            './clientHandler/config.ini:/config.ini',
        ],
        'depends_on':
            [f'airportHandler{i+1}' for i in range(AMOUNT_OF_AIRPORT_HANDLER)] + \
            [f'query1Handler{i+1}' for i in range(AMOUNT_OF_QUERY1_HANDLER)],
        'networks': [
            'middleware_testing_net',
        ],
        'restart': 'on-failure',
    }

def create_query1Handler(i):
    return {
        'container_name': f'query1Handler{i}',
        'image': 'query1_handler:latest',
        'entrypoint': 'python3 /main.py',
        'environment': [
            'PYTHONUNBUFFERED=1',
            'LOGGING_LEVEL=INFO',
        ],
        'volumes': [
            './query1Handler/config.ini:/config.ini',
        ],
        'depends_on': [
            'resultHandler',
        ],
        'networks': [
            'middleware_testing_net',
        ],
        'restart': 'on-failure',
    }

def create_airportHandler(i):
    return {
        'container_name': f'airportHandler{i}',
        'image': 'airport_handler:latest',
        'entrypoint': 'python3 /main.py',
        'environment': [
            'PYTHONUNBUFFERED=1',
            'LOGGING_LEVEL=INFO',
        ],
        'volumes': [
            './airportHandler/config.ini:/config.ini',
        ],
        'depends_on': [
            'resultHandler',
        ],
        'networks': [
            'middleware_testing_net',
        ],
        'restart': 'on-failure',
    }

def create_resultHandler():
    return {
        'container_name': 'resultHandler',
        'image': 'result_handler:latest',
        'entrypoint': 'python3 /main.py',
        'environment': [
            'PYTHONUNBUFFERED=1',
            'LOGGING_LEVEL=INFO',
        ],
        'volumes': [
            './resultHandler/config.ini:/config.ini',
        ],
        'networks': [
            'middleware_testing_net',
        ],
        'restart': 'on-failure',
    }

def create_file():
    config = {}
    config['version'] = '3.9'
    config['name'] = 'tp1'
    config['services'] = {}

    config['services']['client'] = create_client()
    config['services']['clientHandler'] = create_clientHandler()

    for i in range(AMOUNT_OF_AIRPORT_HANDLER):
        config['services'][f'airportHandler{i+1}'] = create_airportHandler(i+1)

    for i in range(AMOUNT_OF_QUERY1_HANDLER):
        config['services'][f'query1Handler{i+1}'] = create_query1Handler(i+1)

    config['services']['resultHandler'] = create_resultHandler()

    config['networks'] = {}
    config['networks']['middleware_testing_net'] = create_network()

    with open('docker-compose-dev.yaml', 'w') as file:
        yaml.dump(config, file)


if __name__ == '__main__':
    create_file()