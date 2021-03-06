import socket
from queue import Queue
import traceback
import threading
from threading import Lock
from functools import partial
import time
import json
from multiprocessing.pool import ThreadPool
import logging


"""
Klasa rezprezentujaca pojedynczy semafor.
Sluzy do przechowywania semaforow w kolejce.
"""
class Semaphore:

    def __init__(self, name, pingOwner):
        self.queue = Queue(maxsize=0)
        self.pingOwnerThread = threading.Thread(target=pingOwner, args=(name,), daemon=True)
        self.end = False


"""
Klasa reprezentujaca klienta, ktory oczekuje 
na wejscie do sekcji krytycznej. Przechowuje
niezbedne informacje o kliencie jak adres i 
pomocnicza flage informujaca o dostepnosci klienta
"""
class WaitClient:

    def __init__(self, addr):
        self.addr = addr
        self.alive = True


"""
Klasa implementujaca metody sluzace do zarzadzania semaforami.
Wszystkie metody potrzebuja w argumentach wywolania socketa, 
na ktorym moga sie komunikowac z klientem. Ponadto klasa ta
implementuje metode odpowiedzialna za cykliczne wysylanie
komunikator PING do klientow bedacych wlascicielami semaforow
przechowywanych w tej klasie w celu weryfikacji ich dostepnosci.
"""
class Semaphores:

    TIMEOUT = 5
    CLIENT_PORT = 8080

    def __init__(self):
        self.semaphores = dict()

    def create(self, sock, name):
        result = "{\"type\":\"CREATE\""
        if name not in self.semaphores.keys():
            result += ",\"result\":\"CREATED\",\"sem_name\":\"%s\"" % (name,)
            self.semaphores.update({ name : Semaphore(name, partial(Semaphores.__pinging, self)) })
            self.semaphores[name].pingOwnerThread.start()
        else:
            result += ",\"result\":\"ERROR\",\"message\":\"Semaphore %s already exists\"" % (name,)
        return result + '}'

    def delete(self, sock, name):
        result = "{\"type\":\"DELETE\""
        if name in self.semaphores.keys():
            if self.semaphores[name].queue.empty():
                if not self.semaphores[name].pingOwnerThread.isAlive():
                    self.semaphores[name].end = True
                    self.semaphores[name].pingOwnerThread.join()
                self.semaphores.pop(name, None)
                result += ",\"result\":\"DELETED\",\"sem_name\":\"%s\"" % (name,)
            else:
                result += ",\"result\":\"ERROR\",\"message\":\"Semaphore %s is abandoned\"" % (name,)
        else:
            result += ",\"result\":\"ERROR\",\"message\":\"Semaphore %s doesn't exist\"" % (name,)
        return result + '}'

    def p(self, sock, name, clientAddr):
        logger = logging.getLogger('server')
        result = "{\"type\":\"LOCK\""
        client = clientAddr[:clientAddr.find(':')]
        if name in self.semaphores.keys():
            if client not in list(self.semaphores[name].queue.queue) or client != self.semaphores[name].queue.queue[0].addr:
                if not self.semaphores[name].queue.empty():
                    self.semaphores[name].queue.put(WaitClient(client))
                    wait = "{\"type\":\"LOCK\",\"result\":\"WAIT\",\"sem_name\":\"%s\"}" % (name,)
                    try:
                        sock.settimeout(Semaphores.TIMEOUT)
                        sock.send(bytes(wait, 'ascii'))
                        time.sleep(1)
                        ping = "{\"type\":\"PING\",\"sem_name\":\"%s\"}" % (name,)
                        while self.semaphores[name].queue.queue[0].addr != client:
                            sock.send(bytes(ping, 'ascii'))

                            received_msg = ''
                            while '}' not in received_msg:
                                received_msg += str(sock.recv(1024), 'ascii')

                            data = json.loads(received_msg)
                            if data['type'] == 'PONG':
                                logger.info("Wait {}".format(data))
                                time.sleep(1)
                            else:
                                raise socket.timeout
                    except (socket.timeout, json.JSONDecodeError):
                        logger.info(traceback.format_exc())
                        i = 0
                        while self.semaphores[name].queue.queue[i].addr != client:
                            i += 1
                        self.semaphores[name].queue.queue[i].alive = False
                        return None
                else:
                    self.semaphores[name].queue.put(WaitClient(client))
            result += ",\"result\":\"ENTER\",\"sem_name\":\"%s\"" % (name,)
        else:
            result += ",\"result\":\"ERROR\",\"message\":\"Semaphore %s doesn't exist\"" % (name,)
        return result + '}'

    def v(self, sock, name, clientAddr):
        client = clientAddr[:clientAddr.find(':')]
        logger = logging.getLogger('server')
        result = "{\"type\":\"UNLOCK\""
        if name in self.semaphores.keys():
            if not self.semaphores[name].queue.empty() and client == self.semaphores[name].queue.queue[0].addr:
                self.semaphores[name].queue.get_nowait()
            while not self.semaphores[name].queue.empty() and not self.semaphores[name].queue.queue[0].alive:
                self.semaphores[name].queue.get_nowait()
            result += ",\"result\":\"UNLOCKED\",\"sem_name\":\"%s\"" % (name,)
        else:
            result += ",\"result\":\"ERROR\",\"message\":\"Semaphore %s doesn't exist\"" % (name,)
        return result + '}'

    def getAwaiting(self, sock, name):
        result = "{\"type\":\"GET_AWAITING\""
        empty = True
        if name in self.semaphores.keys():
            result += ",\"result\":\"AWAITING\",\"sem_name\":\"%s\",\"message\":[" % (name,)
            waiting = list(self.semaphores[name].queue.queue)
            if len(waiting) > 0:
                empty = False
            for cl in waiting:
                result += "\"{}\",".format(cl.addr)

            if empty:
                result += "]"
            else:
                result = result[:-1] + "]"
        else:
            result += ",\"result\":\"ERROR\",\"message\":\"Semaphore %s doesn't exist\"" % (name,)

        return result + '}'

    def __pinging(self, name):
        logger = logging.getLogger('server')
        ping = "{\"type\":\"PING\",\"sem_name\":\"%s\"}" % (name,)

        while True:
            try:
                if self.semaphores[name].end:
                   break
            except KeyError:
                return

            addr = None
            try:
                while addr is None:
                    clientQueue = list(self.semaphores[name].queue.queue)
                    if len(clientQueue) > 0:
                        addr = clientQueue[0].addr
                        # logger.info("First client on semaphore {} address {}".format(name, addr))
            except KeyError:
                return
            else:
                try:
                    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
                        sock.settimeout(Semaphores.TIMEOUT)
                        try:
                            sock.connect((addr, Semaphores.CLIENT_PORT))
                            sock.send(bytes(ping, 'ascii'))
                        except ConnectionRefusedError:
                            logger.info("Client {} disconnected".format(addr))
                            if not self.semaphores[name].queue.empty() and addr == self.semaphores[name].queue.queue[0].addr:
                                self.semaphores[name].queue.get_nowait()
                        else:
                            try:
                                received_msg = ''
                                while '}' not in received_msg:
                                    received_msg += str(sock.recv(1024), 'ascii')
                                data = json.loads(received_msg)
                                logger.info("Inside {}".format(data))
                                if data['type'] != "PONG":
                                    if not self.semaphores[name].queue.empty() and addr == self.semaphores[name].queue.queue[0].addr:
                                        self.semaphores[name].queue.get_nowait()
                            except json.JSONDecodeError:
                                if not self.semaphores[name].queue.empty() and addr == self.semaphores[name].queue.queue[0].addr:
                                    self.semaphores[name].queue.get_nowait()
                except socket.timeout:
                    logger.info("Client {} disconnected".format(addr))
                    if not self.semaphores[name].queue.empty() and addr == self.semaphores[name].queue.queue[0].addr:
                        self.semaphores[name].queue.get_nowait()
            finally:
                time.sleep(1)
