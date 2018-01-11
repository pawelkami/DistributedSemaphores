package pl.edu.pw.elka;

import java.util.ArrayList;
import java.util.List;

public class CreatedSemaphores {
    List<Semaphore> semaphoreList;
    private static CreatedSemaphores instance = null;

    private CreatedSemaphores()
    {
        semaphoreList = new ArrayList<Semaphore>();
    }

    public static CreatedSemaphores getInstance()
    {
        if(instance == null)
            instance = new CreatedSemaphores();
        return instance;
    }

    public void addSemaphore(Semaphore s)
    {
        semaphoreList.add(s);
    }

    public void deleteSemaphore(String semaphoreName)
    {
        for(Semaphore s : semaphoreList)
        {
            if(s.name.equalsIgnoreCase(semaphoreName))
            {
                semaphoreList.remove(s);
                return;
            }
        }
    }

    public List<Semaphore> getSemaphoreList()
    {
        return semaphoreList;
    }

    public void changeSemaphoreWaitStatus(String semaphoreName, boolean isWaiting)
    {
        for(Semaphore s : semaphoreList)
        {
            if(s.name.equalsIgnoreCase(semaphoreName))
            {
                s.isWaiting = isWaiting;
                return;
            }
        }
    }

    public boolean checkIfWaitingForAnySemaphore()
    {
        for(Semaphore s : semaphoreList)
        {
            if(s.isWaiting)
                return true;
        }

        return false;
    }
}
