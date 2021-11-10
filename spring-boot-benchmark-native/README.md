# Spring Boot Benchmark Native

This application intends represents a barebones Spring Boot application but using GraalVM.
As expected, the startup time is very quick.

```
2021-11-09 22:25:12.160  INFO 1 --- [           main] o.s.nativex.NativeListener               : This application is bootstrapped with code generated with Spring AOT

  .   ____          _            __ _ _
 /\\ / ___'_ __ _ _(_)_ __  __ _ \ \ \ \
( ( )\___ | '_ | '_| | '_ \/ _` | \ \ \ \
 \\/  ___)| |_)| | | | | || (_| |  ) ) ) )
  '  |____| .__|_| |_|_| |_\__, | / / / /
 =========|_|==============|___/=/_/_/_/
 :: Spring Boot ::                (v2.5.6)

2021-11-09 22:25:12.162  INFO 1 --- [           main] miller79.Application                     : Starting Application using Java 11.0.13 on 3e6cf9d62649 with PID 1 (/workspace/miller79.Application started by cnb in /workspace)
2021-11-09 22:25:12.162  INFO 1 --- [           main] miller79.Application                     : No active profile set, falling back to default profiles: default
2021-11-09 22:25:12.220  INFO 1 --- [           main] o.s.b.a.e.web.EndpointLinksResolver      : Exposing 1 endpoint(s) beneath base path '/actuator'
2021-11-09 22:25:12.226  WARN 1 --- [           main] i.m.c.i.binder.jvm.JvmGcMetrics          : GC notifications will not be available because MemoryPoolMXBeans are not provided by the JVM
2021-11-09 22:25:12.269  INFO 1 --- [           main] o.s.b.web.embedded.netty.NettyWebServer  : Netty started on port 8080
2021-11-09 22:25:12.271  INFO 1 --- [           main] miller79.Application                     : Started Application in 0.119 seconds (JVM running for 0.12)
```