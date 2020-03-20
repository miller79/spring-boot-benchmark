package miller79;

import javax.jms.ConnectionFactory;

import org.apache.activemq.ActiveMQConnectionFactory;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;

@Configuration
public class Config {
	@Bean
	public ConnectionFactory webMQConnectionFactory() {
		return new ActiveMQConnectionFactory("vm://localhost?broker.persistent=false");
	}
}
