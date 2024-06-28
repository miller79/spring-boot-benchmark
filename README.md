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

## Build and Measure Runtimes

The `measure-runtime.sh` Bash script will build and run all projects and provide startup times. The following dependencies are required to be able to run this script:

- Maven 3.6.3+
- JDK 21+
- Docker

Each application starts up and stops itself by running the following method in the main class of each application:

`SpringApplication.run(Application.class, args).close();`

This script builds the applications using `Maven` and the goal `spring-boot:build-image`. The different maven profiles will allow the builds to build with the following:

- plain - Builds without any customization
- aot - Builds with AOT enabled
- cds - Builds with CDS enabled
- aot+cds - Builds with CDS and AOT enabled
- native - Builds with native enabled

Once the application is built, the script will run the application ten times with the following settings:

- --cpus=".6"
- -e="JAVA_TOOL_OPTIONS=-XX:ActiveProcessorCount=1"

## Issues

- In Camel version 4.6.0, `camel-activemq-starter` uses `activemq-client-jakarta` which is obsoleted by `activemq-client` however it is still included. The projects that use it are excluding it currently and including `spring-boot-starter-activemq` to bring in the new client. I am supposing this will be addressed in a later release.
- In `spring-boot-benchmark-all-native`, the Application class defines the bean for the `ActiveMQConnectionFactory` directly. From the research that I've seen, the AutoConfiguration for ActiveMQ included `@ConfigurationOnProperty` annotations which is not compatible with GraalVM which does not work out of the box. Created an [issue](https://github.com/spring-projects/spring-boot/issues/41212) to follow.

## Results

Here are the final results of a run from my PC:

```
========================================================================================================================
|| Final Results                                                                                                      ||
========================================================================================================================
| Application                                        | Startup Time:                  | Process Time:                  |
|                                                    | Min, Max, Average              | Min, Max, Average              |
------------------------------------------------------------------------------------------------------------------------
| spring-boot-benchmark-original-native              | 0.116, 0.504, 0.1998           |  0.122, 0.542, 0.2121          |
------------------------------------------------------------------------------------------------------------------------
| spring-boot-benchmark-original-cds                 | 5.4, 6.778, 6.1521             |  6.097, 7.688, 6.8819          |
------------------------------------------------------------------------------------------------------------------------
| spring-boot-benchmark-data-jpa-cds                 | 11.689, 20.29, 14.5861         |  12.593, 21.571, 15.6495       |
------------------------------------------------------------------------------------------------------------------------
| spring-boot-benchmark-camel-activemq-aot           | 9.888, 12.062, 10.7655         |  11.272, 13.602, 12.1423       |
------------------------------------------------------------------------------------------------------------------------
| spring-boot-benchmark-data-rest-native             | 0.861, 1.163, 0.9913           |  0.867, 1.169, 0.9982          |
------------------------------------------------------------------------------------------------------------------------
| spring-boot-benchmark-data-rest-aot+cds            | 11.9, 18.79, 15.0261           |  12.775, 19.878, 16.1505       |
------------------------------------------------------------------------------------------------------------------------
| spring-boot-benchmark-data-rest-cds                | 15.005, 20.398, 17.3889        |  15.989, 22.064, 18.5519       |
------------------------------------------------------------------------------------------------------------------------
| spring-boot-benchmark-tomcat-cds                   | 6.302, 9.682, 8.1092           |  7.102, 11.57, 9.1051          |
------------------------------------------------------------------------------------------------------------------------
| spring-boot-benchmark-original-aot+cds             | 3.504, 6.595, 4.5267           |  4.209, 8.485, 5.3364          |
------------------------------------------------------------------------------------------------------------------------
| spring-boot-benchmark-data-jpa-aot                 | 14.679, 18.886, 16.6908        |  16.01, 20.361, 18.2855        |
------------------------------------------------------------------------------------------------------------------------
| spring-boot-benchmark-tomcat-aot                   | 7.098, 10.093, 8.3552          |  8.47, 11.197, 9.7114          |
------------------------------------------------------------------------------------------------------------------------
| spring-boot-benchmark-data-jpa-native              | 0.736, 1.717, 1.1757           |  0.746, 1.729, 1.1948          |
------------------------------------------------------------------------------------------------------------------------
| spring-boot-benchmark-original-aot                 | 6.871, 13.605, 9.2289          |  8.508, 15.816, 10.8647        |
------------------------------------------------------------------------------------------------------------------------
| spring-boot-benchmark-all-cds                      | 16.188, 26.815, 19.998         |  16.989, 28.518, 21.0117       |
------------------------------------------------------------------------------------------------------------------------
| spring-boot-benchmark-data-jpa-aot+cds             | 8.517, 18.192, 12.2364         |  9.379, 19.418, 13.3851        |
------------------------------------------------------------------------------------------------------------------------
| spring-boot-benchmark-tomcat-plain                 | 9.722, 12.891, 10.4677         |  10.992, 14.221, 11.8509       |
------------------------------------------------------------------------------------------------------------------------
| spring-boot-benchmark-data-rest-plain              | 26.673, 40.582, 32.4325        |  28.479, 42.487, 34.3314       |
------------------------------------------------------------------------------------------------------------------------
| spring-boot-benchmark-data-rest-aot                | 19.486, 24.782, 21.7139        |  20.992, 26.266, 23.2517       |
------------------------------------------------------------------------------------------------------------------------
| spring-boot-benchmark-camel-activemq-aot+cds       | 6.005, 7.602, 6.5759           |  6.796, 8.389, 7.33            |
------------------------------------------------------------------------------------------------------------------------
| spring-boot-benchmark-all-native                   | 1.284, 1.722, 1.4603           |  1.292, 1.734, 1.4688          |
------------------------------------------------------------------------------------------------------------------------
| spring-boot-benchmark-all-aot                      | 20.592, 25.209, 22.6483        |  22.007, 26.587, 24.1641       |
------------------------------------------------------------------------------------------------------------------------
| spring-boot-benchmark-tomcat-native                | 0.191, 0.869, 0.4541           |  0.197, 0.9, 0.4852            |
------------------------------------------------------------------------------------------------------------------------
| spring-boot-benchmark-camel-activemq-plain         | 13.194, 16.782, 14.8112        |  14.502, 19.202, 16.3162       |
------------------------------------------------------------------------------------------------------------------------
| spring-boot-benchmark-all-plain                    | 23.286, 26.009, 24.6382        |  24.89, 27.604, 26.0414        |
------------------------------------------------------------------------------------------------------------------------
| spring-boot-benchmark-data-jpa-plain               | 17.203, 44.187, 26.9829        |  18.418, 47.585, 28.8031       |
------------------------------------------------------------------------------------------------------------------------
| spring-boot-benchmark-camel-activemq-cds           | 8.203, 10.212, 8.722           |  8.901, 11.077, 9.4917         |
------------------------------------------------------------------------------------------------------------------------
| spring-boot-benchmark-camel-activemq-native        | 0.405, 0.772, 0.541            |  0.411, 0.781, 0.5488          |
------------------------------------------------------------------------------------------------------------------------
| spring-boot-benchmark-tomcat-aot+cds               | 4.108, 9.486, 5.1814           |  4.802, 10.668, 6.037          |
------------------------------------------------------------------------------------------------------------------------
| spring-boot-benchmark-all-aot+cds                  | 14.307, 17.992, 15.3892        |  15.124, 19.092, 16.3185       |
------------------------------------------------------------------------------------------------------------------------
| spring-boot-benchmark-original-plain               | 8.79, 13.608, 9.6677           |  9.881, 14.816, 10.9862        |
------------------------------------------------------------------------------------------------------------------------
```