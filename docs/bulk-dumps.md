# Bulk data dumps

The MusicBrainz full export lives at
`https://data.metabrainz.org/pub/musicbrainz/data/fullexport/`. `LATEST` names
the current snapshot; each snapshot ships `.tar.bz2` archives of the PostgreSQL
`COPY` tables. `mbdump.tar.bz2` holds the core tables `pymusicbrainz.bulk`
streams: `artist`, `release`, `recording`, `release_group`, `label`, `work`.

> The archive is **multi-GB compressed**. Every function streams — bz2 is
> decompressed on the fly, the tar member is read in chunks, and rows are
> yielded one at a time. Nothing loads a table (let alone the archive) into
> memory.

## Streaming typed rows

```python
import pymusicbrainz as mb

for artist in mb.stream_artists(limit=1000):
    print(artist.mbid, artist.name, artist.begin_date)
```

Typed streams: `stream_artists`, `stream_releases`, `stream_recordings`,
`stream_labels`, `stream_release_groups`, `stream_works`. For raw dicts (keyed
by `bulk.COLUMNS`):

```python
for row in mb.stream_rows("artist", limit=10):
    print(row["gid"], row["name"])
```

## Source resolution

`stream_*` / `stream_rows` resolve the source in this order:

- `url=` — stream the archive directly over HTTP (no full download to disk);
- `path=` — read a specific local `.tar.bz2`;
- otherwise the cached snapshot archive, downloaded on demand.

```python
mb.stream_artists(url=mb.bulk.archive_url(), limit=100)   # HTTP stream
mb.stream_artists(path="/data/mbdump.tar.bz2")           # local
mb.stream_artists(snapshot="20260527-002102", limit=100) # pinned snapshot
```

## Caching & download

```python
snap = mb.latest_snapshot()                  # "20260527-002102"
path = mb.download(snap)                      # streams to ~/.cache/pymusicbrainz
```

Override the cache directory with the `PYMUSICBRAINZ_CACHE_DIR` env var.
`download` streams to disk in 1 MB blocks and is idempotent (`force=True` to
refetch).

## Sampling and smoke tests

Pass `limit=N` to read only the first N rows of a table — the way to sample or
smoke-test without reading the whole dump.

## Column schema

Dump TSV is header-less (PostgreSQL `COPY`), so the column order per table is
declared in `bulk.COLUMNS`. `\N` is decoded to `None`; escaped tabs/newlines
are unescaped. If the upstream schema changes, update `COLUMNS`.
