# Spring Boot Benchmark Tomcat

This application takes the spring-boot-benchmark-original and replaces webflux with web to test Tomcat vs Netty.

The following is the logs of the startup running on my box.

```
  .   ____          _            __ _ _
 /\\ / ___'_ __ _ _(_)_ __  __ _ \ \ \ \
( ( )\___ | '_ | '_| | '_ \/ _` | \ \ \ \
 \\/  ___)| |_)| | | | | || (_| |  ) ) ) )
  '  |____| .__|_| |_|_| |_\__, | / / / /
 =========|_|==============|___/=/_/_/_/
 :: Spring Boot ::        (v2.2.5.RELEASE)

2020-03-11 22:16:52.406  INFO 1 --- [           main] miller79.Application                     : Starting Application on 4e3390868df0 with PID 1 (/app started by root in /)
2020-03-11 22:16:52.410  INFO 1 --- [           main] miller79.Application                     : No active profile set, falling back to default profiles: default
2020-03-11 22:16:59.909  INFO 1 --- [           main] o.s.b.w.embedded.tomcat.TomcatWebServer  : Tomcat initialized with port(s): 8080 (http)
2020-03-11 22:17:00.097  INFO 1 --- [           main] o.apache.catalina.core.StandardService   : Starting service [Tomcat]
2020-03-11 22:17:00.098  INFO 1 --- [           main] org.apache.catalina.core.StandardEngine  : Starting Servlet engine: [Apache Tomcat/9.0.31]
2020-03-11 22:17:00.905  INFO 1 --- [           main] o.a.c.c.C.[Tomcat].[localhost].[/]       : Initializing Spring embedded WebApplicationContext
2020-03-11 22:17:00.906  INFO 1 --- [           main] o.s.web.context.ContextLoader            : Root WebApplicationContext: initialization completed in 8201 ms
2020-03-11 22:17:06.208  INFO 1 --- [           main] o.s.b.w.embedded.tomcat.TomcatWebServer  : Tomcat started on port(s): 8080 (http) with context path ''
2020-03-11 22:17:06.302  INFO 1 --- [           main] miller79.Application                     : Started Application in 16.39 seconds (JVM running for 19.441)
```