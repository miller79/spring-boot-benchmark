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
- aot-cds - Builds with CDS and AOT enabled
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
| spring-boot-benchmark-original-plain               | 9.989, 14.901, 11.8747         |  11.491, 17.195, 13.5438       |
------------------------------------------------------------------------------------------------------------------------
| spring-boot-benchmark-original-aot                 | 7.008, 18.018, 9.4724          |  8.287, 20.188, 11.2263        |
------------------------------------------------------------------------------------------------------------------------
| spring-boot-benchmark-original-cds                 | 8.104, 19.09, 13.191           |  9.771, 21.29, 14.7226         |
------------------------------------------------------------------------------------------------------------------------
| spring-boot-benchmark-original-aot-cds             | 5.181, 7.785, 6.434            |  5.88, 9.101, 7.4714           |
------------------------------------------------------------------------------------------------------------------------
| spring-boot-benchmark-original-native              | 0.145, 0.446, 0.2489           |  0.152, 0.513, 0.2642          |
------------------------------------------------------------------------------------------------------------------------
| spring-boot-benchmark-tomcat-plain                 | 11.666, 14.9, 12.9377          |  13.097, 16.481, 14.542        |
------------------------------------------------------------------------------------------------------------------------
| spring-boot-benchmark-tomcat-aot                   | 7.974, 11.987, 10.1224         |  9.404, 14.191, 11.8725        |
------------------------------------------------------------------------------------------------------------------------
| spring-boot-benchmark-tomcat-cds                   | 6.916, 7.713, 7.3429           |  7.683, 8.585, 8.1807          |
------------------------------------------------------------------------------------------------------------------------
| spring-boot-benchmark-tomcat-aot-cds               | 4.684, 5.986, 5.0483           |  5.419, 7.084, 5.9454          |
------------------------------------------------------------------------------------------------------------------------
| spring-boot-benchmark-tomcat-native                | 0.209, 0.471, 0.3202           |  0.216, 0.487, 0.3306          |
------------------------------------------------------------------------------------------------------------------------
| spring-boot-benchmark-data-jpa-plain               | 16.199, 20.315, 17.8666        |  17.566, 21.896, 19.3883       |
------------------------------------------------------------------------------------------------------------------------
| spring-boot-benchmark-data-jpa-aot                 | 14.108, 19.295, 15.6525        |  15.473, 20.66, 17.1351        |
------------------------------------------------------------------------------------------------------------------------
| spring-boot-benchmark-data-jpa-cds                 | 10.597, 17.581, 12.684         |  11.31, 18.883, 13.6205        |
------------------------------------------------------------------------------------------------------------------------
| spring-boot-benchmark-data-jpa-aot-cds             | 8.007, 9.789, 8.7004           |  8.802, 10.683, 9.5063         |
------------------------------------------------------------------------------------------------------------------------
| spring-boot-benchmark-data-jpa-native              | 0.549, 1.481, 0.9247           |  0.555, 1.495, 0.9354          |
------------------------------------------------------------------------------------------------------------------------
| spring-boot-benchmark-data-rest-plain              | 20.205, 24.02, 21.6028         |  21.486, 26.692, 23.1459       |
------------------------------------------------------------------------------------------------------------------------
| spring-boot-benchmark-data-rest-aot                | 17.788, 26.499, 20.7267        |  19.111, 27.716, 22.1661       |
------------------------------------------------------------------------------------------------------------------------
| spring-boot-benchmark-data-rest-cds                | 12.718, 14.988, 13.8293        |  13.506, 15.779, 14.6482       |
------------------------------------------------------------------------------------------------------------------------
| spring-boot-benchmark-data-rest-aot-cds            | 11.001, 12.808, 11.6866        |  11.705, 13.675, 12.5341       |
------------------------------------------------------------------------------------------------------------------------
| spring-boot-benchmark-data-rest-native             | 1.005, 1.478, 1.1487           |  1.012, 1.486, 1.1561          |
------------------------------------------------------------------------------------------------------------------------
| spring-boot-benchmark-camel-activemq-plain         | 12.903, 16.906, 14.9848        |  14.187, 18.796, 16.6511       |
------------------------------------------------------------------------------------------------------------------------
| spring-boot-benchmark-camel-activemq-aot           | 10.214, 11.797, 11.0616        |  11.695, 13.087, 12.3859       |
------------------------------------------------------------------------------------------------------------------------
| spring-boot-benchmark-camel-activemq-cds           | 8.414, 12.793, 9.7299          |  9.406, 13.594, 10.6389        |
------------------------------------------------------------------------------------------------------------------------
| spring-boot-benchmark-camel-activemq-aot-cds       | 6.296, 8.108, 6.8838           |  7.02, 9.491, 7.7457           |
------------------------------------------------------------------------------------------------------------------------
| spring-boot-benchmark-camel-activemq-native        | 0.443, 1.002, 0.6824           |  0.45, 1.033, 0.6969           |
------------------------------------------------------------------------------------------------------------------------
| spring-boot-benchmark-all-plain                    | 24.48, 34.368, 27.4361         |  25.705, 35.779, 28.8235       |
------------------------------------------------------------------------------------------------------------------------
| spring-boot-benchmark-all-aot                      | 20.777, 29.373, 22.6126        |  22.076, 31.078, 24.0969       |
------------------------------------------------------------------------------------------------------------------------
| spring-boot-benchmark-all-cds                      | 15.491, 26.794, 20.1082        |  16.398, 27.682, 21.0548       |
------------------------------------------------------------------------------------------------------------------------
| spring-boot-benchmark-all-aot-cds                  | 13.198, 21.901, 15.6933        |  14.004, 23.174, 16.6096       |
------------------------------------------------------------------------------------------------------------------------
| spring-boot-benchmark-all-native                   | 1.748, 2.499, 2.0377           |  1.756, 2.508, 2.0479          |
------------------------------------------------------------------------------------------------------------------------
```
