import pytest
import datetime
from itertools import pairwise
from pybgpkitstream import BGPKITStream, BGPStreamConfig
import pybgpstream
from pybgpstream_utils import make_bgpstream


@pytest.fixture
def config():
    return BGPStreamConfig(
        start_time=datetime.datetime(2010, 9, 1, 0, 0),
        end_time=datetime.datetime(2010, 9, 1, 2, 0),
        collectors=["route-views.sydney", "route-views.wide"],
        data_types=["updates"],
    )


@pytest.fixture
def pybgpkit_stream(config):
    """A fixture that returns a BGPKITStream object."""
    return BGPKITStream.from_config(config)


@pytest.fixture
def pybgpstream_stream(config):
    """A fixture that returns a pybgpstream.BGPStream object."""
    return make_bgpstream(config)


def test_pybgpkitstream(pybgpkit_stream, pybgpstream_stream, config):
    """Test if the streamw are consistent and if they return the same number of elements"""
    assert validate_stream(pybgpkit_stream, config) == validate_stream(
        pybgpstream_stream, config
    )


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
