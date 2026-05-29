"""Export a tiny HF-style dataset config from the API path (search)."""
from pymusicbrainz import dataset, set_user_agent

set_user_agent("pymusicbrainz-example/0.0.1 ( me@example.com )")

n = dataset.export_jsonl("artists", "artists.jsonl", query="nirvana", limit=10)
print(f"wrote {n} rows to artists.jsonl")
