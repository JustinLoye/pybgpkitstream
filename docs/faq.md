# FAQ

Frequently asked questions about PyBGPKITStream.

## Why do I need a library to stream BGP data?

Even basic historical BGP data queries often involve several manual steps: locating the correct archive, downloading it, and parsing the contents. For more complex queries, such as those involving multiple collectors or specific time ranges, the difficulty increases as users have to manually manage and synchronize numerous archive files.

The goal of PyBGPStream and PyBGPKITStream is to abstract these complexities away. This allows users to focus on the actual data analysis rather than the infrastructure and boilerplate code required to fetch it.

## Why a new library to stream BGP data?

While PyBGPStream has long been the primary tool for streaming historical BGP data from multiple collectors, it is currently no longer actively maintained. As of early 2026, several key features have become unreliable or non-functional, specifically support for RIS Live and data from certain RIS collectors.

PyBGPKITStream was developed to fill this gap, providing a modern, maintained alternative that restores these capabilities while offering the performance benefits of the BGPKIT ecosystem.

## What's the difference between PyBGPKITStream and PyBGPStream?

PyBGPKITStream is a drop-in replacement for PyBGPStream that uses BGPKIT for retrieve and parsing MRT files. Key advantages:

- **More flexible**: Multiple parser backends
- **Modern Python**: Type hints, pydantic for configuration
- **No down time**: Uses BGPKIT broker that can be self-hosted

Setting up the stream is different, but the output BGP elements have the same format.

## Can I use this with live data?

Yes! Set both `start_time` and `end_time` to `None` for live mode:

```python
from pybgpkitstream import BGPStreamConfig, BGPKITStream

config = BGPStreamConfig(
    collectors=["rrc00"],
    data_types=["updates"],
)

stream = BGPKITStream.from_config(config)
for elem in stream:
    print(elem)  # Live updates
```

## How do I filter for specific data?

Use `FilterOptions`:

```python
from pybgpkitstream import FilterOptions

filters = FilterOptions(
    peer_asn=2497,             # Specific AS
    prefix="192.0.2.0/24",     # Specific prefix
    update_type="announce",    # Only announcements
    ip_version=4,              # IPv4 only
)

config = BGPStreamConfig(
    ...,
    filters=filters,
)
```

## Can I combine multiple filters?

Yes, all filters use AND logic:

```python
filters = FilterOptions(
    peer_asn=2497,
    prefix_super="192.0.2.0/24",
    origin_asn=1234,
    ip_version=4,
)
# Returns: IPv4 prefixes originated by 1234,
#          more general than 192.0.2.0/24,
#          with peer 2497
```

## How to cache the MRT archives?

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

## The stream is slow. How do I improve it?

1. **Switch parser**: Use `pybgpstream` parser instead of `pybgpkit`

2. **Add filters**: Reduce the dataset

3. **Reduce time window**: Request less data

See [Performance Guide](performance.md) for more tips.


## Can I process very large datasets?

Yes! Process in streaming fashion:

```python
# Good: constant memory
count = 0
for elem in stream:
    count += 1

# Bad: grows linearly with elements
elements = list(stream)  # AVOID for large datasets!
```

## More Help

- **Issues**: [GitHub Issues](https://github.com/JustinLoye/pybgpkitstream/issues)
- **Discussions**: [GitHub Discussions](https://github.com/JustinLoye/pybgpkitstream/discussions)
