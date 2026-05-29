"""Export an HF-style dataset config from the dump path (streaming).

Reads the full data dump and flattens the first N rows into JSON Lines, never
materialising a whole table. Use ``source="dump"`` and ``limit=`` to sample.
"""
from pymusicbrainz import dataset

n = dataset.export_jsonl("artists", "artists_dump.jsonl", source="dump", limit=100)
print(f"wrote {n} rows to artists_dump.jsonl")
