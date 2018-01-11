import socket
import select
import json
import traceback
import threading
from functools import partial
import logging
import sys
import time
from ClientExceptions import ClientExceptions, AlreadyExistsException, DoesNotExistException, AbandonedException


class Client:

    TIMEOUT = 10
    CLIENT_PORT = 8080
    SERVER_PORT = 10080

    host = socket.gethostbyname(socket.gethostname())

    def __init__(self):
        self.logger = logging.getLogger('client')
        self.logger.setLevel(logging.DEBUG)
        fh = logging.FileHandler('/home/client.log')
        # fh = logging.StreamHandler(sys.stdout)
        fh.setLevel(logging.DEBUG)
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        fh.setFormatter(formatter)
        self.logger.addHandler(fh)
        self.__startListen(Client.host, Client.CLIENT_PORT)
        # self.__sockSemName = dict()

    def __del__(self):
        self.__listener.join()

    def create(self, semaphoreName):
        it = semaphoreName.find('.')
        serverName = semaphoreName[:it]
        semName = semaphoreName[it+1:]
        ip = socket.gethostbyname(serverName)
        message = "{\"type\":\"CREATE\",\"sem_name\":\"%s\"}" % (semName,)

        self.__send(ip, message)

    # "{\"type\":\"LOCK\",\"sem_name\":\"A\"}"
    def lock(self, semaphoreName):
        it = semaphoreName.find('.')
        serverName = semaphoreName[:it]
        semName = semaphoreName[it + 1:]
        ip = socket.gethostbyname(serverName)
        message = "{\"type\":\"LOCK\",\"sem_name\":\"%s\"}" % (semName,)

        self.logger.info("{}.{} -> {}".format(serverName, semName, ip))

        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            try:
                sock.settimeout(Client.TIMEOUT)
                sock.connect((ip, Client.SERVER_PORT))
                sock.send(bytes(message, 'ascii'))
            except socket.timeout as e:
                raise e

            data = None
            try:
                received_msg = ''
                while '}' not in received_msg:
                    received_msg += str(sock.recv(1024), 'ascii')
                self.logger.info(received_msg)
                data = json.loads(received_msg)
            except json.JSONDecodeError:
                self.logger.info("Inproper json {}".format(data))
                raise Exception("Internal server error")
            else:
                try:
                    self.logger.info("Received: {}".format(data))
                    if data['result'] == 'ENTER':
                        return
                    elif data['result'] == 'WAIT':
                        try:
                            while True:
                                response = None
                                try:
                                    received_msg = ''
                                    while '}' not in received_msg:
                                        received_msg += str(sock.recv(1024), 'ascii')
                                    data = json.loads(received_msg)
                                except json.JSONDecodeError:
                                    response = "{ \"result\" : \"ERROR\"," \
                                               "\"value\": \"Json decode error\"}"
                                else:
                                    try:
                                        self.logger.info("Received: {}".format(data))
                                        if data['type'] == "PING":
                                            response = "{\"type\":\"PONG\",\"sem_name\":\"%s\"}" % (data['sem_name'],)
                                        elif data['result'] == 'ENTER':
                                            break
                                        elif data['result'] == 'ERROR':
                                            ClientExceptions.castException(data['message'])
                                    except:
                                        self.logger.info(traceback.format_exc())
                                finally:
                                    if response:
                                        sock.send(bytes(response, 'ascii'))
                        except socket.timeout as e:
                            raise e
                    elif data['result'] == 'ERROR':
                        ClientExceptions.castException(data['message'])
                except socket.timeout as e:
                    raise e

    # "{\"type\":\"LOCK\",\"sem_name\":\"A\"}"
    def multiLock(self, semaphoresName):
        for semaphoreName in semaphoresName:
            self.lock(semaphoreName)

    # "{\"type\":\"UNLOCK\",\"sem_name\":\"A\"}"
    def unlock(self, semaphoreName):
        it = semaphoreName.find('.')
        serverName = semaphoreName[:it]
        semName = semaphoreName[it + 1:]
        ip = socket.gethostbyname(serverName)
        message = "{\"type\":\"UNLOCK\",\"sem_name\":\"%s\"}" % (semName,)

        self.__send(ip, message)

    # "{\"type\":\"DELETE\",\"sem_name\":\"A\"}"
    def delete(self, semaphoreName):
        it = semaphoreName.find('.')
        serverName = semaphoreName[:it]
        semName = semaphoreName[it + 1:]
        ip = socket.gethostbyname(serverName)
        message = "{\"type\":\"DELETE\",\"sem_name\":\"%s\"}" % (semName,)

        self.__send(ip, message)

    # "{\"type\":\"GET_AWAITING\",\"sem_name\":\"A\"}"
    def getAwaiting(self, semaphoreName):
        it = semaphoreName.find('.')
        serverName = semaphoreName[:it]
        semName = semaphoreName[it + 1:]
        ip = socket.gethostbyname(serverName)
        message = "{\"type\":\"GET_AWAITING\",\"sem_name\":\"%s\"}" % (semName,)

        self.__send(ip, message)

    def __startListen(self, host, port):

        try:
            self.__listener = threading.Thread(target=partial(Client.__listen, self), args=(host, port, ), daemon=True)
            self.__listener.start()
        except:
            self.logger.info(traceback.format_exc())

    def __send(self, ip, message):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            sock.settimeout(Client.TIMEOUT)
            sock.connect((ip, Client.SERVER_PORT))
            sock.send(bytes(message, 'ascii'))
            response = ''
            while '}' not in response:
                response += str(sock.recv(1024), 'ascii')

            try:
                response = json.loads(response)
                # self.logger.info(response['type'])
                if response['result'] == 'ERROR':
                    ClientExceptions.castException(response['message'])
            except socket.timeout:
                pass
            else:
                self.logger.info("Received: {}".format(response))
                return response

    def __listen(self, host, port):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            try:
                sock.bind((host, port))
            except OSError:
                return
            while True:
                sock.listen(5)
                conn, addr = sock.accept()
                response = None
                try:
                    received_msg = ''
                    while '}' not in received_msg:
                        received_msg += str(conn.recv(1024), 'ascii')
                    data = json.loads(received_msg)
                except json.JSONDecodeError:
                    self.logger.info(traceback.format_exc())
                else:
                    self.logger.info("Received: {}".format(data))
                    try:
                        if data['type'] == "PING":
                            response = "{\"type\":\"PONG\",\"sem_name\":\"%s\"}" % (data['sem_name'],)

                    except KeyError as e:
                        self.logger.info(traceback.format_exc())
                finally:
                    # print(data)
                    if response:
                        conn.send(bytes(response, 'ascii'))
