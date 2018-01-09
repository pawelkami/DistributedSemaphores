from client import Client
from ClientExceptions import AbandonedException, DoesNotExistException, AlreadyExistsException
import time

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
    #     print(e)
    # try:
    #     client.create("python_server2_1.B")
    # except (AbandonedException, DoesNotExistException, AlreadyExistsException) as e:
    #     print(e)
    # try:
    #     client.getAwaiting("python_server2_1.A")
    # except (AbandonedException, DoesNotExistException, AlreadyExistsException) as e:
    #     print(e)
    # try:
    #     client.multiLock(["python_server1_1.A", "python_server2_1.B"])
    # except (AbandonedException, DoesNotExistException, AlreadyExistsException) as e:
    #     print(e)
    #
    # time.sleep(20)
    #
    # try:
    #     client.unlock("python_server2_1.B")
    # except (AbandonedException, DoesNotExistException, AlreadyExistsException) as e:
    #     print(e)
    # try:
    #     client.unlock("python_server1_1.A")
    # except (AbandonedException, DoesNotExistException, AlreadyExistsException) as e:
    #     print(e)
    # try:
    #     client.delete("python_server1_1.A")
    # except (AbandonedException, DoesNotExistException, AlreadyExistsException) as e:
    #     print(e)
    # try:
    #     client.delete("python_server2_1.B")
    # except (AbandonedException, DoesNotExistException, AlreadyExistsException) as e:
    #     print(e)

    time.sleep(1)
