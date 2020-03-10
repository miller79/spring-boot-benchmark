package miller79;

import org.springframework.boot.autoconfigure.SpringBootApplication;

import io.micronaut.runtime.Micronaut;

@SpringBootApplication(proxyBeanMethods = false)
public class Application {
	public static void main(String[] args) {
		Micronaut.run(Application.class);
	}
}
