# PyBGPKITStream

A drop-in replacement for PyBGPStream using BGPKIT

## Features

- Generates time-ordered BGP messages on the fly from RIBs and updates MRT files of multiple collectors
- Stream the same BGP messages as PyBGPStream, enabling seamless, drop-in replacement
- Lazy loading consumes minimal memory, making it suitable for large datasets
- Multiple BGP parsers supported: `pybgpkit` (default but slow), `bgpkit-parser`, `bgpdump` and `pybgpstream` single file backend (the latter three are system dependencies)
- Caching with concurrent downloading fully compatible with the BGPKIT parser's caching functionality.
- Performance: for updates, typically 3–10× faster than PyBGPStream; for RIB-only processing, currently about 3–4× slower (see [perf.md](perf.md) for test details).
- A CLI tool

## Quick start

Installation:

```sh
pip install pybgpkitstream
```

Usage:

```python
import datetime
from pybgpkitstream import BGPStreamConfig, BGPKITStream

config = BGPStreamConfig(
    start_time=datetime.datetime(2010, 9, 1, 0, 0),
    end_time=datetime.datetime(2010, 9, 1, 1, 59),
    collectors=["route-views.sydney", "route-views.wide"],
    data_types=["ribs", "updates"],
)

stream = BGPKITStream.from_config(config)

n_elems = 0
for elem in stream:
  n_elems += 1
    
print(f"Processed {n_elems} BGP elements")
```

or in the terminal:

```sh
pybgpkitstream --start-time 2010-09-01T00:00:00 --end-time 2010-09-01T01:59:00 --collectors route-views.sydney route-views.wide --data-types updates > updates.txt
```

## Motivation

PyBGPStream is great but the implementation is complex and stops working when UC San Diego experiences a power outage.  
BGPKIT broker and parser are great, but cannot be used to create an ordered stream of BGP messages from multiple collectors and multiple data types.

## Missing features

- Live mode for RouteViews collectors
- Some PyBGPStream data interface options like csv or sqlite