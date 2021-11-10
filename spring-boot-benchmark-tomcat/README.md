# Spring Boot Benchmark Tomcat

This application takes the spring-boot-benchmark-original and replaces webflux with web to test Tomcat vs Netty.

The following is the logs of the startup running on my box.

```
Calculating JVM memory based on 6868948K available memory
Calculated JVM Memory Configuration: -XX:MaxDirectMemorySize=10M -Xmx6271773K -XX:MaxMetaspaceSize=85175K -XX:ReservedCodeCacheSize=240M -Xss1M (Total Memory: 6868948K, Thread Count: 250, Loaded Class Count: 12624, Headroom: 0%)
Enabling Java Native Memory Tracking
Adding 128 container CA certificates to JVM truststore
Picked up JAVA_TOOL_OPTIONS: -XX:ActiveProcessorCount=1 -Djava.security.properties=/layers/paketo-buildpacks_bellsoft-liberica/java-security-properties/java-security.properties -XX:+ExitOnOutOfMemoryError -XX:MaxDirectMemorySize=10M -Xmx6271773K -XX:MaxMetaspaceSize=85175K -XX:ReservedCodeCacheSize=240M -Xss1M -XX:+UnlockDiagnosticVMOptions -XX:NativeMemoryTracking=summary -XX:+PrintNMTStatistics

  .   ____          _            __ _ _
 /\\ / ___'_ __ _ _(_)_ __  __ _ \ \ \ \
( ( )\___ | '_ | '_| | '_ \/ _` | \ \ \ \
 \\/  ___)| |_)| | | | | || (_| |  ) ) ) )
  '  |____| .__|_| |_|_| |_\__, | / / / /
 =========|_|==============|___/=/_/_/_/
 :: Spring Boot ::                (v2.5.6)

2021-11-09 22:28:16.291  INFO 1 --- [           main] miller79.Application                     : Starting Application v0.0.1-SNAPSHOT using Java 11.0.13 on 9dc532cd5c41 with PID 1 (/workspace/BOOT-INF/classes started by cnb in /workspace)
2021-11-09 22:28:16.374  INFO 1 --- [           main] miller79.Application                     : No active profile set, falling back to default profiles: default
2021-11-09 22:28:21.711  INFO 1 --- [           main] o.s.b.w.embedded.tomcat.TomcatWebServer  : Tomcat initialized with port(s): 8080 (http)
2021-11-09 22:28:21.784  INFO 1 --- [           main] o.apache.catalina.core.StandardService   : Starting service [Tomcat]
2021-11-09 22:28:21.785  INFO 1 --- [           main] org.apache.catalina.core.StandardEngine  : Starting Servlet engine: [Apache Tomcat/9.0.54]
2021-11-09 22:28:21.998  INFO 1 --- [           main] o.a.c.c.C.[Tomcat].[localhost].[/]       : Initializing Spring embedded WebApplicationContext
2021-11-09 22:28:21.999  INFO 1 --- [           main] w.s.c.ServletWebServerApplicationContext : Root WebApplicationContext: initialization completed in 5427 ms
2021-11-09 22:28:25.404  INFO 1 --- [           main] o.s.b.a.e.web.EndpointLinksResolver      : Exposing 1 endpoint(s) beneath base path '/actuator'
2021-11-09 22:28:25.682  INFO 1 --- [           main] o.s.b.w.embedded.tomcat.TomcatWebServer  : Tomcat started on port(s): 8080 (http) with context path ''
2021-11-09 22:28:25.787  INFO 1 --- [           main] miller79.Application                     : Started Application in 11.882 seconds (JVM running for 13.315)
```