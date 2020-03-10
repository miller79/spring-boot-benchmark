# Spring Boot Benchmark All [WIP]

This application represents a minimal version of a high dependency application.
The application this is modeled off of boots up in around 200 seconds.
The goal is to be able to see the progress over the individual pieces and ultimately the time as a whole.
I will attempt to update this README to ensure it is always up to date with the latest information.

The latest logs are the following.

```
  .   ____          _            __ _ _
 /\\ / ___'_ __ _ _(_)_ __  __ _ \ \ \ \
( ( )\___ | '_ | '_| | '_ \/ _` | \ \ \ \
 \\/  ___)| |_)| | | | | || (_| |  ) ) ) )
  '  |____| .__|_| |_|_| |_\__, | / / / /
 =========|_|==============|___/=/_/_/_/
 :: Spring Boot ::        (v2.2.5.RELEASE)

2020-03-10 04:31:26.095  INFO [,,,] 1 --- [           main] c.c.c.ConfigServicePropertySourceLocator : Fetching config from server at : http://localhost:8888
2020-03-10 04:31:27.213  INFO [,,,] 1 --- [           main] c.c.c.ConfigServicePropertySourceLocator : Connect Timeout Exception on Url - http://localhost:8888. Will be trying the next url if available
2020-03-10 04:31:27.214  WARN [,,,] 1 --- [           main] c.c.c.ConfigServicePropertySourceLocator : Could not locate PropertySource: I/O error on GET request for "http://localhost:8888/application/default": Connection refused (Connection refused); nested exception is java.net.ConnectException: Connection refused (Connection refused)
2020-03-10 04:31:27.296  INFO [,,,] 1 --- [           main] miller79.Application                     : No active profile set, falling back to default profiles: default
2020-03-10 04:31:44.394  INFO [,,,] 1 --- [           main] .s.d.r.c.RepositoryConfigurationDelegate : Bootstrapping Spring Data JPA repositories in LAZY mode.
2020-03-10 04:31:44.701  INFO [,,,] 1 --- [           main] .s.d.r.c.RepositoryConfigurationDelegate : Finished Spring Data repository scanning in 200ms. Found 0 JPA repository interfaces.
2020-03-10 04:31:52.006  INFO [,,,] 1 --- [           main] o.s.cloud.context.scope.GenericScope     : BeanFactory id=2995e421-8a00-31bc-967d-743ab547c0d8
2020-03-10 04:31:58.704  INFO [,,,] 1 --- [           main] trationDelegate$BeanPostProcessorChecker : Bean 'org.springframework.transaction.annotation.ProxyTransactionManagementConfiguration' of type [org.springframework.transaction.annotation.ProxyTransactionManagementConfiguration] is not eligible for getting processed by all BeanPostProcessors (for example: not eligible for auto-proxying)
2020-03-10 04:31:59.503  INFO [,,,] 1 --- [           main] trationDelegate$BeanPostProcessorChecker : Bean 'org.apache.camel.spring.boot.CamelAutoConfiguration' of type [org.apache.camel.spring.boot.CamelAutoConfiguration] is not eligible for getting processed by all BeanPostProcessors (for example: not eligible for auto-proxying)
2020-03-10 04:32:05.909  INFO [,,,] 1 --- [           main] o.s.b.w.embedded.tomcat.TomcatWebServer  : Tomcat initialized with port(s): 8080 (http)
2020-03-10 04:32:06.107  INFO [,,,] 1 --- [           main] o.apache.catalina.core.StandardService   : Starting service [Tomcat]
2020-03-10 04:32:06.109  INFO [,,,] 1 --- [           main] org.apache.catalina.core.StandardEngine  : Starting Servlet engine: [Apache Tomcat/9.0.31]
2020-03-10 04:32:08.195  INFO [,,,] 1 --- [           main] o.a.c.c.C.[Tomcat].[localhost].[/]       : Initializing Spring embedded WebApplicationContext
2020-03-10 04:32:08.198  INFO [,,,] 1 --- [           main] o.s.web.context.ContextLoader            : Root WebApplicationContext: initialization completed in 40795 ms
2020-03-10 04:32:12.992  INFO [,,,] 1 --- [           main] o.apache.camel.support.LRUCacheFactory   : Detected and using LURCacheFactory: camel-caffeine-lrucache
2020-03-10 04:32:25.517  INFO [,,,] 1 --- [           main] o.s.s.concurrent.ThreadPoolTaskExecutor  : Initializing ExecutorService 'applicationTaskExecutor'
2020-03-10 04:32:25.909  INFO [,,,] 1 --- [           main] com.zaxxer.hikari.HikariDataSource       : HikariPool-1 - Starting...
2020-03-10 04:32:27.495  INFO [,,,] 1 --- [           main] com.zaxxer.hikari.HikariDataSource       : HikariPool-1 - Start completed.
2020-03-10 04:32:28.306  INFO [,,,] 1 --- [         task-1] o.hibernate.jpa.internal.util.LogHelper  : HHH000204: Processing PersistenceUnitInfo [name: default]
2020-03-10 04:32:29.610  INFO [,,,] 1 --- [         task-1] org.hibernate.Version                    : HHH000412: Hibernate ORM core version 5.4.12.Final
2020-03-10 04:32:30.398  WARN [,,,] 1 --- [           main] JpaBaseConfiguration$JpaWebConfiguration : spring.jpa.open-in-view is enabled by default. Therefore, database queries may be performed during view rendering. Explicitly configure spring.jpa.open-in-view to disable this warning
2020-03-10 04:32:32.094  INFO [,,,] 1 --- [         task-1] o.hibernate.annotations.common.Version   : HCANN000001: Hibernate Commons Annotations {5.1.0.Final}
2020-03-10 04:32:34.704  INFO [,,,] 1 --- [         task-1] org.hibernate.dialect.Dialect            : HHH000400: Using dialect: org.hibernate.dialect.H2Dialect
2020-03-10 04:32:35.795  INFO [,,,] 1 --- [           main] o.a.c.s.boot.SpringBootRoutesCollector   : Loading additional Camel XML routes from: classpath:camel/*.xml
2020-03-10 04:32:35.800  INFO [,,,] 1 --- [           main] o.a.c.s.boot.SpringBootRoutesCollector   : Loading additional Camel XML rests from: classpath:camel-rest/*.xml
2020-03-10 04:32:35.806  INFO [,,,] 1 --- [           main] o.a.c.impl.engine.AbstractCamelContext   : Apache Camel 3.1.0 (CamelContext: camel-1) is starting
2020-03-10 04:32:35.893  INFO [,,,] 1 --- [           main] o.a.c.i.e.DefaultManagementStrategy      : JMX is disabled
2020-03-10 04:32:36.093  INFO [,,,] 1 --- [           main] o.a.c.i.e.HeadersMapFactoryResolver      : Detected and using HeadersMapFactory: camel-headersmap
2020-03-10 04:32:36.512  INFO [,,,] 1 --- [           main] o.a.c.impl.engine.AbstractCamelContext   : StreamCaching is not in use. If using streams then its recommended to enable stream caching. See more details at http://camel.apache.org/stream-caching.html
2020-03-10 04:32:36.592  INFO [,,,] 1 --- [           main] o.a.c.impl.engine.AbstractCamelContext   : Total 0 routes, of which 0 are started
2020-03-10 04:32:36.593  INFO [,,,] 1 --- [           main] o.a.c.impl.engine.AbstractCamelContext   : Apache Camel 3.1.0 (CamelContext: camel-1) started in 0.788 seconds
2020-03-10 04:32:37.404  INFO [,,,] 1 --- [           main] o.s.b.w.embedded.tomcat.TomcatWebServer  : Tomcat started on port(s): 8080 (http) with context path ''
2020-03-10 04:32:37.693  INFO [,,,] 1 --- [           main] miller79.Application                     : Started Application in 90.583 seconds (JVM running for 99.69)
2020-03-10 04:32:39.604  INFO [,,,] 1 --- [         task-1] o.h.e.t.j.p.i.JtaPlatformInitiator       : HHH000490: Using JtaPlatform implementation: [org.hibernate.engine.transaction.jta.platform.internal.NoJtaPlatform]
2020-03-10 04:32:39.809  INFO [,,,] 1 --- [         task-1] j.LocalContainerEntityManagerFactoryBean : Initialized JPA EntityManagerFactory for persistence unit 'default'
```