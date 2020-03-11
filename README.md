# Spring Boot Benchmark

## Introduction

This repository is a small test benchmark for Spring Boot running in Docker.
It is meant to be a demonstration of the performance concerns with Spring Boot and will hopefully lead to documentation that can focus on the desired solution.
The end goal of this benchmark is to be the most optimal configured Spring Boot application in relationship to startup time.
This hopefully will be a demo that could be used for others who are working on the same problem.

An issue for Spring Boot that follows this is available [here](https://github.com/spring-projects/spring-boot/issues/19911).

## Benchmarks Available

The following benchmarks are available within this project.

### spring-boot-benchmark-original

This application is a barebones Spring Boot application demonstrating the optimized way to create an application with just `spring-boot-starter-webflux`.

### spring-boot-benchmark-data-jpa

This application shows optimizations for applications using Spring Boot using `spring-boot-starter-data-jpa`.

### spring-boot-benchmark-data-rest

This application shows optimizations for applications using Spring Boot using `spring-boot-starter-data-rest`.

### spring-boot-benchmark-cloud-config

This application takes the spring-boot-benchmark-original and adds `spring-cloud-starter-config`.

### spring-boot-benchmark-camel-activemq

This application takes the spring-boot-benchmark-original and adds `camel-activemq-starter`.

### spring-boot-benchmark-keycloak

This application takes the spring-boot-benchmark-original and adds `keycloak-spring-boot-starter`.

### spring-boot-benchmark-micronaut

This application wraps the spring-boot-benchmark-original with the Micronaut framework.

### spring-boot-benchmark-all

This application reflects the minimal application with all dependencies added.

## Build and Run Application

Go to the folder of the benchmark you would like to run an run the following commands.

```
docker build -t spring-boot-benchmark .
docker run --cpus=".6" spring-boot-benchmark
```

## Stop All Local Running Docker Quickly (PowerShell commands)

```
docker ps -a -q | % { docker stop $_ }
docker ps -a -q | % { docker rm $_ }
```

## Resources

[Various Framework Benchmark](various-framework-benchmark.md)