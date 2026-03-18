# Parser Backends

PyBGPKITStream supports multiple parser backends for different use cases.

## Available Parsers

### PyBGPKIT (Default)

- **Name**: `pybgpkit`
- **Speed**: Slow
- **Dependencies**: None
- **Use Case**: Zero-dependency installation, prototyping

```python
stream = BGPKITStream.from_config(config, parser_name="pybgpkit")
```

### BGPKIT Parser

- **Name**: `bgpkit`
- **Speed**: Fast (~10x faster than pybgpkit)
- **Dependencies**: Install from cargo
- **Use Case**: Large-scale processing

Installation:
```bash
cargo install bgpkit-parser --features cli
```

```python
stream = BGPKITStream.from_config(config, parser_name="bgpkit")
```

### BGPDump

- **Name**: `bgpdump`
- **Speed**: Fast, comparable to BGPKIT
- **Dependencies**: Classic MRT parser utility
- **Use Case**: Legacy systems, compatibility

Installation:
```bash
apt-get install bgpdump
```

```python
stream = BGPKITStream.from_config(config, parser_name="bgpdump")
```

### PyBGPStream

- **Name**: `pybgpstream`
- **Speed**: Fastest
- **Dependencies**: `pip install pybgpstream`
- **Use Case**: Large-scale processing

Installation: follow the [CI steps](https://github.com/JustinLoye/pybgpkitstream/blob/main/.github/workflows/ci.yml)

```python
stream = BGPKITStream.from_config(config, parser_name="pybgpstream")
```