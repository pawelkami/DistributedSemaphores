import socket

def client(ip, port, message):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.connect((ip, port))
        sock.sendall(bytes(message, 'ascii'))
        response = str(sock.recv(1024), 'ascii')
        print("Received: {}".format(response))


if __name__ == "__main__":

    HOST, PORT = "localhost", 9999

    client(HOST, PORT, "First message")
    client(HOST, PORT, "Second message")
    client(HOST, PORT, "Third message")
