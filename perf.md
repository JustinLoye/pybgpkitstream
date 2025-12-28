# Performances

Here are reported runtime comparison between `PyBGPKITStream` and `PyBGPStream` for different scenarios.
Both libraries involve downloading stuff, so comparing short runtimes should be taken with a grain of salt.
The scenarios consist in extracting BGP elements and counting them for a combination of parameters:

- Cache type: no cache, cache miss and cache hit
- Data type: update, RIB
- Collectors:
    - single (`["route-views2"]`)
    - few (`["rrc00", "route-views2"]`)
    - many (`["rrc00", "rrc01", "rrc03", "rrc04", "rrc05", "route-views2", "route-views.sydney", "route-views.wide", "route-views.linx", "route-views.eqix"]`)
- Duration: Short (2 hours), Long (1 day) in September 2010

Experiments ran on a single core of an AMD Ryzen 9 5900X 12-Core Processor.
Performances depend on the MRT parser, so each of them are reported next.

## PyBGPKIT (default)

This parser is the slowest but don't need any system dependencies

|            |           |            |          |                           |               |                           |             |             |
| ---------- | --------- | ---------- | -------- | ------------------------- | ------------- | ------------------------- | ----------- | ----------- |
|            |           |            |          | BGPElem count             | BGPElem count | Runtime (s)               | Runtime (s) | Analysis    |
| Library    |           |            |          | PyBGPKITStream (pybgpkit) | PyBGPStream   | PyBGPKITStream (pybgpkit) | PyBGPStream | Speedup (x) |
| Cache Type | Data Type | Collectors | Duration |                           |               |                           |             |             |
| No cache   | Update    | Single     | Short    | 1189804                   | 1189817       | 17.1                      | 12.6        | 0.737       |
| No cache   | Update    | Single     | Long     | 14677496                  | 14677533      | 198.5                     | 122.2       | 0.616       |
| No cache   | Update    | Few        | Short    | 1366879                   | 1367545       | 25.2                      | 50.6        | 2.007       |
| No cache   | Update    | Few        | Long     | 18016697                  | 18024606      | 262.1                     | 557.1       | 2.125       |
| No cache   | Update    | Many       | Short    | 3205031                   | 3220764       | 57.6                      | 69.9        | 1.214       |
| No cache   | Update    | Many       | Long     | 45866344                  | 43828368      | 726.3                     | 732.5       | 1.008       |
| No cache   | RIB       | Single     | Short    | 11477411                  | 11477411      | 141.1                     | 9.7         | 0.069       |
| No cache   | RIB       | Single     | Long     | 137766515                 | 137766515     | 1604.3                    | 107.4       | 0.067       |
| No cache   | RIB       | Few        | Short    | 15396782                  | 15396782      | 181.2                     | 13.5        | 0.075       |
| No cache   | RIB       | Few        | Long     | 149524859                 | 149524859     | 1769.2                    | 117.7       | 0.067       |
| No cache   | RIB       | Many       | Short    | 32470926                  | 32470926      | 515.5                     | 28.2        | 0.055       |
| No cache   | RIB       | Many       | Long     | 319104746                 | 319104746     | 4384.8                    | 237.6       | 0.054       |
| Cache miss | Update    | Single     | Short    | 1189804                   | 1189817       | 17.8                      | 12.5        | 0.704       |
| Cache miss | Update    | Single     | Long     | 14677496                  | 14677533      | 197.1                     | 122.6       | 0.622       |
| Cache miss | Update    | Few        | Short    | 1366879                   | 1367545       | 22.2                      | 51.1        | 2.305       |
| Cache miss | Update    | Few        | Long     | 18016697                  | 18024606      | 261.5                     | 563.4       | 2.154       |
| Cache miss | Update    | Many       | Short    | 3205031                   | 3220764       | 56                        | 70.3        | 1.257       |
| Cache miss | Update    | Many       | Long     | 45866344                  | 43828368      | 711                       | 750.2       | 1.055       |
| Cache miss | RIB       | Single     | Short    | 11477411                  | 11477411      | 136                       | 10.2        | 0.075       |
| Cache miss | RIB       | Single     | Long     | 137766515                 | 137766515     | 1624.3                    | 112.1       | 0.069       |
| Cache miss | RIB       | Few        | Short    | 15396782                  | 15396782      | 183.2                     | 14.7        | 0.081       |
| Cache miss | RIB       | Few        | Long     | 149524859                 | 149524859     | 1721.2                    | 125.9       | 0.073       |
| Cache miss | RIB       | Many       | Short    | 32470926                  | 32470926      | 520.4                     | 36.4        | 0.07        |
| Cache miss | RIB       | Many       | Long     | 319104746                 | 319104746     | 4392.7                    | 324.6       | 0.074       |
| Cache hit  | Update    | Single     | Short    | 1189804                   | 1189817       | 17.6                      | 12.6        | 0.712       |
| Cache hit  | Update    | Single     | Long     | 14677496                  | 14677533      | 196.1                     | 113.2       | 0.577       |
| Cache hit  | Update    | Few        | Short    | 1366879                   | 1367545       | 21.5                      | 45.4        | 2.11        |
| Cache hit  | Update    | Few        | Long     | 18016697                  | 18024606      | 256.3                     | 444.8       | 1.735       |
| Cache hit  | Update    | Many       | Short    | 3205031                   | 3220764       | 56.6                      | 50.6        | 0.894       |
| Cache hit  | Update    | Many       | Long     | 45866344                  | 43828368      | 707.5                     | 563.4       | 0.796       |
| Cache hit  | RIB       | Single     | Short    | 11477411                  | 11477411      | 135.7                     | 5.3         | 0.039       |
| Cache hit  | RIB       | Single     | Long     | 137766515                 | 137766515     | 1626.9                    | 59.3        | 0.036       |
| Cache hit  | RIB       | Few        | Short    | 15396782                  | 15396782      | 182.8                     | 7.2         | 0.039       |
| Cache hit  | RIB       | Few        | Long     | 149524859                 | 149524859     | 1762.8                    | 64.8        | 0.037       |
| Cache hit  | RIB       | Many       | Short    | 32470926                  | 32470926      | 513.6                     | 17.8        | 0.035       |
| Cache hit  | RIB       | Many       | Long     | 319104746                 | 319104746     | 4470.8                    | 168.5       | 0.038       |

## BGPKIT CLI

Run `bgpkit-parser` command (install with cargo)

|            |           |            |          |                         |               |                         |             |             |
| ---------- | --------- | ---------- | -------- | ----------------------- | ------------- | ----------------------- | ----------- | ----------- |
|            |           |            |          | BGPElem count           | BGPElem count | Runtime (s)             | Runtime (s) | Analysis    |
| Library    |           |            |          | PyBGPKITStream (bgpkit) | PyBGPStream   | PyBGPKITStream (bgpkit) | PyBGPStream | Speedup (x) |
| Cache Type | Data Type | Collectors | Duration |                         |               |                         |             |             |
| No cache   | Update    | Single     | Short    | 1192850                 | 1189817       | 5.1                     | 12.6        | 2.457       |
| No cache   | Update    | Single     | Long     | 14681823                | 14677533      | 42.9                    | 122.2       | 2.851       |
| No cache   | Update    | Few        | Short    | 1370963                 | 1367545       | 6.3                     | 50.6        | 8.003       |
| No cache   | Update    | Few        | Long     | 18022558                | 18024606      | 66                      | 557.1       | 8.441       |
| No cache   | Update    | Many       | Short    | 3175726                 | 3220764       | 16.3                    | 69.9        | 4.3         |
| No cache   | Update    | Many       | Long     | 45852132                | 43828368      | 184.6                   | 732.5       | 3.967       |
| No cache   | RIB       | Single     | Short    | 11477411                | 11477411      | 33.6                    | 9.7         | 0.288       |
| No cache   | RIB       | Single     | Long     | 137766515               | 137766515     | 374.8                   | 107.4       | 0.287       |
| No cache   | RIB       | Few        | Short    | 15396782                | 15396782      | 43.4                    | 13.5        | 0.312       |
| No cache   | RIB       | Few        | Long     | 149524859               | 149524859     | 414.8                   | 117.7       | 0.284       |
| No cache   | RIB       | Many       | Short    | 27974192                | 32470926      | 103.4                   | 28.2        | 0.273       |
| No cache   | RIB       | Many       | Long     | 314608012               | 319104746     | 918.7                   | 237.6       | 0.259       |
| Cache miss | Update    | Single     | Short    | 1192850                 | 1189817       | 5                       | 12.5        | 2.505       |
| Cache miss | Update    | Single     | Long     | 14681823                | 14677533      | 43.6                    | 122.6       | 2.811       |
| Cache miss | Update    | Few        | Short    | 1370963                 | 1367545       | 6.9                     | 51.1        | 7.441       |
| Cache miss | Update    | Few        | Long     | 18022558                | 18024606      | 65.9                    | 563.4       | 8.55        |
| Cache miss | Update    | Many       | Short    | 3175726                 | 3220764       | 16.7                    | 70.3        | 4.212       |
| Cache miss | Update    | Many       | Long     | 45852132                | 43828368      | 184.3                   | 750.2       | 4.069       |
| Cache miss | RIB       | Single     | Short    | 11477411                | 11477411      | 33.9                    | 10.2        | 0.3         |
| Cache miss | RIB       | Single     | Long     | 137766515               | 137766515     | 376.7                   | 112.1       | 0.298       |
| Cache miss | RIB       | Few        | Short    | 15396782                | 15396782      | 43.5                    | 14.7        | 0.339       |
| Cache miss | RIB       | Few        | Long     | 149524859               | 149524859     | 410.5                   | 125.9       | 0.307       |
| Cache miss | RIB       | Many       | Short    | 27974192                | 32470926      | 103.8                   | 36.4        | 0.351       |
| Cache miss | RIB       | Many       | Long     | 314608012               | 319104746     | 936.6                   | 324.6       | 0.347       |
| Cache hit  | Update    | Single     | Short    | 1192850                 | 1189817       | 4.9                     | 12.6        | 2.542       |
| Cache hit  | Update    | Single     | Long     | 14681823                | 14677533      | 43.7                    | 113.2       | 2.59        |
| Cache hit  | Update    | Few        | Short    | 1370963                 | 1367545       | 5.8                     | 45.4        | 7.848       |
| Cache hit  | Update    | Few        | Long     | 18022558                | 18024606      | 59.2                    | 444.8       | 7.509       |
| Cache hit  | Update    | Many       | Short    | 3175726                 | 3220764       | 15.6                    | 50.6        | 3.246       |
| Cache hit  | Update    | Many       | Long     | 45852132                | 43828368      | 170.2                   | 563.4       | 3.311       |
| Cache hit  | RIB       | Single     | Short    | 11477411                | 11477411      | 31.3                    | 5.3         | 0.17        |
| Cache hit  | RIB       | Single     | Long     | 137766515               | 137766515     | 362.5                   | 59.3        | 0.164       |
| Cache hit  | RIB       | Few        | Short    | 15396782                | 15396782      | 38.5                    | 7.2         | 0.186       |
| Cache hit  | RIB       | Few        | Long     | 149524859               | 149524859     | 385.6                   | 64.8        | 0.168       |
| Cache hit  | RIB       | Many       | Short    | 27974192                | 32470926      | 98.7                    | 17.8        | 0.18        |
| Cache hit  | RIB       | Many       | Long     | 314608012               | 319104746     | 884.2                   | 168.5       | 0.191       |


## PyBGPStream single-file backend

Use PyBGPStream as an MRT parser

|            |           |            |          |                              |               |                              |             |             |
| ---------- | --------- | ---------- | -------- | ---------------------------- | ------------- | ---------------------------- | ----------- | ----------- |
|            |           |            |          | BGPElem count                | BGPElem count | Runtime (s)                  | Runtime (s) | Analysis    |
| Library    |           |            |          | PyBGPKITStream (pybgpstream) | PyBGPStream   | PyBGPKITStream (pybgpstream) | PyBGPStream | Speedup (x) |
| Cache Type | Data Type | Collectors | Duration |                              |               |                              |             |             |
| No cache   | Update    | Single     | Short    | 1189804                      | 1189817       | 5                            | 12.6        | 2.543       |
| No cache   | Update    | Single     | Long     | 14677496                     | 14677533      | 39.6                         | 122.2       | 3.09        |
| No cache   | Update    | Few        | Short    | 1367532                      | 1367545       | 7.9                          | 50.6        | 6.413       |
| No cache   | Update    | Few        | Long     | 18024565                     | 18024606      | 76.6                         | 557.1       | 7.27        |
| No cache   | Update    | Many       | Short    | 3220538                      | 3220764       | 19.6                         | 69.9        | 3.574       |
| No cache   | Update    | Many       | Long     | 46116166                     | 43828368      | 218.7                        | 732.5       | 3.349       |
| No cache   | RIB       | Single     | Short    | 11477411                     | 11477411      | 23.3                         | 9.7         | 0.416       |
| No cache   | RIB       | Single     | Long     | 137766515                    | 137766515     | 215.2                        | 107.4       | 0.499       |
| No cache   | RIB       | Few        | Short    | 15396782                     | 15396782      | 27.6                         | 13.5        | 0.49        |
| No cache   | RIB       | Few        | Long     | 149524859                    | 149524859     | 230.1                        | 117.7       | 0.512       |
| No cache   | RIB       | Many       | Short    | 32470926                     | 32470926      | 71.2                         | 28.2        | 0.396       |
| No cache   | RIB       | Many       | Long     | 319104746                    | 319104746     | 524.5                        | 237.6       | 0.453       |
| Cache miss | Update    | Single     | Short    | 1189804                      | 1189817       | 4.6                          | 12.5        | 2.723       |
| Cache miss | Update    | Single     | Long     | 14677496                     | 14677533      | 37.9                         | 122.6       | 3.231       |
| Cache miss | Update    | Few        | Short    | 1367532                      | 1367545       | 8.2                          | 51.1        | 6.236       |
| Cache miss | Update    | Few        | Long     | 18024565                     | 18024606      | 75.9                         | 563.4       | 7.425       |
| Cache miss | Update    | Many       | Short    | 3220538                      | 3220764       | 19                           | 70.3        | 3.704       |
| Cache miss | Update    | Many       | Long     | 46116166                     | 43828368      | 216.1                        | 750.2       | 3.471       |
| Cache miss | RIB       | Single     | Short    | 11477411                     | 11477411      | 20.2                         | 10.2        | 0.505       |
| Cache miss | RIB       | Single     | Long     | 137766515                    | 137766515     | 208.2                        | 112.1       | 0.539       |
| Cache miss | RIB       | Few        | Short    | 15396782                     | 15396782      | 27.9                         | 14.7        | 0.529       |
| Cache miss | RIB       | Few        | Long     | 149524859                    | 149524859     | 226.7                        | 125.9       | 0.555       |
| Cache miss | RIB       | Many       | Short    | 32470926                     | 32470926      | 71.2                         | 36.4        | 0.511       |
| Cache miss | RIB       | Many       | Long     | 319104746                    | 319104746     | 541.2                        | 324.6       | 0.6         |
| Cache hit  | Update    | Single     | Short    | 1189804                      | 1189817       | 4.8                          | 12.6        | 2.617       |
| Cache hit  | Update    | Single     | Long     | 14677496                     | 14677533      | 40.4                         | 113.2       | 2.8         |
| Cache hit  | Update    | Few        | Short    | 1367532                      | 1367545       | 6.6                          | 45.4        | 6.862       |
| Cache hit  | Update    | Few        | Long     | 18024565                     | 18024606      | 70.3                         | 444.8       | 6.328       |
| Cache hit  | Update    | Many       | Short    | 3220538                      | 3220764       | 17.9                         | 50.6        | 2.825       |
| Cache hit  | Update    | Many       | Long     | 46116166                     | 43828368      | 203.3                        | 563.4       | 2.771       |
| Cache hit  | RIB       | Single     | Short    | 11477411                     | 11477411      | 16.9                         | 5.3         | 0.315       |
| Cache hit  | RIB       | Single     | Long     | 137766515                    | 137766515     | 195.3                        | 59.3        | 0.304       |
| Cache hit  | RIB       | Few        | Short    | 15396782                     | 15396782      | 22.2                         | 7.2         | 0.323       |
| Cache hit  | RIB       | Few        | Long     | 149524859                    | 149524859     | 210.4                        | 64.8        | 0.308       |
| Cache hit  | RIB       | Many       | Short    | 32470926                     | 32470926      | 58.1                         | 17.8        | 0.306       |
| Cache hit  | RIB       | Many       | Long     | 319104746                    | 319104746     | 498.2                        | 168.5       | 0.338       |

## bgdump

|            |           |            |          |                          |               |                          |             |             |
| ---------- | --------- | ---------- | -------- | ------------------------ | ------------- | ------------------------ | ----------- | ----------- |
|            |           |            |          | BGPElem count            | BGPElem count | Runtime (s)              | Runtime (s) | Analysis    |
| Library    |           |            |          | PyBGPKITStream (bgpdump) | PyBGPStream   | PyBGPKITStream (bgpdump) | PyBGPStream | Speedup (x) |
| Cache Type | Data Type | Collectors | Duration |                          |               |                          |             |             |
| No cache   | Update    | Single     | Short    | 1189804                  | 1189817       | 4.3                      | 12.6        | 2.902       |
| No cache   | Update    | Single     | Long     | 14677496                 | 14677533      | 35.1                     | 122.2       | 3.487       |
| No cache   | Update    | Few        | Short    | 1366879                  | 1367545       | 5.3                      | 50.6        | 9.547       |
| No cache   | Update    | Few        | Long     | 18016697                 | 18024606      | 54.3                     | 557.1       | 10.266      |
| No cache   | Update    | Many       | Short    |                          | 3220764       |                          | 69.9        |             |
| No cache   | Update    | Many       | Long     |                          | 43828368      |                          | 732.5       |             |
| No cache   | RIB       | Single     | Short    | 11477411                 | 11477411      | 28.6                     | 9.7         | 0.338       |
| No cache   | RIB       | Single     | Long     | 137766515                | 137766515     | 311.5                    | 107.4       | 0.345       |
| No cache   | RIB       | Few        | Short    | 15396782                 | 15396782      | 36.5                     | 13.5        | 0.371       |
| No cache   | RIB       | Few        | Long     | 149524859                | 149524859     | 338.2                    | 117.7       | 0.348       |
| No cache   | RIB       | Many       | Short    | 32470926                 | 32470926      | 87.7                     | 28.2        | 0.322       |
| No cache   | RIB       | Many       | Long     | 319104746                | 319104746     | 780.3                    | 237.6       | 0.305       |
| Cache miss | Update    | Single     | Short    | 1189804                  | 1189817       | 4.4                      | 12.5        | 2.851       |
| Cache miss | Update    | Single     | Long     | 14677496                 | 14677533      | 36.4                     | 122.6       | 3.37        |
| Cache miss | Update    | Few        | Short    | 1366879                  | 1367545       | 7.4                      | 51.1        | 6.882       |
| Cache miss | Update    | Few        | Long     | 18016697                 | 18024606      | 52.3                     | 563.4       | 10.78       |
| Cache miss | Update    | Many       | Short    |                          | 3220764       |                          | 70.3        |             |
| Cache miss | Update    | Many       | Long     |                          | 43828368      |                          | 750.2       |             |
| Cache miss | RIB       | Single     | Short    | 11477411                 | 11477411      | 29                       | 10.2        | 0.351       |
| Cache miss | RIB       | Single     | Long     | 137766515                | 137766515     | 314.6                    | 112.1       | 0.356       |
| Cache miss | RIB       | Few        | Short    | 15396782                 | 15396782      | 35.8                     | 14.7        | 0.412       |
| Cache miss | RIB       | Few        | Long     | 149524859                | 149524859     | 335.8                    | 125.9       | 0.375       |
| Cache miss | RIB       | Many       | Short    | 32470926                 | 32470926      | 86.6                     | 36.4        | 0.421       |
| Cache miss | RIB       | Many       | Long     | 319104746                | 319104746     | 773.7                    | 324.6       | 0.42        |
| Cache hit  | Update    | Single     | Short    | 1189804                  | 1189817       | 4.4                      | 12.6        | 2.846       |
| Cache hit  | Update    | Single     | Long     | 14677496                 | 14677533      | 35.1                     | 113.2       | 3.224       |
| Cache hit  | Update    | Few        | Short    | 1366879                  | 1367545       | 6.3                      | 45.4        | 7.189       |
| Cache hit  | Update    | Few        | Long     | 17987216                 | 18024606      | 52.9                     | 444.8       | 8.416       |
| Cache hit  | Update    | Many       | Short    |                          | 3220764       |                          | 50.6        |             |
| Cache hit  | Update    | Many       | Long     |                          | 43828368      |                          | 563.4       |             |
| Cache hit  | RIB       | Single     | Short    | 11477411                 | 11477411      | 25.4                     | 5.3         | 0.209       |
| Cache hit  | RIB       | Single     | Long     | 137766515                | 137766515     | 301.6                    | 59.3        | 0.197       |
| Cache hit  | RIB       | Few        | Short    | 15396782                 | 15396782      | 31.7                     | 7.2         | 0.226       |
| Cache hit  | RIB       | Few        | Long     | 149524859                | 149524859     | 318.7                    | 64.8        | 0.203       |
| Cache hit  | RIB       | Many       | Short    | 32470926                 | 32470926      | 81.4                     | 17.8        | 0.219       |
| Cache hit  | RIB       | Many       | Long     | 319104746                | 319104746     | 740.7                    | 168.5       | 0.227       |
