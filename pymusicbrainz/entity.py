"""Web-service access — the no-key live path.

The MusicBrainz web service answers JSON at ``musicbrainz.org/ws/2`` with no
API key, subject to a descriptive ``User-Agent`` and a hard one-request-per-
second rate limit (both enforced by :mod:`pymusicbrainz.transport`).

Three request shapes are wrapped, each MBID-anchored:

- **lookup** — fetch one entity by MBID (``/ws/2/<entity>/<mbid>``).
- **search** — Lucene query against the search index
  (``/ws/2/<entity>?query=...``).
- **browse** — list entities linked to another entity
  (``/ws/2/<entity>?<link>=<mbid>``).

Supported entities: artist, release, recording, release-group, label, work.
"""
from __future__ import annotations

from typing import Any, Dict, Iterator, List, Optional, Union

from pymusicbrainz import transport
from pymusicbrainz.models import (
    Artist,
    EntityType,
    Label,
    Recording,
    Release,
    ReleaseGroup,
    SearchResult,
    Work,
    model_for,
)

# The web service caps result pages at 100.
MAX_LIMIT = 100

# The JSON response key holding a search/browse list, per entity.
_LIST_KEY = {
    EntityType.ARTIST: "artists",
    EntityType.RELEASE: "releases",
    EntityType.RECORDING: "recordings",
    EntityType.RELEASE_GROUP: "release-groups",
    EntityType.LABEL: "labels",
    EntityType.WORK: "works",
}


def _coerce_type(entity: Union[str, EntityType]) -> EntityType:
    if isinstance(entity, EntityType):
        return entity
    return EntityType(entity)


def lookup(
    entity: Union[str, EntityType],
    mbid: str,
    *,
    inc: Optional[List[str]] = None,
):
    """Fetch one entity by MBID and return its typed model.

    Args:
        entity: one of the six entity types (str or :class:`EntityType`).
        mbid: the entity MBID (UUID).
        inc: optional ``inc=`` sub-queries (e.g. ``["aliases", "tags"]``).

    Returns:
        The typed model (:class:`~pymusicbrainz.models.Artist`, etc.).
    """
    etype = _coerce_type(entity)
    params: Dict[str, Any] = {}
    if inc:
        params["inc"] = "+".join(inc)
    data = transport.get_json(f"{etype.value}/{mbid}", params)
    return model_for(etype).from_api(data)


def search(
    entity: Union[str, EntityType],
    query: str,
    *,
    limit: int = 25,
    offset: int = 0,
) -> SearchResult:
    """Search an entity index with a Lucene query.

    Args:
        entity: one of the six entity types.
        query: a Lucene query string (free text works too).
        limit: page size (server caps at 100).
        offset: pagination offset.

    Returns:
        A :class:`~pymusicbrainz.models.SearchResult` of typed models.
    """
    etype = _coerce_type(entity)
    if not query or not query.strip():
        return SearchResult(entity_type=etype)
    params = {
        "query": query.strip(),
        "limit": max(1, min(int(limit), MAX_LIMIT)),
        "offset": max(0, int(offset)),
    }
    data = transport.get_json(etype.value, params)
    return _result_from_api(etype, data)


def browse(
    entity: Union[str, EntityType],
    *,
    limit: int = 25,
    offset: int = 0,
    **links: str,
) -> SearchResult:
    """Browse entities linked to another entity.

    Pass exactly one link as a keyword, e.g.
    ``browse("release-group", artist=mbid)`` or
    ``browse("release", label=mbid)``. See the MusicBrainz API docs for the
    valid link per entity.

    Returns:
        A :class:`~pymusicbrainz.models.SearchResult` of typed models.
    """
    etype = _coerce_type(entity)
    params: Dict[str, Any] = {
        "limit": max(1, min(int(limit), MAX_LIMIT)),
        "offset": max(0, int(offset)),
    }
    for k, v in links.items():
        if v:
            params[k] = v
    data = transport.get_json(etype.value, params)
    return _result_from_api(etype, data)


def iter_search(
    entity: Union[str, EntityType],
    query: str,
    *,
    page_size: int = 100,
    max_results: Optional[int] = None,
) -> Iterator[Any]:
    """Yield search hits across pages, one model at a time.

    Honours the rate limit (one request per page). ``max_results`` caps the
    total yielded — useful for building a dataset config without exhausting an
    open-ended query.
    """
    etype = _coerce_type(entity)
    yielded = 0
    offset = 0
    while True:
        page = search(etype, query, limit=page_size, offset=offset)
        if not len(page):
            break
        for ent in page:
            yield ent
            yielded += 1
            if max_results is not None and yielded >= max_results:
                return
        offset += len(page)
        if not page.has_more:
            break


def iter_browse(
    entity: Union[str, EntityType],
    *,
    page_size: int = 100,
    max_results: Optional[int] = None,
    **links: str,
) -> Iterator[Any]:
    """Yield browse hits across pages, one model at a time."""
    etype = _coerce_type(entity)
    yielded = 0
    offset = 0
    while True:
        page = browse(etype, limit=page_size, offset=offset, **links)
        if not len(page):
            break
        for ent in page:
            yield ent
            yielded += 1
            if max_results is not None and yielded >= max_results:
                return
        offset += len(page)
        if not page.has_more:
            break


# Convenience typed lookups ------------------------------------------------

def get_artist(mbid: str, **kw: Any) -> Artist:
    return lookup(EntityType.ARTIST, mbid, **kw)


def get_release(mbid: str, **kw: Any) -> Release:
    return lookup(EntityType.RELEASE, mbid, **kw)


def get_recording(mbid: str, **kw: Any) -> Recording:
    return lookup(EntityType.RECORDING, mbid, **kw)


def get_release_group(mbid: str, **kw: Any) -> ReleaseGroup:
    return lookup(EntityType.RELEASE_GROUP, mbid, **kw)


def get_label(mbid: str, **kw: Any) -> Label:
    return lookup(EntityType.LABEL, mbid, **kw)


def get_work(mbid: str, **kw: Any) -> Work:
    return lookup(EntityType.WORK, mbid, **kw)


# ---------------------------------------------------------------------------

def _result_from_api(etype: EntityType, data: dict) -> SearchResult:
    from pymusicbrainz._clean import to_int

    data = data or {}
    raw = data.get(_LIST_KEY[etype]) or []
    model = model_for(etype)
    return SearchResult(
        entities=[model.from_api(item) for item in raw],
        count=to_int(data.get("count")) or len(raw),
        offset=to_int(data.get("offset")) or 0,
        entity_type=etype,
    )
