
"""
Klasa ze statyczna metoda sluzaca do tworzenia wyjatkow
adekwatnych do komunikatow otrzymanych z serwera
"""
class ClientExceptions:

    @staticmethod
    def castException(exceptMsg):
        if 'is abandoned' in exceptMsg or "is currently in use" in exceptMsg:
            raise AbandonedException(exceptMsg)
        elif "doesn't exist" in exceptMsg:
            raise DoesNotExistException(exceptMsg)
        elif "already exists" in exceptMsg:
            raise AlreadyExistsException(exceptMsg)
        else:
            raise RuntimeError(exceptMsg)

class AbandonedException(Exception):
    pass


class DoesNotExistException(Exception):
    pass


class AlreadyExistsException(Exception):
    pass
