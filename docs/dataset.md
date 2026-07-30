# Hugging Face datasets

`pymusicbrainz.dataset` flattens MusicBrainz entities into tabular rows, one Hugging
Face dataset **config** per core entity. Every config streams and never materializes
a whole source in memory, and every row carries `musicbrainz_id`, so configs join
cleanly across entities.

## Provenance and license (read this first)

MusicBrainz core data is public domain (CC0). Derived data is CC-BY-NC-SA. The web
service requires a descriptive User-Agent and one request per second. See
[`../PROVENANCE.md`](../PROVENANCE.md). Carry the matching license and attribution in
any dataset card you publish.

## Configs

| config | entity | anchor |
| --- | --- | --- |
| `artists` | artist | `musicbrainz_id` |
| `releases` | release | `musicbrainz_id` |
| `recordings` | recording | `musicbrainz_id` |
| `labels` | label | `musicbrainz_id` |
| `release_groups` | release-group | `musicbrainz_id` |
| `works` | work | `musicbrainz_id` |

## Two sources

Each config can be filled from either path:

```python
from pymusicbrainz import dataset

# API path (rate-limited search/browse, no key): focused, current data
dataset.rows("artists", query="nirvana", limit=100)
dataset.rows("release_groups", artist="<mbid>", limit=100)   # browse link

# dump path: the whole-corpus backbone (streaming .tar.bz2)
dataset.rows("artists", source="dump", limit=100)
dataset.rows("recordings", source="dump", path="/data/mbdump.tar.bz2")
```

## Export to JSON Lines

```python
dataset.export_jsonl("artists", "artists.jsonl", query="nirvana", limit=1000)
dataset.export_jsonl("recordings", "recordings.jsonl", source="dump", limit=5000)
dataset.export_all("mb_dataset", source="dump", limit=1000)   # all six configs
```

`export_jsonl` streams end to end, from request or dump, through model and extra, to
JSON line. Pass `limit=N` to cap the number of rows.

## Building a `datasets.DatasetDict`

```python
from datasets import Dataset, DatasetDict
from pymusicbrainz import dataset
dd = DatasetDict({
    cfg: Dataset.from_generator(
        lambda c=cfg: dataset.rows(c, source="dump", limit=10000)
    )
    for cfg in ("artists", "labels")
})
```

---
[← IDs](ids.md) · [Home](README.md)
