import datetime
from pydantic import BaseModel, Field, DirectoryPath, field_validator
from typing import Literal
from ipaddress import IPv4Address, IPv6Address


class FilterOptions(BaseModel):
    """A unified model for the available filter options."""

    origin_asn: int | None = Field(
        default=None, description="Filter by the origin AS number."
    )
    prefix: str | None = Field(
        default=None, description="Filter by an exact prefix match."
    )
    prefix_super: str | None = Field(
        default=None,
        description="Filter by the exact prefix and its more general super-prefixes.",
    )
    prefix_sub: str | None = Field(
        default=None,
        description="Filter by the exact prefix and its more specific sub-prefixes.",
    )
    prefix_super_sub: str | None = Field(
        default=None,
        description="Filter by the exact prefix and both its super- and sub-prefixes.",
    )
    peer_ip: str | IPv4Address | IPv6Address | None = Field(
        default=None, description="Filter by the IP address of a single BGP peer."
    )
    peer_ips: list[str | IPv4Address | IPv6Address] | None = Field(
        default=None, description="Filter by a list of BGP peer IP addresses."
    )
    peer_asn: int | None = Field(
        default=None, description="Filter by the AS number of the BGP peer."
    )
    update_type: Literal["withdraw", "announce"] | None = Field(
        default=None, description="Filter by the BGP update message type."
    )
    as_path: str | None = Field(
        default=None, description="Filter by a regular expression matching the AS path."
    )
    ip_version: Literal[4, 6] | None = Field(
        default=None, description="Filter by ip version."
    )


class BGPStreamConfig(BaseModel):
    """
    Unified BGPStream config, compatible with BGPKIT and pybgpstream
    """

    start_time: datetime.datetime = Field(description="Start of the stream")
    end_time: datetime.datetime = Field(description="End of the stream")
    collectors: list[str] = Field(description="List of collectors to get data from")
    data_types: list[Literal["ribs", "updates"]] = Field(
        description="List of archives files to consider (`ribs` or `updates`)"
    )

    filters: FilterOptions | None = Field(default=None, description="Optional filters")

    @field_validator("start_time", "end_time")
    @classmethod
    def normalize_to_utc(cls, dt: datetime.datetime) -> datetime.datetime:
        # if naive datetime (not timezone-aware) assume it's UTC
        if dt.tzinfo is None:
            return dt.replace(tzinfo=datetime.timezone.utc)
        # if timezone-aware, convert to utc
        else:
            return dt.astimezone(datetime.timezone.utc)


AVAILABLE_PARSERS = Literal["pybgpkit", "bgpkit", "pybgpstream", "bgpdump"]


class PyBGPKITStreamConfig(BaseModel):
    """Unified BGPStream config and parameters related to PyBGPKIT implementation (optional)"""

    bgpstream_config: BGPStreamConfig

    max_concurrent_downloads: int | None = Field(
        default=10, description="Maximum concurrent downloads of archive files."
    )

    cache_dir: DirectoryPath | None = Field(
        default=None,
        description="Specifies the directory for caching downloaded files.",
    )

    ram_fetch: bool | None = Field(
        default=True,
        description=(
            "If caching is disabled, fetch temp files in shared RAM memory (/dev/shml) or normal disc temp dir (/tmp)."
            "Default (True) improve perfomance and reduce disk wear, at the expense of increased RAM usage."
        ),
    )

    chunk_time: datetime.timedelta | None = Field(
        default=datetime.timedelta(hours=2),
        description=(
            "Interval for the fetch/parse cycles (benefits: avoid long prefetch time + periodic temps cleanup when caching is disabled)."
            "Slower value means less RAM/disk used at the cost of performance."
        ),
    )

    parser: AVAILABLE_PARSERS = Field(
        default="pybgpkit",
        description=(
            "MRT files parser. Default `pybgpkit` is installed but slow, the others are system dependencies."
        ),
    )
