# Web service

The MusicBrainz web service answers JSON at `https://musicbrainz.org/ws/2` with
no API key. `pymusicbrainz.entity` wraps three request shapes, each MBID-
anchored and returning typed models.

> The service requires a descriptive `User-Agent` and one request per second.
> Both are enforced by `pymusicbrainz.transport` (`set_user_agent`, `set_delay`,
> default 1.1 s). See [`../PROVENANCE.md`](../PROVENANCE.md).

## Entities

`artist`, `release`, `recording`, `release-group`, `label`, `work` — pass the
type as a string or `pymusicbrainz.EntityType`.

## Lookup — one entity by MBID

```python
import pymusicbrainz as mb

mb.lookup("artist", "5b11f4ce-a62d-471e-81fc-a69a8278c7da")
mb.get_release("<mbid>", inc=["release-groups"])   # optional inc= sub-queries
```

## Search — Lucene query

```python
res = mb.search("recording", 'recording:"Smells Like Teen Spirit"', limit=10)
print(res.count, res.offset, res.has_more)
for rec in res:
    print(rec.mbid, rec.title, rec.length_str)
```

`iter_search` pages automatically (one request per page, rate-limited):

```python
for rec in mb.iter_search("recording", "nirvana", max_results=250):
    ...
```

## Browse — entities linked to another

Pass exactly one link keyword (see the API docs for valid links per entity):

```python
mb.browse("release-group", artist="<artist-mbid>")
mb.browse("release", label="<label-mbid>")
mb.browse("recording", release="<release-mbid>")
```

`iter_browse` pages the same way:

```python
for rg in mb.iter_browse("release-group", artist="<mbid>", max_results=100):
    print(rg.title)
```

## Pagination

`search`/`browse` accept `limit` (server cap 100, `mb.MAX_LIMIT`) and `offset`.
`SearchResult.count` is the server total; `has_more` tells you when to page.
