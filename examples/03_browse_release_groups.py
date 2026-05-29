"""Browse the release groups (albums/singles/EPs) linked to an artist."""
import pymusicbrainz as mb

mb.set_user_agent("pymusicbrainz-example/0.0.1 ( me@example.com )")

ARTIST = "5b11f4ce-a62d-471e-81fc-a69a8278c7da"  # Nirvana
for rg in mb.iter_browse("release-group", artist=ARTIST, max_results=25):
    kind = rg.primary_type or "?"
    print(f"  [{kind:7}] {rg.first_release_date or '????'}  {rg.title}")
