package pl.edu.pw.elka;

public class Main {
    public static void main(String[] args)
    {
        (new Thread(new RequestListener())).start();
        new ConsoleUI().run();
    }
}
