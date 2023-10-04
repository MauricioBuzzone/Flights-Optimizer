FROM python:3.9.7-slim

COPY middleware /middleware
COPY utils /utils
COPY model /model
COPY test /

RUN pip install pika
RUN python -m unittest test_utils.py