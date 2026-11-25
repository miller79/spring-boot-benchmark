# Spring Boot Benchmark

**[Latest benchmark results](https://miller79.github.io/spring-boot-benchmark/)** - startup-time matrices per scenario: build profiles down, CPU settings across, milliseconds and original ratios in each cell.

- [Spring Boot Benchmark](#spring-boot-benchmark)
  - [Introduction](#introduction)
  - [Where to see the results](#where-to-see-the-results)
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

## Where to see the results

Start with the **[startup-time matrices](https://miller79.github.io/spring-boot-benchmark/)**, not Actions. Jump to a scenario: build profiles are rows, CPU settings are columns, and each cell shows the started median **ms** plus its ratio to `plain` with the original **95% confidence interval**. Expand the wall-time matrix for container start-to-exit times. Each scenario shows its publication date and benchmark commit once; follow that commit for the dependency versions actually measured. Published results may be older than the repository's current version.

| Need | Where |
|---|---|
| Latest published full run per scenario | [Startup-time matrices](https://miller79.github.io/spring-boot-benchmark/), generated automatically by the existing Pages workflow. |
| Complete published history | Download `data.js` from the table page, or browse [`bench-data/data.js`](https://github.com/miller79/spring-boot-benchmark/blob/bench-data/data.js). |
| Rerun locally | [Build and Measure Runtimes](#build-and-measure-runtimes): `./measure-runtime.sh 5` (JDK 25 and Docker). |
| PR smoke results or detailed diagnostics | [Actions](https://github.com/miller79/spring-boot-benchmark/actions) > **benchmark** > run > **Summary**; artifacts `results-<module>` retain raw files for 30 days. |
| Regression alerts | [Issues](https://github.com/miller79/spring-boot-benchmark/issues), title `Benchmark alert: <module>`. |

Published history already exists. Pages availability depends on the [one-time setup](#benchmark-dashboard); if the site is unavailable, a maintainer can redeploy the existing data by running **pages** on `main`. This does not require a fresh benchmark.

Smoke versus full: a `pull_request` run is a **smoke** benchmark (`plain` and `aot-cds`, 0.6 CPU, 10 starts, one repeat, head vs base). It shows up only in the job summary and artifacts and is never published. A **full** run (all 8 profiles, 3 CPU profiles, 30 starts) happens on a push to `main`, and only those runs reach `bench-data`, the dashboard and the alerts. A manual `workflow_dispatch` run uses the grid you choose and never publishes. If a module cannot be published, its `publish (<module>)` job turns the run red. How the workflow works is described under [Continuous benchmarking](#continuous-benchmarking-github-actions).

## Benchmarks Available

| Scenario | Source directory |
|---|---|
| WebFlux (Netty) | [original](spring-boot-benchmark-original/) |
| Spring MVC (Tomcat) | [tomcat](spring-boot-benchmark-tomcat/) |
| Data JPA | [data-jpa](spring-boot-benchmark-data-jpa/) |
| Data REST | [data-rest](spring-boot-benchmark-data-rest/) |
| ActiveMQ | [activemq](spring-boot-benchmark-activemq/) |
| All dependencies | [all](spring-boot-benchmark-all/) |

Application sources stay in these directories; shared Maven configuration is in `spring-boot-benchmark-parent/`, benchmark and publishing tools are in `ci/`, and local measurement logs are in `run-logs/`.

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

The `benchmark` workflow (`.github/workflows/benchmark.yml`, drivers in `ci/`) runs the startup benchmark on GitHub-hosted `ubuntu-24.04` runners. There is no schedule: it runs only when benchmarked code changes, or manually.

| Trigger | What runs |
|---|---|
| `pull_request` (same-repo branches only, never forks) | Only modules whose `src/`, `pom.xml` or `.mvn/` changed (or all, if `spring-boot-benchmark-parent`, `ci/` or the workflow changed). Smoke: `plain` and `aot-cds`, 0.6 CPU, 10 starts, **merge result (`refs/pull/N/merge`) vs the PR base**; a module that is new in the PR runs head only. Results appear in the job summary; nothing is commented or published. With 10 starts the p95 column is only indicative. |
| `push` to `main` (same path filters) | Full grid for every module changed since the **last successful push run** (not just since the previous commit): 8 profiles x 0.6/1.0/2.0 CPU x 30 starts. If that run is unknown, every module runs. Ratios and absolute times of each module that benchmarked successfully are appended to the `bench-data` branch; a regression alert opens (or updates) one issue per module. A module that cannot be published, or whose runs left a cell with too few successful starts (below), turns the run red. |
| `workflow_dispatch` | Choose modules, profiles, CPU profiles and iterations (profiles and CPU profiles must be known names, iterations 1-999, duplicates are removed). Never publishes. Tick `spike` to record disk headroom, cgroup/cpuset behaviour and run-to-run noise (3 repeats). |

How to read the results:

- Each module builds and benchmarks in its own job (one VM). Variants run interleaved in random order, pinned to cores 2-3 with `--cpus`/`--memory`. `p06` reproduces `measure-runtime.sh`.
- **Trust ratios to `plain` inside one job. Treat absolute times as orientation only**: do not compare them across runs or with numbers from other machines. Shared VMs are noisy; summaries show 95% bootstrap intervals.
- The apps close themselves after startup, so "wall" is container start to exit, and "started" is Spring's own `Started Application in` line. "wall" includes the `docker start` latency (roughly constant), which pulls wall ratios of very fast variants such as `native` towards 1; prefer "started" for those. `cpu.stat` throttling and `memory.peak` are sampled while the container runs (a lower bound).
- History lives on the `bench-data` branch (created automatically). Each module is its own series group (`spring-boot-benchmark-<module>`): a regression alert fires when a ratio worsens by more than 20% against **that module's previous published run, and only for series present in it**. There is no confidence-interval test, only the threshold, which is a starting value until the spike measures real noise.
- Only the ratio series raise alerts, so a regression of `plain` itself (all other ratios improve) is **not alerted**; it may be visible in the absolute history, but those numbers are noisy on shared runners and nobody is notified about them.
- Pushes that are queued behind a running benchmark can be cancelled by newer ones; no module is lost, because the next successful run covers everything changed since the last successful one. A module that failed or whose results artifact is missing is not published; its publish job fails, so the run is red and it is retried by the next push to `main`. A changed module directory unknown to `ci/plan.sh` also fails the plan instead of being skipped.
- **Regression versus publish error.** The benchmark action fails its step the same way for a regression alert (raised after it pushed the data) and for a publish error (nothing pushed), and has no outputs to tell them apart. The publish job therefore checks `bench-data` itself: it must have moved and its `data.js` must hold this commit's entry for the module (`ci/landed.sh`, `ci/verify_published.py`). If not, the job is red and the next push retries the module. If the data landed and the action still failed, that is treated as a regression: the module issue is opened or updated and the job is green. **A regression does not hold back the "last successful push run"**: it means "ingested", not "fast enough". Its data point is already published, and a later push compares against that already-regressed point and stays silent, so holding it back would only re-benchmark commits for nothing. The issue is the alert; it is retried 3 times and, if it still cannot be opened, the job is red. Recovery is to re-run that run's failed jobs: the action ignores same-commit entries when it picks the baseline, so the re-run alerts again (and adds a duplicate data point), while a later push does not.
- **Minimum samples.** Every variant and CPU profile needs at least 5 successful starts (`MIN_OK_SAMPLES` in `ci/bench.py`, the same number `ci/report.py` needs to publish a ratio; if fewer than 5 starts are scheduled in total, all must succeed). Otherwise the bench job fails and the module is not published. The publish job checks this again from the results file (which records the expected CPU profiles): an empty series or any cell below the minimum fails it (`report.py series --require-nonempty`). A failed `docker wait` or `docker inspect` marks that start as failed with the reason in the results file.
- `ci/build.sh` removes the buildpack cache volumes (`pack-cache-*.build`/`.launch`, which are named, so `docker volume prune` does not touch them) after each image; `disk.log` still records disk use.
- Unit tests for `ci/` run in the separate `ci-tests` workflow (read-only token, no secrets; separate so a test failure cannot hold back benchmark pushes). Locally: `python3 ci/test_report.py`, `python3 ci/test_bench.py`, `python3 ci/test_verify_published.py`, `ci/test-plan.sh`, `ci/test-maven.sh`, `python3 ci/test_workflows.py`, `ci/test-clean-docker.sh`, `ci/test-landed.sh`, `ci/test-pages-probe.sh`, `ci/test-stage-pages.sh`, `python3 ci/test_results_page.py`. The workflow also runs actionlint, and runs on any change under `.github/workflows/`.
- Benchmark jobs are not meant to be required checks. A failed or noisy run still shows a red check on the PR, but does not block merging unless someone makes it required (this includes Dependabot PRs). `github-actions` updates keep the pinned action SHAs current.

### Benchmark dashboard

**https://miller79.github.io/spring-boot-benchmark/** shows static startup-time matrices, readable without JavaScript or chart libraries. Each scenario has eight build-profile rows and three CPU-setting columns; startup milliseconds are prominent, with original ratios/intervals beneath. Wall-time matrices use native HTML disclosures. The existing `pages` workflow checks out the published history, then `ci/stage-pages.sh` generates `index.html` using `ci/results_page.py`. Only the generated page and the unchanged `data.js` are served. The action-generated chart template remains on `bench-data`, but is no longer the deployed landing page.

The `pages` workflow runs after each `benchmark` push run on the default branch (`workflow_run`), and can be run by hand (Actions > pages > Run workflow, default branch only) to redeploy or bootstrap the site. It is separate so that a Pages failure never turns a benchmark run red or holds back the last successful push run; a failure is red on the `pages` workflow only. Only an HTTP 404 for `bench-data` is skipped (no history yet); any other error, or a missing `index.html`/`data.js`, fails it.

**One-time setup (repo admin):** Settings > Pages > Build and deployment > Source = **GitHub Actions** (not "Deploy from a branch": pushes made with `GITHUB_TOKEN` do not trigger a branch-based Pages build). Settings > Environments > `github-pages` > restrict deployment branches to `main`. The workflow pins `benchmark-data-dir-path: '.'` and `gh-pages-branch: bench-data`, so history is always written to the root of `bench-data` (`data.js`, `index.html`), never to `dev/bench/`, and merge order does not matter for that; the dashboard reads the root of `bench-data`.

- **Latest results:** the newest ratio publication is selected per module, not one global commit. Different modules may have different dates; the table shows each publication's UTC date and benchmark commit explicitly. Updates only happen when a full run benchmarks that module.
- **Past/specific published runs:** each scenario has a newest-first date/commit index. Latest startup matrices stay visible; follow an older run link and expand its matrices without JavaScript. If there is only one recorded publication, the page says no earlier published run exists. These are published benchmark records, not Actions run IDs; smoke/manual runs remain in Actions and are not in this history.
- **Ratios:** median of the variant divided by median of `plain` in the same job; below 1 is faster. The original 95% bootstrap intervals are shown alongside the published values. These are the numbers to trust, and the only ones that alert (more than 20% worse than the previous published run).
- **Absolute medians (ms):** shown only from the same commit, published after its selected ratio entry. Missing or older absolute data is `n/a`, not silently carried forward. If a module has only absolute history, it is labeled **absolute only**. Shared runners differ, so compare variants within one run, not machines or dates. Nothing alerts on absolute times.
- **Smoke vs full:** pull requests run a smoke benchmark (`plain` and `aot-cds`, 0.6 CPU, 10 starts, head vs base) and show it only in the job summary. The dashboard holds only full runs (8 profiles, 3 CPU profiles, 30 starts) from pushes to `main`.
- The raw data is `data.js` on the `bench-data` branch. That branch is written only by the workflow on `main`; do not edit it by hand.
- **Static presentation:** the page does not execute `data.js`, load third-party scripts, or render commit author metadata/messages. Raw published history is preserved as a download; the old chart template is not served.

## Results

Read the **[latest benchmark results](https://miller79.github.io/spring-boot-benchmark/)**. The matrices are generated from published history rather than manually copied into this README. See [Where to see the results](#where-to-see-the-results) for raw history and diagnostics, and [Build and Measure Runtimes](#build-and-measure-runtimes) to reproduce a local comparison.
