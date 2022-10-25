FROM alpine:3.16

RUN apk --no-cache add python3 py-pip py3-smbus

WORKDIR /
RUN pip3 install bme680 flask flask-httpauth prometheus_client waitress
COPY ./entrypoint.py /entrypoint.py

ENTRYPOINT ["python3" , "/entrypoint.py"]

