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
| spring-boot-benchmark-original-plain               | 8.19, 9.696, 8.7806            |  9.296, 10.801, 9.9285         |
------------------------------------------------------------------------------------------------------------------------
| spring-boot-benchmark-original-aot                 | 6.179, 8.175, 6.7681           |  7.366, 10.483, 8.0865         |
------------------------------------------------------------------------------------------------------------------------
| spring-boot-benchmark-original-cds                 | 5.202, 7.395, 5.9091           |  5.864, 8.191, 6.6751          |
------------------------------------------------------------------------------------------------------------------------
| spring-boot-benchmark-original-aot-cds             | 3.495, 5.4, 4.224              |  4.189, 6.356, 4.9973          |
------------------------------------------------------------------------------------------------------------------------
| spring-boot-benchmark-original-native              | 0.088, 0.192, 0.1212           |  0.094, 0.201, 0.1283          |
------------------------------------------------------------------------------------------------------------------------
| spring-boot-benchmark-tomcat-plain                 | 8.723, 11.1, 9.2169            |  9.885, 12.473, 10.4112        |
------------------------------------------------------------------------------------------------------------------------
| spring-boot-benchmark-tomcat-aot                   | 6.6, 8.092, 6.881              |  7.709, 9.209, 8.0676          |
------------------------------------------------------------------------------------------------------------------------
| spring-boot-benchmark-tomcat-cds                   | 5.515, 6.812, 6.097            |  6.205, 7.596, 6.8311          |
------------------------------------------------------------------------------------------------------------------------
| spring-boot-benchmark-tomcat-aot-cds               | 3.704, 4.88, 4.1367            |  4.485, 5.796, 4.9141          |
------------------------------------------------------------------------------------------------------------------------
| spring-boot-benchmark-tomcat-native                | 0.142, 0.289, 0.1962           |  0.149, 0.296, 0.2038          |
------------------------------------------------------------------------------------------------------------------------
| spring-boot-benchmark-data-jpa-plain               | 15.298, 18.212, 16.4144        |  16.419, 19.403, 17.69         |
------------------------------------------------------------------------------------------------------------------------
| spring-boot-benchmark-data-jpa-aot                 | 12.403, 21.375, 14.7301        |  13.801, 24.086, 16.2954       |
------------------------------------------------------------------------------------------------------------------------
| spring-boot-benchmark-data-jpa-cds                 | 9.422, 12.704, 10.4674         |  10.116, 13.695, 11.3036       |
------------------------------------------------------------------------------------------------------------------------
| spring-boot-benchmark-data-jpa-aot-cds             | 7.417, 8.615, 7.9381           |  8.214, 9.413, 8.7113          |
------------------------------------------------------------------------------------------------------------------------
| spring-boot-benchmark-data-jpa-native              | 0.458, 0.757, 0.6115           |  0.463, 0.77, 0.6199           |
------------------------------------------------------------------------------------------------------------------------
| spring-boot-benchmark-data-rest-plain              | 18.121, 23.22, 19.5354         |  19.393, 24.508, 20.8207       |
------------------------------------------------------------------------------------------------------------------------
| spring-boot-benchmark-data-rest-aot                | 16.397, 22.992, 18.2479        |  17.694, 24.289, 19.5999       |
------------------------------------------------------------------------------------------------------------------------
| spring-boot-benchmark-data-rest-cds                | 11.815, 15.585, 12.9804        |  12.609, 16.384, 13.8197       |
------------------------------------------------------------------------------------------------------------------------
| spring-boot-benchmark-data-rest-aot-cds            | 9.61, 11.208, 10.2171          |  10.395, 12.176, 11.0337       |
------------------------------------------------------------------------------------------------------------------------
| spring-boot-benchmark-data-rest-native             | 0.851, 1.009, 0.947            |  0.859, 1.019, 0.9548          |
------------------------------------------------------------------------------------------------------------------------
| spring-boot-benchmark-camel-activemq-plain         | 11.319, 23.708, 14.2471        |  12.581, 25.503, 15.729        |
------------------------------------------------------------------------------------------------------------------------
| spring-boot-benchmark-camel-activemq-aot           | 8.921, 10.5, 9.5242            |  10.108, 11.696, 10.8044       |
------------------------------------------------------------------------------------------------------------------------
| spring-boot-benchmark-camel-activemq-cds           | 7.601, 8.689, 7.9881           |  8.311, 9.486, 8.7727          |
------------------------------------------------------------------------------------------------------------------------
| spring-boot-benchmark-camel-activemq-aot-cds       | 5.399, 7.723, 6.1178           |  6.185, 8.589, 6.8748          |
------------------------------------------------------------------------------------------------------------------------
| spring-boot-benchmark-camel-activemq-native        | 0.383, 0.618, 0.4813           |  0.39, 0.627, 0.4885           |
------------------------------------------------------------------------------------------------------------------------
| spring-boot-benchmark-all-plain                    | 21.782, 30.397, 26.4149        |  23.302, 32.386, 28.02         |
------------------------------------------------------------------------------------------------------------------------
| spring-boot-benchmark-all-aot                      | 20.4, 34.183, 26.66            |  21.923, 36.198, 28.31         |
------------------------------------------------------------------------------------------------------------------------
| spring-boot-benchmark-all-cds                      | 14.599, 18.706, 16.2118        |  15.405, 19.812, 17.1498       |
------------------------------------------------------------------------------------------------------------------------
| spring-boot-benchmark-all-aot-cds                  | 12.01, 13.306, 12.6582         |  12.894, 14.195, 13.5219       |
------------------------------------------------------------------------------------------------------------------------
| spring-boot-benchmark-all-native                   | 1.127, 1.348, 1.224            |  1.134, 1.358, 1.2311          |
------------------------------------------------------------------------------------------------------------------------
```
