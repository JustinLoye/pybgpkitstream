# Changelog

## [0.5.0] - 2026-05-14

### Changed

- Project renamed from `pybgpkitstream` to `pybgpflux`.
- `BGPKITStream` class renamed to `BGPStream`.
- `PyBGPKITStreamConfig` and `BGPStreamConfig` merged into a single flat `BGPStreamConfig`. Implementation parameters (`parser`, `cache_dir`, `ram_fetch`, `chunk_time`, `max_concurrent_downloads`) are now optional fields on `BGPStreamConfig` directly — no more nested config.
- CLI entry point renamed from `pybgpkitstream` to `pybgpflux`.

### Removed

- `PyBGPKITStreamConfig` class and its `bgpstream_config` nested field.
- `nest_bgpstream_params` model validator (no longer needed with flat config).
