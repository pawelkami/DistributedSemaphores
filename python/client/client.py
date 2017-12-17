import socket
import select
import json
import traceback
import threading
from functools import partial


class Client:

    TIMEOUT = 10

    port = 10080

    def __init__(self):
        self.__startListen("localhost", 8080)
        # self.__sockSemName = dict()

    def __del__(self):
        self.__listener.join()

    def create(self, serverName, semName):
        ip = socket.gethostbyname(serverName)
        ip = "LOCALHOST"
        message = "{\"type\":\"CREATE\",\"sem_name\":\"%s\"}" % (semName,)

        self.__send(ip, message)

    # "{\"type\":\"LOCK\",\"sem_name\":\"A\"}"
    def lock(self, serverName, semName):
        ip = socket.gethostbyname(serverName)
        ip = "LOCALHOST"
        message = "{\"type\":\"LOCK\",\"sem_name\":\"%s\"}" % (semName,)

        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            sock.connect((ip, Client.port))
            sock.send(bytes(message, 'ascii'))

            try:
                data = json.loads(str(sock.recv(1024), 'ascii'))
            except json.JSONDecodeError:
                raise Exception("Internal server error")
            else:
                try:
                    if data['type'] == 'ENTER':
                        print("Received: {}".format(data))
                        return
                    elif data['type'] == 'WAIT':
                        port = sock.getsockname()[1]
                        # print(port)
                        sock.close()
                        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
                            sock.settimeout(Client.TIMEOUT)
                            sock.bind(('LOCALHOST', port))
                            try:
                                while True:
                                    sock.listen(1)
                                    conn, addr = sock.accept()
                                    response = None
                                    try:
                                        data = json.loads(str(conn.recv(1024), 'ascii'))
                                    except json.JSONDecodeError:
                                        response = "{ \"type\" : \"ERROR\"," \
                                                   "\"value\": \"Json decode error\"}"
                                    else:
                                        try:
                                            print("Received: {}".format(data))
                                            if data['type'] == "PING":
                                                response = "{\"type\":\"PONG\",\"sem_name\":\"%s\"}" % (data['sem_name'],)
                                            elif data['type'] == 'ENTER':
                                                break
                                        except:
                                            print(traceback.format_exc())
                                    finally:
                                        if response:
                                            conn.send(bytes(response, 'ascii'))
                            except socket.timeout as e:
                                raise e
                except socket.timeout as e:
                    raise e
                except Exception as e:
                    print(traceback.format_exc())

    # "{\"type\":\"UNLOCK\",\"sem_name\":\"A\"}"
    def unlock(self, serverName, semName):
        ip = socket.gethostbyname(serverName)
        ip = "LOCALHOST"
        message = "{\"type\":\"UNLOCK\",\"sem_name\":\"%s\"}" % (semName,)

        self.__send(ip, message)

    # "{\"type\":\"DELETE\",\"sem_name\":\"A\"}"
    def delete(self, serverName, semName):
        ip = socket.gethostbyname(serverName)
        ip = "LOCALHOST"
        message = "{\"type\":\"DELETE\",\"sem_name\":\"%s\"}" % (semName,)

        self.__send(ip, message)

    # "{\"type\":\"GET_AWAITING\",\"sem_name\":\"A\"}"
    def getAwaiting(self, serverName, semName):
        ip = socket.gethostbyname(serverName)
        ip = "LOCALHOST"
        message = "{\"type\":\"GET_AWAITING\",\"sem_name\":\"%s\"}" % (semName,)

        self.__send(ip, message)

    def __startListen(self, host, port):

        try:
            self.__listener = threading.Thread(target=partial(Client.__listen, self), args=(host, port, ), daemon=True)
            self.__listener.start()
        except:
            print(traceback.format_exc())

    def __send(self, ip, message):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            sock.connect((ip, Client.port))
            sock.send(bytes(message, 'ascii'))
            response = str(sock.recv(1024), 'ascii')

            try:
                print(json.loads(response)['type'])
            except:
                print(traceback.format_exc())
            else:
                print("Received: {}".format(response))
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
                    data = json.loads(str(conn.recv(1024), 'ascii'))
                except json.JSONDecodeError:
                    response = "{ \"type\" : \"ERROR\"," \
                               "\"value\": \"Json decode error\"}"
                else:
                    print("Received: {}".format(data))
                    try:
                        if data['type'] == "PING":
                            response = "{\"type\":\"PONG\",\"sem_name\":\"%s\"}" % (data['sem_name'],)

                    except KeyError as e:
                        print(traceback.format_exc())
                        response = "{ \"type\" : \"ERROR\"," \
                                   "\"value\": \"Json decode error\"}"
                    except:
                        print(traceback.format_exc())
                finally:
                    # print(data)
                    if response:
                        conn.send(bytes(response, 'ascii'))
