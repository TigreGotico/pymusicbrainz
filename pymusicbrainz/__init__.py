"""pymusicbrainz — Python metadata client for MusicBrainz.

Two no-key data paths, both MBID-anchored:

- :mod:`pymusicbrainz.entity` — the **web service** (``musicbrainz.org/ws/2``):
  lookup / search / browse for artist, release, recording, release-group,
  label and work. Requires a descriptive ``User-Agent`` and one request per
  second; both are enforced by :mod:`pymusicbrainz.transport`.
- :mod:`pymusicbrainz.bulk` — the **full data dumps** (the bulk backbone):
  streaming, memory-safe parsing of the ``.tar.bz2`` PostgreSQL ``COPY`` tables.

:mod:`pymusicbrainz.ids` emits the canonical ``musicbrainz_id`` (MBID) anchor
for metadatarr.
"""
from pymusicbrainz.version import __version__
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
from pymusicbrainz.entity import (
    browse,
    get_artist,
    get_label,
    get_recording,
    get_release,
    get_release_group,
    get_work,
    iter_browse,
    iter_search,
    lookup,
    search,
    MAX_LIMIT,
)
from pymusicbrainz import bulk, dataset, entity, ids
from pymusicbrainz.bulk import (
    download,
    latest_snapshot,
    stream_artists,
    stream_labels,
    stream_recordings,
    stream_release_groups,
    stream_releases,
    stream_rows,
    stream_works,
)
from pymusicbrainz.ids import (
    ANCHOR_KEY,
    artist_to_extra,
    canonical_mbid,
    entity_key,
    label_to_extra,
    recording_to_extra,
    release_group_to_extra,
    release_to_extra,
    to_extra,
    work_to_extra,
)
from pymusicbrainz.transport import (
    reset_session,
    set_delay,
    set_session,
    set_user_agent,
)

__all__ = [
    "__version__",
    # models
    "Artist",
    "Release",
    "Recording",
    "ReleaseGroup",
    "Label",
    "Work",
    "SearchResult",
    "EntityType",
    "model_for",
    # web service
    "entity",
    "lookup",
    "search",
    "browse",
    "iter_search",
    "iter_browse",
    "get_artist",
    "get_release",
    "get_recording",
    "get_release_group",
    "get_label",
    "get_work",
    "MAX_LIMIT",
    # bulk dumps
    "bulk",
    "download",
    "latest_snapshot",
    "stream_rows",
    "stream_artists",
    "stream_releases",
    "stream_recordings",
    "stream_labels",
    "stream_release_groups",
    "stream_works",
    # ids / metadatarr
    "ids",
    "ANCHOR_KEY",
    "canonical_mbid",
    "entity_key",
    "to_extra",
    "artist_to_extra",
    "release_to_extra",
    "recording_to_extra",
    "release_group_to_extra",
    "label_to_extra",
    "work_to_extra",
    # dataset
    "dataset",
    # transport
    "set_user_agent",
    "set_delay",
    "reset_session",
    "set_session",
]
