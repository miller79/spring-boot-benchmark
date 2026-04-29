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

This repository is a benchmark for Spring Boot 4.0.6 running on Java 25 in Docker.
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

The script accepts an optional argument for the number of test iterations (default: 10):

```bash
./measure-runtime.sh       # runs 10 iterations per configuration
./measure-runtime.sh 5     # runs 5 iterations per configuration
```

Output is automatically logged to a timestamped file in the `run-logs/` directory.

Each application starts up and stops itself by running the following method in the main class of each application:

`SpringApplication.run(Application.class, args).close();`

This script builds the applications using `Maven` and the goal `spring-boot:build-image`. The different maven profiles will allow the builds to build with the following:

- plain - Builds without any customization
- aot - Builds with Spring AOT enabled
- cds - Builds with CDS enabled
- aot-caching - Builds with JVM AOT Caching enabled
- aot-aot-caching - Builds with Spring AOT and JVM AOT Caching enabled
- aot-cds - Builds with CDS and Spring AOT enabled
- alpaquita - Builds with the `bellsoft/buildpacks.builder:musl` builder
- native - Builds with native enabled

Once the application is built, the script will run the application ten times (by default) with the following settings:

- --cpus=".6"
- --memory=1g
- -e="JAVA_TOOL_OPTIONS=-XX:ActiveProcessorCount=1"

## Results

Ran on 04/29/2026 with Spring Boot 4.0.6, JDK 25, 10 iterations per configuration, --cpus=.6, --memory=1g, -XX:ActiveProcessorCount=1

| Application | Startup Time (Min, Max, Avg) | Process Time (Min, Max, Avg) |
|---|---|---|
| spring-boot-benchmark-original-plain | 7.791, 9.377, 8.418 | 8.79, 10.455, 9.4817 |
| spring-boot-benchmark-original-aot | 5.809, 8.094, 6.6121 | 6.901, 9.383, 7.759 |
| spring-boot-benchmark-original-cds | 3.59, 4.404, 4.0615 | 4.196, 5.206, 4.7741 |
| spring-boot-benchmark-original-aot-cds | 2.591, 3.602, 2.9039 | 3.198, 4.655, 3.6099 |
| spring-boot-benchmark-original-aot-caching | 3.583, 5.193, 4.3728 | 4.192, 6.075, 5.1621 |
| spring-boot-benchmark-original-aot-aot-caching | 2.313, 3.294, 2.7122 | 2.913, 4.079, 3.3775 |
| spring-boot-benchmark-original-alpaquita | 7.832, 9.389, 8.5106 | 9.114, 10.8, 9.7947 |
| spring-boot-benchmark-original-native | 0.094, 0.153, 0.1197 | 0.103, 0.162, 0.1282 |
| spring-boot-benchmark-tomcat-plain | 7.792, 9.298, 8.5671 | 8.798, 10.313, 9.6209 |
| spring-boot-benchmark-tomcat-aot | 6.018, 6.576, 6.3122 | 7.01, 7.658, 7.3253 |
| spring-boot-benchmark-tomcat-cds | 3.419, 4.011, 3.6893 | 4.069, 4.67, 4.3197 |
| spring-boot-benchmark-tomcat-aot-cds | 2.496, 3.206, 2.747 | 3.081, 3.902, 3.3485 |
| spring-boot-benchmark-tomcat-aot-caching | 3.797, 6.108, 4.9471 | 4.398, 6.814, 5.6937 |
| spring-boot-benchmark-tomcat-aot-aot-caching | 2.404, 3.105, 2.6787 | 3.0, 3.799, 3.334 |
| spring-boot-benchmark-tomcat-alpaquita | 8.515, 9.702, 8.963 | 9.69, 10.998, 10.2174 |
| spring-boot-benchmark-tomcat-native | 0.131, 0.208, 0.1602 | 0.138, 0.219, 0.1685 |
| spring-boot-benchmark-data-jpa-plain | 12.899, 15.009, 13.9766 | 13.992, 16.382, 15.17 |
| spring-boot-benchmark-data-jpa-aot | 11.295, 12.396, 11.844 | 12.468, 13.672, 13.0746 |
| spring-boot-benchmark-data-jpa-cds | 5.398, 6.901, 5.8048 | 6.301, 7.9, 6.7885 |
| spring-boot-benchmark-data-jpa-aot-cds | 3.602, 5.824, 4.1062 | 4.59, 6.802, 5.0336 |
| spring-boot-benchmark-data-jpa-aot-caching | 5.395, 6.411, 5.8252 | 6.29, 7.592, 6.8142 |
| spring-boot-benchmark-data-jpa-aot-aot-caching | 3.397, 4.609, 4.0125 | 4.198, 6.165, 5.0609 |
| spring-boot-benchmark-data-jpa-alpaquita | 13.015, 16.895, 14.7009 | 14.323, 18.295, 16.0923 |
| spring-boot-benchmark-data-jpa-native | 0.26, 0.411, 0.3245 | 0.268, 0.421, 0.334 |
| spring-boot-benchmark-data-rest-plain | 15.284, 18.207, 16.1593 | 16.37, 19.38, 17.3121 |
| spring-boot-benchmark-data-rest-aot | 12.915, 13.903, 13.4296 | 14.084, 15.108, 14.5582 |
| spring-boot-benchmark-data-rest-cds | 5.112, 6.901, 6.3723 | 6.087, 7.987, 7.303 |
| spring-boot-benchmark-data-rest-aot-cds | 3.719, 4.599, 4.1893 | 4.515, 5.583, 5.0656 |
| spring-boot-benchmark-data-rest-aot-caching | 6.103, 6.605, 6.2522 | 6.971, 7.477, 7.1875 |
| spring-boot-benchmark-data-rest-aot-aot-caching | 4.208, 5.013, 4.5537 | 5.098, 5.983, 5.4711 |
| spring-boot-benchmark-data-rest-alpaquita | 15.386, 17.497, 16.6553 | 16.579, 19.065, 17.9915 |
| spring-boot-benchmark-data-rest-native | 0.412, 0.659, 0.515 | 0.422, 0.669, 0.5245 |
| spring-boot-benchmark-activemq-plain | 8.612, 9.726, 9.1591 | 9.623, 10.793, 10.2002 |
| spring-boot-benchmark-activemq-aot | 6.592, 7.791, 7.1568 | 7.602, 9.005, 8.2222 |
| spring-boot-benchmark-activemq-cds | 3.702, 5.619, 4.0951 | 4.315, 6.212, 4.7057 |
| spring-boot-benchmark-activemq-aot-cds | 2.614, 3.089, 2.7703 | 3.274, 3.672, 3.3819 |
| spring-boot-benchmark-activemq-aot-caching | 3.811, 3.997, 3.8854 | 4.466, 4.659, 4.5275 |
| spring-boot-benchmark-activemq-aot-aot-caching | 2.101, 2.706, 2.4419 | 2.663, 3.367, 3.0266 |
| spring-boot-benchmark-activemq-alpaquita | 6.884, 8.899, 7.3584 | 7.793, 9.815, 8.3171 |
| spring-boot-benchmark-activemq-native | 0.132, 0.219, 0.1712 | 0.139, 0.228, 0.1783 |
| spring-boot-benchmark-all-plain | 12.5, 14.488, 13.3445 | 13.376, 15.458, 14.263 |
| spring-boot-benchmark-all-aot | 10.602, 12.915, 11.37 | 11.487, 13.823, 12.2796 |
| spring-boot-benchmark-all-cds | 5.11, 5.699, 5.3745 | 5.911, 6.504, 6.1812 |
| spring-boot-benchmark-all-aot-cds | 3.509, 6.9, 4.1451 | 4.295, 7.98, 5.0287 |
| spring-boot-benchmark-all-aot-caching | 4.912, 5.799, 5.3089 | 5.714, 6.601, 6.0894 |
| spring-boot-benchmark-all-aot-aot-caching | 3.603, 4.697, 4.0012 | 4.319, 5.508, 4.8076 |
| spring-boot-benchmark-all-alpaquita | 12.591, 14.688, 13.5187 | 13.679, 15.786, 14.5517 |
| spring-boot-benchmark-all-native | 0.34, 0.457, 0.3828 | 0.348, 0.465, 0.3904 |
