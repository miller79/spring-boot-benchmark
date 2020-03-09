# Spring Boot Benchmark Data JPA

This application takes the `spring-boot-benchmark-original` project and adds H2 and `spring-boot-starter-data-jpa`.
The analysis after adding this using the restriction of .4 CPU appears to be an additional 15-20 seconds of bootup time.
The main culprit of this time seems to be within the `HibernateJpaAutoConfiguration` which appears to start up both Hikari and Hibernate even though lazy-initialization is on.

The following is the logs of the startup running on my box.

```
  .   ____          _            __ _ _
 /\\ / ___'_ __ _ _(_)_ __  __ _ \ \ \ \
( ( )\___ | '_ | '_| | '_ \/ _` | \ \ \ \
 \\/  ___)| |_)| | | | | || (_| |  ) ) ) )
  '  |____| .__|_| |_|_| |_\__, | / / / /
 =========|_|==============|___/=/_/_/_/
 :: Spring Boot ::        (v2.2.5.RELEASE)

2020-03-09 16:45:46.503  INFO 1 --- [           main] miller79.Application                     : Starting Application on 83febf0f84fd with PID 1 (/app started by root in /)
2020-03-09 16:45:46.598  INFO 1 --- [           main] miller79.Application                     : No active profile set, falling back to default profiles: default
2020-03-09 16:46:04.194  INFO 1 --- [           main] .s.d.r.c.RepositoryConfigurationDelegate : Bootstrapping Spring Data JPA repositories in LAZY mode.
2020-03-09 16:46:04.410  INFO 1 --- [           main] .s.d.r.c.RepositoryConfigurationDelegate : Finished Spring Data repository scanning in 107ms. Found 0 JPA repository interfaces.
2020-03-09 16:46:13.209  INFO 1 --- [           main] o.s.s.concurrent.ThreadPoolTaskExecutor  : Initializing ExecutorService 'applicationTaskExecutor'
2020-03-09 16:46:13.303  INFO 1 --- [           main] com.zaxxer.hikari.HikariDataSource       : HikariPool-1 - Starting...
2020-03-09 16:46:15.894  INFO 1 --- [           main] com.zaxxer.hikari.HikariDataSource       : HikariPool-1 - Start completed.
2020-03-09 16:46:17.295  INFO 1 --- [         task-1] o.hibernate.jpa.internal.util.LogHelper  : HHH000204: Processing PersistenceUnitInfo [name: default]
2020-03-09 16:46:18.493  INFO 1 --- [         task-1] org.hibernate.Version                    : HHH000412: Hibernate ORM core version 5.4.12.Final
2020-03-09 16:46:20.900  INFO 1 --- [           main] o.s.b.web.embedded.netty.NettyWebServer  : Netty started on port(s): 8080
2020-03-09 16:46:20.994  INFO 1 --- [           main] miller79.Application                     : Started Application in 41.612 seconds (JVM running for 47.826)
2020-03-09 16:46:21.002  INFO 1 --- [         task-1] o.hibernate.annotations.common.Version   : HCANN000001: Hibernate Commons Annotations {5.1.0.Final}
2020-03-09 16:46:22.901  INFO 1 --- [         task-1] org.hibernate.dialect.Dialect            : HHH000400: Using dialect: org.hibernate.dialect.H2Dialect
2020-03-09 16:46:27.803  INFO 1 --- [         task-1] o.h.e.t.j.p.i.JtaPlatformInitiator       : HHH000490: Using JtaPlatform implementation: [org.hibernate.engine.transaction.jta.platform.internal.NoJtaPlatform]
2020-03-09 16:46:27.897  INFO 1 --- [         task-1] j.LocalContainerEntityManagerFactoryBean : Initialized JPA EntityManagerFactory for persistence unit 'default'
```