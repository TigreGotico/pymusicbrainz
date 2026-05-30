# pymusicbrainz

Python metadata client for [MusicBrainz](https://musicbrainz.org) — the open
music encyclopedia. Two no-key data paths, both anchored on the **MBID** (the
canonical music entity id):

- **Web service** (`musicbrainz.org/ws/2`) — lookup / search / browse for
  artist, release, recording, release-group, label and work. No API key;
  requires a descriptive `User-Agent` and one request per second (both
  enforced).
- **Full data dumps** (`data.metabrainz.org/.../fullexport`) — the bulk
  backbone; streaming, memory-safe parsing of the `.tar.bz2` PostgreSQL `COPY`
  tables.

## Install

```bash
pip install -e .
pip install -e ".[stealth]"      # adds curl-cffi transport
pip install -e ".[test]"      # adds pytest
```

Pure-Python, Python >= 3.8. Runtime deps: `requests`, `unblock_requests`.

## Web service

```python
import pymusicbrainz as mb

# polite, MusicBrainz-mandated identification (set yours)
mb.set_user_agent("myapp/1.0 ( me@example.com )")

artist = mb.get_artist("5b11f4ce-a62d-471e-81fc-a69a8278c7da")
print(artist.name, artist.type, artist.country)   # Nirvana Group US

res = mb.search("artist", "nirvana", limit=5)
for hit in res:
    print(hit.mbid, hit.name)

# browse release groups linked to an artist
for rg in mb.iter_browse("release-group", artist=artist.mbid, max_results=20):
    print(rg.title, rg.first_release_date)
```

The transport throttles to >= 1 request/second automatically. Lookup, search
and browse are available for all six entities.

## Bulk dumps (memory-safe streaming)

```python
import pymusicbrainz as mb

# the full export is several GB compressed — this never loads it whole.
for artist in mb.stream_artists(limit=1000):     # downloads on demand, caches
    print(artist.mbid, artist.name)
```

The archive is cached under `~/.cache/pymusicbrainz` (override with
`PYMUSICBRAINZ_CACHE_DIR`). Pass `url=` to stream over HTTP without a full
download, `path=` to read a local `.tar.bz2`, or `limit=N` to sample.

## External IDs

`pymusicbrainz.ids` flattens any entity into a flat dict of namespaced external
IDs, anchored on `musicbrainz_id`:

```python
extra = mb.to_extra(artist)
# {"musicbrainz_id": "...", "musicbrainz_artist_id": "...", "musicbrainz_name": "Nirvana", ...}
```

## Hugging Face datasets

`pymusicbrainz.dataset` exposes one streaming config per entity (`artists`,
`releases`, `recordings`, `labels`, `release_groups`, `works`), sourced from
either the API (`query=`/browse link) or the dumps (`source="dump"`). See
[`docs/dataset.md`](docs/dataset.md).

## Provenance

Core data is public domain (CC0); derived data is CC-BY-NC-SA. The web service
requires a descriptive User-Agent and 1 req/sec. See [`PROVENANCE.md`](PROVENANCE.md).

## Test

```bash
pytest                       # offline, fixture-backed
pytest -m live               # one live smoke (lookup + search)
```
