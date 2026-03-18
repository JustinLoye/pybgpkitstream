# BGPElement

::: pybgpkitstream.bgpelement.BGPElement
    options:
      show_source: true
      show_root_heading: true
      heading_level: 2

## Using BGPElement

Each BGP message in a stream is represented as a `BGPElement` namedtuple containing:

- **time** (float): Unix timestamp of the message
- **type** (Literal["R", "A", "W"]): Element type ("R" = RIB (routing table snapshot), "A" = Announce (new/updated prefix), "W" = Withdraw (removed prefix))
- **collector** (str): Source collector name
- **peer_asn** (int): BGP peer AS number
- **peer_address** (str): BGP peer IP address
- **fields** (ElementFields): Dictionary containing:
  - "prefix" (str): IPv4 or IPv6 prefix
  - "next-hop" (str): Next-hop IP address
  - "as-path" (str): AS path (space-separated AS numbers)
  - "communities" (list[str]): BGP communities

## Example Usage

```python
for elem in stream:
    print(f"Type: {elem.type}")
    print(f"Time: {elem.time}")
    print(f"Collector: {elem.collector}")
    print(f"Peer: {elem.peer_asn} ({elem.peer_address})")
    print(f"Prefix: {elem.fields['prefix']}")
    print(f"AS Path: {elem.fields.get('as-path')}")
    print(f"Communities: {elem.fields.get('communities', [])}")
    print("---")
```

## String Representation

BGPElement has a compatible string format with PyBGPStream:

```python
print(elem)
# Output: A|1283289600.000000|route-views.wide|2497|192.0.2.1|192.0.2.0/24|192.0.2.254|64512 64513|||
```
