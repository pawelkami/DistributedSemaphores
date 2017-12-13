import socket
import json
import traceback
import threading


class Client:

    port = 10080

    def __init__(self):
        self.__listen("localhost", 8080)

    # "{\"type\":\"CREATE\",\"sem_name\":\"A\"}"
    def create(self, serverName, semName):
        ip = socket.gethostbyname(serverName)
        ip = "LOCALHOST"
        message = "{\"type\":\"CREATE\",\"sem_name\":\"%s\"}" % (semName,)

        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            sock.connect((ip, Client.port))
            sock.sendall(bytes(message, 'ascii'))
            response = str(sock.recv(1024), 'ascii')

            try:
                print(json.loads(response)['type'])
            except:
                print(traceback.format_exc())
            print("Received: {}".format(response))

    # tutaj trzeba sie zablokowac na porcie i czekac az przyjdzie enter
    # oprocz tego odpowiadac na pingi pongami i samemu kontrolowac czy
    # pingi przychodza i jak nie to znaczy, ze serwer sie wysypal i wtedy
    # obsluzyc taka sytuacje
    # "{\"type\":\"LOCK\",\"sem_name\":\"A\"}"
    def lock(self, serverName, semName):
        pass

    # "{\"type\":\"UNLOCK\",\"sem_name\":\"A\"}"
    def unlock(self, serverName, semName):
        pass

    # "{\"type\":\"DELETE\",\"sem_name\":\"A\"}"
    def delete(self, serverName, semName):
        pass

    # "{\"type\":\"GET_AWAITING\",\"sem_name\":\"A\"}"
    def getAwaiting(self, serverName, semName):
        pass

    def __listen(self, host, port):
        pass
