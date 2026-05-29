"""Search the artist index with a free-text / Lucene query."""
import pymusicbrainz as mb

mb.set_user_agent("pymusicbrainz-example/0.0.1 ( me@example.com )")

res = mb.search("artist", "nirvana", limit=5)
print(f"{res.count} total matches; showing {len(res)}")
for hit in res:
    extra = f" ({hit.disambiguation})" if hit.disambiguation else ""
    print(f"  {hit.mbid}  {hit.name}{extra}")
