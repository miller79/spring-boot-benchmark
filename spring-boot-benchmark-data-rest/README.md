# Spring Boot Benchmark Data Rest

This application takes the `spring-boot-benchmark-jpa` project and adds `spring-boot-starter-data-rest` and querydsl.

The following is the logs of the startup running on my box.

```
C:\Users\jisaal1\git\spring-boot-benchmark\spring-boot-benchmark-data-rest>docker run --rm --cpus=".6" -e="BPL_SPRING_CLOUD_BINDINGS_ENABLED=false" -e="JAVA_TOOL_OPTIONS=-XX:ActiveProcessorCount=1" spring-boot-benchmark
Calculating JVM memory based on 6863764K available memory
Calculated JVM Memory Configuration: -XX:MaxDirectMemorySize=10M -Xmx6232797K -XX:MaxMetaspaceSize=118966K -XX:ReservedCodeCacheSize=240M -Xss1M (Total Memory: 6863764K, Thread Count: 250, Loaded Class Count: 18590, Headroom: 0%)
Enabling Java Native Memory Tracking
Adding 128 container CA certificates to JVM truststore
Picked up JAVA_TOOL_OPTIONS: -XX:ActiveProcessorCount=1 -Djava.security.properties=/layers/paketo-buildpacks_bellsoft-liberica/java-security-properties/java-security.properties -XX:+ExitOnOutOfMemoryError -XX:MaxDirectMemorySize=10M -Xmx6232797K -XX:MaxMetaspaceSize=118966K -XX:ReservedCodeCacheSize=240M -Xss1M -XX:+UnlockDiagnosticVMOptions -XX:NativeMemoryTracking=summary -XX:+PrintNMTStatistics

  .   ____          _            __ _ _
 /\\ / ___'_ __ _ _(_)_ __  __ _ \ \ \ \
( ( )\___ | '_ | '_| | '_ \/ _` | \ \ \ \
 \\/  ___)| |_)| | | | | || (_| |  ) ) ) )
  '  |____| .__|_| |_|_| |_\__, | / / / /
 =========|_|==============|___/=/_/_/_/
 :: Spring Boot ::                (v2.5.6)

2021-11-09 22:12:58.200  INFO 1 --- [           main] miller79.Application                     : Starting Application v0.0.1-SNAPSHOT using Java 11.0.13 on e3248fe47807 with PID 1 (/workspace/BOOT-INF/classes started by cnb in /workspace)
2021-11-09 22:12:58.275  INFO 1 --- [           main] miller79.Application                     : No active profile set, falling back to default profiles: default
2021-11-09 22:13:03.379  INFO 1 --- [           main] .s.d.r.c.RepositoryConfigurationDelegate : Bootstrapping Spring Data JPA repositories in DEFAULT mode.
2021-11-09 22:13:03.482  INFO 1 --- [           main] .s.d.r.c.RepositoryConfigurationDelegate : Finished Spring Data repository scanning in 90 ms. Found 0 JPA repository interfaces.
2021-11-09 22:13:07.387  INFO 1 --- [           main] o.s.b.w.embedded.tomcat.TomcatWebServer  : Tomcat initialized with port(s): 8080 (http)
2021-11-09 22:13:07.404  INFO 1 --- [           main] o.apache.catalina.core.StandardService   : Starting service [Tomcat]
2021-11-09 22:13:07.404  INFO 1 --- [           main] org.apache.catalina.core.StandardEngine  : Starting Servlet engine: [Apache Tomcat/9.0.54]
2021-11-09 22:13:07.803  INFO 1 --- [           main] o.a.c.c.C.[Tomcat].[localhost].[/]       : Initializing Spring embedded WebApplicationContext
2021-11-09 22:13:07.803  INFO 1 --- [           main] w.s.c.ServletWebServerApplicationContext : Root WebApplicationContext: initialization completed in 9307 ms
2021-11-09 22:13:11.195  INFO 1 --- [           main] com.zaxxer.hikari.HikariDataSource       : HikariPool-1 - Starting...
2021-11-09 22:13:12.080  INFO 1 --- [           main] com.zaxxer.hikari.HikariDataSource       : HikariPool-1 - Start completed.
2021-11-09 22:13:12.402  INFO 1 --- [           main] o.hibernate.jpa.internal.util.LogHelper  : HHH000204: Processing PersistenceUnitInfo [name: default]
2021-11-09 22:13:12.589  INFO 1 --- [           main] org.hibernate.Version                    : HHH000412: Hibernate ORM core version 5.4.32.Final
2021-11-09 22:13:13.275  INFO 1 --- [           main] o.hibernate.annotations.common.Version   : HCANN000001: Hibernate Commons Annotations {5.1.2.Final}
2021-11-09 22:13:13.888  INFO 1 --- [           main] org.hibernate.dialect.Dialect            : HHH000400: Using dialect: org.hibernate.dialect.H2Dialect
2021-11-09 22:13:14.970  INFO 1 --- [           main] o.h.e.t.j.p.i.JtaPlatformInitiator       : HHH000490: Using JtaPlatform implementation: [org.hibernate.engine.transaction.jta.platform.internal.NoJtaPlatform]
2021-11-09 22:13:14.989  INFO 1 --- [           main] j.LocalContainerEntityManagerFactoryBean : Initialized JPA EntityManagerFactory for persistence unit 'default'
2021-11-09 22:13:15.404  WARN 1 --- [           main] JpaBaseConfiguration$JpaWebConfiguration : spring.jpa.open-in-view is enabled by default. Therefore, database queries may be performed during view rendering. Explicitly configure spring.jpa.open-in-view to disable this warning
2021-11-09 22:13:20.973  INFO 1 --- [           main] o.s.b.a.e.web.EndpointLinksResolver      : Exposing 1 endpoint(s) beneath base path '/actuator'
2021-11-09 22:13:21.396  INFO 1 --- [           main] o.s.b.w.embedded.tomcat.TomcatWebServer  : Tomcat started on port(s): 8080 (http) with context path ''
2021-11-09 22:13:21.492  INFO 1 --- [           main] miller79.Application                     : Started Application in 25.71 seconds (JVM running for 27.596)
```