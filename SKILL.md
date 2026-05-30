---
name: pymusicbrainz
description: Query MusicBrainz artists, releases, and recordings via a no-key Python client, giving voice-first agents structured music metadata on behalf of users who cannot navigate the website.
---
# pymusicbrainz — MusicBrainz for agents

## When to use

Use this skill when a user asks a music-metadata question that requires looking up
an artist, album, track, label, or composition — especially in a hands-free or
screen-free context where navigating musicbrainz.org is not an option.  Examples:

- "Who released *Dummy* and in what year?"
- "What country is Portishead from?"
- "List all studio albums by Massive Attack."
- "How long is 'Teardrop'?"

The MusicBrainz database is community-maintained, covers all genres and eras, and
is freely queryable with no API key.

## Install

```bash
pip install pymusicbrainz
```

## Core operations

All functions live in `pymusicbrainz` (top-level import).  Every returned object
carries an `mbid` (UUID) — the canonical cross-reference anchor — plus a `.url`
property pointing to the entity's MusicBrainz page.

---

### `search(entity, query, *, limit=25, offset=0) -> SearchResult`

Search any entity type by free-text or Lucene query.  Returns a `SearchResult`
(iterable, `len()`, `.has_more`, `.count`, `.offset`).

```python
import pymusicbrainz as mb

results = mb.search("artist", "Portishead")
for artist in results:
    print(artist.mbid, artist.name, artist.country)
# → 8f6bd1e4-fbe1-45ba-aa69-a6770ff98b13  Portishead  GB
```

Key fields on `Artist`: `mbid`, `name`, `sort_name`, `type` (Person/Group/…),
`country`, `begin_date`, `end_date`, `disambiguation`, `aliases`.

---

### `lookup(entity, mbid, *, inc=None) -> Artist | Release | Recording | …`

Fetch one entity by its known MBID.  Pass `inc` sub-queries for richer data
(e.g. `["aliases", "tags"]`).

```python
artist = mb.lookup("artist", "8f6bd1e4-fbe1-45ba-aa69-a6770ff98b13")
print(artist.name, artist.begin_date)
# → Portishead  1991
```

---

### `browse(entity, *, limit=25, offset=0, **links) -> SearchResult`

List entities linked to another entity by MBID.  Pass exactly one link keyword.

```python
# All release-groups (albums/singles/EPs) by Portishead
artist_mbid = "8f6bd1e4-fbe1-45ba-aa69-a6770ff98b13"
page = mb.browse("release-group", artist=artist_mbid, limit=100)
for rg in page:
    print(rg.title, rg.primary_type, rg.first_release_date)
```

Key fields on `ReleaseGroup`: `mbid`, `title`, `primary_type` (Album/Single/EP/…),
`secondary_types`, `first_release_date`, `artist_credit`.

---

### `iter_search(entity, query, *, page_size=100, max_results=None) -> Iterator`

Paginate automatically through all search hits, one model per iteration.
Respects the rate limit between pages.

```python
for recording in mb.iter_search("recording", "artist:Portishead", max_results=50):
    print(recording.title, recording.length_str)
```

---

### `iter_browse(entity, *, page_size=100, max_results=None, **links) -> Iterator`

Same as `iter_search` but for browse queries — use when the full linked set
exceeds one page.

```python
for release in mb.iter_browse("release", artist=artist_mbid):
    print(release.title, release.date, release.country)
```

---

### Typed convenience lookups

| Function | Returns | Key fields |
|---|---|---|
| `get_artist(mbid)` | `Artist` | `name`, `type`, `country`, `begin_date`, `end_date` |
| `get_release(mbid)` | `Release` | `title`, `status`, `date`, `country`, `artist_credit` |
| `get_recording(mbid)` | `Recording` | `title`, `length_ms`, `length_str`, `artist_credit`, `isrcs` |
| `get_release_group(mbid)` | `ReleaseGroup` | `title`, `primary_type`, `first_release_date` |
| `get_label(mbid)` | `Label` | `name`, `type`, `country`, `label_code` |
| `get_work(mbid)` | `Work` | `title`, `type`, `language`, `iswcs` |

```python
rec = mb.get_recording("08b3e557-cd63-4b13-9c4a-20ce5f5571eb")
print(rec.title, rec.length_str)
# → Teardrop  5:29
```

Every model has `.to_dict()` for JSON serialisation and `.url` for the
canonical MusicBrainz page link.

## Access notes

The MusicBrainz web service at `musicbrainz.org/ws/2` requires no API key.
A descriptive `User-Agent` header and a maximum of one request per second are
mandatory — both are enforced automatically by the transport layer.  For bulk
access (millions of records), use the official data dumps via
`pymusicbrainz.bulk` (`stream_artists`, `stream_releases`, etc.) rather than
the live API.

## Speaking the results (accessibility)

- For an artist query, speak the canonical name, country, type (person or group),
  and active years; offer to list albums or credits next.
- For a release or release-group, speak the title, primary type (album/single/EP),
  release year, and the credited artist(s).
- For a recording, speak the track title, artist, duration (`length_str`), and,
  if known, the album it appears on.
- When a user asks "what year was X released", prefer `ReleaseGroup.first_release_date`
  (the earliest known release worldwide) over individual `Release.date` entries.
