package pl.edu.pw.elka;

public class Defines {

    public static final String JSON_OPERATION_TYPE = "type";
    public static final String JSON_RESULT = "result";
    public static final String JSON_SEMAPHORE_NAME = "sem_name";
    public static final String JSON_MESSAGE = "message";

    // JSON for client - client (deadlock detection)
    public static final String JSON_BLOCKED_ID = "blocked_client_id";
    public static final String JSON_SRC_CLIENT_ID = "src_client_id";
    public static final String JSON_DST_CLIENT_ID = "dst_client_id";


    // client -> server
    public static final String OPERATION_CREATE_SEMAPHORE = "CREATE";
    public static final String OPERATION_LOCK = "LOCK";
    public static final String OPERATION_UNLOCK = "UNLOCK";
    public static final String OPERATION_DELETE = "DELETE";
    public static final String OPERATION_GET_AWAITING = "GET_AWAITING";
    public static final String RESPONSE_PONG = "PONG";


    // server -> client
    public static final String RESPONSE_CREATED_SEMAPHORE = "CREATED";
    public static final String RESPONSE_WAIT = "WAIT";
    public static final String RESPONSE_ENTER = "ENTER";
    public static final String RESPONSE_ERROR = "ERROR";
    public static final String RESPONSE_OK = "OK";
    public static final String RESPONSE_AWAITING = "AWAITING";
    public static final String OPERATION_PING = "PING";


    // client -> client
    public static final String OPERATION_PROBE = "PROBE";








}
