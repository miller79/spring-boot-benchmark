# Spring Boot Benchmark Data JPA

This application takes the `spring-boot-benchmark-original` project and adds H2 and `spring-boot-starter-data-jpa`.
The analysis after adding this using the restriction of .4 CPU appears to be an additional 15-20 seconds of bootup time.
The main culprit of this time seems to be within the `HibernateJpaAutoConfiguration` which appears to start up both Hikari and Hibernate even though lazy-initialization is on.

The following is the logs of the startup running on my box.

```
Calculating JVM memory based on 6859544K available memory
Calculated JVM Memory Configuration: -XX:MaxDirectMemorySize=10M -Xmx6437234K -XX:MaxMetaspaceSize=115109K -XX:ReservedCodeCacheSize=240M -Xss1M (Total Memory: 6859544K, Thread Count: 50, Loaded Class Count: 17909, Headroom: 0%)
Enabling Java Native Memory Tracking
Adding 128 container CA certificates to JVM truststore
Picked up JAVA_TOOL_OPTIONS: -XX:ActiveProcessorCount=1 -Djava.security.properties=/layers/paketo-buildpacks_bellsoft-liberica/java-security-properties/java-security.properties -XX:+ExitOnOutOfMemoryError -XX:MaxDirectMemorySize=10M -Xmx6437234K -XX:MaxMetaspaceSize=115109K -XX:ReservedCodeCacheSize=240M -Xss1M -XX:+UnlockDiagnosticVMOptions -XX:NativeMemoryTracking=summary -XX:+PrintNMTStatistics

  .   ____          _            __ _ _
 /\\ / ___'_ __ _ _(_)_ __  __ _ \ \ \ \
( ( )\___ | '_ | '_| | '_ \/ _` | \ \ \ \
 \\/  ___)| |_)| | | | | || (_| |  ) ) ) )
  '  |____| .__|_| |_|_| |_\__, | / / / /
 =========|_|==============|___/=/_/_/_/
 :: Spring Boot ::                (v2.5.6)

2021-11-09 22:10:50.470  INFO 1 --- [           main] miller79.Application                     : Starting Application v0.0.1-SNAPSHOT using Java 11.0.13 on f6f488517472 with PID 1 (/workspace/BOOT-INF/classes started by cnb in /workspace)
2021-11-09 22:10:50.473  INFO 1 --- [           main] miller79.Application                     : No active profile set, falling back to default profiles: default
2021-11-09 22:10:55.083  INFO 1 --- [           main] .s.d.r.c.RepositoryConfigurationDelegate : Bootstrapping Spring Data JPA repositories in DEFAULT mode.
2021-11-09 22:10:55.178  INFO 1 --- [           main] .s.d.r.c.RepositoryConfigurationDelegate : Finished Spring Data repository scanning in 77 ms. Found 0 JPA repository interfaces.
2021-11-09 22:10:58.286  INFO 1 --- [           main] com.zaxxer.hikari.HikariDataSource       : HikariPool-1 - Starting...
2021-11-09 22:10:59.279  INFO 1 --- [           main] com.zaxxer.hikari.HikariDataSource       : HikariPool-1 - Start completed.
2021-11-09 22:10:59.681  INFO 1 --- [           main] o.hibernate.jpa.internal.util.LogHelper  : HHH000204: Processing PersistenceUnitInfo [name: default]
2021-11-09 22:11:00.001  INFO 1 --- [           main] org.hibernate.Version                    : HHH000412: Hibernate ORM core version 5.4.32.Final
2021-11-09 22:11:00.769  INFO 1 --- [           main] o.hibernate.annotations.common.Version   : HCANN000001: Hibernate Commons Annotations {5.1.2.Final}
2021-11-09 22:11:01.396  INFO 1 --- [           main] org.hibernate.dialect.Dialect            : HHH000400: Using dialect: org.hibernate.dialect.H2Dialect
2021-11-09 22:11:02.495  INFO 1 --- [           main] o.h.e.t.j.p.i.JtaPlatformInitiator       : HHH000490: Using JtaPlatform implementation: [org.hibernate.engine.transaction.jta.platform.internal.NoJtaPlatform]
2021-11-09 22:11:02.570  INFO 1 --- [           main] j.LocalContainerEntityManagerFactoryBean : Initialized JPA EntityManagerFactory for persistence unit 'default'
2021-11-09 22:11:04.881  INFO 1 --- [           main] o.s.b.a.e.web.EndpointLinksResolver      : Exposing 1 endpoint(s) beneath base path '/actuator'
2021-11-09 22:11:06.683  INFO 1 --- [           main] o.s.b.web.embedded.netty.NettyWebServer  : Netty started on port 8080
2021-11-09 22:11:06.778  INFO 1 --- [           main] miller79.Application                     : Started Application in 18.383 seconds (JVM running for 19.883)
```