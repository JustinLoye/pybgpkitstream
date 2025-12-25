import pybgpstream
from pybgpkitstream import PyBGPKITStreamConfig
from pybgpkitstream.bgpparser import generate_bgpstream_filters


def make_bgpstream(config: PyBGPKITStreamConfig) -> pybgpstream.BGPStream:
    stream = pybgpstream.BGPStream(
        from_time=config.bgpstream_config.start_time.isoformat(" "),
        until_time=config.bgpstream_config.end_time.isoformat(" "),
        collectors=config.bgpstream_config.collectors,
        record_types=config.bgpstream_config.data_types,
        filter=generate_bgpstream_filters(config.bgpstream_config.filters),
    )
    if config.cache_dir:
        stream.set_data_interface_option("broker", "cache-dir", str(config.cache_dir))

    return stream
