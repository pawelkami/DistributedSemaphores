package pl.edu.pw.elka;

/**
 * Klasa reprezentująca semafor.
 */
public class Semaphore {
    public String name; // semaphore name
    public boolean isWaiting; // is semaphore in waiting queue
    public boolean isDeadlock; // true if deadlock occured

    public Semaphore() {
        name = "";
        isWaiting = true;
        isDeadlock = false;
    }
}
