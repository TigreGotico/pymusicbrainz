"""Stream the first N artists from the full data dump (memory-safe).

The full export is several GB compressed; this never loads a whole table into
memory. ``limit`` caps the rows read. The archive is cached under
``~/.cache/pymusicbrainz`` (override with ``PYMUSICBRAINZ_CACHE_DIR``).
"""
import pymusicbrainz as mb

for artist in mb.stream_artists(limit=20):
    print(artist.mbid, "|", artist.name, "|", artist.begin_date or "")
