#!/bin/bash
#
# This script measures the runtime of each application using 0.6 CPU and 1 ActiveProcessorCount
#
# Feel free to change the script to play around with different options to your liking.
#
set -e
set -o pipefail

declare -A results
declare -a resultsOrdered
declare currentResult=0
totalTests=${1:-10}
if ! [[ "$totalTests" =~ ^[0-9]+$ ]] || [ "$totalTests" -eq 0 ]; then
  echo "ERROR: Test count must be a positive integer, got: '$totalTests'" >&2
  exit 1
fi

# Set up logging
mkdir -p run-logs
LOG_FILE="run-logs/benchmark-$(date +%Y-%m-%d-%H%M%S).log"
DATE_COPY="run-logs/$(date +%Y-%m-%d).log"

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
  local -a testProcessTimes

  for key in "${!testRawResults[@]}"
  do
    testProcessTimes[$key]=$(abstractProcessTime "${testRawResults[$key]}")
  done

  echo ${testProcessTimes[@]}
}

addResults () {
  local arrayVal="$1"
  local calculatedVal="$2"

  results[$arrayVal]="$calculatedVal"
  resultsOrdered[$currentResult]="$arrayVal"
  currentResult=$((currentResult+1))
}

buildAndRunTest () {
  local projectName="$1"
  local projectType="$2"
  local fullProjectName="$projectName-$projectType"
  local -a testRawResults
  local -a testStartupTimes
  local -a testProcessTimes

  echo "Building $fullProjectName..."
  $projectName/mvnw -f $projectName/pom.xml -P$projectType clean spring-boot:build-image -DimageName=$fullProjectName
  
  echo "Running $fullProjectName for logging purposes..."
  timeout 120 docker run --rm --cpus=".6" --memory=1g -e="JAVA_TOOL_OPTIONS=-XX:ActiveProcessorCount=1" docker.io/library/$fullProjectName:LOCAL-SNAPSHOT || echo "WARNING: Logging run for $fullProjectName failed or timed out"

  echo "Running $fullProjectName for benchmarking..."
  for (( i = 0; i < $totalTests; i++))
  do
    testRawResults[$i]=$(timeout 120 docker run --rm --cpus=".6" --memory=1g -e="JAVA_TOOL_OPTIONS=-XX:ActiveProcessorCount=1" docker.io/library/$fullProjectName:LOCAL-SNAPSHOT 2>&1 | grep "Started Application in" | sed 's/^.*\(Started Application in.*\).*$/\1/') || true
    if [ -z "${testRawResults[$i]}" ]; then
      echo "WARNING: Test run $i for $fullProjectName did not produce expected output"
    fi
    echo "${testRawResults[$i]}"
  done
  
  # Filter out empty results from failed/timed-out runs
  local -a validResults
  for (( i = 0; i < ${#testRawResults[@]}; i++ ))
  do
    if [ -n "${testRawResults[$i]}" ]; then
      validResults+=("${testRawResults[$i]}")
    fi
  done

  if [ ${#validResults[@]} -eq 0 ]; then
    echo "WARNING: All $totalTests runs failed for $fullProjectName — skipping stats calculation"
    addResults "$fullProjectName" "N/A | N/A"
    return
  fi

  if [ ${#validResults[@]} -lt ${#testRawResults[@]} ]; then
    echo "WARNING: Only ${#validResults[@]} of ${#testRawResults[@]} runs produced results for $fullProjectName"
  fi

  testStartupTimes=$(abstractStartupTimes "${validResults[@]}")
  testProcessTimes=$(abstractProcessTimes "${validResults[@]}")
  calculatedStartupTimes=$(calculateStats ${testStartupTimes[@]})
  calculatedProcessTimes=$(calculateStats ${testProcessTimes[@]})

  addResults "$fullProjectName" "$calculatedStartupTimes | $calculatedProcessTimes"
}

executeTest () {
  local projectName="$1"

  echo "=== Starting test module: $projectName at $(date '+%Y-%m-%d %H:%M:%S') ==="

  buildAndRunTest $1 "plain"
  buildAndRunTest $1 "aot"
  buildAndRunTest $1 "cds"
  buildAndRunTest $1 "aot-cds"
  buildAndRunTest $1 "aot-caching"
  buildAndRunTest $1 "aot-aot-caching"
  buildAndRunTest $1 "alpaquita"
  buildAndRunTest $1 "native"

  echo "=== Completed test module: $projectName at $(date '+%Y-%m-%d %H:%M:%S') ==="
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
  local length=120

  printf "\n\n"
  printMultipleCharacters "=" $length
  printf "|| %-114s ||\n" "Final Results"
  printMultipleCharacters "=" $length
  printf "| %-50s | %-30s | %-30s |\n" "Application" "Startup Time:" "Process Time:"
  printf "| %-50s | %-30s | %-30s |\n" "" "Min, Max, Average" "Min, Max, Average"

  for key in "${resultsOrdered[@]}"
  do
    printMultipleCharacters "-" $length
    printf "| %-50s | %-30s | %-30s |\n" "$key" "${results[$key]%%|*}" "${results[$key]#*|}"
  done

  printMultipleCharacters "-" $length
}

run_benchmarks() {
  executeTest spring-boot-benchmark-original
  executeTest spring-boot-benchmark-tomcat
  executeTest spring-boot-benchmark-data-jpa
  executeTest spring-boot-benchmark-data-rest
  executeTest spring-boot-benchmark-activemq
  executeTest spring-boot-benchmark-all

  showResults
}

run_benchmarks 2>&1 | tee -a "$LOG_FILE"

# Create a date-only copy of the log (symlinks don't work on Git Bash/Windows)
cp "$LOG_FILE" "$DATE_COPY"