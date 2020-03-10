# Spring Boot Benchmark Original

This application takes the spring-boot-benchmark-original and adds `camel-activemq-starter`.
The observations seems to show that it adds an additional 7-10 seconds to startup time.

```
  .   ____          _            __ _ _
 /\\ / ___'_ __ _ _(_)_ __  __ _ \ \ \ \
( ( )\___ | '_ | '_| | '_ \/ _` | \ \ \ \
 \\/  ___)| |_)| | | | | || (_| |  ) ) ) )
  '  |____| .__|_| |_|_| |_\__, | / / / /
 =========|_|==============|___/=/_/_/_/
 :: Spring Boot ::        (v2.2.5.RELEASE)

2020-03-10 03:45:11.399  INFO 1 --- [           main] miller79.Application                     : Starting Application on a5ff495a11af with PID 1 (/app started by root in /)
2020-03-10 03:45:11.401  INFO 1 --- [           main] miller79.Application                     : No active profile set, falling back to default profiles: default
2020-03-10 03:45:31.607  INFO 1 --- [           main] trationDelegate$BeanPostProcessorChecker : Bean 'org.apache.camel.spring.boot.CamelAutoConfiguration' of type [org.apache.camel.spring.boot.CamelAutoConfiguration] is not eligible for getting processed by all BeanPostProcessors (for example: not eligible for auto-proxying)
2020-03-10 03:45:36.996  INFO 1 --- [           main] o.apache.camel.support.LRUCacheFactory   : Detected and using LURCacheFactory: camel-caffeine-lrucache
2020-03-10 03:45:39.098  INFO 1 --- [           main] o.a.c.s.boot.SpringBootRoutesCollector   : Loading additional Camel XML routes from: classpath:camel/*.xml
2020-03-10 03:45:39.100  INFO 1 --- [           main] o.a.c.s.boot.SpringBootRoutesCollector   : Loading additional Camel XML rests from: classpath:camel-rest/*.xml
2020-03-10 03:45:42.504  INFO 1 --- [           main] o.s.b.web.embedded.netty.NettyWebServer  : Netty started on port(s): 8080
2020-03-10 03:45:42.595  INFO 1 --- [           main] miller79.Application                     : Started Application in 36.29 seconds (JVM running for 42.869)
```