"""Flat, tabular rows for Hugging Face datasets.

Each config is a streaming row flattener, one per core entity. Rows can be
sourced two ways, both streaming and MBID-anchored:

- **API path** (default): paginated ``search``/``browse`` over the web service
  (rate-limited, no key). Drive it with a ``query=`` (search) or a link such as
  ``artist=<mbid>`` (browse). Good for building focused, current datasets.
- **dump path**: pass ``source="dump"`` to flatten the full data dumps via
  :mod:`pymusicbrainz.bulk` (the whole-corpus backbone).

================  =======================  ==============================
config            entity                   anchor
================  =======================  ==============================
``artists``       artist                   ``musicbrainz_id`` (MBID)
``releases``      release                  ``musicbrainz_id`` (MBID)
``recordings``    recording                ``musicbrainz_id`` (MBID)
``labels``        label                    ``musicbrainz_id`` (MBID)
``release_groups`` release-group           ``musicbrainz_id`` (MBID)
``works``         work                     ``musicbrainz_id`` (MBID)
================  =======================  ==============================

Every row carries ``musicbrainz_id`` so the configs join cleanly across entities.

PROVENANCE: MusicBrainz core data is public domain (CC0); derived data is
CC-BY-NC-SA. See ``PROVENANCE.md`` and ``docs/dataset.md``.
"""
from __future__ import annotations

import json
from typing import Any, Dict, Iterable, Iterator, Optional

from pymusicbrainz import bulk, entity
from pymusicbrainz.ids import to_extra
from pymusicbrainz.models import EntityType

CONFIGS = (
    "artists",
    "releases",
    "recordings",
    "labels",
    "release_groups",
    "works",
)

_CONFIG_ENTITY = {
    "artists": EntityType.ARTIST,
    "releases": EntityType.RELEASE,
    "recordings": EntityType.RECORDING,
    "labels": EntityType.LABEL,
    "release_groups": EntityType.RELEASE_GROUP,
    "works": EntityType.WORK,
}

_CONFIG_BULK_TABLE = {
    "artists": "artist",
    "releases": "release",
    "recordings": "recording",
    "labels": "label",
    "release_groups": "release_group",
    "works": "work",
}


def rows(
    config: str,
    *,
    source: str = "api",
    query: Optional[str] = None,
    limit: Optional[int] = None,
    **kw: Any,
) -> Iterator[Dict[str, Any]]:
    """Stream flat ``extra``-shaped rows for a named *config*.

    Args:
        config: one of :data:`CONFIGS`.
        source: ``"api"`` (search/browse) or ``"dump"`` (full data dumps).
        query: for the API path — a Lucene query (search). Omit and pass a
            browse link as a kwarg (e.g. ``artist="<mbid>"``).
        limit: cap rows yielded (the smoke-test / sampling knob).
        **kw: extra kwargs forwarded to the underlying stream (browse links for
            the API path; ``path=``/``url=``/``snapshot=`` for the dump path).

    Yields one ``dict`` per entity, keyed by the flat ``extra`` namespace.
    """
    if config not in _CONFIG_ENTITY:
        raise ValueError(f"unknown config {config!r}; choose from {CONFIGS}")
    etype = _CONFIG_ENTITY[config]

    if source == "dump":
        table = _CONFIG_BULK_TABLE[config]
        for obj in bulk_typed(table, limit=limit, **kw):
            yield to_extra(obj)
        return

    if source != "api":
        raise ValueError(f"unknown source {source!r}; choose 'api' or 'dump'")

    if query:
        stream = entity.iter_search(etype, query, max_results=limit, **kw)
    else:
        stream = entity.iter_browse(etype, max_results=limit, **kw)
    for obj in stream:
        yield to_extra(obj)


def bulk_typed(table: str, *, limit: Optional[int] = None, **kw: Any) -> Iterator[Any]:
    """Stream typed models from a dump table (helper for :func:`rows`)."""
    fn = {
        "artist": bulk.stream_artists,
        "release": bulk.stream_releases,
        "recording": bulk.stream_recordings,
        "label": bulk.stream_labels,
        "release_group": bulk.stream_release_groups,
        "work": bulk.stream_works,
    }[table]
    return fn(limit=limit, **kw)


def export_jsonl(config: str, out_path: str, **kw: Any) -> int:
    """Stream a *config* to a JSON Lines file; return the row count written.

    Streams end to end (request/dump → model → extra → JSON line) — never
    materialises the whole config in memory. Pass ``limit=N`` to cap rows.
    """
    n = 0
    with open(out_path, "w", encoding="utf-8") as fh:
        for row in rows(config, **kw):
            fh.write(json.dumps(row, ensure_ascii=False) + "\n")
            n += 1
    return n


def export_all(
    out_dir: str,
    configs: Iterable[str] = CONFIGS,
    **kw: Any,
) -> Dict[str, int]:
    """Export several configs to ``<out_dir>/<config>.jsonl``; return counts."""
    import os

    os.makedirs(out_dir, exist_ok=True)
    counts: Dict[str, int] = {}
    for cfg in configs:
        counts[cfg] = export_jsonl(cfg, os.path.join(out_dir, f"{cfg}.jsonl"), **kw)
    return counts
