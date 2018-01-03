package pl.edu.pw.elka;


import java.io.IOException;
import java.net.ServerSocket;
import java.net.Socket;
import java.util.concurrent.ExecutorService;
import java.util.concurrent.Executors;
import java.util.logging.Logger;

class RequestListener implements Runnable {

    private ExecutorService executorService = Executors.newFixedThreadPool(10); // number of server threads
    private final int PORT = 8080;

    Logger log = Logger.getLogger(RequestListener.class.getName());


    RequestListener()
    {

    }

    @Override
    public void run()
    {
        //log.info("Creating socket...");
        try(ServerSocket serverSocket = new ServerSocket(PORT))
        {
            while(true) {
//                log.info("Waiting for request...");
                try {
                    Socket s = serverSocket.accept();
//                    log.info("Processing request");
                    executorService.submit(new ClientRequestHandler(s));
                } catch(IOException ioe) {
                    log.warning("Error accepting connection");
                    ioe.printStackTrace();
                }

            }

        }
        catch(IOException e)
        {
            log.warning("Error starting server at port " + PORT);
            e.printStackTrace();
        }
    }
}