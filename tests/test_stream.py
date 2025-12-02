import pytest
import datetime
import tempfile
from itertools import pairwise
from pybgpkitstream import BGPKITStream, BGPStreamConfig
import pybgpstream
from tests.pybgpstream_utils import make_bgpstream


@pytest.fixture
def config():
    return BGPStreamConfig(
        start_time=datetime.datetime(2010, 9, 1, 0, 0),
        end_time=datetime.datetime(2010, 9, 1, 1, 59),
        collectors=["route-views.sydney", "route-views.wide"],
        data_types=["updates"],
    )


@pytest.fixture
def config_with_cache():
    """Configuration with a temporary cache directory."""
    with tempfile.TemporaryDirectory() as tmpdir:
        cache_config = BGPStreamConfig(
            start_time=datetime.datetime(2010, 9, 1, 0, 0),
            end_time=datetime.datetime(2010, 9, 1, 1, 59),
            collectors=["route-views.sydney", "route-views.wide"],
            data_types=["updates"],
            cache_dir=tmpdir,
            max_concurrent_downloads=8,
        )
        yield cache_config


@pytest.fixture
def config_with_chunk():
    """Configuration with a chunking mechanism to balance fetch/parse."""
    with tempfile.TemporaryDirectory() as tmpdir:
        chunk_config = BGPStreamConfig(
            start_time=datetime.datetime(2010, 9, 1, 0, 0),
            end_time=datetime.datetime(2010, 9, 1, 1, 59),
            collectors=["route-views.sydney", "route-views.wide"],
            data_types=["updates"],
            cache_dir=tmpdir,
            max_concurrent_downloads=8,
            chunk_time=datetime.timedelta(minutes=15),
        )
        yield chunk_config


@pytest.fixture
def pybgpkit_stream(config):
    """A fixture that returns a BGPKITStream object."""
    return BGPKITStream.from_config(config)


@pytest.fixture
def pybgpstream_stream(config):
    """A fixture that returns a pybgpstream.BGPStream object."""
    return make_bgpstream(config)


@pytest.fixture
def pybgpkit_stream_with_cache(config_with_cache):
    """A BGPKITStream object using the config with cache."""
    return BGPKITStream.from_config(config_with_cache)


@pytest.fixture
def pybgpstream_stream_with_cache(config_with_cache):
    """A pybgpstream.BGPStream object using the config with cache."""
    return make_bgpstream(config_with_cache)


@pytest.fixture
def pybgpkit_stream_with_chunk(config_with_chunk):
    """A BGPKITStream object using the config with chunking mechanism."""
    return BGPKITStream.from_config(config_with_chunk)


@pytest.fixture
def pybgpstream_stream_with_chunk(config_with_chunk):
    """A pybgpstream.BGPStream object using the config with chunking mechanism."""
    return make_bgpstream(config_with_chunk)


def test_pybgpkitstream(pybgpkit_stream, pybgpstream_stream, config):
    """Test if the streamw are consistent and if they return the same number of elements"""
    assert validate_stream(pybgpkit_stream, config) == validate_stream(
        pybgpstream_stream, config
    )


def test_pybgpkitstream_with_cache(
    pybgpkit_stream_with_cache, pybgpstream_stream_with_cache, config_with_cache
):
    """Test if the streams are consistent and if they return the same number of elements (WITH CACHE)"""
    assert validate_stream(
        pybgpkit_stream_with_cache, config_with_cache
    ) == validate_stream(pybgpstream_stream_with_cache, config_with_cache)


def test_pybgpkitstream_with_chunk(
    pybgpkit_stream_with_chunk, pybgpstream_stream_with_chunk, config_with_chunk
):
    """Test if the streams are consistent and if they return the same number of elements (WITH CACHE)"""
    assert validate_stream(
        pybgpkit_stream_with_chunk, config_with_chunk
    ) == validate_stream(pybgpstream_stream_with_chunk, config_with_chunk)


def validate_stream(
    stream: BGPKITStream | pybgpstream.BGPStream, config: BGPStreamConfig
):
    """Test if the output of `stream` is consistent with `config`"""

    types = set()
    collectors = set()
    peer_asns = set()
    times = []

    for i, elem in enumerate(stream):
        types.add(elem.type)
        collectors.add(elem.collector)
        peer_asns.add(elem.peer_asn)
        times.append(elem.time)

    assert i > 0

    if "ribs" in config.data_types:
        assert "R" in types
    if "updates" in config.data_types:
        assert "W" in types and "A" in types

    assert collectors == set(config.collectors)

    if config.filters and config.filters.peer_asn:
        assert peer_asns == set(config.filters.peer_asn)

    assert all([a <= b for a, b in pairwise(times)])
    assert times[0] >= config.start_time.timestamp()
    assert times[-1] <= config.end_time.timestamp()

    return i
