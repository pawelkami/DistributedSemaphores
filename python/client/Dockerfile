FROM python:3.6-alpine

# port for receiving messages
EXPOSE 8080

RUN mkdir /client

RUN apk --update add g++ linux-headers python3-dev

COPY requirements.txt /client
RUN pip3 install -r /client/requirements.txt

# Copy python files

COPY *.py /client/

# entrypoint sleep because docker-compose kills container after CMD is finished
#ENTRYPOINT sleep 100000000
CMD sleep 15 & python3 /client/main.py & sleep 100000000
