import pytest
import shutil
import importlib
import datetime
from pybgpkitstream import (
    BGPKITStream,
    BGPStreamConfig,
    PyBGPKITStreamConfig,
    FilterOptions,
)
import radix
import os

cache_dir = "cache"
os.makedirs(cache_dir, exist_ok=True)


def has_bgpkit():
    return shutil.which("bgpkit-parser") is not None


def has_bgpdump():
    return shutil.which("bgpdump") is not None


def has_pybgpstream():
    return importlib.util.find_spec("pybgpstream") is not None


PARSERS_TO_TEST = [
    pytest.param("pybgpkit", id="parser:pybgpkit"),
    pytest.param(
        "bgpkit",
        id="parser:bgpkit",
        marks=pytest.mark.skipif(not has_bgpkit(), reason="bgpkit binary not found"),
    ),
    pytest.param(
        "bgpdump",
        id="parser:bgpdump",
        marks=pytest.mark.skipif(not has_bgpdump(), reason="bgpdump binary not found"),
    ),
    pytest.param(
        "pybgpstream",
        id="parser:pybgpstream",
        marks=pytest.mark.skipif(
            not has_pybgpstream(), reason="pybgpstream lib not found"
        ),
    ),
]

# Standard configuration constants to reuse across tests
BASE_START = datetime.datetime(2010, 9, 1, 0, 0)
BASE_END = datetime.datetime(2010, 9, 1, 0, 30)
COLLECTORS = ["route-views.sydney", "route-views.wide"]


def create_stream(parser: str, data_types=["updates"], filters: FilterOptions = None):
    """Helper to create a stream with specific parser and filters."""
    stream_config = BGPStreamConfig(
        start_time=BASE_START,
        end_time=BASE_END,
        collectors=COLLECTORS,
        data_types=data_types,
        filters=filters,
    )
    config = PyBGPKITStreamConfig(
        bgpstream_config=stream_config, parser=parser, cache_dir="cache"
    )
    return BGPKITStream.from_config(config)


@pytest.mark.parametrize("parser", PARSERS_TO_TEST)
def test_parser_rib(parser):
    """
    Ensure every parser can successfully download and parse a basic RIB stream.
    """
    stream = create_stream(parser, data_types=["ribs"])

    count = 0
    for elem in stream:
        count += 1
        # Basic validation that element has content
        assert elem.type == "R"
        assert BASE_START.timestamp() <= elem.time <= BASE_END.timestamp()

    assert count > 0, f"Parser {parser} returned no data for a known valid time range"


@pytest.mark.parametrize("parser", PARSERS_TO_TEST)
def test_parser_update(parser):
    """
    Ensure every parser can successfully download and parse a basic update stream.
    """
    stream = create_stream(parser)

    count = 0
    for elem in stream:
        count += 1
        # Basic validation that element has content
        assert elem.type == "A" or elem.type == "W"
        assert BASE_START.timestamp() <= elem.time <= BASE_END.timestamp()

    assert count > 0, f"Parser {parser} returned no data for a known valid time range"


@pytest.mark.parametrize("parser", PARSERS_TO_TEST)
def test_filter_ip_version_v6(parser):
    """
    Test filtering by IPv6. Should only return prefixes containing ':'.
    """
    filters = FilterOptions(ip_version=6)
    stream = create_stream(parser, filters=filters)

    count = 0
    for elem in stream:
        count += 1
        assert ":" in elem.fields["prefix"], (
            f"Found non-IPv6 prefix: {elem.fields['prefix']}"
        )

    assert count > 0


@pytest.mark.parametrize("parser", PARSERS_TO_TEST)
def test_filter_update_type_withdraw(parser):
    """
    Test filtering by update type 'withdraw'. Should only return withdrawal messages.
    """
    filters = FilterOptions(update_type="withdraw")
    stream = create_stream(parser, filters=filters)

    count = 0
    for elem in stream:
        count += 1
        assert elem.type == "W", f"Found non-withdraw element: {elem.type}"

    assert count > 0


@pytest.mark.parametrize("parser", PARSERS_TO_TEST)
def test_filter_update_type_announce(parser):
    """
    Test filtering by update type 'announce'. Should only return withdrawal messages.
    """
    filters = FilterOptions(update_type="announce")
    stream = create_stream(parser, filters=filters)

    count = 0
    for elem in stream:
        count += 1
        assert elem.type == "A", f"Found non-announce element: {elem.type}"

    assert count > 0


@pytest.mark.parametrize("parser", PARSERS_TO_TEST)
def test_filter_origin_asn(parser):
    """
    Test filtering by a specific origin ASN.
    """
    origin_asn = 27653
    filters = FilterOptions(origin_asn=origin_asn)
    stream = create_stream(parser, filters=filters)

    count = 0
    for elem in stream:
        path = elem.fields.get("as-path", "")
        if path and "{" not in path:
            origin = path.split(" ")[-1]
            assert int(origin) == origin_asn
        count += 1
    assert count > 0


@pytest.mark.parametrize("parser", PARSERS_TO_TEST)
def test_filter_peer_asn(parser):
    """
    Test filtering by a specific peer ASN
    """
    target_peer_asn = 2497
    filters = FilterOptions(peer_asn=target_peer_asn)
    stream = create_stream(parser, filters=filters)

    count = 0
    for elem in stream:
        path = elem.fields.get("as-path", "")
        if path:
            first_asn = path.split(" ")[0]
            assert int(first_asn) == target_peer_asn == elem.peer_asn
        count += 1
    assert count > 0


@pytest.mark.parametrize("parser", PARSERS_TO_TEST)
def test_filter_peer_ip(parser):
    """
    Test filtering by a specific peer ip
    """
    peer_ip = "202.249.2.169"
    filters = FilterOptions(peer_ip=peer_ip)
    stream = create_stream(parser, filters=filters)

    count = 0
    for elem in stream:
        assert elem.peer_address == peer_ip
        count += 1
    assert count > 0


@pytest.mark.parametrize("parser", PARSERS_TO_TEST)
def test_filter_peer_ips(parser):
    """
    Test filtering by a list of peer ips
    """
    peer_ips = ["202.249.2.169", "202.167.228.46"]
    filters = FilterOptions(peer_ips=peer_ips)
    stream = create_stream(parser, filters=filters)

    count = 0
    for elem in stream:
        assert elem.peer_address in peer_ips
        count += 1
    assert count > 0


@pytest.mark.parametrize("parser", PARSERS_TO_TEST)
def test_filter_prefix_exact(parser):
    """
    Test filtering by an exact prefix.
    """
    target_prefix = "213.196.74.0/24"
    filters = FilterOptions(prefix=target_prefix)
    stream = create_stream(parser, filters=filters)

    count = 0
    for elem in stream:
        assert elem.fields["prefix"] == target_prefix
        count += 1
    assert count > 0


@pytest.mark.parametrize("parser", PARSERS_TO_TEST)
def test_filter_prefix_super(parser):
    """
    Test filtering by a prefix and its super-prefixes
    """

    # Search for a target prefixes (one prefix and his supernets)

    # Build the prefix hierarchy
    rtree = radix.Radix()
    filters = FilterOptions(ip_version=4)
    stream = create_stream(parser, filters=filters)
    for elem in stream:
        rtree.add(elem.fields["prefix"])

    # Look for a prefix with at least two supernets (for the sake of completeness)
    # Maybe I could have used Radix.search_covering (not in the doc...)
    child_target_prefix = None
    for rnode in rtree.nodes():
        curr = rnode
        parent_target_prefixes = set()
        while curr.parent:
            parent_target_prefixes.add(curr.parent.prefix)
            curr = curr.parent
        if len(parent_target_prefixes) > 1:
            child_target_prefix = rnode.prefix
            break

    if not child_target_prefix:
        raise RuntimeError("Could not find a prefix with at least 2 supernets")

    filters = FilterOptions(prefix_super=child_target_prefix, ip_version=4)
    stream = create_stream(parser, filters=filters)

    unique_prefixes = set()
    for elem in stream:
        unique_prefixes.add(elem.fields["prefix"])

    assert unique_prefixes == parent_target_prefixes | {child_target_prefix}


@pytest.mark.parametrize("parser", PARSERS_TO_TEST)
def test_filter_prefix_sub(parser):
    """
    Test filtering by a prefix and its sub-prefixes
    """

    # Search for a target prefixes (one prefix and his subnets)
    rtree = radix.Radix()
    filters = FilterOptions(ip_version=4)
    stream = create_stream(parser, filters=filters)
    for elem in stream:
        rtree.add(elem.fields["prefix"])
    for rnode in rtree.nodes():
        subnets_and_self = rtree.search_covered(rnode.prefix)
        if len(subnets_and_self) > 2:
            target_subnet_prefixes = {subnet.prefix for subnet in subnets_and_self}
            target_prefix = rnode.prefix
            break

    filters = FilterOptions(prefix_sub=target_prefix, ip_version=4)
    stream = create_stream(parser, filters=filters)

    unique_prefixes = set()
    for elem in stream:
        unique_prefixes.add(elem.fields["prefix"])

    # target prefix should already by in target_subnet_prefixes
    assert unique_prefixes == target_subnet_prefixes | {target_prefix}


@pytest.mark.parametrize("parser", PARSERS_TO_TEST)
def test_filter_prefix_super_sub(parser):
    """
    Test filtering by a prefix and its super and sub-prefixes
    """

    # Search for a target prefixes (one prefix and his subnets)
    rtree = radix.Radix()
    filters = FilterOptions(ip_version=4)
    stream = create_stream(parser, filters=filters)
    for elem in stream:
        rtree.add(elem.fields["prefix"])
    for rnode in rtree.nodes():
        subnets_and_self = rtree.search_covered(rnode.prefix)
        supernets_and_self = rtree.search_covering(rnode.prefix)
        if len(subnets_and_self) > 1 and len(supernets_and_self) > 1:
            target_subnet_prefixes = {subnet.prefix for subnet in subnets_and_self}
            target_supernet_prefixes = {
                supernet.prefix for supernet in supernets_and_self
            }
            target_prefix = rnode.prefix

    filters = FilterOptions(prefix_super_sub=target_prefix, ip_version=4)
    stream = create_stream(parser, filters=filters)

    unique_prefixes = set()
    for elem in stream:
        unique_prefixes.add(elem.fields["prefix"])

    assert unique_prefixes == target_subnet_prefixes | target_supernet_prefixes | {
        target_prefix
    }


@pytest.mark.parametrize("parser", PARSERS_TO_TEST)
def test_filter_aspath(parser):
    """
    Test filtering by an AS-path regex
    I try a regex to retrieve the peer_asn
    """

    # Get the number of announcement of a **random** peer_asn
    peer_asn = 2497
    stream = create_stream(parser)
    target_count = 0
    for elem in stream:
        if elem.peer_asn == peer_asn and elem.type == "A":
            target_count += 1
    assert target_count > 0

    # Check this number matches with peer_asn extracted with a regex
    # bgpstream uses cisco regex, other tools use normal regex
    if parser == "pybgpstream":
        regex = f"^{peer_asn}_"
    else:
        regex = rf"^{peer_asn}(?:\s|$)"

    filters = FilterOptions(as_path=regex)
    stream = create_stream(parser, filters=filters)
    count = 0
    for elem in stream:
        count += 1
    assert count == target_count
