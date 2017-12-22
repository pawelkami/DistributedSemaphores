package pl.edu.pw.elka;

import com.google.gson.Gson;
import com.google.gson.JsonElement;
import com.google.gson.JsonObject;
import com.google.gson.JsonParser;

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
    private static int TIMEOUT = 5000;

    public RequestHandler(Socket connection) throws SocketException {
        this.socket = connection;
        this.socket.setSoTimeout(TIMEOUT);
    }

    @Override
    public void run() {

        try
        {
            String clientData = recv();

            log.info("Data From Client :" + clientData);
            JsonObject jobj = new Gson().fromJson(clientData, JsonObject.class);
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
        } catch (InterruptedException e) {
            e.printStackTrace();
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
                ServerContext.getInstance().removeFromQueue(semaphoreName, getClientNameFromSocket());
                sendResponse(json.get(Defines.JSON_OPERATION_TYPE).getAsString(),  semaphoreName, Defines.RESPONSE_OK);
            }
            catch (DistributedSemaphoreException e)
            {
                e.printStackTrace();
                sendErrorResponse(json.get(Defines.JSON_OPERATION_TYPE).getAsString(),  semaphoreName, Defines.RESPONSE_ERROR, e.getMessage());
            }

        }


    }

    private synchronized void handleLockSem(JsonObject json) throws InterruptedException {
        String clientName = getClientNameFromSocket();
        String semaphoreName = json.get(Defines.JSON_SEMAPHORE_NAME).getAsString();
        ServerContext.getInstance().createSemaphore(semaphoreName);

        ServerContext.getInstance().addToQueue(semaphoreName, clientName);
        Queue<String> q = ServerContext.getInstance().getClientQueue(semaphoreName);

        if(q.size() == 1)
        {
            sendResponse(json.get(Defines.JSON_OPERATION_TYPE).getAsString(), semaphoreName, Defines.RESPONSE_ENTER);
            // todo sprawdzanie czy jeszcze siedzi w sekcji krytycznej
            return;
        }
        else
        {
            sendResponse(json.get(Defines.JSON_OPERATION_TYPE).getAsString(), semaphoreName, Defines.RESPONSE_WAIT);
        }

        try
        {

            while(true)
            {
                Thread.sleep(1000);
                q = ServerContext.getInstance().getClientQueue(semaphoreName);  // check if semaphore is free
                if(q.peek().equals(clientName))
                {
                    sendResponse(json.get(Defines.JSON_OPERATION_TYPE).getAsString(), semaphoreName, Defines.RESPONSE_ENTER);
                    return;
                }

                sendResponse(Defines.OPERATION_PING, semaphoreName, "");

                String clientResponse = recv();

                JsonParser parser = new JsonParser();
                JsonObject clientJsonResponse = parser.parse(clientResponse).getAsJsonObject();

                if(!(clientJsonResponse.has(Defines.JSON_OPERATION_TYPE) && clientJsonResponse.get(Defines.JSON_OPERATION_TYPE).getAsString().equals(Defines.RESPONSE_PONG)))
                {
                    removeClientFromSemQueue(semaphoreName, clientName);

                    return;
                }

            }
        }
        catch (IOException e)
        {
            log.warning("Client disconnected. Removing him from queue.");
            removeClientFromSemQueue(semaphoreName, clientName);
            e.printStackTrace();
        }



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

            log.info("Sending: " + json.toString());
            dos.flush();
        }
        catch (IOException e)
        {
            e.printStackTrace();
        }
    }

    // remove client from queue if it crashes
    private synchronized void removeClientFromSemQueue(String semName, String clientName)
    {
        Queue<String> q = ServerContext.getInstance().getClientQueue(semName);
        q.remove(clientName);
    }

    private String recv() throws IOException {
        byte[] byteArr = new byte[BUF_SIZE];
        StringBuilder clientData = new StringBuilder();
        String redDataText;
        byte[] redData;
        int red = -1;

        do
        {
            if((red = socket.getInputStream().read(byteArr)) == -1)
            {
                log.warning("Problem reading socket stream");
                throw new IOException("Problem reading socket stream");
            }

            redData = new byte[red];
            System.arraycopy(byteArr, 0, redData, 0, red);
            redDataText = new String(redData,"UTF-8"); // assumption that client sends data UTF-8 encoded
            log.info("message part received:" + redDataText + "len: " + red);
            clientData.append(redDataText);
        } while(clientData.lastIndexOf("}") == -1);
        log.info("Received: " + clientData.toString());

        return clientData.toString();
    }

}
