import time
from itertools import pairwise

from pybgpkitstream import LiveStreamConfig, BGPKITStream


# Normal mode, will transform RIS Live data to BGPElements
rislive_config = LiveStreamConfig(collectors=["rrc00", "rrc07", "rrc21"], jitter_buffer_delay=None)

stream = BGPKITStream.from_config(rislive_config)

times = []
start = time.time()
for i, elem in enumerate(stream):
    times.append(elem.time)
    if time.time() - start > 30:
        break


# Watch out RIS Live output is jittery (sligthly unordered timestamps)...
assert not all(t1 <= t2 for t1, t2 in pairwise(times))

# That's why it's possible, at the cost of extra latency, to use a jitter buffer.
# Here we add 15 seconds of latency.
rislive_config = LiveStreamConfig(collectors=["rrc00", "rrc07", "rrc21"], jitter_buffer_delay=15.0)

stream = BGPKITStream.from_config(rislive_config)

times = []
start = time.time()
for i, elem in enumerate(stream):
    times.append(elem.time)
    if time.time() - start > 30:
        break
    
assert all(t1 <= t2 for t1, t2 in pairwise(times))