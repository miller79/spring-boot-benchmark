# Spring Boot Benchmark Data Keycloak

This application takes the `spring-boot-benchmark-original` project and changes `spring-boot-starter-webflux` to `spring-boot-starter-web` and adds `keycloak-spring-boot-starter`.
Observations with this involves the change to using Tomcat vs Netty which is known to be a bit slower.
Keycloak itself does not appear to add a significant time to the startup times.

The following is the logs of the startup running on my box.

```
Calculating JVM memory based on 6864940K available memory
Calculated JVM Memory Configuration: -XX:MaxDirectMemorySize=10M -Xmx6256952K -XX:MaxMetaspaceSize=95987K -XX:ReservedCodeCacheSize=240M -Xss1M (Total Memory: 6864940K, Thread Count: 250, Loaded Class Count: 14533, Headroom: 0%)
Enabling Java Native Memory Tracking
Adding 128 container CA certificates to JVM truststore
Picked up JAVA_TOOL_OPTIONS: -XX:ActiveProcessorCount=1 -Djava.security.properties=/layers/paketo-buildpacks_bellsoft-liberica/java-security-properties/java-security.properties -XX:+ExitOnOutOfMemoryError -XX:MaxDirectMemorySize=10M -Xmx6256952K -XX:MaxMetaspaceSize=95987K -XX:ReservedCodeCacheSize=240M -Xss1M -XX:+UnlockDiagnosticVMOptions -XX:NativeMemoryTracking=summary -XX:+PrintNMTStatistics

  .   ____          _            __ _ _
 /\\ / ___'_ __ _ _(_)_ __  __ _ \ \ \ \
( ( )\___ | '_ | '_| | '_ \/ _` | \ \ \ \
 \\/  ___)| |_)| | | | | || (_| |  ) ) ) )
  '  |____| .__|_| |_|_| |_\__, | / / / /
 =========|_|==============|___/=/_/_/_/
 :: Spring Boot ::                (v2.5.6)

2021-11-09 22:15:17.673  INFO 1 --- [           main] miller79.Application                     : Starting Application v0.0.1-SNAPSHOT using Java 11.0.13 on 97e873aa18e0 with PID 1 (/workspace/BOOT-INF/classes started by cnb in /workspace)
2021-11-09 22:15:17.679  INFO 1 --- [           main] miller79.Application                     : No active profile set, falling back to default profiles: default
2021-11-09 22:15:24.684  INFO 1 --- [           main] o.s.b.w.embedded.tomcat.TomcatWebServer  : Tomcat initialized with port(s): 8080 (http)
2021-11-09 22:15:24.772  INFO 1 --- [           main] o.apache.catalina.core.StandardService   : Starting service [Tomcat]
2021-11-09 22:15:24.772  INFO 1 --- [           main] org.apache.catalina.core.StandardEngine  : Starting Servlet engine: [Apache Tomcat/9.0.54]
2021-11-09 22:15:24.874  INFO 1 --- [           main] o.a.c.c.C.[Tomcat].[localhost].[/]       : Initializing Spring embedded WebApplicationContext
2021-11-09 22:15:24.875  INFO 1 --- [           main] w.s.c.ServletWebServerApplicationContext : Root WebApplicationContext: initialization completed in 6978 ms
2021-11-09 22:15:27.778  INFO 1 --- [           main] o.s.b.a.e.web.EndpointLinksResolver      : Exposing 1 endpoint(s) beneath base path '/actuator'
2021-11-09 22:15:27.981  INFO 1 --- [           main] o.s.b.w.embedded.tomcat.TomcatWebServer  : Tomcat started on port(s): 8080 (http) with context path ''
2021-11-09 22:15:28.075  INFO 1 --- [           main] miller79.Application                     : Started Application in 13.106 seconds (JVM running for 14.675)
```