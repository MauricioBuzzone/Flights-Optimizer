# pip install yaml
import yaml
import argparse

from config import AMOUNT_OF_AIRPORT_HANDLER, AMOUNT_OF_QUERY1_HANDLER
from config import AMOUNT_OF_QUERY4_WORKERS, AMOUNT_OF_QUERY3_WORKERS
from config import LOGGING_LEVEL

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
            f'LOGGING_LEVEL={LOGGING_LEVEL}',
        ],
        'volumes': [
            './client/config.ini:/config.ini',
            './client/airports-codepublic.csv:/airports-codepublic.csv',
            './client/itineraries_random_2M.csv:/itineraries_random_2M.csv',
            './client/results.csv:/results.csv',
        ],
        'depends_on': [
            'clientHandler',
        ],
        'networks': [
            'middleware_testing_net',
        ],
    }

def create_clientHandler():
    return {
        'container_name': 'clientHandler',
        'image': 'client_handler:latest',
        'entrypoint': 'python3 /main.py',
        'environment': [
            'PYTHONUNBUFFERED=1',
            f'LOGGING_LEVEL={LOGGING_LEVEL}',
        ],
        'volumes': [
            './clientHandler/config.ini:/config.ini',
        ],
        'depends_on':
            [f'airportHandler{i+1}' for i in range(AMOUNT_OF_AIRPORT_HANDLER)] + \
            [f'query1Handler{i+1}' for i in range(AMOUNT_OF_QUERY1_HANDLER)] + \
            ['query4Handler'],
        'networks': [
            'middleware_testing_net',
        ],
    }

def create_query1Handler(i):
    return {
        'container_name': f'query1Handler{i}',
        'image': 'query1_handler:latest',
        'entrypoint': 'python3 /main.py',
        'environment': [
            'PYTHONUNBUFFERED=1',
            f'LOGGING_LEVEL={LOGGING_LEVEL}',
            'PEERS='+str(AMOUNT_OF_QUERY1_HANDLER),
        ],
        'volumes': [
            './query1/query1Handler/config.ini:/config.ini',
        ],
        'depends_on': [
            'resultHandler',
        ],
        'networks': [
            'middleware_testing_net',
        ],
    }

def create_airportHandler(i):
    return {
        'container_name': f'query2Handler{i}',
        'image': 'query2_handler:latest',
        'entrypoint': 'python3 /main.py',
        'environment': [
            'PYTHONUNBUFFERED=1',
            f'LOGGING_LEVEL={LOGGING_LEVEL}',
            'PEERS='+str(AMOUNT_OF_AIRPORT_HANDLER),
        ],
        'volumes': [
            './query2/query2Handler/config.ini:/config.ini',
        ],
        'depends_on': [
            'resultHandler',
        ],
        'networks': [
            'middleware_testing_net',
        ],
    }

def create_query3Handler():
    return {
        'container_name': 'query3Handler',
        'image': 'query3_handler:latest',
        'entrypoint': 'python3 /main.py',
        'environment': [
            'PYTHONUNBUFFERED=1',
            f'LOGGING_LEVEL={LOGGING_LEVEL}',
        ],
        'volumes': [
            './query3/query3Handler/config.ini:/config.ini',
        ],
        'depends_on': [f'query3Worker{i+1}' for i in range(AMOUNT_OF_QUERY3_WORKERS)],
        'networks': [
            'middleware_testing_net',
        ],
    }

def create_query3Worker(i):
    return {
        'container_name': f'query3Worker{i}',
        'image': 'query3_worker:latest',
        'entrypoint': 'python3 /main.py',
        'environment': [
            'PYTHONUNBUFFERED=1',
            f'LOGGING_LEVEL={LOGGING_LEVEL}',
            'PEERS='+str(AMOUNT_OF_QUERY3_WORKERS),
        ],
        'volumes': [
            './query3/query3Worker/config.ini:/config.ini',
        ],
        'depends_on': [
            'query3Synchronizer',
        ],
        'networks': [
            'middleware_testing_net',
        ],
    }

def create_query3Synchronizer():
    return {
        'container_name': 'query3Synchronizer',
        'image': 'query3_synchronizer:latest',
        'entrypoint': 'python3 /main.py',
        'environment': [
            'PYTHONUNBUFFERED=1',
            f'LOGGING_LEVEL={LOGGING_LEVEL}',
        ],
        'volumes': [
            './query3/query3Synchronizer/config.ini:/config.ini',
        ],
        'depends_on': [
            'resultHandler',
        ],
        'networks': [
            'middleware_testing_net',
        ],
    }

def create_query4Handler():
    return {
        'container_name': 'query4Handler',
        'image': 'query4_handler:latest',
        'entrypoint': 'python3 /main.py',
        'environment': [
            'PYTHONUNBUFFERED=1',
            f'LOGGING_LEVEL={LOGGING_LEVEL}',
        ],
        'volumes': [
            './query4/query4Handler/config.ini:/config.ini',
        ],
        'depends_on': [f'query4Worker{i+1}' for i in range(AMOUNT_OF_QUERY4_WORKERS)],
        'networks': [
            'middleware_testing_net',
        ],
    }

def create_query4Worker(i):
    return {
        'container_name': f'query4Worker{i}',
        'image': 'query4_worker:latest',
        'entrypoint': 'python3 /main.py',
        'environment': [
            'PYTHONUNBUFFERED=1',
            f'LOGGING_LEVEL={LOGGING_LEVEL}',
            'PEERS='+str(AMOUNT_OF_QUERY4_WORKERS),
        ],
        'volumes': [
            './query4/query4Worker/config.ini:/config.ini',
        ],
        'depends_on': [
            'query4Synchronizer',
        ],
        'networks': [
            'middleware_testing_net',
        ],
    }

def create_query4Synchronizer():
    return {
        'container_name': 'query4Synchronizer',
        'image': 'query4_synchronizer:latest',
        'entrypoint': 'python3 /main.py',
        'environment': [
            'PYTHONUNBUFFERED=1',
            f'LOGGING_LEVEL={LOGGING_LEVEL}',
        ],
        'volumes': [
            './query4/query4Synchronizer/config.ini:/config.ini',
        ],
        'depends_on': [
            'resultHandler',
        ],
        'networks': [
            'middleware_testing_net',
        ],
    }

def create_resultHandler():
    return {
        'container_name': 'resultHandler',
        'image': 'result_handler:latest',
        'entrypoint': 'python3 /main.py',
        'environment': [
            'PYTHONUNBUFFERED=1',
            f'LOGGING_LEVEL={LOGGING_LEVEL}',
        ],
        'volumes': [
            './resultHandler/config.ini:/config.ini',
        ],
        'networks': [
            'middleware_testing_net',
        ],
    }

def create_file():
    config = {}
    config['version'] = '3.9'
    config['name'] = 'tp1'
    config['services'] = {}

    config['services']['client'] = create_client()
    config['services']['clientHandler'] = create_clientHandler()

    # query1
    for i in range(AMOUNT_OF_QUERY1_HANDLER):
        config['services'][f'query1Handler{i+1}'] = create_query1Handler(i+1)

    # query2
    for i in range(AMOUNT_OF_AIRPORT_HANDLER):
        config['services'][f'airportHandler{i+1}'] = create_airportHandler(i+1)

    # query3
    config['services']['query3Handler'] = create_query3Handler()
    for i in range(AMOUNT_OF_QUERY3_WORKERS):
        config['services'][f'query3Worker{i+1}'] = create_query3Worker(i+1)
    config['services']['query3Synchronizer'] = create_query3Synchronizer()

    # query4
    config['services']['query4Handler'] = create_query4Handler()
    for i in range(AMOUNT_OF_QUERY4_WORKERS):
        config['services'][f'query4Worker{i+1}'] = create_query4Worker(i+1)
    config['services']['query4Synchronizer'] = create_query4Synchronizer()

    config['services']['resultHandler'] = create_resultHandler()

    config['networks'] = {}
    config['networks']['middleware_testing_net'] = create_network()

    with open('docker-compose-dev.yaml', 'w') as file:
        yaml.dump(config, file)


if __name__ == '__main__':
    create_file()