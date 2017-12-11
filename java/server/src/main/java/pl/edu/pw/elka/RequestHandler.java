package pl.edu.pw.elka;

import com.google.gson.Gson;
import com.google.gson.JsonElement;
import com.google.gson.JsonObject;

import java.io.DataInputStream;
import java.io.IOException;
import java.io.InputStream;
import java.net.InetSocketAddress;
import java.net.Socket;
import java.net.SocketException;
import java.util.LinkedList;
import java.util.Queue;
import java.util.logging.Logger;

public class RequestHandler implements Runnable {
    private final int PORT = 8080;

    private Socket socket;
    private final int BUF_SIZE = 4 * 1024; // 4 kB
    Logger log = Logger.getLogger(RequestHandler.class.getName());

    public RequestHandler(Socket connection) {
        this.socket = connection;
    }

    @Override
    public void run() {

        try
        {
            byte[] byteArr = new byte[BUF_SIZE];
            StringBuilder clientData = new StringBuilder();
            String redDataText;
            byte[] redData;
            int red = -1;
            if ((red = socket.getInputStream().read(byteArr)) > -1) {
                redData = new byte[red];
                System.arraycopy(byteArr, 0, redData, 0, red);
                redDataText = new String(redData,"UTF-8"); // assumption that client sends data UTF-8 encoded
                log.info("message part received:" + redDataText + " from: " + getClientNameFromSocket());
                clientData.append(redDataText);
            }
            else
            {
                // todo odpowiedz do klienta
                log.warning("Problem reading socket stream");
                return;
            }

            log.info("Data From Client :" + clientData.toString());
            JsonObject jobj = new Gson().fromJson(clientData.toString(), JsonObject.class);
            handleJsonRequest(jobj);



        } catch (IOException e) {
            e.printStackTrace();
        }

        // close socket
        try
        {
            socket.close();
        }
        catch(IOException ioe)
        {
            log.warning("Error closing client connection");
        }
    }

    private void handleJsonRequest(JsonObject json)
    {
        log.info("Handling JSON request");
        JsonElement opJson = json.get("type");
        try
        {
            String operation = opJson.getAsString();
            switch(operation.toLowerCase())
            {
                case "create":
                    handleCreateSem(json);
                    break;
                case "delete":
                    handleDeleteSem(json);
                    break;
                case "lock":
                    handleLockSem(json);
                    break;
                case "unlock":
                    handleUnlockSem(json);
                    break;

                default:
                    log.warning("There is no operation '" + operation + "'");
                    break;
            }

        }
        catch(ClassCastException | IllegalStateException e)
        {
            log.warning("There is no 'type' in received JSON");
            // todo throw?
        }

    }


//    public synchronized void lockSemaphore(String semName, String clientName)
//    {
//        if(!semaphoreToProcessMap.containsKey(semName))
//        {
//            semaphoreToProcessMap.put(semName, new LinkedList<String>());
//        }
//
//        Queue<String> q = semaphoreToProcessMap.get(semName);
//        q.add(clientName);
//        if(q.size() == 1)
//        {
//            // todo wyslij klientowi ze ma locka
//        }
//        else
//        {
//            // todo wyslij klientowi ze musi czekac na swoja kolej
//        }
//
//    }
//
//    public synchronized void unlockSemaphore(String semName, String clientName) {
//        if (!semaphoreToProcessMap.containsKey(semName)) {
//            //throw "No semaphore with name " + semName; // todo
//        }
//
//        Queue<String> q = semaphoreToProcessMap.get(semName);
//        if (q.peek().compareTo(clientName) == 0) {
//            q.remove(); // TODO sprawdzic czy nie inna funkcja
//        } else {
//            //todo błąd
//        }
//    }


    private void handleUnlockSem(JsonObject json)
    {

    }

    private void handleLockSem(JsonObject json)
    {
        String clientName = getClientNameFromSocket();
    }

    private void handleDeleteSem(JsonObject json)
    {

    }

    private void handleCreateSem(JsonObject json)
    {

    }


    private String getClientNameFromSocket()
    {
        // Client name = ip address
        StringBuilder stringBuilder = new StringBuilder();
        InetSocketAddress address = (InetSocketAddress)socket.getRemoteSocketAddress();
        stringBuilder.append(address.getAddress().toString().replace("/", ""));

        return stringBuilder.toString();
    }
}
