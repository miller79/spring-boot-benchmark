# Spring Boot Benchmark

- [Spring Boot Benchmark](#spring-boot-benchmark)
  - [Introduction](#introduction)
  - [Benchmarks Available](#benchmarks-available)
    - [spring-boot-benchmark-original](#spring-boot-benchmark-original)
    - [spring-boot-benchmark-tomcat](#spring-boot-benchmark-tomcat)
    - [spring-boot-benchmark-data-jpa](#spring-boot-benchmark-data-jpa)
    - [spring-boot-benchmark-data-rest](#spring-boot-benchmark-data-rest)
    - [spring-boot-benchmark-activemq](#spring-boot-benchmark-activemq)
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

### spring-boot-benchmark-activemq

This application takes the spring-boot-benchmark-original and adds `spring-boot-starter-activemq`.

### spring-boot-benchmark-all

This application reflects the minimal application with all dependencies added.

## Build and Measure Runtimes

The `measure-runtime.sh` Bash script will build and run all projects and provide startup times. The following dependencies are required to be able to run this script:

- JDK 25+
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

Here are the final results of a run from my PC (last ran 11/25/2025):

```
========================================================================================================================
|| Final Results                                                                                                      ||
========================================================================================================================
| Application                                        | Startup Time:                  | Process Time:                  |
|                                                    | Min, Max, Average              | Min, Max, Average              |
------------------------------------------------------------------------------------------------------------------------
| spring-boot-benchmark-original-plain               | 6.516, 7.614, 6.9799           |  7.492, 8.681, 7.9772          |
------------------------------------------------------------------------------------------------------------------------
| spring-boot-benchmark-original-aot                 | 5.704, 7.098, 6.1168           |  6.772, 8.189, 7.1913          |
------------------------------------------------------------------------------------------------------------------------
| spring-boot-benchmark-original-cds                 | 4.388, 6.179, 4.924            |  4.888, 6.775, 5.4644          |
------------------------------------------------------------------------------------------------------------------------
| spring-boot-benchmark-original-aot-cds             | 2.993, 3.492, 3.1848           |  3.496, 4.074, 3.7259          |
------------------------------------------------------------------------------------------------------------------------
| spring-boot-benchmark-original-alpaquita           | 6.303, 9.006, 7.4432           |  7.296, 10.111, 8.5685         |
------------------------------------------------------------------------------------------------------------------------
| spring-boot-benchmark-original-native              | 0.058, 0.123, 0.0826           |  0.063, 0.13, 0.0879           |
------------------------------------------------------------------------------------------------------------------------
| spring-boot-benchmark-tomcat-plain                 | 6.806, 7.402, 7.1161           |  7.708, 8.29, 8.0054           |
------------------------------------------------------------------------------------------------------------------------
| spring-boot-benchmark-tomcat-aot                   | 5.301, 5.995, 5.5974           |  6.19, 6.98, 6.5058            |
------------------------------------------------------------------------------------------------------------------------
| spring-boot-benchmark-tomcat-cds                   | 4.414, 5.387, 4.6949           |  4.879, 5.864, 5.1563          |
------------------------------------------------------------------------------------------------------------------------
| spring-boot-benchmark-tomcat-aot-cds               | 3.108, 3.776, 3.3864           |  3.602, 4.258, 3.8317          |
------------------------------------------------------------------------------------------------------------------------
| spring-boot-benchmark-tomcat-alpaquita             | 6.885, 7.611, 7.2097           |  7.87, 8.7, 8.2298             |
------------------------------------------------------------------------------------------------------------------------
| spring-boot-benchmark-tomcat-native                | 0.077, 0.178, 0.1123           |  0.082, 0.185, 0.119           |
------------------------------------------------------------------------------------------------------------------------
| spring-boot-benchmark-data-jpa-plain               | 11.313, 13.004, 11.8061        |  12.466, 14.009, 12.861        |
------------------------------------------------------------------------------------------------------------------------
| spring-boot-benchmark-data-jpa-aot                 | 9.383, 10.092, 9.8443          |  10.401, 11.193, 10.8648       |
------------------------------------------------------------------------------------------------------------------------
| spring-boot-benchmark-data-jpa-cds                 | 6.283, 7.305, 6.546            |  6.863, 7.889, 7.1243          |
------------------------------------------------------------------------------------------------------------------------
| spring-boot-benchmark-data-jpa-aot-cds             | 4.78, 5.185, 4.9045            |  5.369, 5.801, 5.5022          |
------------------------------------------------------------------------------------------------------------------------
| spring-boot-benchmark-data-jpa-alpaquita           | 11.71, 20.292, 14.4133         |  12.878, 24.805, 15.961        |
------------------------------------------------------------------------------------------------------------------------
| spring-boot-benchmark-data-jpa-native              | 0.259, 0.489, 0.3248           |  0.266, 0.504, 0.3331          |
------------------------------------------------------------------------------------------------------------------------
| spring-boot-benchmark-data-rest-plain              | 13.899, 16.113, 15.1825        |  15.094, 17.412, 16.3523       |
------------------------------------------------------------------------------------------------------------------------
| spring-boot-benchmark-data-rest-aot                | 12.505, 14.475, 13.4532        |  13.421, 15.702, 14.6098       |
------------------------------------------------------------------------------------------------------------------------
| spring-boot-benchmark-data-rest-cds                | 8.404, 10.599, 9.5891          |  8.985, 11.302, 10.2464        |
------------------------------------------------------------------------------------------------------------------------
| spring-boot-benchmark-data-rest-aot-cds            | 6.708, 8.211, 7.1646           |  7.401, 8.972, 7.8055          |
------------------------------------------------------------------------------------------------------------------------
| spring-boot-benchmark-data-rest-alpaquita          | 15.522, 18.618, 16.933         |  16.801, 20.108, 18.3176       |
------------------------------------------------------------------------------------------------------------------------
| spring-boot-benchmark-data-rest-native             | 0.352, 0.475, 0.4075           |  0.364, 0.482, 0.4157          |
------------------------------------------------------------------------------------------------------------------------
| spring-boot-benchmark-activemq-plain               | 8.274, 10.819, 9.1886          |  9.27, 12.106, 10.2596         |
------------------------------------------------------------------------------------------------------------------------
| spring-boot-benchmark-activemq-aot                 | 7.005, 8.094, 7.4347           |  8.02, 9.362, 8.591            |
------------------------------------------------------------------------------------------------------------------------
| spring-boot-benchmark-activemq-cds                 | 5.386, 6.785, 6.0148           |  5.865, 7.4, 6.573             |
------------------------------------------------------------------------------------------------------------------------
| spring-boot-benchmark-activemq-aot-cds             | 3.926, 5.284, 4.5018           |  4.413, 5.893, 5.0644          |
------------------------------------------------------------------------------------------------------------------------
| spring-boot-benchmark-activemq-alpaquita           | 8.302, 11.701, 9.4432          |  9.473, 13.073, 10.6688        |
------------------------------------------------------------------------------------------------------------------------
| spring-boot-benchmark-activemq-native              | 0.095, 0.203, 0.1581           |  0.1, 0.209, 0.1644            |
------------------------------------------------------------------------------------------------------------------------
| spring-boot-benchmark-all-plain                    | 14.189, 17.001, 15.7882        |  15.269, 18.099, 16.9182       |
------------------------------------------------------------------------------------------------------------------------
| spring-boot-benchmark-all-aot                      | 12.803, 14.797, 13.7631        |  13.899, 15.879, 14.9007       |
------------------------------------------------------------------------------------------------------------------------
| spring-boot-benchmark-all-cds                      | 8.817, 10.602, 9.6784          |  9.41, 11.192, 10.3054         |
------------------------------------------------------------------------------------------------------------------------
| spring-boot-benchmark-all-aot-cds                  | 6.191, 7.71, 6.7228            |  6.712, 8.406, 7.3489          |
------------------------------------------------------------------------------------------------------------------------
| spring-boot-benchmark-all-alpaquita                | 13.995, 18.096, 15.5845        |  15.191, 19.706, 16.8526       |
------------------------------------------------------------------------------------------------------------------------
| spring-boot-benchmark-all-native                   | 0.382, 0.619, 0.4645           |  0.391, 0.629, 0.4728          |
------------------------------------------------------------------------------------------------------------------------
```
