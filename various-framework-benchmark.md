# Straight SB 
 
| Cpu request | Mem request | Cpu limit | Mem limit | Start time | First response | Median response | 95% |
| ----------- | ----------- | --------- | --------- | ---------- | -------------- | --------------- | --- |
| 100m        | 200Mi       | 200m      | 500Mi     | 135s       | 1662           | 182             | 354 |
| 200m        | 250Mi       | 300m      | 500Mi     | 88-96s     | 1113           | 145             | 230 |
| 200m        | 500Mi       | 400m      | 1000Mi    | 65-70s     | 702            | 118             | 223 |
| 400m        | 750Mi       | 600m      | 1000Mi    | 65-70s     | 798            | 112             | 195 |
 
 
# Micronaut w/ Java
 
| Cpu request | Mem request | Cpu limit | Mem limit | Start time | First response | Median Response | 95% |
| ----------- | ----------- | --------- | --------- | ---------- | -------------- | --------------- | --- |
| 100m        | 200Mi       | 200m      | 500Mi     | 65-75      | 1078           | 194             | 904 |
| 200m        | 250Mi       | 300m      | 500Mi     | 50-55s     | 455            | 116             | 242 |
| 200m        | 500Mi       | 400m      | 1000Mi    | 35-40s     | 678            | 122             | 470 |
| 400m        | 750Mi       | 600m      | 1000Mi    | 30-35s     | 477            | 119             | 298 |
 
# Quarkus w/ Java
 
| Cpu request | Mem request | Cpu limit | Mem limit | Start time | First response | Median Response | 95%  |
| ----------- | ----------- | --------- | --------- | ---------- | -------------- | --------------- | ---- |
| 100m        | 200Mi       | 200m      | 500Mi     | 55-60s     | 1962           | 192             | 1174 |
| 200m        | 250Mi       | 300m      | 500Mi     | 45-50s     | 2087           | 149             | 306  |
| 200m        | 500Mi       | 400m      | 1000Mi    | 35-37s     | 1934           | 116             | 233  |
| 400m        | 750Mi       | 600m      | 1000Mi    | 27-29s     | 1287           | 112             | 189  |
 
# Quarkus w/ Graalvm Native
 
| Cpu request | Mem request | Cpu limit | Mem limit | Start time | First response | Median Response | 95% |
| ----------- | ----------- | --------- | --------- | ---------- | -------------- | --------------- | --- |
| 50m         | 200Mi       | 50m       | 200Mi     | 10-15      | 556            | 220             | 912 |
| 100m        | 200Mi       | 200m      | 500Mi     | 5s         | 112            | 108             | 126 |
| 200m        | 250Mi       | 300m      | 500Mi     | 4s         | 126            | 109             | 122 |
| 200m        | 500Mi       | 400m      | 1000Mi    | 4s         | 109            | 108             | 126 |
| 400m        | 750Mi       | 600m      | 1000Mi    | 4-5s       | 128            | 108             | 122 |
 
# Javalin w/ Kotlin
 
| Cpu request | Mem request | Cpu limit | Mem limit | Start time | First response | Median response | 95% |
| ----------- | ----------- | --------- | --------- | ---------- | -------------- | --------------- | --- |
| 100m        | 200Mi       | 200m      | 500Mi     | 45-50s     | 2012           | 201             | 368 |
| 200m        | 250Mi       | 300m      | 500Mi     | 26-34s     | 1567           | 176             | 328 |
| 200m        | 500Mi       | 400m      | 1000Mi    | 22-28s     | 768            | 170             | 265 |
| 400m        | 750Mi       | 600m      | 1000Mi    | 16-24s     | 547            | 170             | 212 |
 
