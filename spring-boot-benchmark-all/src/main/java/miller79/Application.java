package miller79;

import org.apache.activemq.ActiveMQConnectionFactory;
import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;
import org.springframework.context.annotation.Bean;

@SpringBootApplication(proxyBeanMethods = false)
public class Application {
    public static void main(String[] args) {
        SpringApplication.run(Application.class, args).close();
    }

    @Bean
    ActiveMQConnectionFactory activeMqConnectionFactory() {
        return new ActiveMQConnectionFactory();
    }
}
