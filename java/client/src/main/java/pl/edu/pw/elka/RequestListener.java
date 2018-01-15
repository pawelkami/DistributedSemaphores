package pl.edu.pw.elka;

import java.io.IOException;
import java.net.ServerSocket;
import java.net.Socket;
import java.util.concurrent.ExecutorService;
import java.util.concurrent.Executors;
import java.util.logging.Logger;

/**
 * Klasa nasłuchująca żądań od serwerów/klientów. (PING i DEADLOCK)
 */
class RequestListener implements Runnable {

    private ExecutorService executorService = Executors.newFixedThreadPool(10); // number of server threads
    public static final int CLIENT_PORT = 8080;

    private Logger log = Logger.getLogger(RequestListener.class.getName());
    private Client client;
    private boolean shutdown = false;

    RequestListener(Client c) {
        client = c;
    }

    public void setShutdown(boolean s){
        shutdown = s;
    }

    @Override
    public void run() {
        try (ServerSocket serverSocket = new ServerSocket(CLIENT_PORT)) {
            while (!shutdown) {
                try {
                    Socket s = serverSocket.accept();
                    executorService.submit(new ClientRequestHandler(s, client));
                } catch (IOException ioe) {
                    log.warning("Error accepting connection");
                    ioe.printStackTrace();
                }

            }

        } catch (IOException e) {
            log.warning("Error starting server at port " + CLIENT_PORT);
            e.printStackTrace();
        }
    }
}