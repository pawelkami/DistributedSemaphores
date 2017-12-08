# DistributedSemaphores
Distributed Semaphore Server - university project

## Budowanie i uruchamianie kontenerów
### Wchodzimy do katalogu, w którym znajduje się plik docker-compose.yml i uruchamiamy tam komendy:
### docker-compose build
### docker-compose up

## Dostęp do klienta
### Jeśli chcemy sterować klientem, to najpierw uruchamiamy docker-compose a potem możemy wejść na kontener uruchomić odpowiednią aplikację.
### docker exec -ti <nazwa_konteneru> /bin/sh
### <nazwa_konteneru> - np. python_client1_1
