from client import Client
from ClientExceptions import AbandonedException, DoesNotExistException, AlreadyExistsException
import time
import socket

if __name__ == "__main__":

    client = Client()

    # try:
    #     client.create("DESKTOP-KD5T409.A")
    # except (AbandonedException, DoesNotExistException, AlreadyExistsException) as e:
    #     print(e)
    # try:
    #     client.create("DESKTOP-KD5T409.B")
    # except (AbandonedException, DoesNotExistException, AlreadyExistsException) as e:
    #     print(e)
    # try:
    #     client.getAwaiting("DESKTOP-KD5T409.A")
    # except (AbandonedException, DoesNotExistException, AlreadyExistsException) as e:
    #     print(e)
    # try:
    #     client.lock("DESKTOP-KD5T409.A")
    # except (AbandonedException, DoesNotExistException, AlreadyExistsException) as e:
    #     print(e)
    #
    # try:
    #     client.lock("DESKTOP-KD5T409.A")
    # except (AbandonedException, DoesNotExistException, AlreadyExistsException) as e:
    #     print(e)
    #
    # time.sleep(20)
    #
    # try:
    #     client.unlock("DESKTOP-KD5T409.B")
    # except (AbandonedException, DoesNotExistException, AlreadyExistsException) as e:
    #     print(e)
    # try:
    #     client.unlock("DESKTOP-KD5T409.A")
    # except (AbandonedException, DoesNotExistException, AlreadyExistsException) as e:
    #     print(e)
    # try:
    #     client.delete("DESKTOP-KD5T409.A")
    # except (AbandonedException, DoesNotExistException, AlreadyExistsException) as e:
    #     print(e)
    # try:
    #     client.delete("DESKTOP-KD5T409.B")
    # except (AbandonedException, DoesNotExistException, AlreadyExistsException) as e:
    #     print(e)
    #############################################################################################
    try:
        client.create("python_server1.A")
    except (AbandonedException, DoesNotExistException, AlreadyExistsException) as e:
        client.logger.error(e)
    try:
        client.create("java_server1.B")
    except (AbandonedException, DoesNotExistException, AlreadyExistsException) as e:
        client.logger.error(e)
    try:
        client.getAwaiting("java_server1.A")
    except (AbandonedException, DoesNotExistException, AlreadyExistsException) as e:
        client.logger.error(e)
    try:
        host = socket.gethostbyname(socket.gethostname())
        client.logger.info(host)
        client.logger.info(socket.gethostbyname("python_client1"))
        if host == socket.gethostbyname("python_client1"):
            client.lock("python_server1.A")
            time.sleep(3)
            client.lock("java_server1.B")
        elif host == socket.gethostbyname("java_server1"):
            client.lock("java_server1.B")
            time.sleep(2)
            client.lock("python_server1.A")
        else:
            client.multiLock(["python_server1.A", "java_server1.B"])
    except (AbandonedException, DoesNotExistException, AlreadyExistsException) as e:
        client.logger.error(e)

    time.sleep(20)

    try:
        client.unlock("java_server1.B")
    except (AbandonedException, DoesNotExistException, AlreadyExistsException) as e:
        client.logger.error(e)
    try:
        client.unlock("python_server1.A")
    except (AbandonedException, DoesNotExistException, AlreadyExistsException) as e:
        client.logger.error(e)
    try:
        client.delete("python_server1.A")
    except (AbandonedException, DoesNotExistException, AlreadyExistsException) as e:
        client.logger.error(e)
    try:
        client.delete("java_server1.B")
    except (AbandonedException, DoesNotExistException, AlreadyExistsException) as e:
        client.logger.error(e)

    time.sleep(1)
