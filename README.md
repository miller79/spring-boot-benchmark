# Build and Run Application

```
docker build -t spring-boot-benchmark:latest .
docker run --cpus=".4" spring-boot-benchmark:latest
```

# Stop All Local Running Docker Quickly

```
docker ps -a -q | % { docker stop $_ }
docker ps -a -q | % { docker rm $_ }
```