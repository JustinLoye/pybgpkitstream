import pybgpstream
from pybgpkitstream import BGPStreamConfig


def generate_filter_string(config: BGPStreamConfig) -> str:
    """Generates a filter string compatible with BGPStream's C parserfrom an BGPStreamConfig object."""
    parts = []

    # Handle top-level list-based filters
    parts.append(f"collector {' '.join(config.collectors)}")

    parts.append(f"type {' '.join(config.data_types)}")

    # Handle the nested FilterOptions
    if config.filters:
        f = config.filters

        if f.peer_asn:
            parts.append(f"peer {f.peer_asn}")

        if f.as_path:
            # Quote the value to handle potential spaces in the regex
            parts.append(f'aspath "{f.as_path}"')

        if f.origin_asn:
            # Filtering by origin ASN is typically done via an AS path regex
            parts.append(f'aspath "_{f.origin_asn}$"')

        if f.update_type:
            # The parser expects 'announcements' or 'withdrawals'
            value = "announcements" if f.update_type == "announce" else "withdrawals"
            parts.append(f"elemtype {value}")

        # Handle all prefix variations
        if f.prefix:
            parts.append(f"prefix exact {f.prefix}")
        if f.prefix_super:
            parts.append(f"prefix less {f.prefix_super}")
        if f.prefix_sub:
            parts.append(f"prefix more {f.prefix_sub}")
        if f.prefix_super_sub:
            parts.append(f"prefix any {f.prefix_super_sub}")

        # Warn about unsupported fields
        if f.peer_ip or f.peer_ips:
            print(
                "Warning: peer_ip and peer_ips are not supported by this BGPStream filter string parser and will be ignored."
            )

    # Join all parts with 'and' as required by the parser
    return " and ".join(parts)


def make_bgpstream(config: BGPStreamConfig) -> pybgpstream.BGPStream:
    stream = pybgpstream.BGPStream(
        from_time=config.start_time.isoformat(" "),
        until_time=config.end_time.isoformat(" "),
        collectors=config.collectors,
        record_types=config.data_types,
        filter=generate_filter_string(config),
    )
    if config.cache_dir:
        stream.set_data_interface_option("broker", "cache-dir", str(config.cache_dir))

    return stream
