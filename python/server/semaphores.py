import queue
from threading import Lock

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
            self.semaphores.update({ name : queue })
        else:
            result = "{\"type\":\"ERROR\",\"value\":\"Semaphore %s already exists\"}" % (name,)
        return result

    def delete(self, name):
        result = None
        if name in self.semaphores.keys():
            result = "{\"type\":\"DELETED\",\"sem_name\":\"%s\"}" % (name,)
        else:
            result = "{\"type\":\"ERROR\",\"value\":\"Semaphore %s doesn't exist\"}" % (name,)
        return result

    def p(self, name):
        return "{\"type\":\"ENTER\",\"sem_name\":\"%s\"}" % (name,)

    def v(self, name):
        return "{\"type\":\"UNLOCKED\",\"sem_name\":\"%s\"}" % (name,)          # funkcje powinny zwracac jsona oraz adres gdzie odeslac wiadmosc

    def detAwaiting(self, name):
        pass
