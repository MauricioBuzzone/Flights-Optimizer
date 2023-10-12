# Flights-Optimizer
Sistemas Distribuidos I (75.74):  TP Escalabilidad: Middleware y Coordinación de Procesos

## Cómo correr el programa

### Paso 1) System Config
Para cambiar la configuración del sistema (cantidad de workers, logging) se tiene un archivo de configuración `config.py` con el siguiente formato:

```
# Configuration
AMOUNT_OF_AIRPORT_HANDLER = 3
AMOUNT_OF_QUERY1_HANDLER = 1
AMOUNT_OF_QUERY3_WORKERS = 2
AMOUNT_OF_QUERY4_WORKERS = 3
LOGGING_LEVEL = 'ERROR'
```

Una vez realizado un cambio en el archivo de configuración, es necesario correr el siguiente script para crearlo:

```
python3 set_up_docker_compose.py
```

### Paso 2) Middleware Setup
Antes de correr el sistema es necesario asegurar que el middleware está funcionando correctamente, para ello usando el archivo Make hay que correr el siguiente comando:

```
make docker-compose-middleware-up
```

Y esperar que aparezca la siguiente información en la consola:

```
middleware-rabbitmq-1  | 2023-10-12 21:55:37.433712+00:00 [info] <0.678.0> Server startup complete; 4 plugins started.
middleware-rabbitmq-1  | 2023-10-12 21:55:37.433712+00:00 [info] <0.678.0>  * rabbitmq_prometheus
middleware-rabbitmq-1  | 2023-10-12 21:55:37.433712+00:00 [info] <0.678.0>  * rabbitmq_management
middleware-rabbitmq-1  | 2023-10-12 21:55:37.433712+00:00 [info] <0.678.0>  * rabbitmq_web_dispatch
middleware-rabbitmq-1  | 2023-10-12 21:55:37.433712+00:00 [info] <0.678.0>  * rabbitmq_management_agent
```

### Paso 3) System Setup

##### Paso 3.1) Client Config
Para elegir el archivo que lee el cliente, dónde guardará los resultados y otros parámetros, se provee el archivo `client/config.ini`, con la siguiente información

```
[DEFAULT]
SERVER_PORT = 12345
SERVER_IP = ClientHandler
RESULT_PORT = 12345
RESULT_IP = ResultHandler
LOGGING_LEVEL = INFO
CHUNK_SIZE_AIRPORT = 250
CHUNK_SIZE_FLIGHT = 800
AIRPORT_PATH = airports-codepublic.csv
FLIGHT_PATH = itineraries_random_2M.csv
RESULTS_PATH = results.csv
```

El archivo de aeropuertos es `AIRPORT_PATH` y el de vuelos es `FLIGHT_PATH`. Cambiar dichos parámetros en caso de querer probar otros archivos.

##### Paso 3.2) System Run
Para correr el sistema, desde otra terminal correr el siguiente comando:

```
make docker-compose-up
```

Se comenzará a leer el archivo de aeropuertos y vuelos, y se enviarán al sistema para ser procesados. Una vez finalizado el procesamiento será informada por medio de la terminal. Los resultados se obtendrán utilizando un esquema de polling y se imprimirán por pantalla. Además, los resultados serán guardados en un volumen en `/client/results.csv` para un fácil acceso sin necesidad de ingresar al container.

### Paso 4) System Shutdown
Si bien los programas se cierran de manera automática una vez finalizado el procesamiento, el sistema cerrará por completo una vez ejecutado el comando:
```
make docker-compose-down
```