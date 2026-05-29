"""Resolve the latest full-export snapshot and its core archive URL."""
import pymusicbrainz as mb

snap = mb.latest_snapshot()
print("latest snapshot:", snap)
print("core archive URL:", mb.bulk.archive_url(snap))
print("would cache at:", mb.bulk.local_path(snap))
