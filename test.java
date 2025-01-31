import java.rmi.registry.LocateRegistry;
import java.rmi.registry.Registry;

public class RMIClient {
    public static void main(String[] args) {
        try {
            Registry registry = LocateRegistry.getRegistry("localhost", 1099);
            Hello stub = (Hello) registry.lookup("HelloService");
            System.out.println("Response from Server: " + stub.sayHello());
        } catch (Exception e) {
            e.printStackTrace();
        }
    }
}