"""Look up a recording and show its formatted length and ISRCs."""
import pymusicbrainz as mb

mb.set_user_agent("pymusicbrainz-example/0.0.1 ( me@example.com )")

rec = mb.get_recording("af40d6b8-58e8-4ca5-9db8-d4fca0b899e2")
print(rec.title)
print("length:", rec.length_str, f"({rec.length_ms} ms)")
print("ISRCs:", rec.isrcs or "—")
print("credit:", ", ".join(rec.artist_credit) or "—")
