"""Typed dataclasses for MusicBrainz entities.

Every entity is identified by an **MBID** (a UUID) — the canonical music
cross-reference anchor consumed by :mod:`pymusicbrainz.ids`. The fields mirror
the web-service JSON shape, which is the same vocabulary the full data dumps
expose. Each model has a ``to_dict`` and a ``from_api(data)`` classmethod.
"""
from __future__ import annotations

from dataclasses import asdict, dataclass, field
from enum import Enum
from typing import List, Optional


class EntityType(str, Enum):
    """The six core MusicBrainz entity kinds this client models."""

    ARTIST = "artist"
    RELEASE = "release"
    RECORDING = "recording"
    RELEASE_GROUP = "release-group"
    LABEL = "label"
    WORK = "work"


def _drop_none(d: dict) -> dict:
    return {k: v for k, v in d.items() if v not in (None, [], {})}


@dataclass
class Artist:
    """An artist (person or group) — MBID-anchored."""

    mbid: str
    name: Optional[str] = None
    sort_name: Optional[str] = None
    type: Optional[str] = None  # Person, Group, Orchestra, ...
    country: Optional[str] = None
    disambiguation: Optional[str] = None
    begin_date: Optional[str] = None
    end_date: Optional[str] = None
    isnis: List[str] = field(default_factory=list)
    aliases: List[str] = field(default_factory=list)

    entity_type: EntityType = EntityType.ARTIST

    @property
    def url(self) -> str:
        return f"https://musicbrainz.org/artist/{self.mbid}"

    def to_dict(self) -> dict:
        d = asdict(self)
        d["entity_type"] = self.entity_type.value
        return _drop_none(d)

    @classmethod
    def from_api(cls, data: dict) -> "Artist":
        from pymusicbrainz._clean import clean, clean_or_none

        data = data or {}
        life = data.get("life-span") or {}
        return cls(
            mbid=clean(data.get("id")),
            name=clean_or_none(data.get("name")),
            sort_name=clean_or_none(data.get("sort-name")),
            type=clean_or_none(data.get("type")),
            country=clean_or_none(data.get("country")),
            disambiguation=clean_or_none(data.get("disambiguation")),
            begin_date=clean_or_none(life.get("begin")),
            end_date=clean_or_none(life.get("end")),
            isnis=[clean(x) for x in (data.get("isnis") or []) if clean(x)],
            aliases=[
                clean(a.get("name"))
                for a in (data.get("aliases") or [])
                if clean(a.get("name"))
            ],
        )


@dataclass
class ReleaseGroup:
    """A release group (an album/single/EP abstract grouping) — MBID-anchored."""

    mbid: str
    title: Optional[str] = None
    primary_type: Optional[str] = None  # Album, Single, EP, ...
    secondary_types: List[str] = field(default_factory=list)
    first_release_date: Optional[str] = None
    disambiguation: Optional[str] = None
    artist_credit: List[str] = field(default_factory=list)

    entity_type: EntityType = EntityType.RELEASE_GROUP

    @property
    def url(self) -> str:
        return f"https://musicbrainz.org/release-group/{self.mbid}"

    def to_dict(self) -> dict:
        d = asdict(self)
        d["entity_type"] = self.entity_type.value
        return _drop_none(d)

    @classmethod
    def from_api(cls, data: dict) -> "ReleaseGroup":
        from pymusicbrainz._clean import clean, clean_or_none

        data = data or {}
        return cls(
            mbid=clean(data.get("id")),
            title=clean_or_none(data.get("title")),
            primary_type=clean_or_none(data.get("primary-type")),
            secondary_types=[
                clean(x) for x in (data.get("secondary-types") or []) if clean(x)
            ],
            first_release_date=clean_or_none(data.get("first-release-date")),
            disambiguation=clean_or_none(data.get("disambiguation")),
            artist_credit=_credit_names(data.get("artist-credit")),
        )


@dataclass
class Release:
    """A release (a specific issue of a release group) — MBID-anchored."""

    mbid: str
    title: Optional[str] = None
    status: Optional[str] = None  # Official, Promotion, Bootleg, ...
    date: Optional[str] = None
    country: Optional[str] = None
    barcode: Optional[str] = None
    disambiguation: Optional[str] = None
    release_group_mbid: Optional[str] = None
    artist_credit: List[str] = field(default_factory=list)

    entity_type: EntityType = EntityType.RELEASE

    @property
    def url(self) -> str:
        return f"https://musicbrainz.org/release/{self.mbid}"

    def to_dict(self) -> dict:
        d = asdict(self)
        d["entity_type"] = self.entity_type.value
        return _drop_none(d)

    @classmethod
    def from_api(cls, data: dict) -> "Release":
        from pymusicbrainz._clean import clean, clean_or_none

        data = data or {}
        rg = data.get("release-group") or {}
        return cls(
            mbid=clean(data.get("id")),
            title=clean_or_none(data.get("title")),
            status=clean_or_none(data.get("status")),
            date=clean_or_none(data.get("date")),
            country=clean_or_none(data.get("country")),
            barcode=clean_or_none(data.get("barcode")),
            disambiguation=clean_or_none(data.get("disambiguation")),
            release_group_mbid=clean_or_none(rg.get("id")),
            artist_credit=_credit_names(data.get("artist-credit")),
        )


@dataclass
class Recording:
    """A recording (a unique audio capture) — MBID-anchored."""

    mbid: str
    title: Optional[str] = None
    length_ms: Optional[int] = None
    disambiguation: Optional[str] = None
    isrcs: List[str] = field(default_factory=list)
    artist_credit: List[str] = field(default_factory=list)

    entity_type: EntityType = EntityType.RECORDING

    @property
    def url(self) -> str:
        return f"https://musicbrainz.org/recording/{self.mbid}"

    @property
    def length_str(self) -> Optional[str]:
        if not self.length_ms:
            return None
        total = int(self.length_ms) // 1000
        minutes, seconds = divmod(total, 60)
        return f"{minutes}:{seconds:02d}"

    def to_dict(self) -> dict:
        d = asdict(self)
        d["entity_type"] = self.entity_type.value
        return _drop_none(d)

    @classmethod
    def from_api(cls, data: dict) -> "Recording":
        from pymusicbrainz._clean import clean, clean_or_none, to_int

        data = data or {}
        return cls(
            mbid=clean(data.get("id")),
            title=clean_or_none(data.get("title")),
            length_ms=to_int(data.get("length")),
            disambiguation=clean_or_none(data.get("disambiguation")),
            isrcs=[clean(x) for x in (data.get("isrcs") or []) if clean(x)],
            artist_credit=_credit_names(data.get("artist-credit")),
        )


@dataclass
class Label:
    """A label (an imprint / company) — MBID-anchored."""

    mbid: str
    name: Optional[str] = None
    sort_name: Optional[str] = None
    type: Optional[str] = None
    country: Optional[str] = None
    label_code: Optional[int] = None
    disambiguation: Optional[str] = None

    entity_type: EntityType = EntityType.LABEL

    @property
    def url(self) -> str:
        return f"https://musicbrainz.org/label/{self.mbid}"

    def to_dict(self) -> dict:
        d = asdict(self)
        d["entity_type"] = self.entity_type.value
        return _drop_none(d)

    @classmethod
    def from_api(cls, data: dict) -> "Label":
        from pymusicbrainz._clean import clean, clean_or_none, to_int

        data = data or {}
        return cls(
            mbid=clean(data.get("id")),
            name=clean_or_none(data.get("name")),
            sort_name=clean_or_none(data.get("sort-name")),
            type=clean_or_none(data.get("type")),
            country=clean_or_none(data.get("country")),
            label_code=to_int(data.get("label-code")),
            disambiguation=clean_or_none(data.get("disambiguation")),
        )


@dataclass
class Work:
    """A work (a distinct composition) — MBID-anchored."""

    mbid: str
    title: Optional[str] = None
    type: Optional[str] = None
    language: Optional[str] = None
    disambiguation: Optional[str] = None
    iswcs: List[str] = field(default_factory=list)

    entity_type: EntityType = EntityType.WORK

    @property
    def url(self) -> str:
        return f"https://musicbrainz.org/work/{self.mbid}"

    def to_dict(self) -> dict:
        d = asdict(self)
        d["entity_type"] = self.entity_type.value
        return _drop_none(d)

    @classmethod
    def from_api(cls, data: dict) -> "Work":
        from pymusicbrainz._clean import clean, clean_or_none

        data = data or {}
        return cls(
            mbid=clean(data.get("id")),
            title=clean_or_none(data.get("title")),
            type=clean_or_none(data.get("type")),
            language=clean_or_none(data.get("language")),
            disambiguation=clean_or_none(data.get("disambiguation")),
            iswcs=[clean(x) for x in (data.get("iswcs") or []) if clean(x)],
        )


@dataclass
class SearchResult:
    """A page of search results with pagination metadata.

    ``entities`` holds typed models of the searched entity type.
    """

    entities: List[object] = field(default_factory=list)
    count: int = 0
    offset: int = 0
    entity_type: Optional[EntityType] = None

    def __iter__(self):
        return iter(self.entities)

    def __len__(self) -> int:
        return len(self.entities)

    @property
    def has_more(self) -> bool:
        return (self.offset + len(self.entities)) < self.count

    def to_dict(self) -> dict:
        return {
            "count": self.count,
            "offset": self.offset,
            "entity_type": self.entity_type.value if self.entity_type else None,
            "entities": [e.to_dict() for e in self.entities],
        }


# ---------------------------------------------------------------------------

# Maps an EntityType to its model class. Used by search/browse/lookup.
_MODEL_BY_TYPE = {
    EntityType.ARTIST: Artist,
    EntityType.RELEASE: Release,
    EntityType.RECORDING: Recording,
    EntityType.RELEASE_GROUP: ReleaseGroup,
    EntityType.LABEL: Label,
    EntityType.WORK: Work,
}


def model_for(entity_type: EntityType):
    """Return the dataclass for an :class:`EntityType`."""
    return _MODEL_BY_TYPE[entity_type]


def _credit_names(artist_credit) -> List[str]:
    """Flatten a web-service ``artist-credit`` list into plain names."""
    from pymusicbrainz._clean import clean

    out: List[str] = []
    for ac in artist_credit or []:
        if isinstance(ac, dict):
            artist = ac.get("artist") or {}
            name = clean(ac.get("name") or artist.get("name"))
            if name:
                out.append(name)
    return out
