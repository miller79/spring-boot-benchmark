FROM maven:3.6.3-jdk-11 AS build
ADD . /tmp/
WORKDIR /tmp/
RUN mvn package

FROM openjdk:11
ENV JAVA_OPTIONS="-Dquarkus.http.host=0.0.0.0 -Djava.util.logging.manager=org.jboss.logmanager.LogManager"
ENV AB_ENABLED=jmx_exporter
COPY --from=build /tmp/target/lib/* /deployments/lib/
COPY --from=build /tmp/target/*-runner.jar /deployments/app.jar
EXPOSE 8080
ENTRYPOINT exec java $JAVA_OPTIONS -jar /deployments/app.jar