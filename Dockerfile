FROM maven:3.6.0-jdk-11 AS build
COPY src /tmp/src/
COPY pom.xml /tmp/
WORKDIR /tmp/
RUN mvn clean verify

FROM openjdk:11
EXPOSE 8080

ADD target/spring-boot-benchmark.jar spring-boot-benchmark.jar
ENTRYPOINT exec java $JAVA_OPTS -jar spring-boot-benchmark.jar