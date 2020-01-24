# Spring Boot Benchmark

## Introduction

This repository is a small test benchmark for Spring Boot running in Docker.
It is meant to be a demonstration of the performance concerns with Spring Boot and will hopefully lead to documentation that can focus on the desired solution.
The end goal of this benchmark is to be the most optimal configured Spring Boot application in relationship to startup time.
This hopefully will be a demo that could be used for others who are working on the same problem.

An issue for Spring Boot that follows this is available [here](https://github.com/spring-projects/spring-boot/issues/19911).

## Build and Run Application

```
docker build -t spring-boot-benchmark .
docker run --cpus=".6" spring-boot-benchmark
```

## Stop All Local Running Docker Quickly

```
docker ps -a -q | % { docker stop $_ }
docker ps -a -q | % { docker rm $_ }
```