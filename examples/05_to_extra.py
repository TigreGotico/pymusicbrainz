"""Flatten an entity into a flat dict of namespaced external IDs.

Every dict is anchored on ``musicbrainz_id`` (the MBID) — the canonical music
cross-reference key.
"""
import json

import pymusicbrainz as mb

mb.set_user_agent("pymusicbrainz-example/0.0.1 ( me@example.com )")

artist = mb.get_artist("5b11f4ce-a62d-471e-81fc-a69a8278c7da")
print(json.dumps(mb.to_extra(artist), indent=2, ensure_ascii=False))
print("canonical:", mb.canonical_mbid(artist.url))
