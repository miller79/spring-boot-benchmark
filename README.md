# Spring Boot Benchmark

## Introduction

This repository is a benchmark for Spring Boot running in Docker.
It is meant to be a demonstration of the performance concerns with Spring Boot and will hopefully lead to documentation that can focus on the desired solution.
The end goal of this benchmark is to be the most optimal configured Spring Boot application in relationship to startup time.
This hopefully will be a demo that could be used for others who are working on the same problem.

An issue for Spring Boot that this was originally created for is [here](https://github.com/spring-projects/spring-boot/issues/19911).

## Benchmarks Available

The following benchmarks are available within this project.

### spring-boot-benchmark-original

This application is a barebones Spring Boot application demonstrating a way to create an application with just `spring-boot-starter-webflux`.

### spring-boot-benchmark-native

This application takes the spring-boot-benchmark-original and makes it native compatible to run on GraalVM.

### spring-boot-benchmark-tomcat

This application takes the spring-boot-benchmark-original and replaces webflux with web to test Tomcat vs Netty.

### spring-boot-benchmark-data-jpa

This is a Spring Boot application that uses `spring-boot-starter-data-jpa`.

### spring-boot-benchmark-data-rest

This is a Spring Boot application that uses `spring-boot-starter-data-rest`.

### spring-boot-benchmark-camel-activemq

This application takes the spring-boot-benchmark-original and adds `camel-activemq-starter`.

### spring-boot-benchmark-all

This application reflects the minimal application with all dependencies added.

## Build and Measure Runtimes

The `measure-runtime.sh` Bash Script will build and run of the projects and provide startup times. To run this script the following dependencies are required:

- Maven 3.6.3+
- JDK 21+
- Docker

## Results

Here are the logs of a run from my PC:

```
$ ./measure-runtime.sh
Building spring-boot-benchmark-original...
Running spring-boot-benchmark-original...
2024-06-22T06:49:54.963Z  INFO 1 --- [           main] miller79.Application                     : Started Application in 11.231 seconds (process running for 12.676)
2024-06-22T06:50:08.652Z  INFO 1 --- [           main] miller79.Application                     : Started Application in 9.309 seconds (process running for 10.488)
2024-06-22T06:50:24.140Z  INFO 1 --- [           main] miller79.Application                     : Started Application in 9.891 seconds (process running for 11.086)
2024-06-22T06:50:39.548Z  INFO 1 --- [           main] miller79.Application                     : Started Application in 10.11 seconds (process running for 11.299)
2024-06-22T06:50:53.433Z  INFO 1 --- [           main] miller79.Application                     : Started Application in 9.31 seconds (process running for 10.591)
2024-06-22T06:51:08.829Z  INFO 1 --- [           main] miller79.Application                     : Started Application in 9.88 seconds (process running for 11.205)
2024-06-22T06:51:22.629Z  INFO 1 --- [           main] miller79.Application                     : Started Application in 9.391 seconds (process running for 10.587)
2024-06-22T06:51:37.013Z  INFO 1 --- [           main] miller79.Application                     : Started Application in 9.099 seconds (process running for 10.198)
2024-06-22T06:51:50.739Z  INFO 1 --- [           main] miller79.Application                     : Started Application in 9.328 seconds (process running for 10.611)
2024-06-22T06:52:06.333Z  INFO 1 --- [           main] miller79.Application                     : Started Application in 10.1 seconds (process running for 11.381)
Building spring-boot-benchmark-tomcat...
Running spring-boot-benchmark-tomcat...
2024-06-22T06:53:21.927Z  INFO 1 --- [           main] miller79.Application                     : Started Application in 12.101 seconds (process running for 13.476)
2024-06-22T06:53:38.415Z  INFO 1 --- [           main] miller79.Application                     : Started Application in 10.917 seconds (process running for 12.991)
2024-06-22T06:53:52.216Z  INFO 1 --- [           main] miller79.Application                     : Started Application in 10.497 seconds (process running for 11.985)
2024-06-22T06:54:05.097Z  INFO 1 --- [           main] miller79.Application                     : Started Application in 9.902 seconds (process running for 11.193)
2024-06-22T06:54:16.831Z  INFO 1 --- [           main] miller79.Application                     : Started Application in 9.115 seconds (process running for 10.185)
2024-06-22T06:54:29.899Z  INFO 1 --- [           main] miller79.Application                     : Started Application in 10.401 seconds (process running for 11.556)
2024-06-22T06:54:41.613Z  INFO 1 --- [           main] miller79.Application                     : Started Application in 9.083 seconds (process running for 10.078)
2024-06-22T06:54:54.610Z  INFO 1 --- [           main] miller79.Application                     : Started Application in 10.199 seconds (process running for 11.373)
2024-06-22T06:55:06.628Z  INFO 1 --- [           main] miller79.Application                     : Started Application in 9.432 seconds (process running for 10.612)
2024-06-22T06:55:18.607Z  INFO 1 --- [           main] miller79.Application                     : Started Application in 9.007 seconds (process running for 10.366)
Building spring-boot-benchmark-native...

  .   ____          _            __ _ _
 /\\ / ___'_ __ _ _(_)_ __  __ _ \ \ \ \
( ( )\___ | '_ | '_| | '_ \/ _` | \ \ \ \
 \\/  ___)| |_)| | | | | || (_| |  ) ) ) )
  '  |____| .__|_| |_|_| |_\__, | / / / /
 =========|_|==============|___/=/_/_/_/

 :: Spring Boot ::                (v3.3.1)

2024-06-22T01:55:30.631-05:00  INFO 284 --- [           main] miller79.Application                     : Starting Application using Java 21.0.2 with PID 284 (C:\Users\jisaal1\git\spring-boot-benchmark\spring-boot-benchmark-native\target\classes started by jisaal1 in C:\Users\jisaal1\git\spring-boot-benchmark\spring-boot-benchmark-native)
2024-06-22T01:55:30.637-05:00  INFO 284 --- [           main] miller79.Application                     : No active profile set, falling back to 1 default profile: "default"
Running spring-boot-benchmark-native...
2024-06-22T07:06:53.395Z  INFO 1 --- [           main] miller79.Application                     : Started Application in 0.229 seconds (process running for 0.238)
2024-06-22T07:06:56.432Z  INFO 1 --- [           main] miller79.Application                     : Started Application in 0.088 seconds (process running for 0.094)
2024-06-22T07:07:00.536Z  INFO 1 --- [           main] miller79.Application                     : Started Application in 0.095 seconds (process running for 0.101)
2024-06-22T07:07:04.503Z  INFO 1 --- [           main] miller79.Application                     : Started Application in 0.122 seconds (process running for 0.128)
2024-06-22T07:07:07.703Z  INFO 1 --- [           main] miller79.Application                     : Started Application in 0.109 seconds (process running for 0.115)
2024-06-22T07:07:10.629Z  INFO 1 --- [           main] miller79.Application                     : Started Application in 0.078 seconds (process running for 0.087)
2024-06-22T07:07:13.578Z  INFO 1 --- [           main] miller79.Application                     : Started Application in 0.097 seconds (process running for 0.105)
2024-06-22T07:07:16.605Z  INFO 1 --- [           main] miller79.Application                     : Started Application in 0.151 seconds (process running for 0.158)
2024-06-22T07:07:20.979Z  INFO 1 --- [           main] miller79.Application                     : Started Application in 0.138 seconds (process running for 0.148)
2024-06-22T07:07:24.206Z  INFO 1 --- [           main] miller79.Application                     : Started Application in 0.148 seconds (process running for 0.155)
Building spring-boot-benchmark-data-jpa...
Running spring-boot-benchmark-data-jpa...
2024-06-22T07:08:56.285Z  INFO 1 --- [           main] miller79.Application                     : Started Application in 20.8 seconds (process running for 22.335)
2024-06-22T07:09:21.982Z  INFO 1 --- [           main] miller79.Application                     : Started Application in 18.987 seconds (process running for 20.392)
2024-06-22T07:09:43.785Z  INFO 1 --- [           main] miller79.Application                     : Started Application in 17.379 seconds (process running for 18.605)
2024-06-22T07:10:04.295Z  INFO 1 --- [           main] miller79.Application                     : Started Application in 15.996 seconds (process running for 17.109)
2024-06-22T07:10:29.176Z  INFO 1 --- [           main] miller79.Application                     : Started Application in 18.775 seconds (process running for 20.396)
2024-06-22T07:10:50.795Z  INFO 1 --- [           main] miller79.Application                     : Started Application in 17.195 seconds (process running for 18.417)
2024-06-22T07:11:13.582Z  INFO 1 --- [           main] miller79.Application                     : Started Application in 17.389 seconds (process running for 18.58)
2024-06-22T07:11:34.572Z  INFO 1 --- [           main] miller79.Application                     : Started Application in 15.499 seconds (process running for 16.767)
2024-06-22T07:11:57.671Z  INFO 1 --- [           main] miller79.Application                     : Started Application in 17.994 seconds (process running for 19.068)
2024-06-22T07:12:17.280Z  INFO 1 --- [           main] miller79.Application                     : Started Application in 15.397 seconds (process running for 16.51)
Building spring-boot-benchmark-data-rest...
Running spring-boot-benchmark-data-rest...
2024-06-22T07:13:50.860Z  INFO 1 --- [           main] miller79.Application                     : Started Application in 26.391 seconds (process running for 27.995)
2024-06-22T07:14:14.876Z  INFO 1 --- [           main] miller79.Application                     : Started Application in 21.015 seconds (process running for 22.406)
2024-06-22T07:14:41.559Z  INFO 1 --- [           main] miller79.Application                     : Started Application in 23.796 seconds (process running for 25.066)
2024-06-22T07:15:04.072Z  INFO 1 --- [           main] miller79.Application                     : Started Application in 19.699 seconds (process running for 20.903)
2024-06-22T07:15:25.975Z  INFO 1 --- [           main] miller79.Application                     : Started Application in 19.193 seconds (process running for 20.357)
2024-06-22T07:15:49.859Z  INFO 1 --- [           main] miller79.Application                     : Started Application in 20.997 seconds (process running for 22.253)
2024-06-22T07:16:14.266Z  INFO 1 --- [           main] miller79.Application                     : Started Application in 21.587 seconds (process running for 22.777)
2024-06-22T07:16:39.555Z  INFO 1 --- [           main] miller79.Application                     : Started Application in 21.992 seconds (process running for 23.381)
2024-06-22T07:17:02.976Z  INFO 1 --- [           main] miller79.Application                     : Started Application in 20.105 seconds (process running for 21.492)
2024-06-22T07:17:24.376Z  INFO 1 --- [           main] miller79.Application                     : Started Application in 18.616 seconds (process running for 19.807)
Building spring-boot-benchmark-camel-activemq...
Running spring-boot-benchmark-camel-activemq...
2024-06-22T07:18:49.471Z  INFO 1 --- [           main] miller79.Application                     : Started Application in 15.691 seconds (process running for 17.074)
2024-06-22T07:19:05.989Z  INFO 1 --- [           main] miller79.Application                     : Started Application in 13.319 seconds (process running for 14.709)
2024-06-22T07:19:21.069Z  INFO 1 --- [           main] miller79.Application                     : Started Application in 12.391 seconds (process running for 13.492)
2024-06-22T07:19:36.287Z  INFO 1 --- [           main] miller79.Application                     : Started Application in 12.296 seconds (process running for 13.408)
2024-06-22T07:19:52.170Z  INFO 1 --- [           main] miller79.Application                     : Started Application in 13.093 seconds (process running for 14.294)
2024-06-22T07:20:08.677Z  INFO 1 --- [           main] miller79.Application                     : Started Application in 13.61 seconds (process running for 14.891)
2024-06-22T07:20:24.074Z  INFO 1 --- [           main] miller79.Application                     : Started Application in 12.506 seconds (process running for 13.763)
2024-06-22T07:20:40.767Z  INFO 1 --- [           main] miller79.Application                     : Started Application in 13.779 seconds (process running for 14.984)
2024-06-22T07:20:57.973Z  INFO 1 --- [           main] miller79.Application                     : Started Application in 14.298 seconds (process running for 15.576)
2024-06-22T07:21:13.875Z  INFO 1 --- [           main] miller79.Application                     : Started Application in 13.075 seconds (process running for 14.359)
Building spring-boot-benchmark-all...
Running spring-boot-benchmark-all...
2024-06-22T07:22:44.085Z  INFO 1 --- [           main] miller79.Application                     : Started Application in 26.717 seconds (process running for 28.283)
2024-06-22T07:23:10.972Z  INFO 1 --- [           main] miller79.Application                     : Started Application in 23.811 seconds (process running for 25.107)
2024-06-22T07:23:38.275Z  INFO 1 --- [           main] miller79.Application                     : Started Application in 24.41 seconds (process running for 25.612)
2024-06-22T07:24:06.065Z  INFO 1 --- [           main] miller79.Application                     : Started Application in 24.701 seconds (process running for 26.051)
2024-06-22T07:24:33.866Z  INFO 1 --- [           main] miller79.Application                     : Started Application in 24.588 seconds (process running for 25.802)
2024-06-22T07:25:00.362Z  INFO 1 --- [           main] miller79.Application                     : Started Application in 23.207 seconds (process running for 24.788)
2024-06-22T07:25:27.370Z  INFO 1 --- [           main] miller79.Application                     : Started Application in 24.107 seconds (process running for 25.314)
2024-06-22T07:25:55.979Z  INFO 1 --- [           main] miller79.Application                     : Started Application in 25.018 seconds (process running for 26.675)
2024-06-22T07:26:32.759Z  INFO 1 --- [           main] miller79.Application                     : Started Application in 33.481 seconds (process running for 35.16)
2024-06-22T07:27:02.453Z  INFO 1 --- [           main] miller79.Application                     : Started Application in 26.287 seconds (process running for 27.781)

```