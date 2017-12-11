package pl.edu.pw.elka;

import com.google.gson.Gson;
import com.google.gson.JsonElement;
import com.google.gson.JsonObject;

import java.io.*;
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

    private synchronized void handleJsonRequest(JsonObject json)
    {
        log.info("Handling JSON request");
        JsonElement opJson = json.get("type");

        if(!json.has(Defines.JSON_SEMAPHORE_NAME))
        {
            sendErrorResponse(opJson.getAsString(), "", Defines.RESPONSE_ERROR, "Wrong JSON");
            return;
        }

        try
        {
            String operation = opJson.getAsString();
            switch(operation.toUpperCase())
            {
                case Defines.OPERATION_CREATE_SEMAPHORE:
                    handleCreateSem(json);
                    break;
                case Defines.OPERATION_DELETE:
                    handleDeleteSem(json);
                    break;
                case Defines.OPERATION_LOCK:
                    handleLockSem(json);
                    break;
                case Defines.OPERATION_UNLOCK:
                    handleUnlockSem(json);
                    break;

                case Defines.OPERATION_GET_AWAITING:
                    break;

                case Defines.OPERATION_PING:
                    break;

                default:
                    log.warning("There is no operation '" + operation + "'");
                    break;
            }

        }
        catch(ClassCastException | IllegalStateException e)
        {
            log.warning("There is no 'type' in received JSON");
            sendErrorResponse("", "", Defines.RESPONSE_ERROR, "Wrong JSON");
        }

    }


    private synchronized void handleUnlockSem(JsonObject json)
    {
        String semaphoreName = json.get(Defines.JSON_SEMAPHORE_NAME).getAsString();

        if(!ServerContext.getInstance().isSemaphoreExisting(semaphoreName))
        {
            sendErrorResponse(json.get(Defines.JSON_OPERATION_TYPE).getAsString(),  semaphoreName, Defines.RESPONSE_ERROR, "Semaphore does not exist");
        }

        Queue<String> q = ServerContext.getInstance().getClientQueue(semaphoreName);
        if(q.peek().equals(getClientNameFromSocket()))
        {
            try
            {
                ServerContext.getInstance().deleteSemaphore(semaphoreName);
                sendResponse(json.get(Defines.JSON_OPERATION_TYPE).getAsString(),  semaphoreName, Defines.RESPONSE_OK);
            }
            catch (DistributedSemaphoreException e)
            {
                e.printStackTrace();
                sendErrorResponse(json.get(Defines.JSON_OPERATION_TYPE).getAsString(),  semaphoreName, Defines.RESPONSE_ERROR, e.getMessage());
            }

        }


    }

    private synchronized void handleLockSem(JsonObject json)
    {
        String clientName = getClientNameFromSocket();
        String semaphoreName = json.get(Defines.JSON_SEMAPHORE_NAME).getAsString();
        ServerContext.getInstance().createSemaphore(semaphoreName);

        ServerContext.getInstance().addToQueue(semaphoreName, clientName);
        Queue<String> q = ServerContext.getInstance().getClientQueue(semaphoreName);

        sendResponse(json.get(Defines.JSON_OPERATION_TYPE).getAsString(), semaphoreName, q.size() == 1 ? Defines.RESPONSE_ENTER : Defines.RESPONSE_WAIT);

        // TODO zrobić odpytywanie czy nadal żyje GET_AWAITING

    }

    private synchronized void handleDeleteSem(JsonObject json)
    {
        try
        {
            ServerContext.getInstance().deleteSemaphore(json.get(Defines.JSON_SEMAPHORE_NAME).getAsString());
            sendResponse(json.get(Defines.JSON_OPERATION_TYPE).getAsString(),  json.get(Defines.JSON_SEMAPHORE_NAME).getAsString(), Defines.RESPONSE_OK);

        } catch (DistributedSemaphoreException e)
        {
            log.warning(e.getMessage());
            e.printStackTrace();
            sendErrorResponse(json.get(Defines.JSON_OPERATION_TYPE).getAsString(), json.get(Defines.JSON_SEMAPHORE_NAME).getAsString(), Defines.RESPONSE_ERROR, e.getMessage());
        }
    }

    private synchronized void handleCreateSem(JsonObject json)
    {
        ServerContext.getInstance().createSemaphore(json.get(Defines.JSON_SEMAPHORE_NAME).getAsString());

        sendResponse(json.get(Defines.JSON_OPERATION_TYPE).getAsString(), json.get(Defines.JSON_SEMAPHORE_NAME).getAsString(), Defines.RESPONSE_CREATED_SEMAPHORE);
    }


    private String getClientNameFromSocket()
    {
        // Client name = ip address
        StringBuilder stringBuilder = new StringBuilder();
        InetSocketAddress address = (InetSocketAddress)socket.getRemoteSocketAddress();
        stringBuilder.append(address.getAddress().toString().replace("/", ""));

        return stringBuilder.toString();
    }


    private void sendResponse(String type, String semName, String result)
    {
        JsonObject json = new JsonObject();
        json.addProperty("type", type);
        json.addProperty("sem_name", semName);
        json.addProperty("result", result);

        send(json);
    }

    private void sendErrorResponse(String type, String semName, String result, String message)
    {
        JsonObject json = new JsonObject();
        json.addProperty("type", type);
        json.addProperty("sem_name", semName);
        json.addProperty("result", result);
        json.addProperty("message", message);

        send(json);
    }

    private void send(JsonObject json)
    {
        try
        {
            OutputStream os = socket.getOutputStream();
            DataOutputStream dos = new DataOutputStream(os);
            dos.writeBytes(json.toString());
            dos.flush();
        }
        catch (IOException e)
        {
            e.printStackTrace();
        }
    }
}
