import socket
from queue import Queue
import traceback
import threading
from threading import Lock
from functools import partial
import time
import json

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

    def __init__(self, name, func):
        self.queue = Queue(maxsize=0)
        self.thread = threading.Thread(target=func, args=(name,), daemon=True)
        self.end = False

class WaitClient:

    def __init__(self, addr, th):
        self.addr = addr
        self.thread = th
        if self.thread is not None:
            self.thread.start()
        self.end = th is None

class Semaphores:

    TIMEOUT = 10

    def __init__(self):
        self.semaphores = dict()

    def create(self, name):
        result = None
        if name not in self.semaphores.keys():
            result = "{\"type\":\"CREATED\",\"sem_name\":\"%s\"}" % (name,)
            self.semaphores.update({ name : Semaphore(name, partial(Semaphores.__pinging, self)) })
            self.semaphores[name].thread.start()
        else:
            result = "{\"type\":\"ERROR\",\"message\":\"Semaphore %s already exists\"}" % (name,)
        return result

    def delete(self, name):
        result = None
        if name in self.semaphores.keys():
            if self.semaphores[name].queue.empty():
                self.semaphores[name].end = True
                self.semaphores[name].thread.join()
                self.semaphores.pop(name, None)
                result = "{\"type\":\"DELETED\",\"sem_name\":\"%s\"}" % (name,)
            else:
                result = "{\"type\":\"ERROR\",\"message\":\"Semaphore %s is abandoned\"}" % (name,)
        else:
            result = "{\"type\":\"ERROR\",\"message\":\"Semaphore %s doesn't exist\"}" % (name,)
        return result

    def p(self, name, client):
        result = None
        if name in self.semaphores.keys():
            th = None
            if self.semaphores[name].queue.empty():
                result = "{\"type\":\"ENTER\",\"sem_name\":\"%s\"}" % (name,)
            else:
                result = "{\"type\":\"WAIT\",\"sem_name\":\"%s\"}" % (name,)
                th = threading.Thread(target=partial(Semaphores.__pingClient, self), args=(name, client,), daemon=True)
            if client not in list(self.semaphores[name].queue.queue):
                self.semaphores[name].queue.put(WaitClient(client, th))
        else:
            result = "{\"type\":\"ERROR\",\"message\":\"Semaphore %s doesn't exist\"}" % (name,)
        return result

    def v(self, name, client):
        result = None
        if name in self.semaphores.keys():
            self.semaphores[name].queue.get_nowait()
            if not self.semaphores[name].queue.empty():
                message = "{\"type\":\"ENTER\",\"sem_name\":\"%s\"}" % (name,)
                while not self.semaphores[name].queue.empty() and list(self.semaphores[name].queue.queue)[0].end:
                    if list(self.semaphores[name].queue.queue)[0].thread is not None:
                        list(self.semaphores[name].queue.queue)[0].thread.join()
                    self.semaphores[name].queue.get_nowait()
                if not self.semaphores[name].queue.empty():
                    self.semaphores[name].queue.queue[0].end = True
                    list(self.semaphores[name].queue.queue)[0].thread.join()
                    self.__sendMessage(message, list(self.semaphores[name].queue.queue)[0].addr) # tell next client in queue that he is the new owner of this semaphore
            result = "{\"type\":\"UNLOCKED\",\"sem_name\":\"%s\"}" % (name,)
        else:
            result = "{\"type\":\"ERROR\",\"message\":\"Semaphore %s doesn't exist\"}" % (name,)
        return result

    def getAwaiting(self, name):
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
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
                it = addr.index(':')
                print("{}:{}".format(addr[:it], int(addr[it+1:])))
                sock.connect((addr[:it], int(addr[it+1:])))
                sock.send(bytes(message, 'ascii'))
        except:
            print(traceback.format_exc())

    def __pingClient(self, name, addr):
        time.sleep(1)
        ping = "{\"type\":\"PING\",\"sem_name\":\"%s\"}" % (name,)

        i = 0
        while self.semaphores[name].queue.queue[i].addr != addr:
            i += 1

        # print(self.semaphores[name].queue.queue[i].end)
        while not self.semaphores[name].queue.empty() and not self.semaphores[name].queue.queue[i].end:
            it = addr.index(':')
            try:
                with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
                    sock.settimeout(Semaphores.TIMEOUT)
                    try:
                        sock.connect((addr[:it], int(addr[it+1:])))
                        sock.send(bytes(ping, 'ascii'))
                    except ConnectionRefusedError:
                        list(self.semaphores[name].queue.queue)[i].end = True
                    else:
                        try:
                            data = json.loads(str(sock.recv(1024), 'ascii'))
                            print(data)
                            if data['type'] != "PONG":
                                list(self.semaphores[name].queue.queue)[i].end = True
                        except (json.JSONDecodeError, socket.timeout):
                            list(self.semaphores[name].queue.queue)[i].end = True
            except socket.timeout:
                list(self.semaphores[name].queue.queue)[i].end = True
            finally:
                i = 0
                while self.semaphores[name].queue.queue[i].addr != addr:
                    i += 1
                time.sleep(1)

    def __pinging(self, name):
        ping = "{\"type\":\"PING\",\"sem_name\":\"%s\"}" % (name,)
        while not self.semaphores[name].end:
            addr = None
            try:
                while addr is None:
                    clientQueue = list(self.semaphores[name].queue.queue)
                    if len(clientQueue) > 0:
                        addr = clientQueue[0].addr
                    else:
                        time.sleep(1)
                    # print(addr)
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
                        self.semaphores[name].queue.get_nowait()
                    else:
                        try:
                            data = json.loads(str(sock.recv(1024), 'ascii'))
                            print(data)
                            if data['type'] != "PONG":
                                self.semaphores[name].queue.get_nowait()
                        except (json.JSONDecodeError, socket.timeout):
                            self.semaphores[name].queue.get_nowait()
            finally:
                time.sleep(1)
