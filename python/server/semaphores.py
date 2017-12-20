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

# CREATE
# LOCK
# UNLOCK
# DELETE
# GET_AWAITING
# PONG
#
# CREATED
# WAIT
# ENTER
# ERROR
# AWAITING
# PING
#
# PROBE
#
# Klient - serwer:
# {
# “type”	:	“operation_name”,
# “sem_name”   	: 	“semaphore_name”,
#
# }
# Serwer - klient:
# {
# “type”	:	“operation_name”,
# “sem_name”   	: 	“semaphore_name”,
# “result”	:	      “result”
# "message" :         "message"
# }
# Klient - klient:
# {
# “type”	:	“operation_name”,
# “blocked_client_id”	:	“id”,
# “src_client_id”		:	“id”,
# “dst_client_id”		:	“id”
# }
#

class Semaphore:

    def __init__(self, name, pingOwner, pingWait):
        self.queue = Queue(maxsize=0)
        self.pingOwnerThread = threading.Thread(target=pingOwner, args=(name,), daemon=True)
        self.pingWaitThread = threading.Thread(target=pingWait, args=(name,), daemon=True)
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
            self.semaphores.update({ name : Semaphore(name, partial(Semaphores.__pinging, self), partial(Semaphores.__pingWaitingClients, self)) })
            self.semaphores[name].pingOwnerThread.start()
            self.semaphores[name].pingWaitThread.start()
        else:
            result = "{\"type\":\"ERROR\",\"message\":\"Semaphore %s already exists\"}" % (name,)
        return result

    def delete(self, sock, name):
        result = None
        if name in self.semaphores.keys():
            if self.semaphores[name].queue.empty():
                self.semaphores[name].end = True
                self.semaphores[name].pingOwnerThread.join()
                self.semaphores[name].pingWaitThread.join()
                self.semaphores.pop(name, None)
                result = "{\"type\":\"DELETED\",\"sem_name\":\"%s\"}" % (name,)
            else:
                result = "{\"type\":\"ERROR\",\"message\":\"Semaphore %s is abandoned\"}" % (name,)
        else:
            result = "{\"type\":\"ERROR\",\"message\":\"Semaphore %s doesn't exist\"}" % (name,)
        return result

    def p(self, sock, name, client):
        result = None
        if name in self.semaphores.keys():
            if client not in list(self.semaphores[name].queue.queue):
                self.semaphores[name].queue.put(WaitClient(client))
            wait = "{\"type\":\"WAIT\",\"sem_name\":\"%s\"}" % (name,)
            while self.semaphores[name].queue.queue[0].addr == client:
                pass
            result = "{\"type\":\"ENTER\",\"sem_name\":\"%s\"}" % (name,)
        else:
            result = "{\"type\":\"ERROR\",\"message\":\"Semaphore %s doesn't exist\"}" % (name,)
        return result

    def v(self, sock, name, client):
        result = None
        if name in self.semaphores.keys():
            # print(client)
            # print(self.semaphores[name].queue.queue[0].addr)
            it = client.index(':')
            if not self.semaphores[name].queue.empty() and client[:it] == self.semaphores[name].queue.queue[0].addr[:it]:
                self.semaphores[name].queue.get_nowait()
            while not self.semaphores[name].queue.empty() and not self.semaphores[name].queue.queue[0].alive:
                self.semaphores[name].queue.get_nowait()
            if not self.semaphores[name].queue.empty():
                message = "{\"type\":\"ENTER\",\"sem_name\":\"%s\"}" % (name,)
                self.__sendMessage(message, self.semaphores[name].queue.queue[0].addr) # tell next client in queue that he is the new owner of this semaphore
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

    def __sendMessage(self, message, addr):
        logger = logging.getLogger('server')
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
                it = addr.index(':')
                # logger.info("{}:{}".format(addr[:it], int(addr[it+1:])))
                sock.connect((addr[:it], int(addr[it+1:])))
                sock.send(bytes(message, 'ascii'))
        except:
            logger.info(traceback.format_exc())

    def __pingWaitingClients(self, name):
        while not self.semaphores[name].end:
            addrs = []
            for cl in list(self.semaphores[name].queue.queue)[1:]:
                if cl.alive:
                    addrs.append(cl.addr)

            if len(addrs) > 0:
                pool = ThreadPool()
                results = pool.map(partial(Semaphores.__pingClient, self, name), addrs)

                for i in range(0, len(addrs)):
                    if not results[i]:
                        for cl in self.semaphores[name].queue.queue:
                            if cl.addr == addrs[i]:
                                self.semaphores[name].queue.queue[i].alive = False

            time.sleep(1)

    def __pingClient(self, name, addr):
        logger = logging.getLogger('server')
        ping = "{\"type\":\"PING\",\"sem_name\":\"%s\"}" % (name,)
        result = True
        it = addr.index(':')
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
                sock.settimeout(Semaphores.TIMEOUT)
                try:
                    sock.connect((addr[:it], int(addr[it+1:])))
                    sock.send(bytes(ping, 'ascii'))
                except ConnectionRefusedError as e:
                    result = False
                else:
                    try:
                        data = json.loads(str(sock.recv(1024), 'ascii'))
                        logger.info("Wait {}".format(data))
                        if data['type'] != "PONG":
                            result = False
                    except (json.JSONDecodeError, socket.timeout):
                        result = False
        except socket.timeout:
            result = False
        finally:
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
                with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
                    # sock.bind(('LOCALHOST', 0))
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
                        except (json.JSONDecodeError, socket.timeout):
                            if not self.semaphores[name].queue.empty() and addr[:it] == self.semaphores[name].queue.queue[0].addr[:it]:
                                self.semaphores[name].queue.get_nowait()
            finally:
                time.sleep(1)
