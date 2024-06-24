#!/bin/bash
#
# This script measures the runtime of each application using 0.6 CPU and 1 ActiveProcessorCount
#
# Feel free to change the script to play around with different options to your liking.
#
set -e

executeTest () {
  echo "Building $1..."
  mvn -f $1/pom.xml -q $2 clean spring-boot:build-image
  
  echo "Running $1..."
  for i in {1..10}
  do
    echo "`(docker run --rm --cpus=".6" -e="BPL_SPRING_CLOUD_BINDINGS_ENABLED=false" -e="JAVA_TOOL_OPTIONS=-XX:ActiveProcessorCount=1" docker.io/library/$1:LOCAL-SNAPSHOT) 2>&1 | grep "Started Application in"`"
  done
}

executeTest spring-boot-benchmark-original ""
executeTest spring-boot-benchmark-tomcat ""
executeTest spring-boot-benchmark-native "-Pnative"
executeTest spring-boot-benchmark-data-jpa ""
executeTest spring-boot-benchmark-data-rest ""
executeTest spring-boot-benchmark-camel-activemq ""
executeTest spring-boot-benchmark-all ""
executeTest spring-boot-benchmark-all-native "-Pnative"