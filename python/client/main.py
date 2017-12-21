from client import Client
import time

if __name__ == "__main__":

    client = Client()

    client.create("DESKTOP-KD5T409.B")
    client.getAwaiting("DESKTOP-KD5T409.B")
    client.lock("DESKTOP-KD5T409.B")
    time.sleep(20)
    client.unlock("DESKTOP-KD5T409.B")
    client.delete("DESKTOP-KD5T409.B")

    # client.create("python_server1_1.B")
    # client.getAwaiting("python_server1_1.B")
    # client.lock("python_server1_1.B")
    # time.sleep(10)
    # client.unlock("python_server1_1.B")
    # client.delete("python_server1_1.B")

    time.sleep(1)
