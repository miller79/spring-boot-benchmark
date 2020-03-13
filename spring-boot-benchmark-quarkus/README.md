# Spring Boot Benchmark Quarkus

This application is the out of the box quarkus app for startup time comparison purposes only.

The following is the logs of the startup running on my box.

```
2020-03-13 21:06:38,960 WARN  [io.qua.net.run.NettyRecorder] (Thread-0) Localhost lookup took more than one second, you need to add a /etc/hosts entry to improve Quarkus startup time. See https://thoeni.io/post/macos-sierra-java/ for details.
2020-03-13 21:06:40,969 INFO  [io.quarkus] (main) getting-started 1.0-SNAPSHOT (running on Quarkus 1.2.1.Final) started in 13.403s. Listening on: http://0.0.0.0:8080
2020-03-13 21:06:40,970 INFO  [io.quarkus] (main) Profile prod activated.
2020-03-13 21:06:40,974 INFO  [io.quarkus] (main) Installed features: [cdi, resteasy]
```