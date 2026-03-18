# CLI Tool

PyBGPKITStream includes a command-line interface for quick BGP data exploration.

## Installation

The CLI tool is automatically available after installation:

```bash
pip install pybgpkitstream
```

## Basic Usage

### Simple Stream

Stream BGP updates from selected collectors:

```bash
pybgpkitstream \
  --start-time 2010-09-01T00:00:00 \
  --end-time 2010-09-01T02:00:00 \
  --collectors route-views.wide route-views.sydney \
  --data-types updates
```

### Output Format

The CLI outputs elements in pipe-separated format:

```
A|1283289600.000000|route-views.wide|2497|192.0.2.1|192.0.2.0/24|192.0.2.254|2497 2498|None|None|None
```

Fields: `type|time|collector|peer_asn|peer_address|prefix|next-hop|as_path|communities|old_state|new_state`

## Filtering Options

### By Origin AS

```bash
pybgpkitstream \
  --start-time 2010-09-01T00:00:00 \
  --end-time 2010-09-01T02:00:00 \
  --collectors route-views.wide \
  --peer-asn 2497
```

### By Prefix

```bash
# Exact match
pybgpkitstream ... --prefix 192.0.2.0/24

# With super-prefixes (more general)
pybgpkitstream ... --prefix-super 192.0.2.0/25

# With sub-prefixes (more specific)
pybgpkitstream ... --prefix-sub 192.0.2.0/24

# With both super and sub
pybgpkitstream ... --prefix-super-sub 192.0.2.0/25
```

### By Peer

```bash
# Single peer IP
pybgpkitstream ... --peer-ip 192.0.2.1

# Multiple peer IPs
pybgpkitstream ... --peer-ips 192.0.2.1 192.0.2.2 192.0.2.3

# By peer AS
pybgpkitstream ... --peer-asn 2497
```

### By Update Type

```bash
# Announcements only
pybgpkitstream ... --update-type announce

# Withdrawals only
pybgpkitstream ... --update-type withdraw
```

### By AS Path

```bash
# Regular expression matching
pybgpkitstream ... --as-path ".*2497.*"
```

### By IP Version

```bash
# IPv4 only
pybgpkitstream ... --ip-version 4

# IPv6 only
pybgpkitstream ... --ip-version 6
```

## All Options

```bash
pybgpkitstream --help
```

Shows all available command-line options with descriptions.

### Next: [API Reference](../api/overview.md)
