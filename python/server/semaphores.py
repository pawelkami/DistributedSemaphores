import socket
from queue import Queue
import traceback
import ipaddress

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


class Semaphores:

    def __init__(self):
        self.semaphores = dict()

    def create(self, name):
        result = None
        if name not in self.semaphores.keys():
            result = "{\"type\":\"CREATED\",\"sem_name\":\"%s\"}" % (name,)
            self.semaphores.update({ name : Queue(maxsize=0) })
        else:
            result = "{\"type\":\"ERROR\",\"message\":\"Semaphore %s already exists\"}" % (name,)
        return result

    def delete(self, name):
        result = None
        if name in self.semaphores.keys():
            if self.semaphores[name].empty():
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
            if self.semaphores[name].empty():
                result = "{\"type\":\"ENTER\",\"sem_name\":\"%s\"}" % (name,)
            else:
                result = "{\"type\":\"WAIT\",\"sem_name\":\"%s\"}" % (name,)
            if client not in list(self.semaphores[name].queue):
                self.semaphores[name].put(client)
        else:
            result = "{\"type\":\"ERROR\",\"message\":\"Semaphore %s doesn't exist\"}" % (name,)
        return result

    def v(self, name, client):
        result = None
        if name in self.semaphores.keys():
            print(1)
            print(list(self.semaphores[name].queue))
            if not self.semaphores[name].empty():
                temp = self.semaphores[name].get_nowait()
                print(2)
                print(temp)
            if not self.semaphores[name].empty():
                print(3)
                print(list(self.semaphores[name].queue))
                message = "{\"type\":\"ENTER\",\"sem_name\":\"%s\"}" % (name,)
                self.__sendMessage(message, list(self.semaphores[name].queue)[0]) # tell next client in queue that he is the new owner of this semaphore
            result = "{\"type\":\"UNLOCKED\",\"sem_name\":\"%s\"}" % (name,)
        else:
            result = "{\"type\":\"ERROR\",\"message\":\"Semaphore %s doesn't exist\"}" % (name,)
        return result

    def getAwaiting(self, name):
        result = None
        empty = True
        if name in self.semaphores.keys():
            result = "{\"type\":\"AWAITING\",\"sem_name\":\"%s\",\"result\":[" % (name,)
            waiting = list(self.semaphores[name].queue)
            if len(waiting) > 0:
                empty = False
            for cl in waiting:
                result += "\"{}\",".format(cl)

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
                sock.sendall(bytes(message, 'ascii'))
        except:
            print(traceback.format_exc())