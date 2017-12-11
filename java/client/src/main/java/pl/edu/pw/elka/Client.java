package pl.edu.pw.elka;

import com.google.gson.JsonElement;
import com.google.gson.JsonObject;
import com.google.gson.JsonParser;
import com.google.gson.JsonPrimitive;

import java.io.*;
import java.net.*;
import java.util.regex.Pattern;

public class Client {
    private static final int SERVER_PORT = 8080;

    Client()
    {

    }

    public void createSemaphore(String name) throws ClientException {
        if(name.lastIndexOf(".") == -1)
            throw new ClientException("Wrong format of semaphore name. Should be server_name.semaphore_name");

        String[] arr = name.split(Pattern.quote("."));
        if(arr.length != 2)
        {
            throw new ClientException("Wrong format of semaphore name. Should be server_name.semaphore_name");
        }

        JsonObject json = new JsonObject();
        json.addProperty(Defines.JSON_OPERATION_TYPE, Defines.OPERATION_CREATE_SEMAPHORE);
        json.addProperty(Defines.JSON_SEMAPHORE_NAME, arr[1]);

        JsonObject response = sendToServer(json, arr[0]);

        System.out.println("Received response " + response.toString());

        // todo dodac do listy semaforow
        // todo sprawdzic odpowiedz serwera

    }

    private JsonObject sendToServer(JsonObject json, String serverName) throws ClientException {
        try(Socket socket = new Socket(serverName, SERVER_PORT))
        {
            DataOutputStream sockOut = new DataOutputStream(socket.getOutputStream());
            DataInputStream sockIn = new DataInputStream(socket.getInputStream());

            sockOut.writeBytes(json.toString());

            String response = sockIn.readUTF();

            JsonParser parser = new JsonParser();

            return parser.parse(response).getAsJsonObject();

        } catch (UnknownHostException e) {
            e.printStackTrace();
            throw new ClientException("Could not get host address for '" + serverName + "'");
        } catch (IOException e) {
            e.printStackTrace();
            throw new ClientException("Could not get connect to '" + serverName + "'");
        }
    }
}
