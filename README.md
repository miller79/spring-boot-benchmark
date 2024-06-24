# Spring Boot Benchmark

## Introduction

This repository is a benchmark for Spring Boot running in Docker.
It is meant to demonstrate the performance concerns with Spring Boot and, hopefully, lead to documentation that can focus on the desired solution.
The end goal of this benchmark is to be the most optimally configured Spring Boot application in relationship to startup time.
This repository can be used as a benchmark that others can use to demonstrate startup timing benchmarks.

The Spring Boot GitHub issue this repository was created originally for is available [here](https://github.com/spring-projects/spring-boot/issues/19911).

## Benchmarks Available

The following benchmarks are available within this project.

### spring-boot-benchmark-original

This project is a barebones Spring Boot application that demonstrates an application using just `spring-boot-starter-webflux`.

### spring-boot-benchmark-native

This application takes the spring-boot-benchmark-original and makes it native-compatible to run on GraalVM.

### spring-boot-benchmark-tomcat

This application takes the spring-boot-benchmark-original and replaces webflux with web to test Tomcat vs Netty.

### spring-boot-benchmark-data-jpa

This application is a Spring Boot application that uses `spring-boot-starter-data-jpa`.

### spring-boot-benchmark-data-rest

This application is a Spring Boot application that uses `spring-boot-starter-data-rest`.

### spring-boot-benchmark-camel-activemq

This application takes the spring-boot-benchmark-original and adds `camel-activemq-starter`.

### spring-boot-benchmark-all

This application reflects the minimal application with all dependencies added.

### spring-boot-benchmark-all-native

This application reflects the minimal application with all dependencies added running with GraalVM.

## Build and Measure Runtimes

The `measure-runtime.sh` Bash script will build and run all projects and provide startup times. The following dependencies are required to be able to run this script:

- Maven 3.6.3+
- JDK 21+
- Docker

Each application starts up and stops itself by running the following method in the main class of each application:

`SpringApplication.run(Application.class, args).close();`

This script builds the applications using `Maven` and the goal `spring-boot:build-image`. Once the application is built, the script will run the application ten times with the following settings:

- --cpus=".6"
- -e="BPL_SPRING_CLOUD_BINDINGS_ENABLED=false"
- -e="JAVA_TOOL_OPTIONS=-XX:ActiveProcessorCount=1"

## Issues

- In Camel version 4.6.0, `camel-activemq-starter` uses `activemq-client-jakarta` which is obsoleted by `activemq-client` however it is still included. The projects that use it are excluding it currently and including `spring-boot-starter-activemq` to bring in the new client. I am supposing this will be addressed in a later release.
- In `spring-boot-benchmark-all-native`, the Application class defines the bean for the `ActiveMQConnectionFactory` directly. From the research that I've seen, the AutoConfiguration for ActiveMQ included `@ConfigurationOnProperty` annotations which is not compatible with GraalVM which does not work out of the box. Created an [issue](https://github.com/spring-projects/spring-boot/issues/41212) to follow.

## Results

Here are the logs of a run from my PC:

```
$ ./measure-runtime.sh
Building spring-boot-benchmark-original...
Running spring-boot-benchmark-original...
2024-06-24T04:41:34.911Z  INFO 1 --- [           main] miller79.Application                     : Started Application in 9.892 seconds (process running for 11.698)
2024-06-24T04:41:47.703Z  INFO 1 --- [           main] miller79.Application                     : Started Application in 8.389 seconds (process running for 9.504)
2024-06-24T04:42:00.309Z  INFO 1 --- [           main] miller79.Application                     : Started Application in 8.309 seconds (process running for 9.479)
2024-06-24T04:42:13.816Z  INFO 1 --- [           main] miller79.Application                     : Started Application in 8.216 seconds (process running for 9.303)
2024-06-24T04:42:26.313Z  INFO 1 --- [           main] miller79.Application                     : Started Application in 8.093 seconds (process running for 9.197)
2024-06-24T04:42:39.812Z  INFO 1 --- [           main] miller79.Application                     : Started Application in 8.887 seconds (process running for 10.199)
2024-06-24T04:42:55.106Z  INFO 1 --- [           main] miller79.Application                     : Started Application in 10.708 seconds (process running for 11.98)
2024-06-24T04:43:07.712Z  INFO 1 --- [           main] miller79.Application                     : Started Application in 7.815 seconds (process running for 9.006)
2024-06-24T04:43:21.011Z  INFO 1 --- [           main] miller79.Application                     : Started Application in 7.787 seconds (process running for 9.09)
2024-06-24T04:43:33.504Z  INFO 1 --- [           main] miller79.Application                     : Started Application in 7.909 seconds (process running for 9.087)
Building spring-boot-benchmark-tomcat...
Running spring-boot-benchmark-tomcat...
2024-06-24T04:44:43.097Z  INFO 1 --- [           main] miller79.Application                     : Started Application in 16.0 seconds (process running for 18.782)
2024-06-24T04:45:01.101Z  INFO 1 --- [           main] miller79.Application                     : Started Application in 13.401 seconds (process running for 15.498)
2024-06-24T04:45:15.315Z  INFO 1 --- [           main] miller79.Application                     : Started Application in 10.923 seconds (process running for 12.313)
2024-06-24T04:45:30.703Z  INFO 1 --- [           main] miller79.Application                     : Started Application in 11.8 seconds (process running for 13.305)
2024-06-24T04:45:43.014Z  INFO 1 --- [           main] miller79.Application                     : Started Application in 9.116 seconds (process running for 10.414)
2024-06-24T04:45:56.489Z  INFO 1 --- [           main] miller79.Application                     : Started Application in 10.382 seconds (process running for 11.671)
2024-06-24T04:46:08.710Z  INFO 1 --- [           main] miller79.Application                     : Started Application in 9.2 seconds (process running for 10.487)
2024-06-24T04:46:20.305Z  INFO 1 --- [           main] miller79.Application                     : Started Application in 8.611 seconds (process running for 9.909)
2024-06-24T04:46:31.600Z  INFO 1 --- [           main] miller79.Application                     : Started Application in 8.51 seconds (process running for 9.69)
2024-06-24T04:46:44.490Z  INFO 1 --- [           main] miller79.Application                     : Started Application in 9.596 seconds (process running for 11.169)
Building spring-boot-benchmark-native...

  .   ____          _            __ _ _
 /\\ / ___'_ __ _ _(_)_ __  __ _ \ \ \ \
( ( )\___ | '_ | '_| | '_ \/ _` | \ \ \ \
 \\/  ___)| |_)| | | | | || (_| |  ) ) ) )
  '  |____| .__|_| |_|_| |_\__, | / / / /
 =========|_|==============|___/=/_/_/_/

 :: Spring Boot ::                (v3.3.1)

2024-06-23T23:46:56.193-05:00  INFO 15396 --- [           main] miller79.Application                     : Starting Application using Java 21.0.2 with PID 15396 (C:\Users\jisaal1\git\spring-boot-benchmark\spring-boot-benchmark-native\target\classes started by jisaal1 in C:\Users\jisaal1\git\spring-boot-benchmark\spring-boot-benchmark-native)
2024-06-23T23:46:56.200-05:00  INFO 15396 --- [           main] miller79.Application                     : No active profile set, falling back to 1 default profile: "default"
Running spring-boot-benchmark-native...
2024-06-24T04:52:04.830Z  INFO 1 --- [           main] miller79.Application                     : Started Application in 0.202 seconds (process running for 0.212)
2024-06-24T04:52:09.400Z  INFO 1 --- [           main] miller79.Application                     : Started Application in 0.19 seconds (process running for 0.201)
2024-06-24T04:52:13.604Z  INFO 1 --- [           main] miller79.Application                     : Started Application in 0.11 seconds (process running for 0.116)
2024-06-24T04:52:17.171Z  INFO 1 --- [           main] miller79.Application                     : Started Application in 0.207 seconds (process running for 0.215)
2024-06-24T04:52:20.494Z  INFO 1 --- [           main] miller79.Application                     : Started Application in 0.12 seconds (process running for 0.125)
2024-06-24T04:52:23.795Z  INFO 1 --- [           main] miller79.Application                     : Started Application in 0.191 seconds (process running for 0.197)
2024-06-24T04:52:27.190Z  INFO 1 --- [           main] miller79.Application                     : Started Application in 0.121 seconds (process running for 0.128)
2024-06-24T04:52:30.468Z  INFO 1 --- [           main] miller79.Application                     : Started Application in 0.142 seconds (process running for 0.149)
2024-06-24T04:52:34.599Z  INFO 1 --- [           main] miller79.Application                     : Started Application in 0.097 seconds (process running for 0.102)
2024-06-24T04:52:37.778Z  INFO 1 --- [           main] miller79.Application                     : Started Application in 0.147 seconds (process running for 0.158)
Building spring-boot-benchmark-data-jpa...
Running spring-boot-benchmark-data-jpa...
2024-06-24T04:53:45.772Z  INFO 1 --- [           main] miller79.Application                     : Started Application in 16.191 seconds (process running for 18.062)
2024-06-24T04:54:06.192Z  INFO 1 --- [           main] miller79.Application                     : Started Application in 15.316 seconds (process running for 16.388)
2024-06-24T04:54:27.393Z  INFO 1 --- [           main] miller79.Application                     : Started Application in 15.526 seconds (process running for 16.822)
2024-06-24T04:54:49.077Z  INFO 1 --- [           main] miller79.Application                     : Started Application in 15.801 seconds (process running for 17.299)
2024-06-24T04:55:10.180Z  INFO 1 --- [           main] miller79.Application                     : Started Application in 15.303 seconds (process running for 16.776)
2024-06-24T04:55:32.572Z  INFO 1 --- [           main] miller79.Application                     : Started Application in 16.787 seconds (process running for 18.085)
2024-06-24T04:55:53.589Z  INFO 1 --- [           main] miller79.Application                     : Started Application in 15.8 seconds (process running for 17.41)
2024-06-24T04:56:14.665Z  INFO 1 --- [           main] miller79.Application                     : Started Application in 15.567 seconds (process running for 16.793)
2024-06-24T04:56:35.372Z  INFO 1 --- [           main] miller79.Application                     : Started Application in 15.207 seconds (process running for 16.506)
2024-06-24T04:56:56.674Z  INFO 1 --- [           main] miller79.Application                     : Started Application in 15.808 seconds (process running for 17.011)
Building spring-boot-benchmark-data-rest...
Running spring-boot-benchmark-data-rest...
2024-06-24T04:58:10.764Z  INFO 1 --- [           main] miller79.Application                     : Started Application in 24.798 seconds (process running for 26.592)
2024-06-24T04:58:31.455Z  INFO 1 --- [           main] miller79.Application                     : Started Application in 17.681 seconds (process running for 18.96)
2024-06-24T04:58:54.377Z  INFO 1 --- [           main] miller79.Application                     : Started Application in 19.923 seconds (process running for 21.305)
2024-06-24T04:59:17.154Z  INFO 1 --- [           main] miller79.Application                     : Started Application in 18.988 seconds (process running for 20.592)
2024-06-24T04:59:39.267Z  INFO 1 --- [           main] miller79.Application                     : Started Application in 18.904 seconds (process running for 20.386)
2024-06-24T05:00:08.244Z  INFO 1 --- [           main] miller79.Application                     : Started Application in 25.781 seconds (process running for 27.286)
2024-06-24T05:00:38.063Z  INFO 1 --- [           main] miller79.Application                     : Started Application in 22.514 seconds (process running for 26.011)
2024-06-24T05:00:58.940Z  INFO 1 --- [           main] miller79.Application                     : Started Application in 17.787 seconds (process running for 19.09)
2024-06-24T05:01:26.852Z  INFO 1 --- [           main] miller79.Application                     : Started Application in 24.486 seconds (process running for 26.192)
2024-06-24T05:01:48.457Z  INFO 1 --- [           main] miller79.Application                     : Started Application in 18.506 seconds (process running for 19.781)
Building spring-boot-benchmark-camel-activemq...
Running spring-boot-benchmark-camel-activemq...
2024-06-24T05:02:51.355Z  INFO 1 --- [           main] miller79.Application                     : Started Application in 14.113 seconds (process running for 16.296)
2024-06-24T05:03:06.451Z  INFO 1 --- [           main] miller79.Application                     : Started Application in 11.994 seconds (process running for 13.314)
2024-06-24T05:03:22.146Z  INFO 1 --- [           main] miller79.Application                     : Started Application in 12.48 seconds (process running for 13.876)
2024-06-24T05:03:37.336Z  INFO 1 --- [           main] miller79.Application                     : Started Application in 12.185 seconds (process running for 13.372)
2024-06-24T05:03:52.728Z  INFO 1 --- [           main] miller79.Application                     : Started Application in 12.278 seconds (process running for 13.67)
2024-06-24T05:04:07.945Z  INFO 1 --- [           main] miller79.Application                     : Started Application in 12.203 seconds (process running for 13.513)
2024-06-24T05:04:23.334Z  INFO 1 --- [           main] miller79.Application                     : Started Application in 11.999 seconds (process running for 13.393)
2024-06-24T05:04:38.824Z  INFO 1 --- [           main] miller79.Application                     : Started Application in 11.896 seconds (process running for 13.473)
2024-06-24T05:04:57.541Z  INFO 1 --- [           main] miller79.Application                     : Started Application in 15.388 seconds (process running for 16.9)
2024-06-24T05:05:15.044Z  INFO 1 --- [           main] miller79.Application                     : Started Application in 13.816 seconds (process running for 15.316)
Building spring-boot-benchmark-all...
Running spring-boot-benchmark-all...
2024-06-24T05:06:42.508Z  INFO 1 --- [           main] miller79.Application                     : Started Application in 35.571 seconds (process running for 37.259)
2024-06-24T05:07:17.324Z  INFO 1 --- [           main] miller79.Application                     : Started Application in 30.984 seconds (process running for 32.679)
2024-06-24T05:07:43.729Z  INFO 1 --- [           main] miller79.Application                     : Started Application in 23.213 seconds (process running for 24.523)
2024-06-24T05:08:11.112Z  INFO 1 --- [           main] miller79.Application                     : Started Application in 24.01 seconds (process running for 25.376)
2024-06-24T05:08:40.806Z  INFO 1 --- [           main] miller79.Application                     : Started Application in 26.086 seconds (process running for 27.587)
2024-06-24T05:09:13.797Z  INFO 1 --- [           main] miller79.Application                     : Started Application in 29.272 seconds (process running for 30.877)
2024-06-24T05:09:41.920Z  INFO 1 --- [           main] miller79.Application                     : Started Application in 23.814 seconds (process running for 25.699)
2024-06-24T05:10:09.807Z  INFO 1 --- [           main] miller79.Application                     : Started Application in 24.794 seconds (process running for 26.169)
2024-06-24T05:10:40.095Z  INFO 1 --- [           main] miller79.Application                     : Started Application in 26.379 seconds (process running for 28.079)
2024-06-24T05:11:15.612Z  INFO 1 --- [           main] miller79.Application                     : Started Application in 31.714 seconds (process running for 33.419)
Building spring-boot-benchmark-all-native...

  .   ____          _            __ _ _
 /\\ / ___'_ __ _ _(_)_ __  __ _ \ \ \ \
( ( )\___ | '_ | '_| | '_ \/ _` | \ \ \ \
 \\/  ___)| |_)| | | | | || (_| |  ) ) ) )
  '  |____| .__|_| |_|_| |_\__, | / / / /
 =========|_|==============|___/=/_/_/_/

 :: Spring Boot ::                (v3.3.1)

2024-06-24T00:11:30.975-05:00  INFO 11192 --- [           main] miller79.Application                     : Starting Application using Java 21.0.2 with PID 11192 (C:\Users\jisaal1\git\spring-boot-benchmark\spring-boot-benchmark-all-native\target\classes started by jisaal1 in C:\Users\jisaal1\git\spring-boot-benchmark\spring-boot-benchmark-all-native)
2024-06-24T00:11:30.982-05:00  INFO 11192 --- [           main] miller79.Application                     : No active profile set, falling back to 1 default profile: "default"
2024-06-24T00:11:33.353-05:00  INFO 11192 --- [           main] .s.d.r.c.RepositoryConfigurationDelegate : Bootstrapping Spring Data JPA repositories in DEFAULT mode.
2024-06-24T00:11:33.400-05:00  INFO 11192 --- [           main] .s.d.r.c.RepositoryConfigurationDelegate : Finished Spring Data repository scanning in 28 ms. Found 0 JPA repository interfaces.
2024-06-24T00:11:37.246-05:00  INFO 11192 --- [           main] rocessor$ProxyRegisteringAotContribution : Created proxy type class miller79.HelloWorld$$SpringCGLIB$$0 for class miller79.HelloWorld
2024-06-24T00:11:37.402-05:00  INFO 11192 --- [           main] rocessor$ProxyRegisteringAotContribution : Created proxy type class org.springframework.boot.autoconfigure.web.servlet.error.BasicErrorController$$SpringCGLIB$$0 for class org.springframework.boot.autoconfigure.web.servlet.error.BasicErrorController
2024-06-24T00:11:37.861-05:00  INFO 11192 --- [           main] rocessor$ProxyRegisteringAotContribution : Created proxy type class org.springframework.data.rest.webmvc.RepositoryController$$SpringCGLIB$$0 for class org.springframework.data.rest.webmvc.RepositoryController
2024-06-24T00:11:37.891-05:00  INFO 11192 --- [           main] rocessor$ProxyRegisteringAotContribution : Created proxy type class org.springframework.data.rest.webmvc.RepositoryEntityController$$SpringCGLIB$$0 for class org.springframework.data.rest.webmvc.RepositoryEntityController
2024-06-24T00:11:37.940-05:00  INFO 11192 --- [           main] rocessor$ProxyRegisteringAotContribution : Created proxy type class org.springframework.data.rest.webmvc.RepositoryPropertyReferenceController$$SpringCGLIB$$0 for class org.springframework.data.rest.webmvc.RepositoryPropertyReferenceController
2024-06-24T00:11:37.956-05:00  INFO 11192 --- [           main] rocessor$ProxyRegisteringAotContribution : Created proxy type class org.springframework.data.rest.webmvc.RepositorySearchController$$SpringCGLIB$$0 for class org.springframework.data.rest.webmvc.RepositorySearchController
2024-06-24T00:11:37.997-05:00  INFO 11192 --- [           main] rocessor$ProxyRegisteringAotContribution : Created proxy type class org.springframework.data.rest.webmvc.RepositorySchemaController$$SpringCGLIB$$0 for class org.springframework.data.rest.webmvc.RepositorySchemaController
2024-06-24T00:11:38.009-05:00  INFO 11192 --- [           main] rocessor$ProxyRegisteringAotContribution : Created proxy type class org.springframework.data.rest.webmvc.alps.AlpsController$$SpringCGLIB$$0 for class org.springframework.data.rest.webmvc.alps.AlpsController
2024-06-24T00:11:38.022-05:00  INFO 11192 --- [           main] rocessor$ProxyRegisteringAotContribution : Created proxy type class org.springframework.data.rest.webmvc.ProfileController$$SpringCGLIB$$0 for class org.springframework.data.rest.webmvc.ProfileController
2024-06-24T00:11:38.042-05:00  INFO 11192 --- [           main] o.springframework.hateoas.aot.AotUtils   : Registering Spring HATEOAS types in org.springframework.hateoas.mediatype.hal for reflection.
2024-06-24T00:11:38.101-05:00  INFO 11192 --- [           main] o.springframework.hateoas.aot.AotUtils   : Registering Spring HATEOAS types in org.springframework.hateoas.mediatype.hal.forms for reflection.
2024-06-24T00:11:38.134-05:00  INFO 11192 --- [           main] o.springframework.hateoas.aot.AotUtils   : Registering Spring HATEOAS types in org.springframework.hateoas.mediatype.alps for reflection.
2024-06-24T00:11:38.174-05:00  INFO 11192 --- [           main] o.springframework.hateoas.aot.AotUtils   : Registering Spring HATEOAS types in org.springframework.hateoas.mediatype.problem for reflection.
2024-06-24T00:11:38.655-05:00  INFO 11192 --- [           main] o.springframework.hateoas.aot.AotUtils   : Registering Spring HATEOAS types in org.springframework.hateoas for reflection.
Running spring-boot-benchmark-all-native...
2024-06-24T05:22:17.658Z  INFO 1 --- [           main] miller79.Application                     : Started Application in 1.594 seconds (process running for 1.602)
2024-06-24T05:22:20.828Z  INFO 1 --- [           main] miller79.Application                     : Started Application in 1.799 seconds (process running for 1.809)
2024-06-24T05:22:23.242Z  INFO 1 --- [           main] miller79.Application                     : Started Application in 1.281 seconds (process running for 1.29)
2024-06-24T05:22:25.751Z  INFO 1 --- [           main] miller79.Application                     : Started Application in 1.419 seconds (process running for 1.425)
2024-06-24T05:22:28.138Z  INFO 1 --- [           main] miller79.Application                     : Started Application in 1.152 seconds (process running for 1.158)
2024-06-24T05:22:30.979Z  INFO 1 --- [           main] miller79.Application                     : Started Application in 1.533 seconds (process running for 1.542)
2024-06-24T05:22:33.356Z  INFO 1 --- [           main] miller79.Application                     : Started Application in 1.215 seconds (process running for 1.221)
2024-06-24T05:22:35.738Z  INFO 1 --- [           main] miller79.Application                     : Started Application in 1.322 seconds (process running for 1.329)
2024-06-24T05:22:38.050Z  INFO 1 --- [           main] miller79.Application                     : Started Application in 1.31 seconds (process running for 1.316)
2024-06-24T05:22:40.553Z  INFO 1 --- [           main] miller79.Application                     : Started Application in 1.405 seconds (process running for 1.413)
```