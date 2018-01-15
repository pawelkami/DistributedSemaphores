package pl.edu.pw.elka;

/**
 * Klasa reprezentująca wyjątek, który wystąpił po stronie klienta.
 */
public class ClientException extends Exception {
    public ClientException(String msg) {
        super(msg);
    }
}
