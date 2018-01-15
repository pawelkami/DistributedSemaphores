from client import Client
from ClientExceptions import AbandonedException, DoesNotExistException, AlreadyExistsException
import time
import socket

if __name__ == "__main__":

    client = Client()

    try:
        client.create("DESKTOP-KD5T409.A")
    except (AbandonedException, DoesNotExistException, AlreadyExistsException) as e:
        print(e)
    try:
        client.create("DESKTOP-KD5T409.B")
    except (AbandonedException, DoesNotExistException, AlreadyExistsException) as e:
        print(e)
    try:
        client.getAwaiting("DESKTOP-KD5T409.A")
    except (AbandonedException, DoesNotExistException, AlreadyExistsException) as e:
        print(e)
    try:
        client.lock("DESKTOP-KD5T409.A")
    except (AbandonedException, DoesNotExistException, AlreadyExistsException) as e:
        print(e)

    try:
        client.lock("DESKTOP-KD5T409.A")
    except (AbandonedException, DoesNotExistException, AlreadyExistsException) as e:
        print(e)

    time.sleep(20)

    try:
        client.unlock("DESKTOP-KD5T409.B")
    except (AbandonedException, DoesNotExistException, AlreadyExistsException) as e:
        print(e)
    try:
        client.unlock("DESKTOP-KD5T409.A")
    except (AbandonedException, DoesNotExistException, AlreadyExistsException) as e:
        print(e)
    try:
        client.delete("DESKTOP-KD5T409.A")
    except (AbandonedException, DoesNotExistException, AlreadyExistsException) as e:
        print(e)
    try:
        client.delete("DESKTOP-KD5T409.B")
    except (AbandonedException, DoesNotExistException, AlreadyExistsException) as e:
        print(e)
    #############################################################################################
    # try:
    #     client.create("python_server1_1.A")
    # except (AbandonedException, DoesNotExistException, AlreadyExistsException) as e:
    #     client.logger.error(e)
    # try:
    #     client.create("python_server2_1.B")
    # except (AbandonedException, DoesNotExistException, AlreadyExistsException) as e:
    #     client.logger.error(e)
    # try:
    #     client.getAwaiting("python_server2_1.A")
    # except (AbandonedException, DoesNotExistException, AlreadyExistsException) as e:
    #     client.logger.error(e)
    # try:
    #     host = socket.gethostbyname(socket.gethostname())
    #     client.logger.info(host)
    #     client.logger.info(socket.gethostbyname("python_client1_1"))
    #     if host == socket.gethostbyname("python_client1_1"):
    #         client.lock("python_server1_1.A")
    #         time.sleep(3)
    #         client.lock("python_server2_1.B")
    #     elif host == socket.gethostbyname("python_client2_1"):
    #         client.lock("python_server2_1.B")
    #         time.sleep(2)
    #         client.lock("python_server1_1.A")
    #     else:
    #         client.multiLock(["python_server1_1.A", "python_server2_1.B"])
    # except (AbandonedException, DoesNotExistException, AlreadyExistsException) as e:
    #     client.logger.error(e)
    #
    # time.sleep(20)
    #
    # try:
    #     client.unlock("python_server2_1.B")
    # except (AbandonedException, DoesNotExistException, AlreadyExistsException) as e:
    #     client.logger.error(e)
    # try:
    #     client.unlock("python_server1_1.A")
    # except (AbandonedException, DoesNotExistException, AlreadyExistsException) as e:
    #     client.logger.error(e)
    # try:
    #     client.delete("python_server1_1.A")
    # except (AbandonedException, DoesNotExistException, AlreadyExistsException) as e:
    #     client.logger.error(e)
    # try:
    #     client.delete("python_server2_1.B")
    # except (AbandonedException, DoesNotExistException, AlreadyExistsException) as e:
    #     client.logger.error(e)

    time.sleep(1)
