# Performance Guide

Tips and benchmarks for optimal PyBGPKITStream performance.

## Performance Overview

PyBGPKITStream achieves significant performance improvements over PyBGPStream for update processing:

- **Updates**: 3–10× faster than PyBGPStream
- **RIBs**: Currently 3–4× slower (optimization in progress)
- **Memory**: Minimal due to lazy loading

For detailed benchmark results, see [perf.md](https://github.com/JustinLoye/pybgpkitstream/blob/main/perf.md) in the repository.

## Parser Selection

The biggest performance factor is parser choice:

```python
# Fastest: bgpkit-parser (10x speedup)
stream = BGPKITStream.from_config(config, parser_name="bgpkit")

# Slow but no dependencies: pybgpkit (baseline)
stream = BGPKITStream.from_config(config, parser_name="pybgpkit")

# Fast: bgpdump
stream = BGPKITStream.from_config(config, parser_name="bgpdump")
```

**Recommendation**: Install `bgpkit-parser` for production use.

## Filtering for Performance

Applying filters reduces data processed and improves speed:

```python
# Original: processes all elements
stream = BGPKITStream(
    collectors=["route-views.wide"],
    data_type=["updates"],
    ts_start=1283203200,
    ts_end=1283289600,
)

# Filtered: processes fewer elements
stream = BGPKITStream(
    collectors=["route-views.wide"],
    data_type=["updates"],
    ts_start=1283203200,
    ts_end=1283289600,
    filters=FilterOptions(origin_asn=2497),  # Reduces dataset
)
```

## Concurrent Downloads

Control parallel downloads:

```python
# Default: 10 concurrent downloads
stream = BGPKITStream(..., max_concurrent_downloads=10)

# For memory-constrained systems
stream = BGPKITStream(..., max_concurrent_downloads=5)

# For high-throughput systems with plenty of memory
stream = BGPKITStream(..., max_concurrent_downloads=20)
```

## RAM Disk Usage

Use RAM disk (if available) for temporary file storage:

```python
# Automatic: uses /dev/shm (Linux) or /Volumes/RAMDisk (macOS)
stream = BGPKITStream(..., ram_fetch=True)

# Disable to use system temp directory
stream = BGPKITStream(..., ram_fetch=False)
```

**Performance benefit**: 2–3× faster I/O on systems with sufficient free RAM.

## Caching Strategy

Reuse cached files to avoid re-downloading:

```python
# Use persistent cache
stream1 = BGPKITStream(
    ...,
    cache_dir="/data/bgp_cache",
)

# Later: same data is reused from cache
stream2 = BGPKITStream(
    ...,
    cache_dir="/data/bgp_cache",
)
```

**Benefit**: Subsequent runs skip downloads entirely.

## Chunk Time Settings

Set the archive prefetch/parse interval

```python
# Default: 2 hours per chunk
stream = BGPKITStream(..., chunk_time=7200)

# Smaller chunks: more requests but finer control
stream = BGPKITStream(..., chunk_time=1800)  # 30 minutes

# Larger chunks: fewer requests, more data at once
stream = BGPKITStream(..., chunk_time=86400)  # 1 day
```

## Memory Optimization

For very large datasets, minimize memory usage:

```python
# Process in streaming fashion, not storing all elements
element_count = 0
for elem in stream:
    # Process element immediately
    process(elem)
    element_count += 1
    
    # Don't accumulate elements in lists
    # elements.append(elem)  # AVOID!

print(f"Processed {element_count} elements")
```

**Benefit**: Constant memory regardless of dataset size.

## Troubleshooting Performance

### Slow Downloads

1. Check network connectivity
2. Reduce `max_concurrent_downloads` if bandwidth is limited
3. Use `cache_dir` to avoid re-downloading
4. Consider using smaller time windows

### High Memory Usage

1. Reduce `max_concurrent_downloads` to 5 or less
2. Set `ram_fetch=False` to use disk instead of RAM
3. Process elements in streaming fashion, don't accumulate

### Slow Parsing

1. Switch the parser from the default`pybgpkit`
2. Use more specific filters to reduce parsing load

## Further Reading

- [Parser Backends Guide](api/parsers.md)
- [Filtering Guide](guide/filtering.md)
- [Configuration Guide](guide/configuration.md)
