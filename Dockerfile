FROM alpine:3.18

WORKDIR /

RUN apk --no-cache add python3 py3-pip py3-smbus
COPY requirements.txt requirements.txt
RUN pip3 install -r requirements.txt

COPY ./entrypoint.py /entrypoint.py
ENTRYPOINT ["python3" , "/entrypoint.py"]

