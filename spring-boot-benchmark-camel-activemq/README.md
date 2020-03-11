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

2020-03-11 18:56:17.999  INFO 1 --- [           main] miller79.Application                     : Starting Application on 4131dae23a32 with PID 1 (/app started by root in /)
2020-03-11 18:56:18.010  INFO 1 --- [           main] miller79.Application                     : No active profile set, falling back to default profiles: default
2020-03-11 18:56:30.792  INFO 1 --- [           main] trationDelegate$BeanPostProcessorChecker : Bean 'org.apache.camel.spring.boot.CamelAutoConfiguration' of type [org.apache.camel.spring.boot.CamelAutoConfiguration] is not eligible for getting processed by all BeanPostProcessors (for example: not eligible for auto-proxying)
2020-03-11 18:56:32.991  INFO 1 --- [           main] o.apache.camel.support.LRUCacheFactory   : Detected and using LURCacheFactory: camel-caffeine-lrucache
2020-03-11 18:56:34.397  INFO 1 --- [           main] o.a.c.s.boot.SpringBootRoutesCollector   : Loading additional Camel XML routes from: classpath:camel/*.xml
2020-03-11 18:56:34.400  INFO 1 --- [           main] o.a.c.s.boot.SpringBootRoutesCollector   : Loading additional Camel XML rests from: classpath:camel-rest/*.xml
2020-03-11 18:56:37.006  INFO 1 --- [           main] o.s.b.web.embedded.netty.NettyWebServer  : Netty started on port(s): 8080
2020-03-11 18:56:37.092  INFO 1 --- [           main] miller79.Application                     : Started Application in 22.099 seconds (JVM running for 25.338)
```