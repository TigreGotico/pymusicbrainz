# AGENTS.md — pymusicbrainz

Python metadata client for MusicBrainz. Two no-key paths: the web service
(`musicbrainz.org/ws/2`, JSON, descriptive User-Agent + 1 req/sec) and the full
data dumps (`data.metabrainz.org/.../fullexport`, streaming `.tar.bz2`). Every
entity is MBID-anchored; `pymusicbrainz.ids` emits the canonical
`musicbrainz_id` for metadatarr.

## Setup

```bash
pip install -e .
pip install -e ".[stealth]"   # adds curl-cffi transport
pip install -e ".[test]"      # adds pytest
```

Pure-Python, Python >= 3.8. Hard deps: `requests`, `unblock_requests`.

## Test

```bash
pytest -m "not live"   # offline; API tests use a fake injected session, bulk tests use a fixture .tar.bz2
pytest -m live         # one live smoke: artist lookup by MBID + a search
```

Offline tests need no network. `tests/conftest.py` provides a `fake_session`
fixture (canned JSON) and a `fixtures` path. The bulk fixture is
`tests/fixtures/mbdump.sample.tar.bz2` — a tiny POSIX tar of `mbdump/<table>`
TSV members exercising the exact bz2 → tar → row pipeline.

## Layout

- `pymusicbrainz/__init__.py` — public API; re-exports models, entity, bulk,
  ids, dataset, transport.
- `pymusicbrainz/transport.py` — single shared HTTP session. `set_user_agent`
  (MusicBrainz mandates a descriptive UA), `set_delay` (>= 1 s throttle; default
  1.1 s), `get_json` (web service), `get` (raw, for streaming dumps). Prefers
  `unblock_requests.CloudflareSession`, falls back to curl-cffi then requests.
- `pymusicbrainz/models.py` — `Artist`, `Release`, `Recording`, `ReleaseGroup`,
  `Label`, `Work`, `SearchResult`, `EntityType`. Each model: `to_dict` +
  `from_api(data)`.
- `pymusicbrainz/entity.py` — `lookup` / `search` / `browse` (+ `iter_search`,
  `iter_browse`) over the web service, plus `get_<entity>` shortcuts.
- `pymusicbrainz/bulk.py` — streaming dump parser. `stream_rows` and typed
  `stream_<entity>`; `download`, `latest_snapshot`, `archive_url`. Streams
  bz2 → tar (`r|`) → line, never loading a table whole; `limit=`, `url=`, `path=`.
- `pymusicbrainz/ids.py` — `to_extra` / `<entity>_to_extra` / `canonical_mbid`:
  bridge a model into the metadatarr `ExternalIds.extra` dict, anchored on
  `musicbrainz_id` (keys namespaced `musicbrainz_`).
- `pymusicbrainz/dataset.py` — HF-style configs (one per entity) over the API
  (`query=`/browse link) or dumps (`source="dump"`); `rows`, `export_jsonl`,
  `export_all`.
- `pymusicbrainz/_clean.py` — internal string/number/TSV helpers.
- `examples/` — runnable one-call scripts; `docs/` — usage docs.

## Conventions (org hard rules)

- Branches: work on `dev`, stable on `master`. Never `main`. `dev` is the
  GitHub default branch.
- Never edit `pymusicbrainz/version.py`; gh-automations bumps semver from
  conventional-commit prefixes.
- New repos are private by default.
- Commit identity: JarbasAi <jarbasai@mailfence.com>.
- No Neon / `neon-*` references. No meta-commentary in code/docs/commits/PRs.

## Gotchas

- The web service rejects clients without a descriptive `User-Agent` and caps
  at one request per second; do not set `set_delay` below 1.0 against the live
  service or you risk HTTP 503.
- The dump tar is read in streaming mode (`r|`), whose members are
  non-seekable — `bulk._iter_member_lines` reads raw bytes and splits on
  newlines rather than wrapping in `TextIOWrapper`.
- `mbdump.tar.bz2` is multi-GB; reaching a deep member by streaming the whole
  archive is slow by nature. For one-off lookups prefer the web service; use
  the dumps for whole-corpus passes.
- Dump TSV column order is header-less (PostgreSQL `COPY`) and declared in
  `bulk.COLUMNS`; if the upstream schema changes, update it there.
- Transport state (`_min_delay`, `_user_agent`, shared `_session`) is
  process-global; `set_*`/`reset_session` mutate module globals.

## CI

No `.github/workflows/` yet — see `TODO.md`. When added, wire to the
`OpenVoiceOS/gh-automations` reusable workflows referenced at `@dev`.
