#!/bin/bash
#
# This script measures the runtime of each application using 0.6 CPU and 1 ActiveProcessorCount
#
# Feel free to change the script to play around with different options to your liking.
#
set -e

declare -A results

calculateStats() {
  local -a values=("$@")
  local min=${values[0]}
  local max=${values[0]}
  local sum=0

  # Iterate through the array to find min, max, and sum
  for value in "${values[@]}"; do
    if (( $(echo "$value $min" | awk '{print ($1 < $2)}') )); then
      min=$value
    fi
    if (( $(echo "$value $max" | awk '{print ($1 > $2)}') )); then
      max=$value
    fi
    sum=$(echo "$sum $value" | awk '{print ($1 + $2)}')
  done

  # Calculate average
  average=$(echo "$sum ${#values[@]}" | awk '{print ($1 / $2)}')

  # Return the results
  echo "$min, $max, $average"
}

abstractStartupTime() {
  local input="$1"
  local startupTime

  # Extract the startup time using regular expression
  startupTime=$(echo "$input" | grep -Eo 'Started Application in ([0-9.]+) seconds' | awk '{print $4}')

  # Return the extracted startup time
  echo "$startupTime"
}

abstractProcessTime() {
  local input="$1"
  local processTime

  # Extract the process time using regular expression
  processTime=$(echo "$input" | grep -Eo 'process running for ([0-9.]+)' | awk '{print $4}')

  # Return the extracted process time
  echo "$processTime"
}

abstractStartupTimes() {
  local testRawResults=("$@")
  local -a testStartupTimes

  for key in "${!testRawResults[@]}"
  do
    testStartupTimes[$key]=$(abstractStartupTime "${testRawResults[$key]}")
  done

  echo ${testStartupTimes[@]}
}

abstractProcessTimes () {
  local testRawResults=("$@")

  for key in "${!testRawResults[@]}"
  do
    testProcessTimes[$key]=$(abstractProcessTime "${testRawResults[$key]}")
  done

  echo ${testProcessTimes[@]}
}

buildAndRunTest () {
  local totalTests=2
  local projectName="$1"
  local projectType="$2"
  local additionalMavenOptions="$3"
  local fullProjectName="$projectName-$projectType"
  local -a testRawResults
  local -a testStartupTimes
  local -a testProcessTimes

  echo "Building $fullProjectName..."
  mvn -f $projectName/pom.xml $additionalMavenOptions clean spring-boot:build-image
  
  echo "Running $fullProjectName for logging purposes..."
  docker run --rm --cpus=".6" -e="BPL_SPRING_CLOUD_BINDINGS_ENABLED=false" -e="JAVA_TOOL_OPTIONS=-XX:ActiveProcessorCount=1" docker.io/library/$projectName:LOCAL-SNAPSHOT

  echo "Running $fullProjectName for benchmarking..."
  for (( i = 0; i < $totalTests; i++))
  do
    testRawResults[$i]=$(docker run --rm --cpus=".6" -e="BPL_SPRING_CLOUD_BINDINGS_ENABLED=false" -e="JAVA_TOOL_OPTIONS=-XX:ActiveProcessorCount=1" docker.io/library/$projectName:LOCAL-SNAPSHOT 2>&1 | grep "Started Application in" | sed 's/^.*\(Started Application in.*\).*$/\1/')
    echo ${testRawResults[$i]}
  done
  
  testStartupTimes=$(abstractStartupTimes "${testRawResults[@]}")
  testProcessTimes=$(abstractProcessTimes "${testRawResults[@]}")

  results["$fullProjectName"]="$(calculateStats ${testStartupTimes[@]}) | $(calculateStats ${testProcessTimes[@]})"
}

executeTest () {
  local projectName="$1"

  buildAndRunTest $1 "plain" ""
  buildAndRunTest $1 "aot" "-Paot"
  buildAndRunTest $1 "cds" "-Pcds"
  buildAndRunTest $1 "aot+cds" "-Paot+cds"
 # buildAndRunTest $1 "native" "-Pnative"
}

printMultipleCharacters () {
  local values="$1"
  local times="$2"

  for (( i = 0; i < $times; i++))
  do
    echo -n "$values"
  done

  printf "\n"
}

showResults () {
  # The total length of the table
  local length=110

  printf "\n\n"
  printMultipleCharacters "=" $length
  printf "|| %-104s ||\n" "Final Results"
  printMultipleCharacters "=" $length
  printf "| %-40s | %-30s | %-30s |\n" "Application" "Startup Time:" "Process Time:"
  printf "| %-40s | %-30s | %-30s |\n" "" "Min, Max, Average" "Min, Max, Average"

  for key in "${!results[@]}"
  do
    printMultipleCharacters "-" $length
    printf "| %-40s | %-30s | %-30s |\n" "$key" "${results[$key]%%|*}" "${results[$key]#*|}"
  done

  printMultipleCharacters "-" $length
}

executeTest spring-boot-benchmark-original
executeTest spring-boot-benchmark-tomcat
executeTest spring-boot-benchmark-data-jpa
executeTest spring-boot-benchmark-data-rest
executeTest spring-boot-benchmark-camel-activemq
executeTest spring-boot-benchmark-all

showResults