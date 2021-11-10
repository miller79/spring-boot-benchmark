# Spring Boot Benchmark Original

This application intends represents a barebones Spring Boot application optimized as much as possible to improve startup time.
Observations from this project include the following:

- Running the application using the main method improved startup time significantly
- Using Netty provided a noticeable improvement in startup time

The following is the logs of the startup running on my box.

```
Calculating JVM memory based on 6867584K available memory
Calculated JVM Memory Configuration: -XX:MaxDirectMemorySize=10M -Xmx6471317K -XX:MaxMetaspaceSize=89066K -XX:ReservedCodeCacheSize=240M -Xss1M (Total Memory: 6867584K, Thread Count: 50, Loaded Class Count: 13311, Headroom: 0%)
Enabling Java Native Memory Tracking
Adding 128 container CA certificates to JVM truststore
Picked up JAVA_TOOL_OPTIONS: -XX:ActiveProcessorCount=1 -Djava.security.properties=/layers/paketo-buildpacks_bellsoft-liberica/java-security-properties/java-security.properties -XX:+ExitOnOutOfMemoryError -XX:MaxDirectMemorySize=10M -Xmx6471317K -XX:MaxMetaspaceSize=89066K -XX:ReservedCodeCacheSize=240M -Xss1M -XX:+UnlockDiagnosticVMOptions -XX:NativeMemoryTracking=summary -XX:+PrintNMTStatistics

  .   ____          _            __ _ _
 /\\ / ___'_ __ _ _(_)_ __  __ _ \ \ \ \
( ( )\___ | '_ | '_| | '_ \/ _` | \ \ \ \
 \\/  ___)| |_)| | | | | || (_| |  ) ) ) )
  '  |____| .__|_| |_|_| |_\__, | / / / /
 =========|_|==============|___/=/_/_/_/
 :: Spring Boot ::                (v2.5.6)

2021-11-09 22:26:47.785  INFO 1 --- [           main] miller79.Application                     : Starting Application vLOCAL-SNAPSHOT using Java 11.0.13 on a36d6f25c502 with PID 1 (/workspace/BOOT-INF/classes started by cnb in /workspace)
2021-11-09 22:26:47.787  INFO 1 --- [           main] miller79.Application                     : No active profile set, falling back to default profiles: default
2021-11-09 22:26:53.204  INFO 1 --- [           main] o.s.b.a.e.web.EndpointLinksResolver      : Exposing 1 endpoint(s) beneath base path '/actuator'
2021-11-09 22:26:55.485  INFO 1 --- [           main] o.s.b.web.embedded.netty.NettyWebServer  : Netty started on port 8080
2021-11-09 22:26:55.575  INFO 1 --- [           main] miller79.Application                     : Started Application in 9.477 seconds (JVM running for 10.879)
```