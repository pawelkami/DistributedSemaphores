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


class Semaphore:

    def __init__(self, name, pingOwner):
        self.queue = Queue(maxsize=0)
        self.pingOwnerThread = threading.Thread(target=pingOwner, args=(name,), daemon=True)
        self.end = False

class WaitClient:

    def __init__(self, addr):
        self.addr = addr
        self.alive = True

class Semaphores:

    TIMEOUT = 10

    def __init__(self):
        self.semaphores = dict()

    def create(self, sock, name):
        result = None
        if name not in self.semaphores.keys():
            result = "{\"type\":\"CREATED\",\"sem_name\":\"%s\"}" % (name,)
            self.semaphores.update({ name : Semaphore(name, partial(Semaphores.__pinging, self)) })
            self.semaphores[name].pingOwnerThread.start()
        else:
            result = "{\"type\":\"ERROR\",\"message\":\"Semaphore %s already exists\"}" % (name,)
        return result

    def delete(self, sock, name):
        result = None
        if name in self.semaphores.keys():
            if self.semaphores[name].queue.empty():
                if not self.semaphores[name].pingOwnerThread.isAlive():
                    self.semaphores[name].end = True
                    self.semaphores[name].pingOwnerThread.join()
                self.semaphores.pop(name, None)
                result = "{\"type\":\"DELETED\",\"sem_name\":\"%s\"}" % (name,)
            else:
                result = "{\"type\":\"ERROR\",\"message\":\"Semaphore %s is abandoned\"}" % (name,)
        else:
            result = "{\"type\":\"ERROR\",\"message\":\"Semaphore %s doesn't exist\"}" % (name,)
        return result

    def p(self, sock, name, client):
        logger = logging.getLogger('server')
        result = None
        if name in self.semaphores.keys():
            if client not in list(self.semaphores[name].queue.queue):
                if not self.semaphores[name].queue.empty():
                    self.semaphores[name].queue.put(WaitClient(client))
                    wait = "{\"type\":\"WAIT\",\"sem_name\":\"%s\"}" % (name,)
                    try:
                        sock.settimeout(Semaphores.TIMEOUT)
                        sock.send(bytes(wait, 'ascii'))
                        ping = "{\"type\":\"PING\",\"sem_name\":\"%s\"}" % (name,)
                        while self.semaphores[name].queue.queue[0].addr != client:
                            sock.send(bytes(ping, 'ascii'))
                            data = json.loads(str(sock.recv(1024), 'ascii'))
                            if data['type'] == 'PONG':
                                logger.info("Wait {}".format(data))
                                time.sleep(1)
                            else:
                                raise socket.timeout
                    except (socket.timeout, json.JSONDecodeError):
                        i = 0
                        while self.semaphores[name].queue.queue[i].addr != client:
                            i += 1
                        self.semaphores[name].queue.queue[i].alive = False
                        return None
                else:
                    self.semaphores[name].queue.put(WaitClient(client))
            result = "{\"type\":\"ENTER\",\"sem_name\":\"%s\"}" % (name,)
        else:
            result = "{\"type\":\"ERROR\",\"message\":\"Semaphore %s doesn't exist\"}" % (name,)
        return result

    def v(self, sock, name, client):
        logger = logging.getLogger('server')
        result = None
        if name in self.semaphores.keys():
            it = client.index(':')
            if not self.semaphores[name].queue.empty() and client[:it] == self.semaphores[name].queue.queue[0].addr[:it]:
                self.semaphores[name].queue.get_nowait()
            while not self.semaphores[name].queue.empty() and not self.semaphores[name].queue.queue[0].alive:
                self.semaphores[name].queue.get_nowait()
            result = "{\"type\":\"UNLOCKED\",\"sem_name\":\"%s\"}" % (name,)
        else:
            result = "{\"type\":\"ERROR\",\"message\":\"Semaphore %s doesn't exist\"}" % (name,)
        return result

    def getAwaiting(self, sock, name):
        result = None
        empty = True
        if name in self.semaphores.keys():
            result = "{\"type\":\"AWAITING\",\"sem_name\":\"%s\",\"result\":[" % (name,)
            waiting = list(self.semaphores[name].queue.queue)
            if len(waiting) > 0:
                empty = False
            for cl in waiting:
                result += "\"{}\",".format(cl.addr)

            if empty:
                result += "]}"
            else:
                result = result[:-1] + "]}"
        else:
            result = "{\"type\":\"ERROR\",\"message\":\"Semaphore %s doesn't exist\"}" % (name,)

        return result

    def __pinging(self, name):
        logger = logging.getLogger('server')
        ping = "{\"type\":\"PING\",\"sem_name\":\"%s\"}" % (name,)
        while not self.semaphores[name].end:
            addr = None
            try:
                while addr is None:
                    clientQueue = list(self.semaphores[name].queue.queue)
                    if len(clientQueue) > 0:
                        addr = clientQueue[0].addr
                    # print("First client address {}".format(addr))
            except KeyError:
                raise Exception('Lack of semaphore {}'.format(name))
            else:
                try:
                    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
                        sock.settimeout(Semaphores.TIMEOUT)
                        it = addr.index(':')
                        try:
                            sock.connect((addr[:it], 8080))
                            sock.send(bytes(ping, 'ascii'))
                        except ConnectionRefusedError:
                            if not self.semaphores[name].queue.empty() and addr[:it] == self.semaphores[name].queue.queue[0].addr[:it]:
                                self.semaphores[name].queue.get_nowait()
                        else:
                            try:
                                data = json.loads(str(sock.recv(1024), 'ascii'))
                                logger.info("Inside {}".format(data))
                                if data['type'] != "PONG":
                                    if not self.semaphores[name].queue.empty() and addr[:it] == self.semaphores[name].queue.queue[0].addr[:it]:
                                        self.semaphores[name].queue.get_nowait()
                            except json.JSONDecodeError:
                                if not self.semaphores[name].queue.empty() and addr[:it] == self.semaphores[name].queue.queue[0].addr[:it]:
                                    self.semaphores[name].queue.get_nowait()
                except socket.timeout:
                    if not self.semaphores[name].queue.empty() and addr[:it] == self.semaphores[name].queue.queue[0].addr[:it]:
                        self.semaphores[name].queue.get_nowait()
            finally:
                time.sleep(1)
