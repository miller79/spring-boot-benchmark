FROM maven:3.6.3-jdk-11 AS build
ADD . /tmp/
WORKDIR /tmp/
RUN mvn package
RUN mkdir /tmp/target/dependency
RUN unzip /tmp/target/spring-boot-benchmark-original.jar -d /tmp/target/dependency 

FROM openjdk:11
ARG DEPENDENCY=/tmp/target/dependency
COPY --from=build ${DEPENDENCY}/BOOT-INF/lib /app/lib
COPY --from=build ${DEPENDENCY}/META-INF /app/META-INF
COPY --from=build ${DEPENDENCY}/BOOT-INF/classes /app
EXPOSE 8080
ENTRYPOINT exec java $JAVA_OPTS -Dspring.backgroundpreinitializer.ignore=true -Dspring.config.location=classpath:/application.yml -cp app:app/lib/* miller79.Application