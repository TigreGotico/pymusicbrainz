# Provenance & licensing

`pymusicbrainz` reads structured music metadata from MusicBrainz through two
sources. Their terms differ — know which path produced your data.

## Web service — no key, rate-limited

`https://musicbrainz.org/ws/2/<entity>?fmt=json` — the public XML/JSON web
service. No API key. MusicBrainz requires two things of every client, both
enforced by `pymusicbrainz.transport`:

- A **descriptive `User-Agent`** identifying the application and a contact
  (URL or email). Override with `pymusicbrainz.set_user_agent(...)`.
- A hard **one request per second** rate limit. The default throttle is 1.1 s;
  do not lower it below 1.0 s against the live service (HTTP 503 otherwise).

See <https://musicbrainz.org/doc/MusicBrainz_API> and
<https://musicbrainz.org/doc/MusicBrainz_API/Rate_Limiting>.

## Full data dumps — the bulk backbone

`https://data.metabrainz.org/pub/musicbrainz/data/fullexport/` — `.tar.bz2`
archives of the PostgreSQL `COPY` tables, refreshed regularly. `LATEST` names
the current snapshot. `mbdump.tar.bz2` holds the core tables this client
streams (`artist`, `release`, `recording`, `release-group`, `label`, `work`).

The dumps are **large** (multi-GB compressed). `pymusicbrainz.bulk` streams
them member-by-member and row-by-row — it never loads a whole table, let alone
a whole archive, into memory.

## Data licensing

- **Core data** (the tables this client reads — artists, releases, recordings,
  release groups, labels, works) is released into the **public domain (CC0)**.
- **Derived / supplementary data** (e.g. cover-art links, some annotations) is
  **CC-BY-NC-SA 3.0**.

See <https://musicbrainz.org/doc/About/Data_License>. When redistributing data
or a dataset built from MusicBrainz, carry the appropriate licence and
attribution per the page above.

## Scope

`pymusicbrainz` reads **structured metadata only** (MBIDs, names, titles,
dates, codes, credits) for cataloguing and dataset building. It does not fetch,
host, or redistribute audio.
