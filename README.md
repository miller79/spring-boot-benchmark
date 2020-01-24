# Spring Boot Benchmark

## Introduction

This repository is a small test benchmark for Spring Boot running in Docker.
It is meant to be a demonstration of the performance concerns with Spring Boot and will hopefully lead to a solution in the future.

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