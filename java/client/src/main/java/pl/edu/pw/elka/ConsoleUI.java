package pl.edu.pw.elka;

import java.net.UnknownHostException;
import java.util.Arrays;
import java.util.Scanner;

/**
 * Klasa reprezentująca interfejs użytkownika w konsoli.
 */
public class ConsoleUI {

    ConsoleUI() {

    }

    private void printMenu() {
        System.out.println("");
        System.out.println("Choose one of options. Usage: option semaphore_name. Semaphore name should be formatted as server_name.semaphore_name");
        System.out.println("create - creating semaphore");
        System.out.println("delete - delete semaphore");
        System.out.println("lock - lock semaphore");
        System.out.println("unlock - unlock semaphore");
        System.out.println("awaiting - get list of awaiting clients");
        System.out.println("exit - exit client");
        System.out.println("");
        System.out.print("client> ");

    }


    public void run() {
        try(Client client = new Client())
        {
            while (true) {
                printMenu();
                Scanner input = new Scanner(System.in);

                String line = input.nextLine();
                String[] commands = line.split("\\s+");

                String operation = commands[0];
                String[] sem_names = null;

                if (!operation.equals("exit")) {
                    if (commands.length < 2) {
                        System.out.println("Wrong command");
                        continue;
                    }

                    sem_names = Arrays.copyOfRange(commands, 1, commands.length);
                }

                try {

                    switch (operation.toLowerCase()) {
                        case "create":
                            client.createSemaphore(sem_names[0]);
                            break;

                        case "delete":
                            client.deleteSemaphore(sem_names[0]);
                            break;

                        case "lock":
                            client.lock(sem_names);
                            break;

                        case "unlock":
                            client.unlock(sem_names);
                            break;

                        case "awaiting":
                            client.getAwaiting(sem_names[0]);
                            break;

                        case "exit":
                            System.exit(0);
                            break;

                        default:
                            break;
                    }
                } catch (ClientException | UnknownHostException e) {
                    e.printStackTrace();
                }

            }
        } catch (Exception e) {
            e.printStackTrace();
        }
    }
}
