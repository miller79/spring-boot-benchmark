FROM maven:3.6.3-jdk-11 AS build
COPY src /tmp/src/
COPY pom.xml /tmp/
WORKDIR /tmp/
RUN mvn package

FROM openjdk:11
COPY --from=build /tmp/target/spring-boot-benchmark.jar spring-boot-benchmark.jar
EXPOSE 8080
ENTRYPOINT exec java $JAVA_OPTS -jar spring-boot-benchmark.jar