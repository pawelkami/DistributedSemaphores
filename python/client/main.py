from client import Client
import time

if __name__ == "__main__":

    client = Client()
    client.create("DESKTOP-KD5T409", "B")
    client.getAwaiting("DESKTOP-KD5T409", "B")
    client.lock("DESKTOP-KD5T409", "B")
    time.sleep(5)
    client.unlock("DESKTOP-KD5T409", "B")
    client.delete("DESKTOP-KD5T409", "B")
