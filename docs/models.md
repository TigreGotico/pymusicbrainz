# Models

`pymusicbrainz.models` holds one typed dataclass per core entity. Every model
carries the canonical `mbid` (the MBID) — the cross-reference anchor consumed by
[`ids.py`](ids.md). Each has a `to_dict()` and a `from_api(data)` classmethod,
and a `url` property pointing at musicbrainz.org. Fields are populated from the
web-service JSON, which shares MusicBrainz's vocabulary with the dumps.

`EntityType` enumerates the six kinds (`artist`, `release`, `recording`,
`release-group`, `label`, `work`); `model_for(EntityType)` returns the class.

| model | key fields |
| --- | --- |
| `Artist` | `name`, `sort_name`, `type`, `country`, `begin_date`, `end_date`, `isnis`, `aliases` |
| `ReleaseGroup` | `title`, `primary_type`, `secondary_types`, `first_release_date`, `artist_credit` |
| `Release` | `title`, `status`, `date`, `country`, `barcode`, `release_group_mbid`, `artist_credit` |
| `Recording` | `title`, `length_ms` (+ `length_str`), `isrcs`, `artist_credit` |
| `Label` | `name`, `sort_name`, `type`, `country`, `label_code` |
| `Work` | `title`, `type`, `language`, `iswcs` |

```python
import pymusicbrainz as mb

rec = mb.get_recording("af40d6b8-58e8-4ca5-9db8-d4fca0b899e2")
print(rec.title, rec.length_str)     # "Smells Like Teen Spirit" 5:01
print(rec.to_dict())
```

## SearchResult

`search` and `browse` return a `SearchResult`: iterable over typed entities,
with `count` (server total), `offset`, `entity_type`, and `has_more`.

```python
res = mb.search("label", "DGC")
print(len(res), res.count, res.has_more)
for label in res:
    print(label.mbid, label.name)
```
