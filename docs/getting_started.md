# Getting Started

Get up and running with PyBGPKITStream in just a few minutes.

## Installation

PyBGPKITStream is available from PyPI

Install with pip:

```bash
pip install pybgpkitstream
```

Install with uv:

```bash
uv add pybgpkitstream
```

## Examples

### Basic Stream

```python
import datetime
from pybgpkitstream import BGPStreamConfig, BGPKITStream

# Create configuration
config = BGPStreamConfig(
    start_time=datetime.datetime(2010, 9, 1, 0, 0),
    end_time=datetime.datetime(2010, 9, 1, 2, 0),
    collectors=["route-views.wide", "rrc04"],
    data_types=["updates"],
)

# Create and iterate through the stream
stream = BGPKITStream.from_config(config)
for elem in stream:
    print(elem)
```

### Cache the Archive Files

Caching and more implementation details are configurable via the `PyBGPKITStreamConfig` object:

```python
import datetime
from pybgpkitstream import PyBGPKITStreamConfig, BGPKITStream

config = PyBGPKITStreamConfig(
    start_time=datetime.datetime(2010, 9, 1, 0, 0),
    end_time=datetime.datetime(2010, 9, 1, 2, 0),
    collectors=["route-views.wide", "rrc04"],
    data_types=["updates"],
    cache_dir="cache",
    max_concurrent_downloads=5
)

stream = BGPKITStream.from_config(config)
for elem in stream:
    print(elem)
```

### Stream with Filtering

```python
import datetime
from pybgpkitstream import BGPStreamConfig, FilterOptions, BGPKITStream

config = BGPStreamConfig(
    start_time=datetime.datetime(2010, 9, 1, 0, 0),
    end_time=datetime.datetime(2010, 9, 1, 2, 0),
    collectors=["route-views.wide"],
    data_types=["updates"],
    filters=FilterOptions(
        peer_asn=2497,  # Specific peer ASN
        prefix="206.184.16.0/24",  # Specific prefix
    )
)

stream = BGPKITStream.from_config(config)
for elem in stream:
    print(elem)
```

### Live Streaming

Stream real-time BGP updates from RIS Live:

```python
from pybgpkitstream import BGPStreamConfig, BGPKITStream

# Live mode: no start/end times
config = BGPStreamConfig(
    collectors=["rrc00", "rrc01"],
    data_types=["updates"],
)

stream = BGPKITStream.from_config(config)
for elem in stream:
    print(f"Live: {elem}")
```

## Element Structure

BGPElement maintains the same structure as PyBGPStream, allowing straightforward integration:

```
BGPElement(
    time: float,              # Unix timestamp
    type: Literal["R", "A", "W"],  # RIB, Announce, or Withdraw
    collector: str,           # Collector name
    peer_asn: int,           # BGP peer AS number
    peer_address: str,       # BGP peer IP address
    fields: {
        "prefix": str,       # IPv4 or IPv6 prefix
        "next-hop": str,     # Next-hop IP
        "as-path": str,      # AS path (space-separated)
        "communities": [...] # Community list
    }
)
```


## Next Steps

- [Configuration Guide](guide/configuration.md) - Learn all configuration options
- [Filtering Data](guide/filtering.md) - Apply advanced filters
- [API Reference](api/overview.md) - Explore all classes and methods
