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

```