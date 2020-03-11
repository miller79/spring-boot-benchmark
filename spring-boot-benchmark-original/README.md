# Spring Boot Benchmark Original

This application intends represents a barebones Spring Boot application optimized as much as possible to improve startup time.
Observations from this project include the following:

- Running the application using the main method improved startup time significantly
- Using Netty provided a noticeable improvement in startup time

The following is the logs of the startup running on my box.

```
  .   ____          _            __ _ _
 /\\ / ___'_ __ _ _(_)_ __  __ _ \ \ \ \
( ( )\___ | '_ | '_| | '_ \/ _` | \ \ \ \
 \\/  ___)| |_)| | | | | || (_| |  ) ) ) )
  '  |____| .__|_| |_|_| |_\__, | / / / /
 =========|_|==============|___/=/_/_/_/
 :: Spring Boot ::        (v2.2.5.RELEASE)

2020-03-11 19:19:08.010  INFO 1 --- [           main] miller79.Application                     : Starting Application on 3702526485d5 with PID 1 (/app started by root in /)
2020-03-11 19:19:08.093  INFO 1 --- [           main] miller79.Application                     : No active profile set, falling back to default profiles: default
2020-03-11 19:19:19.808  INFO 1 --- [           main] o.s.b.web.embedded.netty.NettyWebServer  : Netty started on port(s): 8080
2020-03-11 19:19:19.913  INFO 1 --- [           main] miller79.Application                     : Started Application in 15.387 seconds (JVM running for 18.495)
```