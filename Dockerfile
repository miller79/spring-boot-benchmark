FROM maven:3.6.0-jdk-11 AS build
COPY src /usr/src/app/src
COPY pom.xml /usr/src/app
RUN mvn -f /usr/src/app/pom.xml clean verify

FROM openjdk:11
EXPOSE 8080

ADD target/spring-boot-benchmark.jar app.jar
ENTRYPOINT exec java $JAVA_OPTS -jar app.jar