# Quickstart

```bash
pip install -e .
```

MusicBrainz requires every client to send a descriptive `User-Agent` and to make at
most one request per second. The client handles both, but set your own
identification:

```python
import pymusicbrainz as mb

mb.set_user_agent("myapp/1.0 ( me@example.com )")
```

## Look up by MBID

```python
artist = mb.get_artist("5b11f4ce-a62d-471e-81fc-a69a8278c7da")
print(artist.name, artist.type, artist.country)     # Nirvana Group US
print(artist.begin_date, "->", artist.end_date)     # 1987 -> 1994-04-05
```

`get_release`, `get_recording`, `get_release_group`, `get_label`, and `get_work` work
the same way. You can also use the generic form:

```python
work = mb.lookup("work", "<mbid>")
```

## Search

```python
res = mb.search("artist", "nirvana", limit=5)
print(res.count)                       # total matches on the server
for hit in res:
    print(hit.mbid, hit.name)
```

## Browse linked entities

```python
for rg in mb.iter_browse("release-group", artist=artist.mbid, max_results=20):
    print(rg.title, rg.first_release_date)
```

## Rate limiting

The default throttle is 1.1 seconds between requests. Do not set it below 1.0 second
against the live web service:

```python
mb.set_delay(1.0)    # the floor for the live service
```

For the whole-corpus path, which has no per-request limit, see
[bulk-dumps.md](bulk-dumps.md).

---
[Home](README.md) · [Web service →](webservice.md)
