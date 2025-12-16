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

Here are the final results of a run from my PC (last ran 12/15/2025):

```
========================================================================================================================
|| Final Results                                                                                                      ||
========================================================================================================================
| Application                                        | Startup Time:                  | Process Time:                  |
|                                                    | Min, Max, Average              | Min, Max, Average              |
------------------------------------------------------------------------------------------------------------------------
| spring-boot-benchmark-original-plain               | 6.684, 8.495, 7.5075           |  7.767, 9.484, 8.5623          |
------------------------------------------------------------------------------------------------------------------------
| spring-boot-benchmark-original-aot                 | 5.401, 6.605, 5.9337           |  6.379, 7.877, 7.0194          |
------------------------------------------------------------------------------------------------------------------------
| spring-boot-benchmark-original-cds                 | 4.295, 5.408, 4.7517           |  4.779, 5.999, 5.265           |
------------------------------------------------------------------------------------------------------------------------
| spring-boot-benchmark-original-aot-cds             | 3.189, 3.797, 3.4476           |  3.686, 4.412, 3.9872          |
------------------------------------------------------------------------------------------------------------------------
| spring-boot-benchmark-original-aot-caching         | 3.217, 3.8, 3.591              |  3.979, 4.47, 4.2123           |
------------------------------------------------------------------------------------------------------------------------
| spring-boot-benchmark-original-alpaquita           | 6.596, 7.398, 6.8444           |  7.618, 8.574, 7.9868          |
------------------------------------------------------------------------------------------------------------------------
| spring-boot-benchmark-original-native              | 0.058, 0.113, 0.082            |  0.063, 0.118, 0.0868          |
------------------------------------------------------------------------------------------------------------------------
| spring-boot-benchmark-tomcat-plain                 | 7.068, 7.677, 7.2523           |  7.886, 8.492, 8.0983          |
------------------------------------------------------------------------------------------------------------------------
| spring-boot-benchmark-tomcat-aot                   | 5.397, 6.482, 5.8089           |  6.279, 7.395, 6.7217          |
------------------------------------------------------------------------------------------------------------------------
| spring-boot-benchmark-tomcat-cds                   | 4.516, 5.416, 4.7417           |  4.981, 5.895, 5.2043          |
------------------------------------------------------------------------------------------------------------------------
| spring-boot-benchmark-tomcat-aot-cds               | 3.11, 3.59, 3.2803             |  3.601, 4.076, 3.7424          |
------------------------------------------------------------------------------------------------------------------------
| spring-boot-benchmark-tomcat-aot-caching           | 3.31, 3.999, 3.6147            |  3.885, 4.503, 4.1534          |
------------------------------------------------------------------------------------------------------------------------
| spring-boot-benchmark-tomcat-alpaquita             | 7.021, 7.707, 7.2475           |  8.025, 8.689, 8.2632          |
------------------------------------------------------------------------------------------------------------------------
| spring-boot-benchmark-tomcat-native                | 0.079, 0.124, 0.1025           |  0.084, 0.128, 0.1076          |
------------------------------------------------------------------------------------------------------------------------
| spring-boot-benchmark-data-jpa-plain               | 11.197, 12.298, 11.4687        |  12.2, 13.569, 12.514          |
------------------------------------------------------------------------------------------------------------------------
| spring-boot-benchmark-data-jpa-aot                 | 9.296, 9.894, 9.5731           |  10.371, 10.969, 10.617        |
------------------------------------------------------------------------------------------------------------------------
| spring-boot-benchmark-data-jpa-cds                 | 6.004, 6.307, 6.1753           |  6.582, 6.963, 6.7638          |
------------------------------------------------------------------------------------------------------------------------
| spring-boot-benchmark-data-jpa-aot-cds             | 4.502, 5.003, 4.6902           |  5.091, 5.592, 5.2752          |
------------------------------------------------------------------------------------------------------------------------
| spring-boot-benchmark-data-jpa-aot-caching         | 4.595, 4.801, 4.7008           |  5.371, 5.665, 5.4988          |
------------------------------------------------------------------------------------------------------------------------
| spring-boot-benchmark-data-jpa-alpaquita           | 11.306, 12.695, 11.6994        |  12.389, 13.891, 12.8371       |
------------------------------------------------------------------------------------------------------------------------
| spring-boot-benchmark-data-jpa-native              | 0.169, 0.37, 0.2613            |  0.174, 0.38, 0.2677           |
------------------------------------------------------------------------------------------------------------------------
| spring-boot-benchmark-data-rest-plain              | 13.271, 14.185, 13.6251        |  14.163, 15.185, 14.5806       |
------------------------------------------------------------------------------------------------------------------------
| spring-boot-benchmark-data-rest-aot                | 10.903, 11.612, 11.2799        |  11.988, 12.596, 12.2716       |
------------------------------------------------------------------------------------------------------------------------
| spring-boot-benchmark-data-rest-cds                | 7.19, 8.084, 7.4868            |  7.704, 8.678, 8.0104          |
------------------------------------------------------------------------------------------------------------------------
| spring-boot-benchmark-data-rest-aot-cds            | 5.399, 5.824, 5.6424           |  5.9, 6.392, 6.1811            |
------------------------------------------------------------------------------------------------------------------------
| spring-boot-benchmark-data-rest-aot-caching        | 5.306, 6.087, 5.5762           |  6.094, 6.872, 6.3641          |
------------------------------------------------------------------------------------------------------------------------
| spring-boot-benchmark-data-rest-alpaquita          | 13.194, 14.686, 13.9379        |  14.2, 15.982, 15.0387         |
------------------------------------------------------------------------------------------------------------------------
| spring-boot-benchmark-data-rest-native             | 0.316, 0.502, 0.378            |  0.321, 0.509, 0.3845          |
------------------------------------------------------------------------------------------------------------------------
| spring-boot-benchmark-activemq-plain               | 7.674, 8.197, 7.8407           |  8.573, 9.193, 8.7227          |
------------------------------------------------------------------------------------------------------------------------
| spring-boot-benchmark-activemq-aot                 | 5.99, 6.484, 6.2012            |  6.89, 7.5, 7.1059             |
------------------------------------------------------------------------------------------------------------------------
| spring-boot-benchmark-activemq-cds                 | 4.915, 5.399, 5.0915           |  5.372, 5.88, 5.5491           |
------------------------------------------------------------------------------------------------------------------------
| spring-boot-benchmark-activemq-aot-cds             | 3.59, 4.412, 3.7465            |  3.99, 4.888, 4.2158           |
------------------------------------------------------------------------------------------------------------------------
| spring-boot-benchmark-activemq-aot-caching         | 3.798, 4.506, 4.0734           |  4.381, 5.096, 4.6498          |
------------------------------------------------------------------------------------------------------------------------
| spring-boot-benchmark-activemq-alpaquita           | 7.619, 8.008, 7.7791           |  8.603, 9.089, 8.8024          |
------------------------------------------------------------------------------------------------------------------------
| spring-boot-benchmark-activemq-native              | 0.112, 0.179, 0.1456           |  0.117, 0.185, 0.1509          |
------------------------------------------------------------------------------------------------------------------------
| spring-boot-benchmark-all-plain                    | 13.989, 14.894, 14.303         |  14.887, 15.965, 15.2905       |
------------------------------------------------------------------------------------------------------------------------
| spring-boot-benchmark-all-aot                      | 11.71, 12.281, 11.9898         |  12.717, 13.278, 12.9811       |
------------------------------------------------------------------------------------------------------------------------
| spring-boot-benchmark-all-cds                      | 7.924, 9.2, 8.2853             |  8.479, 9.776, 8.8616          |
------------------------------------------------------------------------------------------------------------------------
| spring-boot-benchmark-all-aot-cds                  | 5.802, 6.303, 5.9979           |  6.376, 6.875, 6.5627          |
------------------------------------------------------------------------------------------------------------------------
| spring-boot-benchmark-all-aot-caching              | 5.697, 6.087, 5.8274           |  6.484, 6.971, 6.6759          |
------------------------------------------------------------------------------------------------------------------------
| spring-boot-benchmark-all-alpaquita                | 14.199, 15.723, 14.6288        |  15.298, 17.058, 15.7914       |
------------------------------------------------------------------------------------------------------------------------
| spring-boot-benchmark-all-native                   | 0.348, 0.536, 0.4487           |  0.353, 0.542, 0.4549          |
------------------------------------------------------------------------------------------------------------------------
```
