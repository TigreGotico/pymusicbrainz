# pymusicbrainz

`pymusicbrainz` is a Python client for [MusicBrainz](https://musicbrainz.org), the open
music encyclopedia. It gives you two no-key data paths, both anchored on the **MBID**
(the canonical music entity id):

- **Web service** (`musicbrainz.org/ws/2`): lookup, search, and browse for artist,
  release, recording, release-group, label, and work. No API key is needed. A
  descriptive `User-Agent` and a limit of one request per second are required and
  enforced by the client.
- **Full data dumps** (`data.metabrainz.org/.../fullexport`): the bulk backbone. The
  client streams and parses the `.tar.bz2` PostgreSQL `COPY` tables without loading
  them into memory.

## Install

```bash
pip install -e .
pip install -e ".[stealth]"      # adds curl-cffi transport
pip install -e ".[test]"      # adds pytest
```

The package is pure Python and needs Python 3.8 or later. Runtime dependencies:
`requests`, `unblock_requests`.

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

The transport throttles requests to one per second or slower, automatically. Lookup,
search, and browse work for all six entities.

## Bulk dumps (memory-safe streaming)

```python
import pymusicbrainz as mb

# the full export is several GB compressed; this never loads it whole.
for artist in mb.stream_artists(limit=1000):     # downloads on demand, caches
    print(artist.mbid, artist.name)
```

The archive is cached under `~/.cache/pymusicbrainz` (override with
`PYMUSICBRAINZ_CACHE_DIR`). Pass `url=` to stream over HTTP without a full download,
`path=` to read a local `.tar.bz2` file, or `limit=N` to sample rows.

## External IDs

`pymusicbrainz.ids` flattens any entity into a flat dict of namespaced external IDs,
anchored on `musicbrainz_id`:

```python
extra = mb.to_extra(artist)
# {"musicbrainz_id": "...", "musicbrainz_artist_id": "...", "musicbrainz_name": "Nirvana", ...}
```

## Hugging Face datasets

`pymusicbrainz.dataset` exposes one streaming config per entity (`artists`,
`releases`, `recordings`, `labels`, `release_groups`, `works`), sourced from either the
API (`query=`/browse link) or the dumps (`source="dump"`). See
[`docs/dataset.md`](docs/dataset.md).

## Related projects

`pymusicbrainz` is one of a set of metadata clients maintained by
[LeMetadatarr](https://github.com/LeMetadatarr):

- [pydiscogs](https://github.com/LeMetadatarr/pydiscogs): a client for the Discogs
  database.
- [pyimdb](https://github.com/LeMetadatarr/pyimdb): a client for IMDb data.
- [pyrateyourmusic](https://github.com/LeMetadatarr/pyrateyourmusic): a client for
  Rate Your Music data.
- [pyvndb](https://github.com/LeMetadatarr/pyvndb): a client for the Visual Novel
  Database.

## Provenance

Core data is public domain (CC0); derived data is CC-BY-NC-SA. The web service
requires a descriptive User-Agent and one request per second. See
[`PROVENANCE.md`](PROVENANCE.md).

## Test

```bash
pytest                       # offline, fixture-backed
pytest -m live               # one live smoke (lookup + search)
```
