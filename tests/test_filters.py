import datetime
from pybgpkitstream import BGPKITStream, BGPStreamConfig, FilterOptions

def test_ipv4_filter():
    filters = FilterOptions(ip_version=4)
    config = BGPStreamConfig(
        start_time=datetime.datetime(2010, 9, 1, 0, 0),
        end_time=datetime.datetime(2010, 9, 1, 2, 0),
        collectors=["route-views.sydney", "route-views.wide"],
        data_types=["updates"],
        filters=filters
    )
    
    stream = BGPKITStream.from_config(config)
    
    for i, elem in enumerate(stream):
        assert ":" not in elem.fields["prefix"]
    assert i > 0
    
def test_ipv6_filter():
    filters = FilterOptions(ip_version=6)
    config = BGPStreamConfig(
        start_time=datetime.datetime(2010, 9, 1, 0, 0),
        end_time=datetime.datetime(2010, 9, 1, 2, 0),
        collectors=["route-views.sydney", "route-views.wide"],
        data_types=["updates"],
        filters=filters,
    )

    stream = BGPKITStream.from_config(config)

    for i, elem in enumerate(stream):
        assert "." not in elem.fields["prefix"]
    assert i > 0