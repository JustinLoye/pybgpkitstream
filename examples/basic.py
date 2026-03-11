import datetime
from pybgpkitstream import BGPStreamConfig, BGPKITStream

config = BGPStreamConfig(
    start_time=datetime.datetime(2010, 9, 1, 0, 0),
    end_time=datetime.datetime(2010, 9, 1, 1, 59),
    collectors=["route-views.wide", "rrc04"],
    data_types=["ribs", "updates"],
)

stream = BGPKITStream.from_config(config)

n_elems = 0
for elem in stream:
  n_elems += 1
    
print(f"Processed {n_elems} BGP elements")