# The default MRT parser is pybgpkit
# This example show the currently supported BGP parsers
# They have an impact on the speed and number of BGP elements

import datetime
import time

from pybgpkitstream import PyBGPKITStreamConfig, BGPKITStream

for parser in ["pybgpkit", "bgpkit", "bgpdump", "pybgpstream"]:
    
    config = PyBGPKITStreamConfig(
        start_time=datetime.datetime(2010, 9, 1, 0, 0),
        end_time=datetime.datetime(2010, 9, 1, 1, 59),
        collectors=["route-views.wide", "rrc04"],
        data_types=["ribs", "updates"],
        parser=parser
    )

    stream = BGPKITStream.from_config(config)

    start = time.perf_counter()
    n_elems = 0
    for elem in stream:
        n_elems += 1
        
    print(f"Parser {parser} processed {n_elems} BGP elements in {time.perf_counter() - start:.2f} seconds")
    
# Example output
# Parser pybgpkit processed 1337852 BGP elements in 39.84 seconds
# Parser bgpkit processed 1087167 BGP elements in 13.97 seconds
# Parser bgpdump processed 1337852 BGP elements in 11.80 seconds
# Parser pybgpstream processed 1337852 BGP elements in 14.94 seconds