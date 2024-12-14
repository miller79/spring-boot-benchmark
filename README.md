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

Here are the final results of a run from my PC (last ran 12/13/2024):

```
========================================================================================================================
|| Final Results                                                                                                      ||
========================================================================================================================
| Application                                        | Startup Time:                  | Process Time:                  |
|                                                    | Min, Max, Average              | Min, Max, Average              |
------------------------------------------------------------------------------------------------------------------------
| spring-boot-benchmark-original-plain               | 9.491, 24.509, 12.6429         |  10.9, 28.604, 14.4257         |
------------------------------------------------------------------------------------------------------------------------
| spring-boot-benchmark-original-aot                 | 5.619, 13.597, 7.216           |  6.593, 17.603, 8.6244         |
------------------------------------------------------------------------------------------------------------------------
| spring-boot-benchmark-original-cds                 | 5.106, 11.42, 6.3156           |  5.615, 13.484, 7.087          |
------------------------------------------------------------------------------------------------------------------------
| spring-boot-benchmark-original-aot-cds             | 3.302, 10.79, 5.1467           |  3.806, 11.684, 5.831          |
------------------------------------------------------------------------------------------------------------------------
| spring-boot-benchmark-original-alpaquita           | 8.005, 9.174, 8.2956           |  9.095, 10.298, 9.4848         |
------------------------------------------------------------------------------------------------------------------------
| spring-boot-benchmark-original-native              | 0.068, 0.181, 0.1294           |  0.075, 0.19, 0.1364           |
------------------------------------------------------------------------------------------------------------------------
| spring-boot-benchmark-tomcat-plain                 | 8.205, 12.385, 9.1766          |  9.106, 13.884, 10.239         |
------------------------------------------------------------------------------------------------------------------------
| spring-boot-benchmark-tomcat-aot                   | 6.3, 12.113, 7.4787            |  7.274, 14.478, 8.633          |
------------------------------------------------------------------------------------------------------------------------
| spring-boot-benchmark-tomcat-cds                   | 5.389, 13.594, 6.804           |  5.901, 14.47, 7.3983          |
------------------------------------------------------------------------------------------------------------------------
| spring-boot-benchmark-tomcat-aot-cds               | 3.821, 9.009, 5.0868           |  4.389, 9.907, 5.7382          |
------------------------------------------------------------------------------------------------------------------------
| spring-boot-benchmark-tomcat-alpaquita             | 8.697, 9.214, 9.0449           |  9.863, 10.475, 10.2211        |
------------------------------------------------------------------------------------------------------------------------
| spring-boot-benchmark-tomcat-native                | 0.088, 0.274, 0.1482           |  0.093, 0.284, 0.1541          |
------------------------------------------------------------------------------------------------------------------------
| spring-boot-benchmark-data-jpa-plain               | 14.811, 20.71, 18.2597         |  15.896, 22.708, 19.5969       |
------------------------------------------------------------------------------------------------------------------------
| spring-boot-benchmark-data-jpa-aot                 | 12.293, 16.494, 14.2767        |  13.375, 18.275, 15.5535       |
------------------------------------------------------------------------------------------------------------------------
| spring-boot-benchmark-data-jpa-cds                 | 8.796, 17.815, 10.3555         |  9.373, 20.094, 11.2003        |
------------------------------------------------------------------------------------------------------------------------
| spring-boot-benchmark-data-jpa-aot-cds             | 7.003, 12.39, 8.1563           |  7.676, 14.686, 9.0652         |
------------------------------------------------------------------------------------------------------------------------
| spring-boot-benchmark-data-jpa-alpaquita           | 14.789, 17.397, 15.7205        |  16.097, 18.689, 17.0299       |
------------------------------------------------------------------------------------------------------------------------
| spring-boot-benchmark-data-jpa-native              | 0.403, 0.859, 0.5791           |  0.409, 0.872, 0.5859          |
------------------------------------------------------------------------------------------------------------------------
| spring-boot-benchmark-data-rest-plain              | 18.608, 19.897, 19.3562        |  19.696, 21.088, 20.541        |
------------------------------------------------------------------------------------------------------------------------
| spring-boot-benchmark-data-rest-aot                | 14.798, 23.202, 16.9567        |  15.801, 25.387, 18.2161       |
------------------------------------------------------------------------------------------------------------------------
| spring-boot-benchmark-data-rest-cds                | 11.106, 15.608, 13.5061        |  11.776, 16.406, 14.2652       |
------------------------------------------------------------------------------------------------------------------------
| spring-boot-benchmark-data-rest-aot-cds            | 10.417, 15.812, 12.0309        |  11.282, 16.988, 12.9876       |
------------------------------------------------------------------------------------------------------------------------
| spring-boot-benchmark-data-rest-alpaquita          | 17.791, 22.593, 19.6793        |  18.991, 24.602, 21.1202       |
------------------------------------------------------------------------------------------------------------------------
| spring-boot-benchmark-data-rest-native             | 0.699, 3.022, 1.0291           |  0.704, 3.076, 1.0397          |
------------------------------------------------------------------------------------------------------------------------
| spring-boot-benchmark-camel-activemq-plain         | 11.579, 14.904, 12.3029        |  12.698, 16.967, 13.4719       |
------------------------------------------------------------------------------------------------------------------------
| spring-boot-benchmark-camel-activemq-aot           | 8.692, 14.182, 9.6287          |  9.689, 15.881, 10.7614        |
------------------------------------------------------------------------------------------------------------------------
| spring-boot-benchmark-camel-activemq-cds           | 7.584, 13.107, 8.5939          |  8.196, 14.112, 9.2298         |
------------------------------------------------------------------------------------------------------------------------
| spring-boot-benchmark-camel-activemq-aot-cds       | 5.288, 13.493, 6.765           |  5.89, 15.697, 7.5437          |
------------------------------------------------------------------------------------------------------------------------
| spring-boot-benchmark-camel-activemq-alpaquita     | 11.504, 12.1, 11.8284          |  12.619, 13.374, 13.0346       |
------------------------------------------------------------------------------------------------------------------------
| spring-boot-benchmark-camel-activemq-native        | 0.268, 0.452, 0.3256           |  0.273, 0.459, 0.331           |
------------------------------------------------------------------------------------------------------------------------
| spring-boot-benchmark-all-plain                    | 20.705, 22.89, 21.5767         |  22.016, 23.966, 22.7193       |
------------------------------------------------------------------------------------------------------------------------
| spring-boot-benchmark-all-aot                      | 17.999, 19.012, 18.4784        |  19.089, 20.103, 19.606        |
------------------------------------------------------------------------------------------------------------------------
| spring-boot-benchmark-all-cds                      | 13.1, 18.202, 14.6401          |  13.804, 19.004, 15.3491       |
------------------------------------------------------------------------------------------------------------------------
| spring-boot-benchmark-all-aot-cds                  | 10.898, 15.204, 12.0609        |  11.619, 15.985, 12.76         |
------------------------------------------------------------------------------------------------------------------------
| spring-boot-benchmark-all-alpaquita                | 20.912, 22.608, 21.7008        |  22.293, 23.792, 22.9678       |
------------------------------------------------------------------------------------------------------------------------
| spring-boot-benchmark-all-native                   | 0.974, 1.556, 1.2084           |  0.979, 1.561, 1.2145          |
------------------------------------------------------------------------------------------------------------------------
```
