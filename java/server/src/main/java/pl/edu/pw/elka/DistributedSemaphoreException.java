package pl.edu.pw.elka;

/**
 * Wyjątek z serwera semaforów.
 */
class DistributedSemaphoreException extends Exception {
    DistributedSemaphoreException(String msg) {
        super(msg);
    }
}
