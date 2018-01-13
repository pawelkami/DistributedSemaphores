package pl.edu.pw.elka;


import java.io.IOException;
import java.net.ServerSocket;
import java.net.Socket;
import java.util.concurrent.ExecutorService;
import java.util.concurrent.Executors;
import java.util.logging.Logger;

class Server {

    private ExecutorService executorService = Executors.newFixedThreadPool(10); // number of server threads
    private final int PORT = 10080;

    Logger log = Logger.getLogger(Server.class.getName());


    Server() {

    }

    void runServer() {
        log.info("Creating socket...");
        try (ServerSocket serverSocket = new ServerSocket(PORT)) {
            while (true) {
                log.info("Waiting for request...");
                try {
                    Socket s = serverSocket.accept();
                    log.info("Processing request");
                    executorService.submit(new RequestHandler(s));
                } catch (IOException ioe) {
                    log.warning("Error accepting connection");
                    ioe.printStackTrace();
                }

            }

        } catch (IOException e) {
            log.warning("Error starting server at port " + PORT);
            e.printStackTrace();
        }
    }
}
