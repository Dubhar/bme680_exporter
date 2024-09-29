FROM alpine:3.20

RUN apk --no-cache add python3 py3-pip py3-smbus

WORKDIR /usr/src/app
COPY requirements.txt requirements.txt
RUN python3 -m venv .venv && \
    . .venv/bin/activate && \
    pip3 install -r requirements.txt

COPY entrypoint.py entrypoint.py
ENTRYPOINT [".venv/bin/python3" , "entrypoint.py"]

