package pl.edu.pw.elka;

public class Semaphore {
    public String name;
    public boolean isWaiting;
    public boolean isDeadlock;

    public Semaphore() {
        name = "";
        isWaiting = true;
        isDeadlock = false;
    }
}
