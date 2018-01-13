package pl.edu.pw.elka;

import com.google.gson.JsonArray;
import com.google.gson.JsonObject;
import com.google.gson.JsonParser;

import java.io.DataOutputStream;
import java.io.IOException;
import java.net.InetAddress;
import java.net.Socket;
import java.net.UnknownHostException;
import java.util.logging.Logger;
import java.util.regex.Pattern;

public class Client {
    private static final int SERVER_PORT = 10080;
    private static final int TIMEOUT = 5000;
    private static final int BUF_SIZE = 1024;
    private Logger log = Logger.getLogger(Client.class.getName());

    Client() {

    }

    public void send(Socket socket, String msg) throws IOException {
        DataOutputStream sockOut = new DataOutputStream(socket.getOutputStream());

        sockOut.writeBytes(msg);
        log.info("Sending: " + msg);
    }


    public String recv(Socket socket) throws IOException {
        byte[] byteArr = new byte[BUF_SIZE];
        StringBuilder clientData = new StringBuilder();
        String redDataText;
        byte[] redData;
        int red = -1;

        do {
            if ((red = socket.getInputStream().read(byteArr)) == -1) {
                log.warning("Problem reading socket stream");
                throw new IOException("Problem reading socket stream");
            }

            redData = new byte[red];
            System.arraycopy(byteArr, 0, redData, 0, red);
            redDataText = new String(redData, "UTF-8"); // assumption that client sends data UTF-8 encoded
            clientData.append(redDataText);
        } while (clientData.lastIndexOf("}") == -1);
        log.info("Received: " + clientData.toString());

        return clientData.toString();
    }

    public String sendAndReceive(Socket socket, String msg) throws IOException {
        send(socket, msg);
        return recv(socket);
    }

    private JsonObject sendToServer(JsonObject json, String serverName) throws ClientException {
        try (Socket socket = new Socket(serverName, SERVER_PORT)) {
            socket.setSoTimeout(TIMEOUT);

            String response = sendAndReceive(socket, json.toString());

            JsonParser parser = new JsonParser();
            JsonObject jsonResponse = parser.parse(response).getAsJsonObject();

            if (!checkResponseFormat(jsonResponse))
                throw new ClientException("Wrong format of received response");

            return jsonResponse;

        } catch (UnknownHostException e) {
            e.printStackTrace();
            throw new ClientException("Could not get host address for '" + serverName + "'");
        } catch (IOException e) {
            e.printStackTrace();
            throw new ClientException("Could not get connect to '" + serverName + "'");
        }
    }

    void createSemaphore(String name) throws ClientException {
        String[] arr = splitSemaphoreName(name);

        JsonObject json = new JsonObject();
        json.addProperty(Defines.JSON_OPERATION_TYPE, Defines.OPERATION_CREATE_SEMAPHORE);
        json.addProperty(Defines.JSON_SEMAPHORE_NAME, arr[1]);

        JsonObject response = sendToServer(json, arr[0]);

        if (response.get(Defines.JSON_RESULT).getAsString().equals(Defines.RESPONSE_CREATED_SEMAPHORE)) {
            log.info("Semaphore " + name + " was created.");
        } else {
            log.info("Error: " + response.get(Defines.RESPONSE_ERROR));
        }
    }

    void deleteSemaphore(String name) throws ClientException {
        String[] arr = splitSemaphoreName(name);

        JsonObject json = new JsonObject();
        json.addProperty(Defines.JSON_OPERATION_TYPE, Defines.OPERATION_DELETE);
        json.addProperty(Defines.JSON_SEMAPHORE_NAME, arr[1]);

        JsonObject response = sendToServer(json, arr[0]);

        if (response.get(Defines.JSON_RESULT).getAsString().equals(Defines.RESPONSE_OK)) {
            log.info("Semaphore " + name + " was deleted.");
        } else {
            log.info("Error: " + response.get(Defines.RESPONSE_ERROR));
        }
    }

    public void lock(String[] names) throws ClientException {
        for (String n : names) {
            lock(n);
        }
    }

    public void lock(String name) throws ClientException {
        String[] arr = splitSemaphoreName(name);

        JsonObject json = new JsonObject();
        json.addProperty(Defines.JSON_OPERATION_TYPE, Defines.OPERATION_LOCK);
        json.addProperty(Defines.JSON_SEMAPHORE_NAME, arr[1]);
        String serverName = arr[0];

        try (Socket socket = new Socket(serverName, SERVER_PORT)) {
            socket.setSoTimeout(TIMEOUT);

            String response = sendAndReceive(socket, json.toString());

            JsonParser parser = new JsonParser();
            JsonObject jsonResponse = parser.parse(response).getAsJsonObject();

            if (!checkResponseFormat(jsonResponse))
                throw new ClientException("Wrong format of received response");

            String result = jsonResponse.get(Defines.JSON_RESULT).getAsString();
            if (result.equals(Defines.RESPONSE_ENTER)) {
                log.info("Entering critical section");

                Semaphore s = new Semaphore();
                s.isWaiting = false;
                s.name = name;
                CreatedSemaphores.getInstance().addSemaphore(s);
                return;
            }

            // PING-PONG
            if (result.equals(Defines.RESPONSE_WAIT)) {
                Semaphore s = new Semaphore();
                s.isWaiting = true;
                s.name = name;
                CreatedSemaphores.getInstance().addSemaphore(s);

                initializeDeadlockCheck(name);
                while (true) {
                    response = recv(socket);
                    parser = new JsonParser();
                    jsonResponse = parser.parse(response).getAsJsonObject();

                    if (jsonResponse.get(Defines.JSON_OPERATION_TYPE).getAsString().equals(Defines.OPERATION_PING)) {
                        json = new JsonObject();
                        json.addProperty(Defines.JSON_OPERATION_TYPE, Defines.RESPONSE_PONG);
                        json.addProperty(Defines.JSON_SEMAPHORE_NAME, name);

                        send(socket, json.toString());
                    } else if (jsonResponse.get(Defines.JSON_RESULT).getAsString().equals(Defines.RESPONSE_ENTER)) {
                        log.info("Entering critical section");

                        CreatedSemaphores.getInstance().changeSemaphoreWaitStatus(name, false);
                        return;
                    }
                }
            }

        } catch (UnknownHostException e) {
            e.printStackTrace();
            throw new ClientException("Could not get host address for '" + serverName + "'");
        } catch (IOException e) {
            e.printStackTrace();
            throw new ClientException("Could not get connect to '" + serverName + "'");
        }

    }

    private void initializeDeadlockCheck(String name) throws ClientException, UnknownHostException {
        String criticalSectionClient = getAwaiting(name);

        // if here is no client - don't check - probably we are in critical section right now
        if (criticalSectionClient.isEmpty())
            return;

        JsonObject json = new JsonObject();
        json.addProperty(Defines.JSON_OPERATION_TYPE, Defines.OPERATION_PROBE);
        try {
            json.addProperty(Defines.JSON_BLOCKED_ID, InetAddress.getLocalHost().getHostAddress());
            json.addProperty(Defines.JSON_SRC_CLIENT_ID, InetAddress.getLocalHost().getHostAddress());
        } catch (UnknownHostException e) {
            e.printStackTrace();
        }

        json.addProperty(Defines.JSON_DST_CLIENT_ID, criticalSectionClient);

        try (Socket s = new Socket(criticalSectionClient, RequestListener.CLIENT_PORT)) {
            send(s, json.toString());

        } catch (IOException e) {
            e.printStackTrace();
        }


    }


    private String[] splitSemaphoreName(String name) throws ClientException {
        if (name.lastIndexOf(".") == -1)
            throw new ClientException("Wrong format of semaphore name. Should be server_name.semaphore_name");

        String[] arr = name.split(Pattern.quote("."));
        if (arr.length != 2) {
            throw new ClientException("Wrong format of semaphore name. Should be server_name.semaphore_name");
        }

        return arr;
    }

    private boolean checkResponseFormat(JsonObject json) {
        return json.has(Defines.JSON_OPERATION_TYPE) && json.has(Defines.JSON_SEMAPHORE_NAME) && json.has(Defines.JSON_RESULT);
    }

    void unlock(String name) throws ClientException {
        String[] arr = splitSemaphoreName(name);

        JsonObject json = new JsonObject();
        json.addProperty(Defines.JSON_OPERATION_TYPE, Defines.OPERATION_UNLOCK);
        json.addProperty(Defines.JSON_SEMAPHORE_NAME, arr[1]);

        JsonObject response = sendToServer(json, arr[0]);

        if (response.get(Defines.JSON_RESULT).getAsString().equals(Defines.RESPONSE_OK)) {
            log.info("Semaphore " + name + " unlocked.");
            CreatedSemaphores.getInstance().deleteSemaphore(name);
        } else {
            log.info("Error: " + response.get(Defines.RESPONSE_ERROR));
        }
    }

    public String getAwaiting(String name) throws ClientException, UnknownHostException {
        String[] arr = splitSemaphoreName(name);

        JsonObject json = new JsonObject();
        json.addProperty(Defines.JSON_OPERATION_TYPE, Defines.OPERATION_GET_AWAITING);
        json.addProperty(Defines.JSON_SEMAPHORE_NAME, arr[1]);

        JsonObject response = sendToServer(json, arr[0]);

        if (checkResponseFormat(response)) {
            JsonArray semaphores = response.get(Defines.JSON_MESSAGE).getAsJsonArray();
            if (semaphores.size() > 1) {
                String lockedSemaphore = semaphores.get(0).getAsString();   // first client in list - current critical section owner
                if (lockedSemaphore.equalsIgnoreCase(InetAddress.getLocalHost().getHostAddress())) {
                    return "";
                }

                return lockedSemaphore;
            }

            return "";
        } else {
            throw new ClientException("Get awaiting response format is invalid");
        }
    }
}
