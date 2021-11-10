# Spring Boot Benchmark All [WIP]

This application represents a minimal version of a high dependency application.
The application this is modeled off of boots up in around 200 seconds.
The goal is to be able to see the progress over the individual pieces and ultimately the time as a whole.
I will attempt to update this README to ensure it is always up to date with the latest information.

The latest logs are the following.

```
Calculating JVM memory based on 6862208K available memory
Calculated JVM Memory Configuration: -XX:MaxDirectMemorySize=10M -Xmx6201952K -XX:MaxMetaspaceSize=148255K -XX:ReservedCodeCacheSize=240M -Xss1M (Total Memory: 6862208K, Thread Count: 250, Loaded Class Count: 23761, Headroom: 0%)
Enabling Java Native Memory Tracking
Adding 128 container CA certificates to JVM truststore
Picked up JAVA_TOOL_OPTIONS: -XX:ActiveProcessorCount=1 -Djava.security.properties=/layers/paketo-buildpacks_bellsoft-liberica/java-security-properties/java-security.properties -XX:+ExitOnOutOfMemoryError -XX:MaxDirectMemorySize=10M -Xmx6201952K -XX:MaxMetaspaceSize=148255K -XX:ReservedCodeCacheSize=240M -Xss1M -XX:+UnlockDiagnosticVMOptions -XX:NativeMemoryTracking=summary -XX:+PrintNMTStatistics

  .   ____          _            __ _ _
 /\\ / ___'_ __ _ _(_)_ __  __ _ \ \ \ \
( ( )\___ | '_ | '_| | '_ \/ _` | \ \ \ \
 \\/  ___)| |_)| | | | | || (_| |  ) ) ) )
  '  |____| .__|_| |_|_| |_\__, | / / / /
 =========|_|==============|___/=/_/_/_/
 :: Spring Boot ::                (v2.5.6)

2021-11-09 22:05:38.909  INFO 1 --- [           main] miller79.Application                     : Starting Application v0.0.1-SNAPSHOT using Java 11.0.13 on 991981741f07 with PID 1 (/workspace/BOOT-INF/classes started by cnb in /workspace)
2021-11-09 22:05:38.969  INFO 1 --- [           main] miller79.Application                     : No active profile set, falling back to default profiles: default
2021-11-09 22:05:46.872  INFO 1 --- [           main] .s.d.r.c.RepositoryConfigurationDelegate : Bootstrapping Spring Data JPA repositories in DEFAULT mode.
2021-11-09 22:05:46.983  INFO 1 --- [           main] .s.d.r.c.RepositoryConfigurationDelegate : Finished Spring Data repository scanning in 7 ms. Found 0 JPA repository interfaces.
2021-11-09 22:05:52.894  INFO 1 --- [           main] o.s.b.w.embedded.tomcat.TomcatWebServer  : Tomcat initialized with port(s): 8080 (http)
2021-11-09 22:05:52.971  INFO 1 --- [           main] o.apache.catalina.core.StandardService   : Starting service [Tomcat]
2021-11-09 22:05:52.972  INFO 1 --- [           main] org.apache.catalina.core.StandardEngine  : Starting Servlet engine: [Apache Tomcat/9.0.54]
2021-11-09 22:05:53.190  INFO 1 --- [           main] o.a.c.c.C.[Tomcat].[localhost].[/]       : Initializing Spring embedded WebApplicationContext
2021-11-09 22:05:53.191  INFO 1 --- [           main] w.s.c.ServletWebServerApplicationContext : Root WebApplicationContext: initialization completed in 13894 ms
2021-11-09 22:05:56.811  INFO 1 --- [           main] com.zaxxer.hikari.HikariDataSource       : HikariPool-1 - Starting...
2021-11-09 22:05:58.187  INFO 1 --- [           main] com.zaxxer.hikari.HikariDataSource       : HikariPool-1 - Start completed.
2021-11-09 22:05:58.575  INFO 1 --- [           main] o.hibernate.jpa.internal.util.LogHelper  : HHH000204: Processing PersistenceUnitInfo [name: default]
2021-11-09 22:05:58.806  INFO 1 --- [           main] org.hibernate.Version                    : HHH000412: Hibernate ORM core version 5.4.32.Final
2021-11-09 22:05:59.675  INFO 1 --- [           main] o.hibernate.annotations.common.Version   : HCANN000001: Hibernate Commons Annotations {5.1.2.Final}
2021-11-09 22:06:00.502  INFO 1 --- [           main] org.hibernate.dialect.Dialect            : HHH000400: Using dialect: org.hibernate.dialect.H2Dialect
2021-11-09 22:06:02.198  INFO 1 --- [           main] o.h.e.t.j.p.i.JtaPlatformInitiator       : HHH000490: Using JtaPlatform implementation: [org.hibernate.engine.transaction.jta.platform.internal.NoJtaPlatform]
2021-11-09 22:06:02.208  INFO 1 --- [           main] j.LocalContainerEntityManagerFactoryBean : Initialized JPA EntityManagerFactory for persistence unit 'default'
2021-11-09 22:06:02.585  WARN 1 --- [           main] JpaBaseConfiguration$JpaWebConfiguration : spring.jpa.open-in-view is enabled by default. Therefore, database queries may be performed during view rendering. Explicitly configure spring.jpa.open-in-view to disable this warning
2021-11-09 22:06:12.596  INFO 1 --- [           main] o.s.b.a.e.web.EndpointLinksResolver      : Exposing 1 endpoint(s) beneath base path '/actuator'
2021-11-09 22:06:13.093  INFO 1 --- [           main] o.s.b.w.embedded.tomcat.TomcatWebServer  : Tomcat started on port(s): 8080 (http) with context path ''
2021-11-09 22:06:13.478  INFO 1 --- [           main] o.a.c.impl.engine.AbstractCamelContext   : Routes startup summary (total:0 started:0)
2021-11-09 22:06:13.479  INFO 1 --- [           main] o.a.c.impl.engine.AbstractCamelContext   : Apache Camel 3.11.3 (camel-1) started in 777ms (build:479ms init:216ms start:82ms)
2021-11-09 22:06:13.601  INFO 1 --- [           main] miller79.Application                     : Started Application in 37.211 seconds (JVM running for 39.49)
```