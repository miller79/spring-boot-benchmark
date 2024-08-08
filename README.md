# Spring Boot Benchmark

- [Spring Boot Benchmark](#spring-boot-benchmark)
  - [Introduction](#introduction)
  - [Benchmarks Available](#benchmarks-available)
    - [spring-boot-benchmark-original](#spring-boot-benchmark-original)
    - [spring-boot-benchmark-tomcat](#spring-boot-benchmark-tomcat)
    - [spring-boot-benchmark-data-jpa](#spring-boot-benchmark-data-jpa)
    - [spring-boot-benchmark-data-rest](#spring-boot-benchmark-data-rest)
    - [spring-boot-benchmark-camel-activemq](#spring-boot-benchmark-camel-activemq)
    - [spring-boot-benchmark-all](#spring-boot-benchmark-all)
  - [Build and Measure Runtimes](#build-and-measure-runtimes)
  - [Issues](#issues)
  - [Results](#results)

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

- In Camel version 4.7.0, `camel-activemq-starter` uses `activemq-client-jakarta` which is obsoleted by `activemq-client` however it is still included. The projects that use it are excluding it currently and including `spring-boot-starter-activemq` to bring in the new client. I am supposing this will be addressed in a later release.

## Results

Here are the final results of a run from my PC:

```
========================================================================================================================
|| Final Results                                                                                                      ||
========================================================================================================================
| Application                                        | Startup Time:                  | Process Time:                  |
|                                                    | Min, Max, Average              | Min, Max, Average              |
------------------------------------------------------------------------------------------------------------------------
| spring-boot-benchmark-original-plain               | 8.086, 18.577, 12.1742         |  9.103, 21.799, 13.7733        |
------------------------------------------------------------------------------------------------------------------------
| spring-boot-benchmark-original-aot                 | 5.896, 8.704, 6.977            |  6.912, 10.307, 8.2139         |
------------------------------------------------------------------------------------------------------------------------
| spring-boot-benchmark-original-cds                 | 5.182, 7.272, 5.9191           |  5.699, 8.263, 6.5661          |
------------------------------------------------------------------------------------------------------------------------
| spring-boot-benchmark-original-aot-cds             | 3.502, 4.08, 3.7615            |  4.117, 4.778, 4.4362          |
------------------------------------------------------------------------------------------------------------------------
| spring-boot-benchmark-original-native              | 0.079, 0.193, 0.1163           |  0.084, 0.202, 0.1229          |
------------------------------------------------------------------------------------------------------------------------
| spring-boot-benchmark-tomcat-plain                 | 8.597, 10.911, 9.1768          |  9.777, 11.905, 10.3357        |
------------------------------------------------------------------------------------------------------------------------
| spring-boot-benchmark-tomcat-aot                   | 6.575, 10.594, 7.2222          |  7.668, 13.28, 8.4994          |
------------------------------------------------------------------------------------------------------------------------
| spring-boot-benchmark-tomcat-cds                   | 5.797, 6.694, 6.1422           |  6.311, 7.396, 6.7657          |
------------------------------------------------------------------------------------------------------------------------
| spring-boot-benchmark-tomcat-aot-cds               | 3.799, 4.897, 4.0962           |  4.485, 5.677, 4.739           |
------------------------------------------------------------------------------------------------------------------------
| spring-boot-benchmark-tomcat-native                | 0.138, 0.302, 0.2304           |  0.143, 0.312, 0.2384          |
------------------------------------------------------------------------------------------------------------------------
| spring-boot-benchmark-data-jpa-plain               | 14.709, 19.478, 16.0588        |  15.818, 20.677, 17.2811       |
------------------------------------------------------------------------------------------------------------------------
| spring-boot-benchmark-data-jpa-aot                 | 12.52, 15.198, 13.623          |  13.712, 16.281, 14.8097       |
------------------------------------------------------------------------------------------------------------------------
| spring-boot-benchmark-data-jpa-cds                 | 9.314, 10.698, 9.8407          |  10.003, 11.681, 10.5712       |
------------------------------------------------------------------------------------------------------------------------
| spring-boot-benchmark-data-jpa-aot-cds             | 7.597, 10.507, 8.2779          |  8.321, 11.212, 9.0313         |
------------------------------------------------------------------------------------------------------------------------
| spring-boot-benchmark-data-jpa-native              | 0.506, 1.22, 0.7826            |  0.513, 1.24, 0.7917           |
------------------------------------------------------------------------------------------------------------------------
| spring-boot-benchmark-data-rest-plain              | 20.292, 23.898, 21.3199        |  21.806, 24.998, 22.6984       |
------------------------------------------------------------------------------------------------------------------------
| spring-boot-benchmark-data-rest-aot                | 17.695, 20.081, 18.5229        |  18.971, 21.399, 19.9633       |
------------------------------------------------------------------------------------------------------------------------
| spring-boot-benchmark-data-rest-cds                | 12.891, 14.285, 13.5532        |  13.593, 15.069, 14.3429       |
------------------------------------------------------------------------------------------------------------------------
| spring-boot-benchmark-data-rest-aot-cds            | 10.311, 12.398, 11.3107        |  10.987, 13.266, 12.0801       |
------------------------------------------------------------------------------------------------------------------------
| spring-boot-benchmark-data-rest-native             | 0.94, 1.258, 1.0491            |  0.95, 1.265, 1.057            |
------------------------------------------------------------------------------------------------------------------------
| spring-boot-benchmark-camel-activemq-plain         | 11.903, 13.983, 13.2608        |  12.988, 15.593, 14.5698       |
------------------------------------------------------------------------------------------------------------------------
| spring-boot-benchmark-camel-activemq-aot           | 10.177, 14.708, 11.1364        |  11.396, 16.582, 12.488        |
------------------------------------------------------------------------------------------------------------------------
| spring-boot-benchmark-camel-activemq-cds           | 7.594, 9.51, 8.6488            |  8.211, 10.275, 9.3596         |
------------------------------------------------------------------------------------------------------------------------
| spring-boot-benchmark-camel-activemq-aot-cds       | 5.909, 7.398, 6.4799           |  6.6, 8.109, 7.2219            |
------------------------------------------------------------------------------------------------------------------------
| spring-boot-benchmark-camel-activemq-native        | 0.355, 0.554, 0.4485           |  0.361, 0.564, 0.456           |
------------------------------------------------------------------------------------------------------------------------
| spring-boot-benchmark-all-plain                    | 24.198, 25.71, 24.9632         |  25.388, 27.106, 26.3028       |
------------------------------------------------------------------------------------------------------------------------
| spring-boot-benchmark-all-aot                      | 18.911, 22.394, 20.2736        |  20.308, 23.602, 21.5558       |
------------------------------------------------------------------------------------------------------------------------
| spring-boot-benchmark-all-cds                      | 14.501, 16.276, 15.0425        |  15.289, 17.0, 15.8097         |
------------------------------------------------------------------------------------------------------------------------
| spring-boot-benchmark-all-aot-cds                  | 11.913, 18.708, 13.4271        |  12.786, 19.596, 14.2164       |
------------------------------------------------------------------------------------------------------------------------
| spring-boot-benchmark-all-native                   | 1.109, 1.363, 1.2259           |  1.114, 1.371, 1.2327          |
------------------------------------------------------------------------------------------------------------------------
```
