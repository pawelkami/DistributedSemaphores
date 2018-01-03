package pl.edu.pw.elka;

import com.google.gson.Gson;
import com.google.gson.JsonElement;
import com.google.gson.JsonObject;
import com.sun.jmx.remote.util.ClassLogger;

import java.io.DataOutputStream;
import java.io.IOException;
import java.io.OutputStream;
import java.net.Socket;
import java.net.SocketException;
import java.util.concurrent.Callable;
import java.util.logging.Logger;

public class ClientRequestHandler implements Runnable {
    private static final int TIMEOUT = 5000;
    private static final int BUF_SIZE = 1024;
    private final Socket socket;

    private Logger log = Logger.getLogger(ClientRequestHandler.class.getName());

    public ClientRequestHandler(Socket s) throws SocketException {
        this.socket = s;
        this.socket.setSoTimeout(TIMEOUT);
    }

    @Override
    public void run() {

        try
        {
            String clientData = recv();

            //log.info("Data From Client :" + clientData);
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

    private void handleJsonRequest(JsonObject json) {
        //log.info("Handling JSON request");
        JsonElement opJson = json.get("type");

        if(!json.has(Defines.JSON_SEMAPHORE_NAME))
        {
            return;
        }

        switch(opJson.getAsString())
        {
            case Defines.OPERATION_PING:
                handlePing(json);
                break;
        }



    }

    private void handlePing(JsonObject json) {
        sendResponse(Defines.RESPONSE_PONG, json.get(Defines.JSON_SEMAPHORE_NAME).getAsString(), "");
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

            //log.info("Sending: " + json.toString());
            dos.flush();
        }
        catch (IOException e)
        {
            e.printStackTrace();
        }
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
            clientData.append(redDataText);
        } while(clientData.lastIndexOf("}") == -1);
        //log.info("Received: " + clientData.toString());

        return clientData.toString();
    }
}
