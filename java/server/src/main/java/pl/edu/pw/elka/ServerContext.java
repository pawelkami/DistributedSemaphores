package pl.edu.pw.elka;

import java.util.HashMap;
import java.util.LinkedList;
import java.util.Map;
import java.util.Queue;

public class ServerContext {
    private static ServerContext instance = null;

    // map<semaphore name, process queue>
    // first process in process queue is in critical section
    private Map<String, Queue<String>> semaphoreToProcessMap;

    private ServerContext() {
        semaphoreToProcessMap = new HashMap<>();
    }

    public synchronized static ServerContext getInstance() {
        if (instance == null)
            instance = new ServerContext();
        return instance;
    }


    public synchronized Map<String, Queue<String>> getSemaphoreToProcessMap() {
        return semaphoreToProcessMap;
    }

    public synchronized void setSemaphoreToProcessMap(Map<String, Queue<String>> semaphoreToProcessMap) {
        this.semaphoreToProcessMap = semaphoreToProcessMap;
    }

    public synchronized boolean isSemaphoreExisting(String semName) {
        return semaphoreToProcessMap.containsKey(semName);
    }

    public synchronized Queue<String> getClientQueue(String semName) {
        if (isSemaphoreExisting(semName))
            return semaphoreToProcessMap.get(semName);

        return null;
    }


    public synchronized void createSemaphore(String semName) {
        if (!isSemaphoreExisting(semName))
            semaphoreToProcessMap.put(semName, new LinkedList<String>());
    }


    public synchronized void deleteSemaphore(String semName) throws DistributedSemaphoreException {
        if (isSemaphoreExisting(semName)) {
            Queue<String> q = getClientQueue(semName);
            if (q.isEmpty())
                semaphoreToProcessMap.remove(semName);
            else
                throw new DistributedSemaphoreException("Semaphore is currently in use");
        }
    }

    public synchronized void addToQueue(String semName, String clientName) {
        if (!isSemaphoreExisting(semName))
            createSemaphore(semName);

        getClientQueue(semName).add(clientName);
    }

    public synchronized void removeFromQueue(String semName, String clientName) throws DistributedSemaphoreException {
        if (!isSemaphoreExisting(semName))
            throw new DistributedSemaphoreException("Semaphore with this name doesn't exist");

        Queue<String> q = getClientQueue(semName);

        if (!q.isEmpty() && q.peek().equals(clientName)) {
            q.remove();
        } else {
            throw new DistributedSemaphoreException("Cannot unlock semaphore. Client wasn't an owner of it.");
        }

    }
}
