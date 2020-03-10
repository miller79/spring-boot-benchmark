# Spring Boot Benchmark Data Keycloak

This application takes the `spring-boot-benchmark-original` project and changes `spring-boot-starter-webflux` to `spring-boot-starter-web` and adds `keycloak-spring-boot-starter`.
Observations with this involves the change to using Tomcat vs Netty which is known to be a bit slower.
Keycloak itself does not appear to add a significant time to the startup times.

The following is the logs of the startup running on my box.

```
  .   ____          _            __ _ _
 /\\ / ___'_ __ _ _(_)_ __  __ _ \ \ \ \
( ( )\___ | '_ | '_| | '_ \/ _` | \ \ \ \
 \\/  ___)| |_)| | | | | || (_| |  ) ) ) )
  '  |____| .__|_| |_|_| |_\__, | / / / /
 =========|_|==============|___/=/_/_/_/
 :: Spring Boot ::        (v2.2.5.RELEASE)

2020-03-10 16:41:18.294  INFO 1 --- [           main] miller79.Application                     : Starting Application on ad892b1f1adc with PID 1 (/app started by root in /)
2020-03-10 16:41:18.306  INFO 1 --- [           main] miller79.Application                     : No active profile set, falling back to default profiles: default
2020-03-10 16:41:38.599  INFO 1 --- [           main] o.s.b.w.embedded.tomcat.TomcatWebServer  : Tomcat initialized with port(s): 8080 (http)
2020-03-10 16:41:38.801  INFO 1 --- [           main] o.apache.catalina.core.StandardService   : Starting service [Tomcat]
2020-03-10 16:41:38.892  INFO 1 --- [           main] org.apache.catalina.core.StandardEngine  : Starting Servlet engine: [Apache Tomcat/9.0.31]
2020-03-10 16:41:40.603  INFO 1 --- [           main] o.a.c.c.C.[Tomcat].[localhost].[/]       : Initializing Spring embedded WebApplicationContext
2020-03-10 16:41:40.606  INFO 1 --- [           main] o.s.web.context.ContextLoader            : Root WebApplicationContext: initialization completed in 21505 ms
2020-03-10 16:41:45.906  INFO 1 --- [           main] o.s.b.w.embedded.tomcat.TomcatWebServer  : Tomcat started on port(s): 8080 (http) with context path ''
2020-03-10 16:41:46.005  INFO 1 --- [           main] miller79.Application                     : Started Application in 31.699 seconds (JVM running for 36.707)
```