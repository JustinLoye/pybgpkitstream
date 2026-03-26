import asyncio
import os
import re
import datetime
from typing import Iterator, Literal
from collections import defaultdict
from itertools import chain
from heapq import merge
from operator import attrgetter, itemgetter
import binascii
import logging
from tempfile import TemporaryDirectory

import aiofiles
import aiohttp
import bgpkit
from bgpkit.bgpkit_broker import BrokerItem

from pybgpkitstream.bgpstreamconfig import (
    BGPStreamConfig,
    FilterOptions,
    PyBGPKITStreamConfig,
    LiveStreamConfig,
)
from pybgpkitstream.bgpelement import BGPElement
from pybgpkitstream.bgpparser import (
    BGPParser,
    PyBGPKITParser,
    BGPKITParser,
    PyBGPStreamParser,
    BGPdumpParser,
)
from pybgpkitstream.rislive import RISLiveStream, jitter_buffer_stream
from pybgpkitstream.utils import dt_from_filepath

name2parser = {
    "pybgpkit": PyBGPKITParser,
    "bgpkit": BGPKITParser,
    "pybgpstream": PyBGPStreamParser,
    "bgpdump": BGPdumpParser,
}


logger = logging.getLogger(__name__)

# Download retry constants
MAX_RETRIES = 5
INITIAL_BACKOFF = 0.2  # seconds
REQUEST_DELAY = 0.05 # 50ms


def crc32(input_str: str):
    input_bytes = input_str.encode("utf-8")
    crc = binascii.crc32(input_bytes) & 0xFFFFFFFF
    return f"{crc:08x}"


class Directory:
    """Permanent directory that mimics TemporaryDirectory interface."""

    def __init__(self, path):
        self.name = str(path)

    def cleanup(self):
        """No-op cleanup for permanent directories."""
        pass


def get_shared_memory():
    """Get a RAM-based temp path if available, otherwise fall back to default."""
    if os.path.exists("/dev/shm"):  # Linux tmpfs
        return "/dev/shm"
    elif os.path.exists("/Volumes/RAMDisk"):  # macOS (if mounted)
        return "/Volumes/RAMDisk"
    return None  # Fall back to default temp directory


class BGPKITStream:
    """Stream and process BGP messages from multiple collectors.

    BGPKITStream is a high-performance alternative to PyBGPStream that parses BGP
    MRT files using BGPKIT. It can stream both historical and live BGP data with
    support for advanced filtering, multiple parser backends, and memory-efficient
    lazy loading.

    Attributes:
        collectors (list[str]): List of collector names to fetch data from.
        data_type (list[Literal["update", "rib"]]): Data types to stream ("update" or "rib").
        ts_start (float | None): Start timestamp (Unix epoch). None for live mode.
        ts_end (float | None): End timestamp (Unix epoch). None for live mode.
        filters (FilterOptions): Filtering options for BGP elements.
        cache_dir (Directory | TemporaryDirectory): Cache directory for downloaded files.
        parser_name (str): Backend parser to use ("pybgpkit", "bgpkit", "bgpdump", "pybgpstream").
        max_concurrent_downloads (int): Maximum concurrent file downloads.
        chunk_time (float): Time window (seconds) for processing chunks. Default is 2 hours.
        ram_fetch (bool): Use RAM disk (/dev/shm, /Volumes/RAMDisk) if available.
        jitter_buffer_delay (float): Delay (seconds) for jitter buffer in live mode.

    Examples:
        Stream historical BGP data:

        ```python
        config = BGPStreamConfig(
            start_time=datetime.datetime(2010, 9, 1, 0, 0),
            end_time=datetime.datetime(2010, 9, 1, 2, 0),
            collectors=["route-views.wide"],
        )
        stream = BGPKITStream.from_config(config)
        for elem in stream:
            print(elem)
        ```

        Direct instantiation with filters:

        ```python
        stream = BGPKITStream(
            collectors=["route-views.wide"],
            data_type=["update"],
            ts_start=1283203200,
            ts_end=1283289600,
            filters=FilterOptions(origin_asn=64512),
            parser_name="bgpkit",
        )
        for elem in stream:
            print(f"{elem.prefix}: {elem.fields['as-path']}")
        ```

        Live streaming from RIS Live:

        ```python
        config = BGPStreamConfig(
            collectors=["rrc00"],
            data_types=["updates"],
        )
        stream = BGPKITStream.from_config(config)
        for elem in stream:
            print(f"Live: {elem.type} {elem.prefix}")
        ```
    """
    def __init__(
        self,
        collectors: list[str],
        data_type: list[Literal["update", "rib"]],
        ts_start: float = None,
        ts_end: float = None,
        filters: FilterOptions | None = None,
        cache_dir: str | None = None,
        max_concurrent_downloads: int | None = 10,
        chunk_time: float | None = datetime.timedelta(hours=2).seconds,
        ram_fetch: bool | None = True,
        parser_name: str | None = "pybgpkit",
        jitter_buffer_delay: float | None = 10.0,
    ):
        """Initialize a BGP stream.

        Args:
            collectors: List of collector names (e.g., ["route-views.wide", "rrc04"]).
            data_type: List of data types to stream ("update", "rib", or both).
            ts_start: Start timestamp (Unix epoch) for historical data. None for live mode.
            ts_end: End timestamp (Unix epoch) for historical data. None for live mode.
            filters: Optional FilterOptions to filter BGP elements. Defaults to no filtering.
            cache_dir: Directory to cache downloaded MRT files. If None, uses temporary directory.
            max_concurrent_downloads: Maximum concurrent downloads. Default is 10.
            chunk_time: Time window (seconds) for streaming chunks. Default is 2 hours (7200s).
            ram_fetch: Use RAM disk for temporary files if available. Default is True.
            parser_name: Parser backend ("pybgpkit", "bgpkit", "bgpdump", "pybgpstream").
                Default is "pybgpkit" (no system dependencies).
            jitter_buffer_delay: Delay (seconds) for jitter buffer in live mode. Default is 10.0.

        Raises:
            ValueError: If parser_name is invalid.

        Note:
            For live mode, set both ts_start and ts_end to None.
            For historical data, both ts_start and ts_end must be provided.
        """
        # Stream config
        self.ts_start = ts_start
        self.ts_end = ts_end
        self.collectors = collectors
        self.data_type = data_type
        if not filters:
            filters = FilterOptions()
        self.filters = filters

        # Implementation config
        self.max_concurrent_downloads = max_concurrent_downloads
        self.chunk_time = chunk_time
        self.ram_fetch = ram_fetch
        if cache_dir:
            self.cache_dir = Directory(cache_dir)
        else:
            if ram_fetch:
                self.cache_dir = TemporaryDirectory(dir=get_shared_memory())
            else:
                self.cache_dir = TemporaryDirectory()
        if not parser_name:
            self.parser_name = "pybgpkit"
        else:
            self.parser_name = parser_name

        self.broker = bgpkit.Broker()
        self.parser_cls: BGPParser = name2parser[parser_name]

        # Live config
        self.jitter_buffer_delay = jitter_buffer_delay

    @staticmethod
    def _generate_cache_filename(url):
        """Generate a cache filename compatible with BGPKIT parser."""

        hash_suffix = crc32(url)

        if "updates." in url:
            data_type = "updates"
        elif "rib" in url or "view" in url:
            data_type = "rib"
        else:
            raise ValueError("Could not understand data type from url")

        # Look for patterns like rib.20100901.0200 or updates.20100831.2345
        timestamp_match = re.search(r"(\d{8})\.(\d{4})", url)
        if timestamp_match:
            timestamp = f"{timestamp_match.group(1)}.{timestamp_match.group(2)}"
        else:
            raise ValueError("Could not parse timestamp from url")

        if url.endswith(".bz2"):
            compression_ext = "bz2"
        elif url.endswith(".gz"):
            compression_ext = "gz"
        else:
            raise ValueError("Could not parse extension from url")

        return f"cache-{data_type}.{timestamp}.{hash_suffix}.{compression_ext}"

    def _set_urls(self):
        """Set archive files URL with bgpkit broker"""
        # Set the urls with bgpkit broker
        self.urls = {"rib": defaultdict(list), "update": defaultdict(list)}
        for data_type in self.data_type:
            items: list[BrokerItem] = self.broker.query(
                ts_start=int(self.ts_start - 60),
                ts_end=int(self.ts_end),
                collector_id=",".join(self.collectors),
                data_type=data_type,
            )
            for item in items:
                self.urls[data_type][item.collector_id].append(item.url)
            
    async def _download_file(self, semaphore, session, url, filepath, data_type, rc):
        """Helper coroutine to download a single file with retries and backoff, controlled by a semaphore."""
        async with semaphore:
            for attempt in range(MAX_RETRIES + 1):
                try:
                    # 1. Mandatory 50ms delay before every request attempt
                    await asyncio.sleep(REQUEST_DELAY)

                    logging.debug(f"Attempt {attempt + 1}: Downloading {url}")
                    
                    async with session.get(url) as resp:
                        resp.raise_for_status()
                        
                        # Using a temporary file is safer to avoid partial cache hits
                        temp_filepath = f"{filepath}.tmp"
                        async with aiofiles.open(temp_filepath, mode="wb") as fd:
                            async for chunk in resp.content.iter_chunked(32768):
                                await fd.write(chunk)
                        
                        # Rename temp file to actual filepath on success
                        os.rename(temp_filepath, filepath)
                        return data_type, rc, filepath

                except (aiohttp.ClientError, asyncio.TimeoutError) as e:
                    backoff = INITIAL_BACKOFF * (2 ** attempt)
                    
                    if attempt < MAX_RETRIES:
                        logging.warning(
                            f"Retrying {url} in {backoff}s due to error: {e} (Attempt {attempt + 1}/{MAX_RETRIES})"
                        )
                        await asyncio.sleep(backoff)
                    else:
                        logging.error(f"Failed to download {url} after {MAX_RETRIES} retries: {e}")
                        # Clean up temp file if it exists
                        if os.path.exists(f"{filepath}.tmp"):
                            os.remove(f"{filepath}.tmp")
                        return None

    async def _prefetch_data(self):
        """Download archive files concurrently and cache to `self.cache_dir`"""
        self.paths = {"rib": defaultdict(list), "update": defaultdict(list)}
        tasks = []

        semaphore = asyncio.Semaphore(self.max_concurrent_downloads)

        timeout = aiohttp.ClientTimeout(total=None, sock_read=300)
        async with aiohttp.ClientSession(timeout=timeout) as session:
            # Create all the download tasks.
            for data_type in self.data_type:
                for rc, rc_urls in self.urls[data_type].items():
                    for url in rc_urls:
                        filename = self._generate_cache_filename(url)
                        filepath = os.path.join(self.cache_dir.name, filename)

                        if os.path.exists(filepath):
                            logging.debug(f"{filepath} is a cache hit")
                            self.paths[data_type][rc].append(filepath)
                        else:
                            task = asyncio.create_task(
                                self._download_file(
                                    semaphore, session, url, filepath, data_type, rc
                                )
                            )
                            tasks.append(task)

            if tasks:
                logging.info(
                    f"Starting download of {len(tasks)} files with a concurrency of {self.max_concurrent_downloads}..."
                )
                results = await asyncio.gather(*tasks)

                # Process the results, skipping any 'None' values from failed downloads.
                for result in results:
                    if result:
                        data_type, rc, filepath = result
                        self.paths[data_type][rc].append(filepath)
                logging.info("All downloads finished.")

    def __iter__(self):
        if self.ts_start is None and self.ts_end is None:
            return self._iter_live()
        if "update" in self.data_type:
            return self._iter_update()
        else:
            return self._iter_rib()

    def _iter_update(self) -> Iterator[BGPElement]:
        # __iter__ for data types [ribs, updates] or [updates]
        # try/finally to cleanup the fetching cache
        try:
            # Manager mode: spawn smaller worker streams to balance fetch/parse
            if self.chunk_time:
                current = self.ts_start

                while current < self.ts_end:
                    chunk_end = min(current + self.chunk_time, self.ts_end)

                    logging.info(
                        f"Processing chunk: {datetime.datetime.fromtimestamp(current)} "
                        f"to {datetime.datetime.fromtimestamp(chunk_end)}"
                    )
                    worker = type(self)(
                        ts_start=current,
                        ts_end=chunk_end
                        - 1,  # remove one second because BGPKIT include border
                        collectors=self.collectors,
                        data_type=self.data_type,
                        cache_dir=self.cache_dir.name
                        if isinstance(self.cache_dir, Directory)
                        else None,
                        filters=self.filters,
                        max_concurrent_downloads=self.max_concurrent_downloads,
                        chunk_time=None,  # Worker doesn't chunk itself
                        ram_fetch=self.ram_fetch,
                        parser_name=self.parser_name,
                    )

                    yield from worker
                    current = chunk_end + 1e-7

                return

            self._set_urls()
            asyncio.run(self._prefetch_data())

            # One iterator for each data_type * collector combinations
            # To be merged according to the elements timestamp
            iterators_to_merge = []

            for data_type in self.data_type:
                is_rib = data_type == "rib"

                # Get rib or update files per collector
                rc_to_paths = self.paths[data_type]

                # Chain rib or update iterators to get one stream per collector / data_type
                for rc, paths in rc_to_paths.items():
                    # Don't use a generator here. parsers are lazy anyway
                    parsers = [
                        self.parser_cls(path, is_rib, rc, filters=self.filters)
                        for path in paths
                    ]

                    chained_iterator = chain.from_iterable(parsers)

                    # Add metadata lost by bgpkit for compatibility with pubgpstream
                    # iterators_to_merge.append((chained_iterator, is_rib, rc))
                    iterators_to_merge.append(chained_iterator)

            for bgpelem in merge(*iterators_to_merge, key=attrgetter("time")):
                if self.ts_start <= bgpelem.time <= self.ts_end:
                    yield bgpelem
        finally:
            self.cache_dir.cleanup()

    def _iter_rib(self) -> Iterator[BGPElement]:
        # __iter__ for data types [ribs]
        # try/finally to cleanup the fetching cache
        try:
            # Manager mode: spawn smaller worker streams to balance fetch/parse
            if self.chunk_time:
                current = self.ts_start

                while current < self.ts_end:
                    chunk_end = min(current + self.chunk_time, self.ts_end)

                    logging.info(
                        f"Processing chunk: {datetime.datetime.fromtimestamp(current)} "
                        f"to {datetime.datetime.fromtimestamp(chunk_end)}"
                    )
                    worker = type(self)(
                        ts_start=current,
                        ts_end=chunk_end
                        - 1,  # remove one second because BGPKIT include border
                        collectors=self.collectors,
                        data_type=self.data_type,
                        cache_dir=self.cache_dir.name
                        if isinstance(self.cache_dir, Directory)
                        else None,
                        filters=self.filters,
                        max_concurrent_downloads=self.max_concurrent_downloads,
                        chunk_time=None,  # Worker doesn't chunk itself
                        ram_fetch=self.ram_fetch,
                        parser_name=self.parser_name,
                    )

                    yield from worker
                    current = chunk_end + 1e-7

                return

            self._set_urls()
            asyncio.run(self._prefetch_data())

            rc_to_paths = self.paths["rib"]

            # Agglomerate all RIBs parsers for ordering
            iterators_to_order = []
            for rc, paths in rc_to_paths.items():
                # Don't use a generator here. parsers are lazy anyway
                parsers = [
                    (
                        dt_from_filepath(path),
                        rc,
                        self.parser_cls(path, True, rc, filters=self.filters),
                    )
                    for path in paths
                ]
                iterators_to_order.extend(parsers)

            iterators_to_order.sort(key=itemgetter(0, 1))

            for bgpelem in chain.from_iterable(
                (iterator[2] for iterator in iterators_to_order)
            ):
                if self.ts_start <= bgpelem.time <= self.ts_end:
                    yield bgpelem
        finally:
            self.cache_dir.cleanup()

    def _iter_live(self) -> Iterator[BGPElement]:

        ris_collectors = [
            collector for collector in self.collectors if collector[:3] == "rrc"
        ]

        stream = RISLiveStream(collectors=ris_collectors, filters=self.filters)

        if self.jitter_buffer_delay is not None and self.jitter_buffer_delay > 0:
            stream = jitter_buffer_stream(stream, buffer_delay=self.jitter_buffer_delay)

        for elem in stream:
            yield elem

    @classmethod
    def from_config(
        cls, config: PyBGPKITStreamConfig | BGPStreamConfig | LiveStreamConfig
    ) -> "BGPKITStream":
        """Create a BGPKITStream from a configuration object.

        Factory method to create a stream from various configuration types,
        automatically handling conversions and parameter mappings.

        Args:
            config: Configuration object, one of:
                - BGPStreamConfig: Standard unified configuration.
                - PyBGPKITStreamConfig: Extended configuration with caching and parser options.
                - LiveStreamConfig: Configuration for live RIS Live streaming.

        Returns:
            BGPKITStream: Initialized stream ready for iteration.

        Examples:
            ```python
            from pybgpkitstream import BGPStreamConfig, BGPKITStream
            import datetime

            config = BGPStreamConfig(
                start_time=datetime.datetime(2010, 9, 1, 0, 0),
                end_time=datetime.datetime(2010, 9, 1, 2, 0),
                collectors=["route-views.wide"],
            )
            stream = BGPKITStream.from_config(config)
            for elem in stream:
                print(elem)
            ```
        """
        if isinstance(config, PyBGPKITStreamConfig):
            stream_config = config.bgpstream_config
            return cls(
                ts_start=stream_config.start_time.timestamp(),
                ts_end=stream_config.end_time.timestamp(),
                collectors=stream_config.collectors,
                data_type=[dtype[:-1] for dtype in stream_config.data_types],
                filters=stream_config.filters
                if stream_config.filters
                else FilterOptions(),
                cache_dir=str(config.cache_dir) if config.cache_dir else None,
                max_concurrent_downloads=config.max_concurrent_downloads
                if config.max_concurrent_downloads
                else 10,
                chunk_time=config.chunk_time.seconds if config.chunk_time else None,
                ram_fetch=config.ram_fetch if config.ram_fetch else None,
                parser_name=config.parser if config.parser else "pybgpkit",
            )

        elif isinstance(config, BGPStreamConfig):
            if not config.is_live():
                return cls(
                    ts_start=config.start_time.timestamp(),
                    ts_end=config.end_time.timestamp(),
                    collectors=config.collectors,
                    data_type=[dtype[:-1] for dtype in config.data_types],
                    filters=config.filters if config.filters else FilterOptions(),
                )
            else:
                return cls(
                    collectors=config.collectors,
                    data_type=["update"],
                    filters=config.filters if config.filters else FilterOptions(),
                    jitter_buffer_delay=10,
                )

        elif isinstance(config, LiveStreamConfig):
            return cls(
                collectors=config.collectors,
                data_type=["update"],
                filters=config.filters if config.filters else FilterOptions(),
                jitter_buffer_delay=config.jitter_buffer_delay,
            )

        else:
            raise ValueError("Unsupported config type")
