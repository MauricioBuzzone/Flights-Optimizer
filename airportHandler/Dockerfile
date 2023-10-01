FROM python-base:latest

RUN pip3 install geopy

COPY airportHandler /
COPY utils /
COPY model /

ENTRYPOINT ["/bin/sh"]