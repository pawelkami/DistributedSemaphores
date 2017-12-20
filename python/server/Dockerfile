FROM python:3.6-alpine

# port for receiving messages
EXPOSE 8080

RUN mkdir /server

RUN apk --update add g++ linux-headers python3-dev

COPY requirements.txt /server
RUN pip3 install -r /server/requirements.txt

# Copy python files

COPY *.py /server/

# entrypoint sleep because docker-compose kills container after CMD is finished
# this line should be deleted after server implementation
# ENTRYPOINT sleep 100000000

CMD python3 /server/main.py
