# Configuration Guide

PyBGPKITStream provides two configuration models for different use cases:

- **`BGPStreamConfig`**: Query specification (what data to retrieve)
- **`PyBGPKITStreamConfig`**: Implementation details (how to retrieve it)

Providing implementation details is optionnal.

## Configuration Models

### BGPStreamConfig: Query Specification

`BGPStreamConfig` defines the BGP data query: collectors, time range, data types, and filters. It's format-agnostic and could work with any BGP data provider. See [API Reference](../api/configuration.md#bgpstreamconfig) for full documentation.

### PyBGPKITStreamConfig: Implementation Configuration

`PyBGPKITStreamConfig` extends the query specification with PyBGPKITStream-specific parameters: parser selection, caching strategy, concurrent download limits, and memory options. See [API Reference](../api/configuration.md#pybgpkitstreamconfig) for full documentation.

## Creating Streams

You have three approaches:

### Approach 1: Simple Queries with BGPStreamConfig

For basic queries without implementation customization, use `BGPStreamConfig`:

```python
from pybgpkitstream import BGPStreamConfig, BGPKITStream
import datetime

config = BGPStreamConfig(
    start_time=datetime.datetime(2010, 9, 1, 0, 0),
    end_time=datetime.datetime(2010, 9, 1, 2, 0),
    collectors=["route-views.wide"],
    data_types=["updates"],
)

stream = BGPKITStream.from_config(config)
for elem in stream:
    print(elem)
```

### Approach 2: Full Control with PyBGPKITStreamConfig

For explicit control over implementation details, use `PyBGPKITStreamConfig` with nested `BGPStreamConfig`:

```python
from pybgpkitstream import BGPStreamConfig, PyBGPKITStreamConfig, BGPKITStream
import datetime

query = BGPStreamConfig(
    start_time=datetime.datetime(2010, 9, 1, 0, 0),
    end_time=datetime.datetime(2010, 9, 1, 2, 0),
    collectors=["route-views.wide"],
    data_types=["updates"],
)

config = PyBGPKITStreamConfig(
    bgpstream_config=query,
    parser="bgpkit",
    max_concurrent_downloads=20,
    cache_dir="/tmp/bgp_cache",
    ram_fetch=True,
)

stream = BGPKITStream.from_config(config)
for elem in stream:
    print(elem)
```

### Approach 3: Flat Configuration (Recommended for Most Users)

**BGPStreamConfig fields can be passed directly to PyBGPKITStreamConfig**, eliminating the need for nesting. This is the most practical approach when you need implementation customization:

```python
from pybgpkitstream import PyBGPKITStreamConfig, BGPKITStream
import datetime

# Pass BGPStreamConfig fields directly—no nesting required
config = PyBGPKITStreamConfig(
    start_time=datetime.datetime(2010, 9, 1, 0, 0),
    end_time=datetime.datetime(2010, 9, 1, 2, 0),
    collectors=["route-views.wide"],
    data_types=["updates"],
    # Implementation parameters
    parser="bgpkit",
    max_concurrent_downloads=10,
    cache_dir="/tmp/bgp_cache",
    ram_fetch=True,
)

stream = BGPKITStream.from_config(config)
for elem in stream:
    print(elem)
```

## Query Parameters

These parameters define the BGP data query and are part of `BGPStreamConfig`:

### Time-Based Selection

```python
import datetime
from pybgpkitstream import BGPStreamConfig

# Specify exact time range
config = BGPStreamConfig(
    start_time=datetime.datetime(2010, 9, 1, 0, 0, tzinfo=datetime.timezone.utc),
    end_time=datetime.datetime(2010, 9, 1, 2, 0, tzinfo=datetime.timezone.utc),
    collectors=["route-views.wide"],
)
```

**Important**: 
- Datetimes are assumed to be UTC if no timezone is specified
- Both `start_time` and `end_time` must be provided together, or both left as `None`
- Leaving both times as `None` enables live mode

### Collector Selection

```python
# Single or multiple collectors
config = BGPStreamConfig(
    start_time=datetime.datetime(2010, 9, 1, 0, 0),
    end_time=datetime.datetime(2010, 9, 1, 2, 0),
    collectors=["route-views.wide", "route-views.sydney", "rrc04"],
)
```

Common collectors:
- `route-views.*` - Route Views collectors
- `rrc0*` - RIPE NCC RIS collectors
- Full list available via BGPKIT Broker API

### Data Types

```python
# RIBs: Complete routing table snapshots
config = BGPStreamConfig(
    ...,
    data_types=["ribs"],
)

# Updates: BGP update messages
config = BGPStreamConfig(
    ...,
    data_types=["updates"],
)

# Both
config = BGPStreamConfig(
    ...,
    data_types=["ribs", "updates"],
)
```

## Implementation Parameters

These parameters control how PyBGPKITStream retrieves and processes data. They are part of `PyBGPKITStreamConfig`:

### Parser Selection

```python
from pybgpkitstream import PyBGPKITStreamConfig
import datetime

# Default: pybgpkit (pure Python, slower but no dependencies)
config = PyBGPKITStreamConfig(
    start_time=datetime.datetime(2010, 9, 1, 0, 0),
    end_time=datetime.datetime(2010, 9, 1, 2, 0),
    collectors=["route-views.wide"],
    parser="pybgpkit",
)

# bgpkit-parser (requires system install, fastest)
config = PyBGPKITStreamConfig(
    ...,
    parser="bgpkit",
)

# bgpdump (requires system install)
config = PyBGPKITStreamConfig(
    ...,
    parser="bgpdump",
)

# pybgpstream (requires pip install pybgpstream)
config = PyBGPKITStreamConfig(
    ...,
    parser="pybgpstream",
)
```

### Caching and Download Strategy

```python
from pybgpkitstream import PyBGPKITStreamConfig

config = PyBGPKITStreamConfig(
    ...,
    cache_dir="/tmp/bgp_cache",           # Directory for downloaded files
    ram_fetch=True,                        # Use /dev/shm (Linux) or /Volumes/RAMDisk (macOS) when cache is disabled
    max_concurrent_downloads=10,           # Number of parallel downloads
    chunk_time=datetime.timedelta(hours=2),  # Process data in intervals
)
```

**Parameter details:**
- `cache_dir`: Persistent storage for MRT files. Reused across runs.
- `ram_fetch`: When caching is disabled, use shared memory instead of disk temp space. Improves performance at higher RAM cost.
- `max_concurrent_downloads`: Balance between download speed and resource consumption.
- `chunk_time`: Interval for fetch/parse cycles. Smaller intervals reduce memory usage at the cost of throughput.

## Direct BGPKITStream Constructor

It's possible to bypass Pydantic config validation by instantiating `BGPKITStream` directly:

```python
from pybgpkitstream import BGPKITStream

stream = BGPKITStream(
    collectors=["route-views.wide"],
    data_type=["updates"],
    ts_start=1283203200,  # Unix timestamp
    ts_end=1283289600,    # Unix timestamp
    parser_name="bgpkit",
    max_concurrent_downloads=10,
    cache_dir="/path/to/cache",
    ram_fetch=True,
)
```

### Next: [Filtering Data](filtering.md)
