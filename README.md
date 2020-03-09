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