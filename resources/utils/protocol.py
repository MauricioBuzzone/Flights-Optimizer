import struct
import uuid

SIZE_LENGTH = 4

i = -1
def next():
    global i
    i+=1
    return i

class TlvTypes():
    # sizes
    SIZE_CODE_MSG = 4
    SIZE_UUID = 16
    SIZE_BOOL = 1
    SIZE_CLIENT_ID = 16
    CHUNK_WORKERS_ID_LENGTH = 1 # ADD UP TO 256 UNIQUE WORKERS PER CLUSTER

    # types
    EOF = next()
    WAIT = next()
    POLL = next()
    ACK = next()

    AIRPORT_CHUNK = next()
    AIRPORT = next()
    AIRPORT_COD = next()
    AIRPORT_LATITUDE = next()
    AIRPORT_LONGITUDE = next()

    FLIGHT_CHUNK = next()
    FLIGHT = next()
    FLIGHT_ID = next()
    FLIGHT_ORIGIN = next()
    FLIGHT_DESTINY = next()
    FLIGHT_DISTANCE = next()
    FLIGHT_FARE = next()
    FLIGHT_LEG = next()
    FLIGHT_DURATION_DAYS = next()
    FLIGHT_DURATION_HOURS = next()
    FLIGHT_DURATION_MINUTES = next()

    RESULT_Q4_CHUNK = next()
    RESULT_Q4 = next()
    RESULT_Q4_ORIGIN = next()
    RESULT_Q4_DESTINY = next()
    RESULT_Q4_FARE_AVG = next()
    RESULT_Q4_FARE_MAX = next()
    RESULT_Q4_N = next()

    RESULT_Q3_CHUNK = next()
    RESULT_Q3 = next()
    RESULT_Q3_ORIGIN = next()
    RESULT_Q3_DESTINY = next()
    RESULT_Q3_ID1 = next()
    RESULT_Q3_LEG1 = next()
    RESULT_Q3_DURATION1_HOURS = next()
    RESULT_Q3_DURATION1_MINUTES = next()
    RESULT_Q3_ID2 = next()
    RESULT_Q3_LEG2 = next()
    RESULT_Q3_DURATION2_HOURS = next()
    RESULT_Q3_DURATION2_MINUTES = next()

    LINE_CHUNK = next()
    LINE = next()
    LINE_RAW = next()

def is_eof(bytes):
    if len(bytes) == TlvTypes.SIZE_CODE_MSG:
        data = struct.unpack("!i",bytes)[0]
        return data == TlvTypes.EOF
    elif len(bytes) == TlvTypes.SIZE_CODE_MSG+SIZE_LENGTH:
        data, n = struct.unpack("!ii",bytes)
        return data == TlvTypes.EOF
    else:
        return False

def get_closed_peers(bytes):
    if len(bytes) == TlvTypes.SIZE_CODE_MSG + SIZE_LENGTH:
        data, n = struct.unpack("!ii", bytes)
        return n
    return -1

def make_wait():
    bytes = code_to_bytes(TlvTypes.WAIT)
    bytes += int.to_bytes(i, SIZE_LENGTH, 'big')
    return bytes

def make_eof(i = 0):
    bytes = code_to_bytes(TlvTypes.EOF)
    bytes += int.to_bytes(i, SIZE_LENGTH, 'big')
    return bytes

def generate_idempotency_key():
    return uuid.uuid4()

def code_to_bytes(code: int):
    return int.to_bytes(code, TlvTypes.SIZE_CODE_MSG, 'big')

def integer_to_bytes(i: int, code: int):
    bytes = code_to_bytes(code)
    bytes += int.to_bytes(SIZE_LENGTH, SIZE_LENGTH, 'big')
    bytes += int.to_bytes(i, SIZE_LENGTH, 'big')
    return bytes

def integer_from_bytes(bytes_i):
    return int.from_bytes(bytes_i, 'big')

def string_to_bytes(s: str, code: int):
    bytes = code_to_bytes(code)
    bytes_s = s.encode('utf-8')
    bytes += int.to_bytes(len(bytes_s), SIZE_LENGTH, 'big')
    bytes += bytes_s
    return bytes

def string_from_bytes(bytes_s):
    return bytes_s.decode('utf-8')

def float_to_bytes(f:float, code: int):
    bytes = code_to_bytes(code)
    bytes_f = struct.pack('!f', f)
    bytes += int.to_bytes(len(bytes_f), SIZE_LENGTH, 'big')
    bytes += bytes_f
    return bytes

def float_from_bytes(bytes_f):
    return struct.unpack('!f', bytes_f)[0]

def bool_to_bytes(b: bool):
    return bool.to_bytes(b, TlvTypes.SIZE_BOOL, 'big')

def bool_from_bytes(bytes_b):
    return bool.from_bytes(bytes_b, 'big')

def idempotency_key_to_bytes(ik):
    return ik.bytes

def idempotency_key_from_bytes(bytes_ik):
    return uuid.UUID(bytes=bytes_ik)

# Workers should be a list of integers (from 0 to 255)
def workers_to_bytes(workers: list):
    bytes_w = b''.join([int.to_bytes(i, TlvTypes.CHUNK_WORKERS_ID_LENGTH, 'big') for i in workers])
    raw = int.to_bytes(len(bytes_w), SIZE_LENGTH, 'big')
    raw += bytes_w
    return raw

def workers_from_bytes(bytes_w):
    if len(bytes_w) == 0:
        return []
    workers = []
    for i in range(0, len(bytes_w), TlvTypes.CHUNK_WORKERS_ID_LENGTH):
        w_i = int.from_bytes(bytes_w[i:i+TlvTypes.CHUNK_WORKERS_ID_LENGTH], 'big')
        workers.append(w_i)
    return workers

class UnexpectedType(Exception):
    pass