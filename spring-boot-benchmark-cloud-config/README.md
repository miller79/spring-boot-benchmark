# Spring Boot Benchmark Original

This application takes the spring-boot-benchmark-original and adds `spring-cloud-starter-config`.
This shows the time added when adding this dependency.
Once adding this dependency, it was observed that the startup time added around 7 seconds.

The following is the logs of the startup running on my box.

```
  .   ____          _            __ _ _
 /\\ / ___'_ __ _ _(_)_ __  __ _ \ \ \ \
( ( )\___ | '_ | '_| | '_ \/ _` | \ \ \ \
 \\/  ___)| |_)| | | | | || (_| |  ) ) ) )
  '  |____| .__|_| |_|_| |_\__, | / / / /
 =========|_|==============|___/=/_/_/_/
 :: Spring Boot ::        (v2.2.5.RELEASE)

2020-03-10 03:11:06.998  INFO 1 --- [           main] c.c.c.ConfigServicePropertySourceLocator : Fetching config from server at : http://localhost:8888
2020-03-10 03:11:08.312  INFO 1 --- [           main] c.c.c.ConfigServicePropertySourceLocator : Connect Timeout Exception on Url - http://localhost:8888. Will be trying the next url if available
2020-03-10 03:11:08.313  WARN 1 --- [           main] c.c.c.ConfigServicePropertySourceLocator : Could not locate PropertySource: I/O error on GET request for "http://localhost:8888/application/default": Connection refused (Connection refused); nested exception is java.net.ConnectException: Connection refused (Connection refused)
2020-03-10 03:11:08.395  INFO 1 --- [           main] miller79.Application                     : No active profile set, falling back to default profiles: default
2020-03-10 03:11:16.696  INFO 1 --- [           main] o.s.cloud.context.scope.GenericScope     : BeanFactory id=3c43be89-354f-332d-9454-965348ff8eed
2020-03-10 03:11:23.496  INFO 1 --- [           main] o.s.b.web.embedded.netty.NettyWebServer  : Netty started on port(s): 8080
2020-03-10 03:11:23.805  INFO 1 --- [           main] miller79.Application                     : Started Application in 30.697 seconds (JVM running for 39.079)
```