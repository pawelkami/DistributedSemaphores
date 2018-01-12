from http import client
from threading import Thread
from socketserver import BaseRequestHandler, ThreadingMixIn, TCPServer
from semaphores import Semaphores
import traceback
import json
import socket
import logging
import sys

SERVER_PORT = 10080

class ThreadedTCPRequestHandler(BaseRequestHandler):

    def handle(self):
        logger = logging.getLogger('server')
        data = None
        response = None
        client_id = str(self.client_address[0]) + ':' + str(self.client_address[1]) # socket.gethostbyaddr(self.client_address[0])[0]
        # client_id = socket.gethostbyaddr(self.client_address[0])[0]
        # print(client_id)
        try:
            received_msg = ''
            while '}' not in received_msg:
                received_msg += str(self.request.recv(4096), 'ascii')
            logger.info("Received message: " + received_msg)
            data = json.loads(received_msg)
        except json.JSONDecodeError:
            response = "{ \"type\" : \"ERROR\"," \
                       "\"value\": \"Json decode error\"}"
        else:
            try:
                if data['type'] == "LOCK":
                    response = self.server._semaphores.p(self.request, data['sem_name'], client_id)
                elif data['type'] == "CREATE":
                    response = self.server._semaphores.create(self.request, data['sem_name'])
                elif data['type'] == "DELETE":
                    response = self.server._semaphores.delete(self.request, data['sem_name'])
                elif data['type'] == "UNLOCK":
                    response = self.server._semaphores.v(self.request, data['sem_name'], client_id)
                elif data['type'] == "GET_AWAITING":
                    response = self.server._semaphores.getAwaiting(self.request, data['sem_name'])
            except KeyError as e:
                logger.info(traceback.format_exc())
                response = "{ \"type\" : \"ERROR\"," \
                           "\"value\": \"Json decode error\"}"
        finally:
            if response:
                logger.info(response)
                self.request.send(bytes(response, 'ascii'))



class ThreadedTCPServer(ThreadingMixIn, TCPServer):

    def __init__(self, addr_port, handler):
        self._semaphores = Semaphores()
        super(ThreadingMixIn, self).__init__(addr_port, handler)
        super(TCPServer, self).__init__(addr_port, handler)


def run():
    logger = logging.getLogger('server')
    logger.setLevel(logging.DEBUG)

    fh = logging.FileHandler('/home/server.log')
    # fh = logging.StreamHandler(sys.stdout)

    fh.setLevel(logging.DEBUG)
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    fh.setFormatter(formatter)
    logger.addHandler(fh)

    print(socket.gethostbyname(socket.gethostname()))
    HOST, PORT = socket.gethostname(), SERVER_PORT

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
