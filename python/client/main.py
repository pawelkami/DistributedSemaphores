import socket
import json
import traceback

def client(ip, port, message):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.connect((ip, port))
        sock.sendall(bytes(message, 'ascii'))
        response = str(sock.recv(1024), 'ascii')

        try:
            print(json.loads(response)['type'])
        except:
            print(traceback.format_exc())
        print("Received: {}".format(response))


if __name__ == "__main__":

    HOST, PORT = "localhost", 9999

    client(HOST, PORT, "{\"type\":\"CREATE\",\"sem_name\":\"A\"}")
    client(HOST, PORT, "{\"type\":\"LOCK\",\"sem_name\":\"A\"}")
    client(HOST, PORT, "{\"type\":\"UNLOCK\",\"sem_name\":\"A\"}")
    client(HOST, PORT, "{\"type\":\"DELETE\",\"sem_name\":\"A\"}")
