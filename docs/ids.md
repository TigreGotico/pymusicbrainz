# IDs

The **MBID** (a UUID) is MusicBrainz's identifier for every entity, and the
dominant cross-reference anchor in music metadata: Discogs, Spotify, Wikidata,
ISRC/ISWC registries and others all carry an MBID. `pymusicbrainz.ids` converts
any entity model to a flat dict of namespaced external IDs, anchored on
`musicbrainz_id`.

## Canonicalising

```python
import pymusicbrainz as mb

mb.canonical_mbid("5b11f4ce-a62d-471e-81fc-a69a8278c7da")           # the MBID
mb.canonical_mbid("https://musicbrainz.org/artist/5b11f4ce-...")    # extracted
mb.canonical_mbid(artist)                                           # from a model
```

## To an `extra` dict

```python
extra = mb.to_extra(artist)
# {
#   "musicbrainz_id": "5b11f4ce-...",          # the anchor (any entity)
#   "musicbrainz_artist_id": "5b11f4ce-...",   # per-entity id key
#   "musicbrainz_url": "https://musicbrainz.org/artist/5b11f4ce-...",
#   "musicbrainz_name": "Nirvana",
#   "musicbrainz_artist_type": "Group",
#   ...
# }
```

`to_extra` dispatches on the model type. Per-entity converters are also exposed:
`artist_to_extra`, `release_to_extra`, `recording_to_extra`,
`release_group_to_extra`, `label_to_extra`, `work_to_extra`.

## Key namespace

- `musicbrainz_id` — the canonical MBID anchor, emitted for every entity.
- `musicbrainz_<entity>_id` — disambiguates the entity type in a flat dict
  (`entity_key(EntityType.WORK)` → `"musicbrainz_work_id"`).
- All values are strings; list-valued fields (ISNI, ISRC, ISWC, secondary
  types, artist credits) are JSON-encoded arrays.
