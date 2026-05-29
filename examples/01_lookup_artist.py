"""Look up an artist by MBID over the web service (no key, rate-limited)."""
import pymusicbrainz as mb

mb.set_user_agent("pymusicbrainz-example/0.0.1 ( me@example.com )")

artist = mb.get_artist("5b11f4ce-a62d-471e-81fc-a69a8278c7da")
print(artist.name, "|", artist.type, "|", artist.country)
print("active:", artist.begin_date, "->", artist.end_date)
print("ISNI:", artist.isnis)
print(artist.url)
