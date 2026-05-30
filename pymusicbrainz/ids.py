"""Converters from pymusicbrainz models to flat ``str -> str`` dicts of namespaced external IDs.

The canonical anchor key is ``musicbrainz_id`` (the MBID); because nearly every
other music source (Discogs, Spotify, Wikidata, ISRC/ISWC registries, …) carries
an MBID, a clean ``musicbrainz_id`` lets a consumer cross-reference a single hit
out to the rest of the graph. Per-entity keys (``musicbrainz_artist_id``,
``musicbrainz_release_id``, …) disambiguate entity types. Values are strings or
JSON-encoded arrays so the dict stays flat.
"""
from __future__ import annotations

import json
from typing import TYPE_CHECKING, Optional, Union

from pymusicbrainz.models import EntityType

if TYPE_CHECKING:
    from pymusicbrainz.models import (
        Artist,
        Label,
        Recording,
        Release,
        ReleaseGroup,
        Work,
    )

# The canonical key used across every entity.
ANCHOR_KEY = "musicbrainz_id"

# Per-entity id key, so a flat extra dict stays unambiguous.
_ENTITY_KEY = {
    EntityType.ARTIST: "musicbrainz_artist_id",
    EntityType.RELEASE: "musicbrainz_release_id",
    EntityType.RECORDING: "musicbrainz_recording_id",
    EntityType.RELEASE_GROUP: "musicbrainz_release_group_id",
    EntityType.LABEL: "musicbrainz_label_id",
    EntityType.WORK: "musicbrainz_work_id",
}


def canonical_mbid(obj: Union[object, str]) -> Optional[str]:
    """Return the canonical MBID for a model or raw id string."""
    from pymusicbrainz._clean import extract_mbid, is_mbid

    if isinstance(obj, str):
        s = obj.strip()
        if is_mbid(s):
            return s.lower()
        return extract_mbid(s)
    mbid = getattr(obj, "mbid", None)
    return mbid or None


def entity_key(entity_type: EntityType) -> str:
    """Return the per-entity ``musicbrainz_<entity>_id`` key."""
    return _ENTITY_KEY[entity_type]


def _base_extra(obj) -> dict:
    extra = {ANCHOR_KEY: obj.mbid}
    etype = getattr(obj, "entity_type", None)
    if isinstance(etype, EntityType):
        extra[_ENTITY_KEY[etype]] = obj.mbid
    url = getattr(obj, "url", None)
    if url:
        extra["musicbrainz_url"] = url
    return extra


def artist_to_extra(artist: "Artist") -> dict:
    """Convert an :class:`~pymusicbrainz.models.Artist` to an ``extra`` dict."""
    extra = _base_extra(artist)
    if artist.name:
        extra["musicbrainz_name"] = artist.name
    if artist.sort_name:
        extra["musicbrainz_sort_name"] = artist.sort_name
    if artist.type:
        extra["musicbrainz_artist_type"] = artist.type
    if artist.country:
        extra["musicbrainz_country"] = artist.country
    if artist.disambiguation:
        extra["musicbrainz_disambiguation"] = artist.disambiguation
    if artist.isnis:
        extra["musicbrainz_isni"] = json.dumps(artist.isnis)
    return extra


def release_group_to_extra(rg: "ReleaseGroup") -> dict:
    """Convert a :class:`~pymusicbrainz.models.ReleaseGroup` to an ``extra`` dict."""
    extra = _base_extra(rg)
    if rg.title:
        extra["musicbrainz_title"] = rg.title
    if rg.primary_type:
        extra["musicbrainz_primary_type"] = rg.primary_type
    if rg.secondary_types:
        extra["musicbrainz_secondary_types"] = json.dumps(rg.secondary_types)
    if rg.first_release_date:
        extra["musicbrainz_first_release_date"] = rg.first_release_date
    if rg.artist_credit:
        extra["musicbrainz_artist_credit"] = json.dumps(rg.artist_credit)
    return extra


def release_to_extra(release: "Release") -> dict:
    """Convert a :class:`~pymusicbrainz.models.Release` to an ``extra`` dict."""
    extra = _base_extra(release)
    if release.title:
        extra["musicbrainz_title"] = release.title
    if release.status:
        extra["musicbrainz_status"] = release.status
    if release.date:
        extra["musicbrainz_date"] = release.date
    if release.country:
        extra["musicbrainz_country"] = release.country
    if release.barcode:
        extra["musicbrainz_barcode"] = release.barcode
    if release.release_group_mbid:
        extra["musicbrainz_release_group_id"] = release.release_group_mbid
    if release.artist_credit:
        extra["musicbrainz_artist_credit"] = json.dumps(release.artist_credit)
    return extra


def recording_to_extra(recording: "Recording") -> dict:
    """Convert a :class:`~pymusicbrainz.models.Recording` to an ``extra`` dict."""
    extra = _base_extra(recording)
    if recording.title:
        extra["musicbrainz_title"] = recording.title
    if recording.length_ms is not None:
        extra["musicbrainz_length_ms"] = str(recording.length_ms)
    if recording.isrcs:
        extra["musicbrainz_isrc"] = json.dumps(recording.isrcs)
    if recording.artist_credit:
        extra["musicbrainz_artist_credit"] = json.dumps(recording.artist_credit)
    return extra


def label_to_extra(label: "Label") -> dict:
    """Convert a :class:`~pymusicbrainz.models.Label` to an ``extra`` dict."""
    extra = _base_extra(label)
    if label.name:
        extra["musicbrainz_name"] = label.name
    if label.sort_name:
        extra["musicbrainz_sort_name"] = label.sort_name
    if label.type:
        extra["musicbrainz_label_type"] = label.type
    if label.country:
        extra["musicbrainz_country"] = label.country
    if label.label_code is not None:
        extra["musicbrainz_label_code"] = str(label.label_code)
    return extra


def work_to_extra(work: "Work") -> dict:
    """Convert a :class:`~pymusicbrainz.models.Work` to an ``extra`` dict."""
    extra = _base_extra(work)
    if work.title:
        extra["musicbrainz_title"] = work.title
    if work.type:
        extra["musicbrainz_work_type"] = work.type
    if work.language:
        extra["musicbrainz_language"] = work.language
    if work.iswcs:
        extra["musicbrainz_iswc"] = json.dumps(work.iswcs)
    return extra


_TO_EXTRA = {
    EntityType.ARTIST: artist_to_extra,
    EntityType.RELEASE_GROUP: release_group_to_extra,
    EntityType.RELEASE: release_to_extra,
    EntityType.RECORDING: recording_to_extra,
    EntityType.LABEL: label_to_extra,
    EntityType.WORK: work_to_extra,
}


def to_extra(obj) -> dict:
    """Dispatch any entity model to its ``extra`` converter."""
    etype = getattr(obj, "entity_type", None)
    if etype not in _TO_EXTRA:
        raise TypeError(f"no extra converter for {type(obj).__name__}")
    return _TO_EXTRA[etype](obj)
