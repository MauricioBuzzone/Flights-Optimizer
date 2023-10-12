FROM python:3.9.7-slim

COPY resources/middleware /middleware
COPY resources/utils /utils
COPY resources/model /model
COPY resources/test /

RUN pip install pika
RUN python -m unittest test_utils.py