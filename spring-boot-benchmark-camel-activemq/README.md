# Spring Boot Benchmark Camel ActiveMQ

This application takes the spring-boot-benchmark-original and adds `camel-activemq-starter`.
The observations seems to show that it adds an additional 7-10 seconds to startup time.

```
Calculating JVM memory based on 6859416K available memory
Calculated JVM Memory Configuration: -XX:MaxDirectMemorySize=10M -Xmx6243187K -XX:MaxMetaspaceSize=104228K -XX:ReservedCodeCacheSize=240M -Xss1M (Total Memory: 6859416K, Thread Count: 250, Loaded Class Count: 15988, Headroom: 0%)
Enabling Java Native Memory Tracking
Adding 128 container CA certificates to JVM truststore
Picked up JAVA_TOOL_OPTIONS: -XX:ActiveProcessorCount=1 -Djava.security.properties=/layers/paketo-buildpacks_bellsoft-liberica/java-security-properties/java-security.properties -XX:+ExitOnOutOfMemoryError -XX:MaxDirectMemorySize=10M -Xmx6243187K -XX:MaxMetaspaceSize=104228K -XX:ReservedCodeCacheSize=240M -Xss1M -XX:+UnlockDiagnosticVMOptions -XX:NativeMemoryTracking=summary -XX:+PrintNMTStatistics

  .   ____          _            __ _ _
 /\\ / ___'_ __ _ _(_)_ __  __ _ \ \ \ \
( ( )\___ | '_ | '_| | '_ \/ _` | \ \ \ \
 \\/  ___)| |_)| | | | | || (_| |  ) ) ) )
  '  |____| .__|_| |_|_| |_\__, | / / / /
 =========|_|==============|___/=/_/_/_/
 :: Spring Boot ::                (v2.5.6)

2021-11-09 22:08:46.196  INFO 1 --- [           main] miller79.Application                     : Starting Application v0.0.1-SNAPSHOT using Java 11.0.13 on 73f419907ddd with PID 1 (/workspace/BOOT-INF/classes started by cnb in /workspace)
2021-11-09 22:08:46.198  INFO 1 --- [           main] miller79.Application                     : No active profile set, falling back to default profiles: default
2021-11-09 22:08:53.681  INFO 1 --- [           main] o.s.b.w.embedded.tomcat.TomcatWebServer  : Tomcat initialized with port(s): 8080 (http)
2021-11-09 22:08:53.693  INFO 1 --- [           main] o.apache.catalina.core.StandardService   : Starting service [Tomcat]
2021-11-09 22:08:53.693  INFO 1 --- [           main] org.apache.catalina.core.StandardEngine  : Starting Servlet engine: [Apache Tomcat/9.0.54]
2021-11-09 22:08:54.072  INFO 1 --- [           main] o.a.c.c.C.[Tomcat].[localhost].[/]       : Initializing Spring embedded WebApplicationContext
2021-11-09 22:08:54.076  INFO 1 --- [           main] w.s.c.ServletWebServerApplicationContext : Root WebApplicationContext: initialization completed in 7492 ms
2021-11-09 22:09:00.688  INFO 1 --- [           main] o.s.b.a.e.web.EndpointLinksResolver      : Exposing 1 endpoint(s) beneath base path '/actuator'
2021-11-09 22:09:00.977  INFO 1 --- [           main] o.s.b.w.embedded.tomcat.TomcatWebServer  : Tomcat started on port(s): 8080 (http) with context path ''
2021-11-09 22:09:01.188  INFO 1 --- [           main] o.a.c.impl.engine.AbstractCamelContext   : Routes startup summary (total:0 started:0)
2021-11-09 22:09:01.189  INFO 1 --- [           main] o.a.c.impl.engine.AbstractCamelContext   : Apache Camel 3.11.3 (camel-1) started in 384ms (build:279ms init:102ms start:3ms)
2021-11-09 22:09:01.271  INFO 1 --- [           main] miller79.Application                     : Started Application in 17.474 seconds (JVM running for 19.277)
```