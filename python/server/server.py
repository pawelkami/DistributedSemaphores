from threading import Thread
from socketserver import BaseRequestHandler, ThreadingMixIn, TCPServer
from semaphores import Semaphores
import traceback
import json
import socket

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


class ThreadedTCPRequestHandler(BaseRequestHandler):

    def handle(self):
        data = None
        response = None
        client_id = str(self.client_address[0]) + ':' + str(self.client_address[1]) # socket.gethostbyaddr(self.client_address[0])[0]
        try:
            data = json.loads(str(self.request.recv(4096), 'ascii'))
        except json.JSONDecodeError:
            response = "{ \"type\" : \"ERROR\"," \
                       "\"value\": \"Json decode error\"}"
        else:
            # print("type: {}".format(data['type']))
            # print("name: {}".format(data['sem_name']))
            try:
                if data['type'] == "LOCK":
                    response = self.server._semaphores.p(data['sem_name'], client_id)
                elif data['type'] == "PONG":
                    # self.server._semaphores.pong(data['sem_name'])
                    pass
                elif data['type'] == "CREATE":
                    response = self.server._semaphores.create(data['sem_name'])
                elif data['type'] == "DELETE":
                    response = self.server._semaphores.delete(data['sem_name'])
                elif data['type'] == "UNLOCK":
                    response = self.server._semaphores.v(data['sem_name'], client_id)
                elif data['type'] == "GET_AWAITING":
                    response = self.server._semaphores.getAwaiting(data['sem_name'])
            except KeyError as e:
                print(traceback.format_exc())
                response = "{ \"type\" : \"ERROR\"," \
                           "\"value\": \"Json decode error\"}"
            except:
                print(traceback.format_exc())
        finally:
            # print(data)
            self.request.sendall(bytes(response, 'ascii'))



class ThreadedTCPServer(ThreadingMixIn, TCPServer):

    def __init__(self, addr_port, handler):
        self._semaphores = Semaphores()
        super(ThreadingMixIn, self).__init__(addr_port, handler)
        super(TCPServer, self).__init__(addr_port, handler)


def run():
    HOST, PORT = "localhost", 10080

    server = ThreadedTCPServer((HOST, PORT), ThreadedTCPRequestHandler)
    with server:

        # Start a thread with the server -- that thread will then start one
        # more thread for each request
        server_thread = Thread(target=server.serve_forever)

        try:
            # Exit the server thread when the main thread terminates
            server_thread.daemon = True
            server_thread.start()
            print("Server loop running in thread:", server_thread.name)
            while server_thread.isAlive():
                server_thread.join(1)
        except (KeyboardInterrupt, SystemExit):
            print("Terminate server")
        finally:
            server.shutdown()
