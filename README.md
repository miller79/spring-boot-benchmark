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
- alpaquita - Builds with the `bellsoft/buildpacks.builder:musl` builder
- native - Builds with native enabled

Once the application is built, the script will run the application ten times with the following settings:

- --cpus=".6"
- -e="JAVA_TOOL_OPTIONS=-XX:ActiveProcessorCount=1"

## Results

Here are the final results of a run from my PC:

```
========================================================================================================================
|| Final Results                                                                                                      ||
========================================================================================================================
| Application                                        | Startup Time:                  | Process Time:                  |
|                                                    | Min, Max, Average              | Min, Max, Average              |
------------------------------------------------------------------------------------------------------------------------
| spring-boot-benchmark-original-plain               | 8.378, 12.604, 9.7692          |  9.581, 14.495, 11.0335        |
------------------------------------------------------------------------------------------------------------------------
| spring-boot-benchmark-original-aot                 | 6.003, 8.477, 6.6145           |  7.083, 11.194, 7.8444         |
------------------------------------------------------------------------------------------------------------------------
| spring-boot-benchmark-original-cds                 | 5.112, 6.819, 5.7469           |  5.803, 7.682, 6.4022          |
------------------------------------------------------------------------------------------------------------------------
| spring-boot-benchmark-original-aot-cds             | 3.588, 4.516, 3.9229           |  4.192, 5.191, 4.5841          |
------------------------------------------------------------------------------------------------------------------------
| spring-boot-benchmark-original-alpaquita           | 8.697, 15.596, 10.5913         |  9.802, 17.211, 12.0752        |
------------------------------------------------------------------------------------------------------------------------
| spring-boot-benchmark-original-native              | 0.069, 0.184, 0.1116           |  0.073, 0.19, 0.1166           |
------------------------------------------------------------------------------------------------------------------------
| spring-boot-benchmark-tomcat-plain                 | 8.307, 13.292, 9.3311          |  9.587, 14.288, 10.486         |
------------------------------------------------------------------------------------------------------------------------
| spring-boot-benchmark-tomcat-aot                   | 6.39, 7.599, 6.8674            |  7.313, 8.697, 7.9061          |
------------------------------------------------------------------------------------------------------------------------
| spring-boot-benchmark-tomcat-cds                   | 5.977, 6.79, 6.286             |  6.484, 7.661, 6.853           |
------------------------------------------------------------------------------------------------------------------------
| spring-boot-benchmark-tomcat-aot-cds               | 3.831, 5.086, 4.2316           |  4.525, 5.761, 4.8637          |
------------------------------------------------------------------------------------------------------------------------
| spring-boot-benchmark-tomcat-alpaquita             | 8.987, 11.795, 9.8015          |  10.181, 12.972, 11.0675       |
------------------------------------------------------------------------------------------------------------------------
| spring-boot-benchmark-tomcat-native                | 0.093, 0.225, 0.1585           |  0.098, 0.232, 0.1645          |
------------------------------------------------------------------------------------------------------------------------
| spring-boot-benchmark-data-jpa-plain               | 14.385, 16.503, 15.4201        |  15.498, 17.579, 16.5759       |
------------------------------------------------------------------------------------------------------------------------
| spring-boot-benchmark-data-jpa-aot                 | 12.305, 14.084, 13.3639        |  13.503, 15.268, 14.5626       |
------------------------------------------------------------------------------------------------------------------------
| spring-boot-benchmark-data-jpa-cds                 | 9.496, 10.493, 9.9839          |  10.088, 11.199, 10.6851       |
------------------------------------------------------------------------------------------------------------------------
| spring-boot-benchmark-data-jpa-aot-cds             | 7.286, 10.7, 8.2781            |  7.891, 11.486, 8.9731         |
------------------------------------------------------------------------------------------------------------------------
| spring-boot-benchmark-data-jpa-alpaquita           | 15.981, 17.008, 16.3793        |  17.092, 18.398, 17.7338       |
------------------------------------------------------------------------------------------------------------------------
| spring-boot-benchmark-data-jpa-native              | 0.378, 0.848, 0.4789           |  0.383, 0.862, 0.4848          |
------------------------------------------------------------------------------------------------------------------------
| spring-boot-benchmark-data-rest-plain              | 19.097, 20.793, 19.9728        |  20.183, 21.88, 21.1247        |
------------------------------------------------------------------------------------------------------------------------
| spring-boot-benchmark-data-rest-aot                | 16.209, 18.595, 17.1899        |  17.297, 19.787, 18.3371       |
------------------------------------------------------------------------------------------------------------------------
| spring-boot-benchmark-data-rest-cds                | 12.599, 13.991, 13.2396        |  13.378, 14.701, 14.0175       |
------------------------------------------------------------------------------------------------------------------------
| spring-boot-benchmark-data-rest-aot-cds            | 10.008, 12.195, 11.0608        |  10.799, 12.99, 11.8259        |
------------------------------------------------------------------------------------------------------------------------
| spring-boot-benchmark-data-rest-alpaquita          | 19.087, 21.116, 20.2374        |  20.29, 22.976, 21.6308        |
------------------------------------------------------------------------------------------------------------------------
| spring-boot-benchmark-data-rest-native             | 0.694, 1.205, 0.8502           |  0.699, 1.216, 0.8565          |
------------------------------------------------------------------------------------------------------------------------
| spring-boot-benchmark-camel-activemq-plain         | 11.584, 13.327, 12.5575        |  12.601, 14.51, 13.6266        |
------------------------------------------------------------------------------------------------------------------------
| spring-boot-benchmark-camel-activemq-aot           | 8.903, 10.518, 9.5045          |  9.909, 11.508, 10.6015        |
------------------------------------------------------------------------------------------------------------------------
| spring-boot-benchmark-camel-activemq-cds           | 7.807, 9.082, 8.4406           |  8.401, 9.605, 9.0378          |
------------------------------------------------------------------------------------------------------------------------
| spring-boot-benchmark-camel-activemq-aot-cds       | 5.984, 6.808, 6.2226           |  6.514, 7.417, 6.839           |
------------------------------------------------------------------------------------------------------------------------
| spring-boot-benchmark-camel-activemq-alpaquita     | 12.4, 13.777, 12.9513          |  13.714, 15.79, 14.3385        |
------------------------------------------------------------------------------------------------------------------------
| spring-boot-benchmark-camel-activemq-native        | 0.331, 0.485, 0.404            |  0.337, 0.493, 0.4109          |
------------------------------------------------------------------------------------------------------------------------
| spring-boot-benchmark-all-plain                    | 22.512, 24.193, 23.2872        |  23.71, 25.297, 24.4781        |
------------------------------------------------------------------------------------------------------------------------
| spring-boot-benchmark-all-aot                      | 19.202, 24.789, 21.2369        |  20.219, 26.279, 22.5846       |
------------------------------------------------------------------------------------------------------------------------
| spring-boot-benchmark-all-cds                      | 14.903, 16.112, 15.5751        |  15.579, 16.812, 16.3018       |
------------------------------------------------------------------------------------------------------------------------
| spring-boot-benchmark-all-aot-cds                  | 12.502, 13.981, 13.395         |  13.203, 14.771, 14.1316       |
------------------------------------------------------------------------------------------------------------------------
| spring-boot-benchmark-all-alpaquita                | 21.698, 23.688, 23.013         |  23.278, 25.092, 24.3671       |
------------------------------------------------------------------------------------------------------------------------
| spring-boot-benchmark-all-native                   | 1.615, 3.399, 1.8697           |  1.625, 3.417, 1.8797          |
------------------------------------------------------------------------------------------------------------------------
```
