# Spring Boot Benchmark

- [Spring Boot Benchmark](#spring-boot-benchmark)
  - [Introduction](#introduction)
  - [Benchmarks Available](#benchmarks-available)
    - [spring-boot-benchmark-original](#spring-boot-benchmark-original)
    - [spring-boot-benchmark-tomcat](#spring-boot-benchmark-tomcat)
    - [spring-boot-benchmark-data-jpa](#spring-boot-benchmark-data-jpa)
    - [spring-boot-benchmark-data-rest](#spring-boot-benchmark-data-rest)
    - [spring-boot-benchmark-activemq](#spring-boot-benchmark-activemq)
    - [spring-boot-benchmark-all](#spring-boot-benchmark-all)
  - [Build and Measure Runtimes](#build-and-measure-runtimes)
  - [Continuous benchmarking (GitHub Actions)](#continuous-benchmarking-github-actions)
    - [Benchmark dashboard](#benchmark-dashboard)
  - [Results](#results)

## Introduction

This repository is a benchmark for Spring Boot 4.1.1 running on Java 25 in Docker.
It is meant to demonstrate the performance concerns with Spring Boot and, hopefully, lead to documentation that can focus on the desired solution.
The end goal of this benchmark is to be the most optimally configured Spring Boot application in relationship to startup time.
This repository can be used as a benchmark that others can use to demonstrate startup timing benchmarks.

The Spring Boot GitHub issue this repository was created originally for is available [here](https://github.com/spring-projects/spring-boot/issues/19911).

## Benchmarks Available

The following benchmarks are available within this project.

### spring-boot-benchmark-original

This project is a barebones Spring Boot application that demonstrates an application using just `spring-boot-starter-webflux`.

### spring-boot-benchmark-tomcat

This application takes the spring-boot-benchmark-original and replaces webflux with web to test Tomcat vs Netty.

### spring-boot-benchmark-data-jpa

This application is a Spring Boot application that uses `spring-boot-starter-data-jpa`.

### spring-boot-benchmark-data-rest

This application is a Spring Boot application that uses `spring-boot-starter-data-rest`.

### spring-boot-benchmark-activemq

This application takes the spring-boot-benchmark-original and adds `spring-boot-starter-activemq`.

### spring-boot-benchmark-all

This application reflects the minimal application with all dependencies added.

## Build and Measure Runtimes

The `measure-runtime.sh` Bash script will build and run all projects and provide startup times. The following dependencies are required to be able to run this script:

- JDK 25+
- Docker

The script accepts an optional argument for the number of test iterations (default: 10):

```bash
./measure-runtime.sh       # runs 10 iterations per configuration
./measure-runtime.sh 5     # runs 5 iterations per configuration
```

Output is automatically logged to a timestamped file in the `run-logs/` directory.

Each application starts up and stops itself by running the following method in the main class of each application:

`SpringApplication.run(Application.class, args).close();`

This script builds the applications using `Maven` and the goal `spring-boot:build-image`. The different maven profiles will allow the builds to build with the following:

- plain - Builds without any customization
- aot - Builds with Spring AOT enabled
- cds - Builds with CDS enabled
- aot-caching - Builds with JVM AOT Caching enabled
- aot-aot-caching - Builds with Spring AOT and JVM AOT Caching enabled
- aot-cds - Builds with CDS and Spring AOT enabled
- alpaquita - Builds with the `bellsoft/buildpacks.builder:musl` builder
- native - Builds with native enabled

Once the application is built, the script will run the application ten times (by default) with the following settings:

- --cpus=".6"
- --memory=1g
- -e="JAVA_TOOL_OPTIONS=-XX:ActiveProcessorCount=1"

## Running locally / behind a corporate mirror

Builds use the project's Maven wrapper (`mvnw`) by default. In an environment where the wrapper cannot download Maven (for example behind a corporate mirror), use a Maven that is already installed and, if needed, your own settings file:

```bash
export BENCH_MAVEN_MODE=system                    # wrapper (default) | system
export BENCH_MAVEN_SETTINGS=$HOME/mirror-settings.xml   # optional, passed to Maven as -s
./measure-runtime.sh 5
```

- `wrapper` runs `bash <module>/mvnw`. `system` runs `mvn` from `PATH` and fails with a clear message if it is missing.
- `BENCH_MAVEN_SETTINGS` applies in both modes and must point to a readable file. Any other `BENCH_MAVEN_MODE` value is rejected.
- Both `measure-runtime.sh` and `ci/build.sh` (used by the workflow) read the same variables. The `benchmark` workflow's manual run has matching `maven_mode` and `maven_settings` inputs; the settings path must exist on the runner.
- Check the selection logic with `ci/test-maven.sh`.

## Continuous benchmarking (GitHub Actions)

**Where to see the results**

| Where | What you see | When available |
|---|---|---|
| [Actions](https://github.com/miller79/spring-boot-benchmark/actions) > workflow **benchmark** > a run > **Summary** (the `bench (<module>)` jobs) | Tables per module and CPU profile: started/wall medians, p95 and ratio to `plain` with 95% intervals, throttling, peak memory. | Every run that benchmarked a module. Works today. |
| Same run > **Artifacts** > `results-<module>` | The raw results files of that module (kept 30 days). | Same as above. |
| Branch [`bench-data`](https://github.com/miller79/spring-boot-benchmark/tree/bench-data), file `data.js` (the dashboard's `index.html` is next to it) | The published history: ratio to `plain` per module, plus absolute median ms in the `-absolute` series (best effort). | After the first full run on `main` has published. Not there yet (**Unverified** until seen). |
| Dashboard https://miller79.github.io/spring-boot-benchmark/ | Charts of that history. See [Benchmark dashboard](#benchmark-dashboard). | After the one-time Pages setup below and a `main` run. **Unverified**: not seen live. |
| [Issues](https://github.com/miller79/spring-boot-benchmark/issues), title `Benchmark alert: <module>` | A ratio worse than 120% of that module's previous published run (one issue per module, updated on repeat). The action also comments on the commit. | After a regression on a full `main` run. |

Smoke versus full: a `pull_request` run is a **smoke** benchmark (`plain` and `aot-cds`, 0.6 CPU, 10 starts, one repeat, head vs base). It shows up only in the job summary and artifacts and is never published. A **full** run (all 8 profiles, 3 CPU profiles, 30 starts) happens on a push to `main`, and only those runs reach `bench-data`, the dashboard and the alerts. A manual `workflow_dispatch` run uses the grid you choose and never publishes. If a module cannot be published, its `publish (<module>)` job turns the run red.

The `benchmark` workflow (`.github/workflows/benchmark.yml`, drivers in `ci/`) runs the startup benchmark on GitHub-hosted `ubuntu-24.04` runners. There is no schedule: it runs only when benchmarked code changes, or manually.

| Trigger | What runs |
|---|---|
| `pull_request` (same-repo branches only, never forks) | Only modules whose `src/`, `pom.xml` or `.mvn/` changed (or all, if `spring-boot-benchmark-parent`, `ci/` or the workflow changed). Smoke: `plain` and `aot-cds`, 0.6 CPU, 10 starts, **merge result (`refs/pull/N/merge`) vs the PR base**; a module that is new in the PR runs head only. Results appear in the job summary; nothing is commented or published. With 10 starts the p95 column is only indicative. |
| `push` to `main` (same path filters) | Full grid for every module changed since the **last successful push run** (not just since the previous commit): 8 profiles x 0.6/1.0/2.0 CPU x 30 starts. If that run is unknown, every module runs. Ratios and absolute times of each module that benchmarked successfully are appended to the `bench-data` branch; a regression alert opens (or updates) one issue per module. A module that cannot be published, or whose runs left a cell with too few successful starts (below), turns the run red. |
| `workflow_dispatch` | Choose modules, profiles, CPU profiles and iterations (profiles and CPU profiles must be known names, iterations 1-999, duplicates are removed). Never publishes. Tick `spike` to record disk headroom, cgroup/cpuset behaviour and run-to-run noise (3 repeats). |

How to read the results:

- Each module builds and benchmarks in its own job (one VM). Variants run interleaved in random order, pinned to cores 2-3 with `--cpus`/`--memory`. `p06` reproduces `measure-runtime.sh`.
- **Trust ratios to `plain` inside one job. Treat absolute times as orientation only**: do not compare them across runs or with the table below (a different machine). Shared VMs are noisy; summaries show 95% bootstrap intervals.
- The apps close themselves after startup, so "wall" is container start to exit, and "started" is Spring's own `Started Application in` line. "wall" includes the `docker start` latency (roughly constant), which pulls wall ratios of very fast variants such as `native` towards 1; prefer "started" for those. `cpu.stat` throttling and `memory.peak` are sampled while the container runs (a lower bound).
- History lives on the `bench-data` branch (created automatically). Each module is its own series group (`spring-boot-benchmark-<module>`): a regression alert fires when a ratio worsens by more than 20% against **that module's previous published run, and only for series present in it**. There is no confidence-interval test, only the threshold, which is a starting value until the spike measures real noise.
- Only the ratio series raise alerts, so a regression of `plain` itself (all other ratios improve) is **not alerted**; it may be visible in the absolute series on the dashboard, but those numbers are noisy on shared runners and nobody is notified about them.
- Pushes that are queued behind a running benchmark can be cancelled by newer ones; no module is lost, because the next successful run covers everything changed since the last successful one. A module that failed or whose results artifact is missing is not published; its publish job fails, so the run is red and it is retried by the next push to `main`. A changed module directory unknown to `ci/plan.sh` also fails the plan instead of being skipped.
- **Regression versus publish error.** The benchmark action fails its step the same way for a regression alert (raised after it pushed the data) and for a publish error (nothing pushed), and has no outputs to tell them apart. The publish job therefore checks `bench-data` itself: it must have moved and its `data.js` must hold this commit's entry for the module (`ci/landed.sh`, `ci/verify_published.py`). If not, the job is red and the next push retries the module. If the data landed and the action still failed, that is treated as a regression: the module issue is opened or updated and the job is green. **A regression does not hold back the "last successful push run"**: it means "ingested", not "fast enough". Its data point is already published, and a later push compares against that already-regressed point and stays silent, so holding it back would only re-benchmark commits for nothing. The issue is the alert; it is retried 3 times and, if it still cannot be opened, the job is red. Recovery is to re-run that run's failed jobs: the action ignores same-commit entries when it picks the baseline, so the re-run alerts again (and adds a duplicate data point), while a later push does not.
- **Minimum samples.** Every variant and CPU profile needs at least 5 successful starts (`MIN_OK_SAMPLES` in `ci/bench.py`, the same number `ci/report.py` needs to publish a ratio; if fewer than 5 starts are scheduled in total, all must succeed). Otherwise the bench job fails and the module is not published. The publish job checks this again from the results file (which records the expected CPU profiles): an empty series or any cell below the minimum fails it (`report.py series --require-nonempty`). A failed `docker wait` or `docker inspect` marks that start as failed with the reason in the results file.
- `ci/build.sh` removes the buildpack cache volumes (`pack-cache-*.build`/`.launch`, which are named, so `docker volume prune` does not touch them) after each image; `disk.log` still records disk use.
- Unit tests for `ci/` run in the separate `ci-tests` workflow (read-only token, no secrets; separate so a test failure cannot hold back benchmark pushes). Locally: `python3 ci/test_report.py`, `python3 ci/test_bench.py`, `python3 ci/test_verify_published.py`, `ci/test-plan.sh`, `ci/test-maven.sh`, `python3 ci/test_workflows.py`, `ci/test-clean-docker.sh`, `ci/test-landed.sh`, `ci/test-pages-probe.sh`, `ci/test-stage-pages.sh`. The workflow also runs actionlint, and runs on any change under `.github/workflows/`.
- Benchmark jobs are not meant to be required checks. A failed or noisy run still shows a red check on the PR, but does not block merging unless someone makes it required (this includes Dependabot PRs). `github-actions` updates keep the pinned action SHAs current.

### Benchmark dashboard

Charts of the published history: **https://miller79.github.io/spring-boot-benchmark/** (deployed by the separate `pages` workflow from `index.html` and `data.js` at the root of the `bench-data` branch; **Unverified**: not seen live. Treat the link as working only after a second `main` run has been seen updating the site). The `pages` workflow runs after each `benchmark` push run on the default branch (`workflow_run`), and can be run by hand (Actions > pages > Run workflow, default branch only) to redeploy or bootstrap the site. It is separate so that a Pages failure never turns a benchmark run red or holds back the last successful push run; a failure is red on the `pages` workflow only. Only an HTTP 404 for `bench-data` is skipped (no history yet); any other error, or a missing `index.html`/`data.js`, fails it.

**One-time setup (repo admin):** Settings > Pages > Build and deployment > Source = **GitHub Actions** (not "Deploy from a branch": pushes made with `GITHUB_TOKEN` do not trigger a branch-based Pages build). Settings > Environments > `github-pages` > restrict deployment branches to `main`. The workflow pins `benchmark-data-dir-path: '.'` and `gh-pages-branch: bench-data`, so history is always written to the root of `bench-data` (`data.js`, `index.html`), never to `dev/bench/`, and merge order does not matter for that; the dashboard reads the root of `bench-data`.

- **Latest results:** each chart ends at the newest point, one per full run on `main` that benchmarked the module. A module appears only after a push to `main` has benchmarked it, and it is updated only when a run benchmarks it (a change to the module, to the parent, to `ci/` or to the workflow, or an unknown last successful run, benchmarks every module), so different modules can show different commit dates (hover a point for the commit).
- **Ratio charts** (`<module> / <profile> / <cpu> / started|wall ratio to plain`, unit `ratio`): median of the variant divided by median of `plain` from the same job; below 1 is faster than `plain`. The tooltip carries the 95% bootstrap interval. These are the numbers to trust, and the only ones that alert (more than 20% worse than the previous published run).
- **Absolute charts** (`spring-boot-benchmark-<module>-absolute`, `... median ms`, unit `ms`): median startup in milliseconds, `plain` included, for the same profiles and CPU limits. Shared runners differ from run to run, so use them to see order of magnitude and compare variants within one point, not to compare points over time. Nothing alerts on them, and the absolute chart may miss a run (its publish is best effort and only warns, while the ratio series still advances).
- **Smoke vs full:** pull requests run a smoke benchmark (`plain` and `aot-cds`, 0.6 CPU, 10 starts, head vs base) and show it only in the job summary. The dashboard holds only full runs (8 profiles, 3 CPU profiles, 30 starts) from pushes to `main`.
- The raw data is `data.js` on the `bench-data` branch. That branch is written only by the workflow on `main`; do not edit it by hand.
- **Accepted risk:** the action's generated `index.html` loads Chart.js 2.9.2 from `cdn.jsdelivr.net` without Subresource Integrity. 2.9.2 is affected by GHSA-h68q-55jf-x68w (CVE-2020-7746, prototype pollution; fixed in 2.9.4). Exploitability is not shown: the page is static and `data.js` is written by the workflow but also carries the head commit's message, author name and URL taken from the push event, so it is not limited to fixed names, and the page renders it in the visitor's browser. Only `index.html` and `data.js` are published to Pages. Optional follow-up: vendor an SRI-pinned `index.html` with a newer Chart.js.

## Results

Ran on 04/29/2026 with Spring Boot 4.0.6, JDK 25, 10 iterations per configuration, --cpus=.6, --memory=1g, -XX:ActiveProcessorCount=1

| Application | Startup Time (Min, Max, Avg) | Process Time (Min, Max, Avg) |
|---|---|---|
| spring-boot-benchmark-original-plain | 7.791, 9.377, 8.418 | 8.79, 10.455, 9.4817 |
| spring-boot-benchmark-original-aot | 5.809, 8.094, 6.6121 | 6.901, 9.383, 7.759 |
| spring-boot-benchmark-original-cds | 3.59, 4.404, 4.0615 | 4.196, 5.206, 4.7741 |
| spring-boot-benchmark-original-aot-cds | 2.591, 3.602, 2.9039 | 3.198, 4.655, 3.6099 |
| spring-boot-benchmark-original-aot-caching | 3.583, 5.193, 4.3728 | 4.192, 6.075, 5.1621 |
| spring-boot-benchmark-original-aot-aot-caching | 2.313, 3.294, 2.7122 | 2.913, 4.079, 3.3775 |
| spring-boot-benchmark-original-alpaquita | 7.832, 9.389, 8.5106 | 9.114, 10.8, 9.7947 |
| spring-boot-benchmark-original-native | 0.094, 0.153, 0.1197 | 0.103, 0.162, 0.1282 |
| spring-boot-benchmark-tomcat-plain | 7.792, 9.298, 8.5671 | 8.798, 10.313, 9.6209 |
| spring-boot-benchmark-tomcat-aot | 6.018, 6.576, 6.3122 | 7.01, 7.658, 7.3253 |
| spring-boot-benchmark-tomcat-cds | 3.419, 4.011, 3.6893 | 4.069, 4.67, 4.3197 |
| spring-boot-benchmark-tomcat-aot-cds | 2.496, 3.206, 2.747 | 3.081, 3.902, 3.3485 |
| spring-boot-benchmark-tomcat-aot-caching | 3.797, 6.108, 4.9471 | 4.398, 6.814, 5.6937 |
| spring-boot-benchmark-tomcat-aot-aot-caching | 2.404, 3.105, 2.6787 | 3.0, 3.799, 3.334 |
| spring-boot-benchmark-tomcat-alpaquita | 8.515, 9.702, 8.963 | 9.69, 10.998, 10.2174 |
| spring-boot-benchmark-tomcat-native | 0.131, 0.208, 0.1602 | 0.138, 0.219, 0.1685 |
| spring-boot-benchmark-data-jpa-plain | 12.899, 15.009, 13.9766 | 13.992, 16.382, 15.17 |
| spring-boot-benchmark-data-jpa-aot | 11.295, 12.396, 11.844 | 12.468, 13.672, 13.0746 |
| spring-boot-benchmark-data-jpa-cds | 5.398, 6.901, 5.8048 | 6.301, 7.9, 6.7885 |
| spring-boot-benchmark-data-jpa-aot-cds | 3.602, 5.824, 4.1062 | 4.59, 6.802, 5.0336 |
| spring-boot-benchmark-data-jpa-aot-caching | 5.395, 6.411, 5.8252 | 6.29, 7.592, 6.8142 |
| spring-boot-benchmark-data-jpa-aot-aot-caching | 3.397, 4.609, 4.0125 | 4.198, 6.165, 5.0609 |
| spring-boot-benchmark-data-jpa-alpaquita | 13.015, 16.895, 14.7009 | 14.323, 18.295, 16.0923 |
| spring-boot-benchmark-data-jpa-native | 0.26, 0.411, 0.3245 | 0.268, 0.421, 0.334 |
| spring-boot-benchmark-data-rest-plain | 15.284, 18.207, 16.1593 | 16.37, 19.38, 17.3121 |
| spring-boot-benchmark-data-rest-aot | 12.915, 13.903, 13.4296 | 14.084, 15.108, 14.5582 |
| spring-boot-benchmark-data-rest-cds | 5.112, 6.901, 6.3723 | 6.087, 7.987, 7.303 |
| spring-boot-benchmark-data-rest-aot-cds | 3.719, 4.599, 4.1893 | 4.515, 5.583, 5.0656 |
| spring-boot-benchmark-data-rest-aot-caching | 6.103, 6.605, 6.2522 | 6.971, 7.477, 7.1875 |
| spring-boot-benchmark-data-rest-aot-aot-caching | 4.208, 5.013, 4.5537 | 5.098, 5.983, 5.4711 |
| spring-boot-benchmark-data-rest-alpaquita | 15.386, 17.497, 16.6553 | 16.579, 19.065, 17.9915 |
| spring-boot-benchmark-data-rest-native | 0.412, 0.659, 0.515 | 0.422, 0.669, 0.5245 |
| spring-boot-benchmark-activemq-plain | 8.612, 9.726, 9.1591 | 9.623, 10.793, 10.2002 |
| spring-boot-benchmark-activemq-aot | 6.592, 7.791, 7.1568 | 7.602, 9.005, 8.2222 |
| spring-boot-benchmark-activemq-cds | 3.702, 5.619, 4.0951 | 4.315, 6.212, 4.7057 |
| spring-boot-benchmark-activemq-aot-cds | 2.614, 3.089, 2.7703 | 3.274, 3.672, 3.3819 |
| spring-boot-benchmark-activemq-aot-caching | 3.811, 3.997, 3.8854 | 4.466, 4.659, 4.5275 |
| spring-boot-benchmark-activemq-aot-aot-caching | 2.101, 2.706, 2.4419 | 2.663, 3.367, 3.0266 |
| spring-boot-benchmark-activemq-alpaquita | 6.884, 8.899, 7.3584 | 7.793, 9.815, 8.3171 |
| spring-boot-benchmark-activemq-native | 0.132, 0.219, 0.1712 | 0.139, 0.228, 0.1783 |
| spring-boot-benchmark-all-plain | 12.5, 14.488, 13.3445 | 13.376, 15.458, 14.263 |
| spring-boot-benchmark-all-aot | 10.602, 12.915, 11.37 | 11.487, 13.823, 12.2796 |
| spring-boot-benchmark-all-cds | 5.11, 5.699, 5.3745 | 5.911, 6.504, 6.1812 |
| spring-boot-benchmark-all-aot-cds | 3.509, 6.9, 4.1451 | 4.295, 7.98, 5.0287 |
| spring-boot-benchmark-all-aot-caching | 4.912, 5.799, 5.3089 | 5.714, 6.601, 6.0894 |
| spring-boot-benchmark-all-aot-aot-caching | 3.603, 4.697, 4.0012 | 4.319, 5.508, 4.8076 |
| spring-boot-benchmark-all-alpaquita | 12.591, 14.688, 13.5187 | 13.679, 15.786, 14.5517 |
| spring-boot-benchmark-all-native | 0.34, 0.457, 0.3828 | 0.348, 0.465, 0.3904 |
