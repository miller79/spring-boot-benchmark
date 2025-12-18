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
- aot - Builds with Spring AOT enabled
- cds - Builds with CDS enabled
- aot-caching - Builds with JVM AOT Caching enabled
- aot-aot-caching - Builds with Spring AOT and JVM AOT Caching enabled
- aot-cds - Builds with CDS and Spring AOT enabled
- alpaquita - Builds with the `bellsoft/buildpacks.builder:musl` builder
- native - Builds with native enabled

Once the application is built, the script will run the application ten times with the following settings:

- --cpus=".6"
- -e="JAVA_TOOL_OPTIONS=-XX:ActiveProcessorCount=1"

## Results

Here are the final results of a run from my PC (last ran 12/17/2025):

```
========================================================================================================================
|| Final Results                                                                                                      ||
========================================================================================================================
| Application                                        | Startup Time:                  | Process Time:                  |
|                                                    | Min, Max, Average              | Min, Max, Average              |
------------------------------------------------------------------------------------------------------------------------
| spring-boot-benchmark-original-plain               | 6.005, 6.597, 6.2242           |  6.899, 7.482, 7.1394          |
------------------------------------------------------------------------------------------------------------------------
| spring-boot-benchmark-original-aot                 | 4.609, 5.105, 4.8901           |  5.502, 6.09, 5.8037           |
------------------------------------------------------------------------------------------------------------------------
| spring-boot-benchmark-original-cds                 | 4.115, 5.494, 4.7519           |  4.598, 5.979, 5.2611          |
------------------------------------------------------------------------------------------------------------------------
| spring-boot-benchmark-original-aot-cds             | 2.695, 3.381, 2.9979           |  3.173, 3.893, 3.5105          |
------------------------------------------------------------------------------------------------------------------------
| spring-boot-benchmark-original-aot-caching         | 3.097, 4.317, 3.9281           |  3.691, 5.075, 4.5655          |
------------------------------------------------------------------------------------------------------------------------
| spring-boot-benchmark-original-aot-aot-caching     | 2.11, 3.006, 2.4103            |  2.769, 3.775, 3.0349          |
------------------------------------------------------------------------------------------------------------------------
| spring-boot-benchmark-original-alpaquita           | 6.027, 7.71, 6.7064            |  7.169, 9.114, 7.8678          |
------------------------------------------------------------------------------------------------------------------------
| spring-boot-benchmark-original-native              | 0.056, 0.28, 0.0892            |  0.06, 0.305, 0.096            |
------------------------------------------------------------------------------------------------------------------------
| spring-boot-benchmark-tomcat-plain                 | 6.498, 7.779, 7.1228           |  7.386, 8.783, 8.0379          |
------------------------------------------------------------------------------------------------------------------------
| spring-boot-benchmark-tomcat-aot                   | 4.993, 5.58, 5.2817            |  5.793, 6.583, 6.1357          |
------------------------------------------------------------------------------------------------------------------------
| spring-boot-benchmark-tomcat-cds                   | 4.207, 4.812, 4.4181           |  4.68, 5.2, 4.841              |
------------------------------------------------------------------------------------------------------------------------
| spring-boot-benchmark-tomcat-aot-cds               | 3.005, 3.993, 3.3744           |  3.464, 4.479, 3.8351          |
------------------------------------------------------------------------------------------------------------------------
| spring-boot-benchmark-tomcat-aot-caching           | 3.4, 4.01, 3.627               |  3.898, 4.691, 4.1661          |
------------------------------------------------------------------------------------------------------------------------
| spring-boot-benchmark-tomcat-aot-aot-caching       | 2.103, 2.403, 2.2284           |  2.588, 2.881, 2.734           |
------------------------------------------------------------------------------------------------------------------------
| spring-boot-benchmark-tomcat-alpaquita             | 6.498, 7.083, 6.7622           |  7.486, 8.084, 7.7409          |
------------------------------------------------------------------------------------------------------------------------
| spring-boot-benchmark-tomcat-native                | 0.075, 0.123, 0.0998           |  0.08, 0.127, 0.1043           |
------------------------------------------------------------------------------------------------------------------------
| spring-boot-benchmark-data-jpa-plain               | 10.392, 11.491, 10.8737        |  11.368, 12.472, 11.8473       |
------------------------------------------------------------------------------------------------------------------------
| spring-boot-benchmark-data-jpa-aot                 | 8.702, 10.193, 9.3786          |  9.674, 11.111, 10.3265        |
------------------------------------------------------------------------------------------------------------------------
| spring-boot-benchmark-data-jpa-cds                 | 5.698, 6.501, 5.9515           |  6.194, 7.079, 6.5147          |
------------------------------------------------------------------------------------------------------------------------
| spring-boot-benchmark-data-jpa-aot-cds             | 4.307, 7.323, 5.1831           |  4.812, 7.918, 5.792           |
------------------------------------------------------------------------------------------------------------------------
| spring-boot-benchmark-data-jpa-aot-caching         | 4.286, 4.598, 4.442            |  5.078, 5.416, 5.2296          |
------------------------------------------------------------------------------------------------------------------------
| spring-boot-benchmark-data-jpa-aot-aot-caching     | 3.227, 3.902, 3.4532           |  4.071, 4.677, 4.2367          |
------------------------------------------------------------------------------------------------------------------------
| spring-boot-benchmark-data-jpa-alpaquita           | 10.591, 14.296, 11.5724        |  11.769, 15.509, 12.705        |
------------------------------------------------------------------------------------------------------------------------
| spring-boot-benchmark-data-jpa-native              | 0.185, 0.227, 0.2107           |  0.19, 0.233, 0.2163           |
------------------------------------------------------------------------------------------------------------------------
| spring-boot-benchmark-data-rest-plain              | 12.394, 14.183, 12.8582        |  13.289, 15.1, 13.7816         |
------------------------------------------------------------------------------------------------------------------------
| spring-boot-benchmark-data-rest-aot                | 10.295, 11.725, 10.9951        |  11.323, 12.608, 11.939        |
------------------------------------------------------------------------------------------------------------------------
| spring-boot-benchmark-data-rest-cds                | 6.991, 7.69, 7.2811            |  7.479, 8.193, 7.8158          |
------------------------------------------------------------------------------------------------------------------------
| spring-boot-benchmark-data-rest-aot-cds            | 5.209, 5.909, 5.4845           |  5.78, 6.395, 6.0331           |
------------------------------------------------------------------------------------------------------------------------
| spring-boot-benchmark-data-rest-aot-caching        | 5.187, 5.688, 5.4289           |  5.994, 6.481, 6.2189          |
------------------------------------------------------------------------------------------------------------------------
| spring-boot-benchmark-data-rest-aot-aot-caching    | 3.706, 4.305, 3.9282           |  4.566, 5.073, 4.7107          |
------------------------------------------------------------------------------------------------------------------------
| spring-boot-benchmark-data-rest-alpaquita          | 12.724, 14.111, 13.1833        |  13.796, 15.183, 14.2606       |
------------------------------------------------------------------------------------------------------------------------
| spring-boot-benchmark-data-rest-native             | 0.271, 0.361, 0.3176           |  0.278, 0.369, 0.3248          |
------------------------------------------------------------------------------------------------------------------------
| spring-boot-benchmark-activemq-plain               | 6.971, 8.4, 7.5704             |  7.886, 9.279, 8.4503          |
------------------------------------------------------------------------------------------------------------------------
| spring-boot-benchmark-activemq-aot                 | 5.595, 7.394, 5.9783           |  6.401, 8.679, 6.8944          |
------------------------------------------------------------------------------------------------------------------------
| spring-boot-benchmark-activemq-cds                 | 4.682, 5.005, 4.808            |  5.083, 5.495, 5.2234          |
------------------------------------------------------------------------------------------------------------------------
| spring-boot-benchmark-activemq-aot-cds             | 3.198, 3.795, 3.508            |  3.686, 4.282, 3.954           |
------------------------------------------------------------------------------------------------------------------------
| spring-boot-benchmark-activemq-aot-caching         | 3.423, 3.884, 3.6559           |  4.002, 4.382, 4.1856          |
------------------------------------------------------------------------------------------------------------------------
| spring-boot-benchmark-activemq-aot-aot-caching     | 2.299, 2.591, 2.452            |  2.881, 3.081, 2.9804          |
------------------------------------------------------------------------------------------------------------------------
| spring-boot-benchmark-activemq-alpaquita           | 7.194, 7.902, 7.4777           |  8.183, 8.898, 8.4689          |
------------------------------------------------------------------------------------------------------------------------
| spring-boot-benchmark-activemq-native              | 0.093, 0.174, 0.1369           |  0.098, 0.179, 0.1416          |
------------------------------------------------------------------------------------------------------------------------
| spring-boot-benchmark-all-plain                    | 12.887, 13.788, 13.286         |  13.802, 14.69, 14.2325        |
------------------------------------------------------------------------------------------------------------------------
| spring-boot-benchmark-all-aot                      | 10.912, 11.284, 11.1261        |  11.88, 12.274, 12.0947        |
------------------------------------------------------------------------------------------------------------------------
| spring-boot-benchmark-all-cds                      | 7.493, 9.413, 7.8118           |  7.995, 9.984, 8.3555          |
------------------------------------------------------------------------------------------------------------------------
| spring-boot-benchmark-all-aot-cds                  | 5.604, 6.499, 5.8771           |  6.172, 6.991, 6.4195          |
------------------------------------------------------------------------------------------------------------------------
| spring-boot-benchmark-all-aot-caching              | 5.406, 5.819, 5.5864           |  6.186, 6.626, 6.3847          |
------------------------------------------------------------------------------------------------------------------------
| spring-boot-benchmark-all-aot-aot-caching          | 3.719, 4.396, 4.0306           |  4.509, 5.272, 4.8112          |
------------------------------------------------------------------------------------------------------------------------
| spring-boot-benchmark-all-alpaquita                | 13.291, 14.187, 13.6541        |  14.309, 15.199, 14.7325       |
------------------------------------------------------------------------------------------------------------------------
| spring-boot-benchmark-all-native                   | 0.379, 0.55, 0.4461            |  0.386, 0.557, 0.4528          |
------------------------------------------------------------------------------------------------------------------------
```
