# Spring Boot Benchmark

## Introduction

This repository is a benchmark for Spring Boot running in Docker.
It is meant to be a demonstration of the performance concerns with Spring Boot and will hopefully lead to documentation that can focus on the desired solution.
The end goal of this benchmark is to be the most optimal configured Spring Boot application in relationship to startup time.
This hopefully will be a demo that could be used for others who are working on the same problem.

An issue for Spring Boot that this was originally created for is [here](https://github.com/spring-projects/spring-boot/issues/19911).

## Benchmarks Available

The following benchmarks are available within this project.

### spring-boot-benchmark-original

This application is a barebones Spring Boot application demonstrating a way to create an application with just `spring-boot-starter-webflux`.

### spring-boot-benchmark-native

This application takes the spring-boot-benchmark-original and makes it native compatible to run on GraalVM.

### spring-boot-benchmark-tomcat

This application takes the spring-boot-benchmark-original and replaces webflux with web to test Tomcat vs Netty.

### spring-boot-benchmark-data-jpa

This is a Spring Boot application that uses `spring-boot-starter-data-jpa`.

### spring-boot-benchmark-data-rest

This is a Spring Boot application that uses `spring-boot-starter-data-rest`.

### spring-boot-benchmark-camel-activemq

This application takes the spring-boot-benchmark-original and adds `camel-activemq-starter`.

### spring-boot-benchmark-all

This application reflects the minimal application with all dependencies added.

## Build and Measure Runtimes

The `measure-runtime.sh` Bash Script will build and run of the projects and provide startup times. To run this script the following dependencies are required:

- Maven 3.6.3+
- JDK 21+
- Docker

## Results

Here are the logs of a run from my PC:

```
```