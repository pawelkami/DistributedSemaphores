package pl.edu.pw.elka;

import java.util.Scanner;

public class ConsoleUI
{

    private Client client;

    ConsoleUI()
    {
        client = new Client();
    }

    private void printMenu()
    {
        System.out.println("Choose one of options. Usage: option semaphore_name. Semaphore name should be formatted as server_name.semaphore_name");
        System.out.println("create - creating semaphore");
        System.out.println("delete - delete semaphore");
        System.out.println("lock - lock semaphore");
        System.out.println("unlock - unlock semaphore");
        System.out.println("deadlock - test for deadlock");

    }


    public void run()
    {
        while(true)
        {
            printMenu();
            Scanner input = new Scanner(System.in);
            String operation = input.next();
            String sem_name = null;

            if(!operation.equals("deadlock"))
                sem_name = input.next();

            try {

                switch (operation.toLowerCase()) {
                    case "create":
                        client.createSemaphore(sem_name);
                        break;

                    case "delete":
                        break;

                    case "lock":
                        break;

                    case "unlock":
                        break;

                    case "deadlock":
                        break;

                    default:
                        break;
                }
            }
            catch (ClientException e) {
                e.printStackTrace();
            }
        }
    }
}
