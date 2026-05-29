"""Stream-parse the MusicBrainz full data dumps — the bulk path.

The full export at ``data.metabrainz.org/.../fullexport`` ships large
``.tar.bz2`` archives of PostgreSQL ``COPY`` tables (tab-separated, ``\\N`` for
NULL). ``mbdump.tar.bz2`` alone is several GB and the uncompressed ``artist``,
``release`` and ``recording`` tables have tens of millions of rows, so every
function here **streams**: bz2 is decompressed on the fly, the tar member is
read line by line, and rows are yielded one dict at a time. Nothing loads a
whole table — let alone a whole archive — into memory.

Each TSV table has a fixed, header-less column order (PostgreSQL ``COPY``), so
the column names are declared here per table (``COLUMNS``).

Files are cached on disk (``~/.cache/pymusicbrainz`` by default, override with
``PYMUSICBRAINZ_CACHE_DIR``) and fetched on demand. Pass ``limit=N`` to sample
a table without reading it whole, or ``url=``/``path=`` to point at a specific
archive.

PROVENANCE: MusicBrainz core data is in the public domain (CC0); derived tables
are CC-BY-NC-SA. See ``PROVENANCE.md`` and ``docs/dataset.md``.
"""
from __future__ import annotations

import bz2
import os
import tarfile
from pathlib import Path
from typing import Any, Dict, Iterator, List, Optional

from pymusicbrainz import transport

# The canonical archive holding the core tables we stream.
CORE_ARCHIVE = "mbdump.tar.bz2"

# Column order of the core tables inside the dump (PostgreSQL COPY, no header).
# These follow the public MusicBrainz schema; only the leading columns each
# table is keyed/typed on are needed downstream.
COLUMNS: Dict[str, List[str]] = {
    "artist": [
        "id", "gid", "name", "sort_name", "begin_date_year", "begin_date_month",
        "begin_date_day", "end_date_year", "end_date_month", "end_date_day",
        "type", "area", "gender", "comment", "edits_pending", "last_updated",
        "ended", "begin_area", "end_area",
    ],
    "release": [
        "id", "gid", "name", "artist_credit", "release_group", "status",
        "packaging", "language", "script", "barcode", "comment", "edits_pending",
        "quality", "last_updated",
    ],
    "release_group": [
        "id", "gid", "name", "artist_credit", "type", "comment",
        "edits_pending", "last_updated",
    ],
    "recording": [
        "id", "gid", "name", "artist_credit", "length", "comment",
        "edits_pending", "last_updated", "video",
    ],
    "label": [
        "id", "gid", "name", "sort_name", "begin_date_year", "begin_date_month",
        "begin_date_day", "end_date_year", "end_date_month", "end_date_day",
        "label_code", "type", "area", "comment", "edits_pending", "last_updated",
        "ended",
    ],
    "work": [
        "id", "gid", "name", "type", "comment", "edits_pending", "last_updated",
        "language",
    ],
}

# Path of each table inside the tar archive.
MEMBER = {table: f"mbdump/{table}" for table in COLUMNS}


def cache_dir() -> Path:
    """Resolve the on-disk cache dir (``PYMUSICBRAINZ_CACHE_DIR`` or default)."""
    env = os.environ.get("PYMUSICBRAINZ_CACHE_DIR")
    base = Path(env) if env else Path.home() / ".cache" / "pymusicbrainz"
    base.mkdir(parents=True, exist_ok=True)
    return base


def latest_snapshot() -> str:
    """Return the latest full-export snapshot id (e.g. ``20260527-002102``)."""
    resp = transport.get(f"{transport.DUMP_BASE}/LATEST")
    return resp.text.strip()


def archive_url(snapshot: Optional[str] = None, archive: str = CORE_ARCHIVE) -> str:
    """Full download URL for an archive in a snapshot (default: latest)."""
    snap = snapshot or latest_snapshot()
    return f"{transport.DUMP_BASE}/{snap}/{archive}"


def local_path(snapshot: str, archive: str = CORE_ARCHIVE) -> Path:
    """Cache path for an archive in a snapshot."""
    return cache_dir() / f"{snapshot}-{archive}"


def download(
    snapshot: Optional[str] = None,
    archive: str = CORE_ARCHIVE,
    *,
    force: bool = False,
    chunk: int = 1 << 20,
) -> Path:
    """Fetch an archive to the cache (idempotent unless *force*).

    Streams to disk in *chunk*-byte blocks — the compressed file is never held
    in memory. Returns the local ``.tar.bz2`` path.
    """
    snap = snapshot or latest_snapshot()
    path = local_path(snap, archive)
    if path.exists() and not force and path.stat().st_size > 0:
        return path
    resp = transport.get(archive_url(snap, archive), stream=True)
    tmp = path.with_suffix(path.suffix + ".part")
    with open(tmp, "wb") as fh:
        for block in resp.iter_content(chunk_size=chunk):
            if block:
                fh.write(block)
    tmp.replace(path)
    return path


def _parse_line(line: str, columns: List[str]) -> Dict[str, Any]:
    from pymusicbrainz._clean import tsv_value

    parts = line.rstrip("\n").split("\t")
    row: Dict[str, Any] = {}
    for i, col in enumerate(columns):
        row[col] = tsv_value(parts[i]) if i < len(parts) else None
    return row


def _iter_member_lines(fileobj) -> Iterator[str]:
    """Yield decoded lines from a tar member file object, streaming.

    The member comes from a non-seekable streaming tar (``r|``), so a
    ``TextIOWrapper`` can't be used — read raw bytes and split on newlines,
    buffering only one logical line at a time.
    """
    buf = b""
    while True:
        chunk = fileobj.read(1 << 16)
        if not chunk:
            break
        buf += chunk
        while True:
            nl = buf.find(b"\n")
            if nl < 0:
                break
            line = buf[: nl + 1]
            buf = buf[nl + 1:]
            yield line.decode("utf-8", "replace")
    if buf:
        yield buf.decode("utf-8", "replace")


def stream_rows(
    table: str,
    *,
    limit: Optional[int] = None,
    snapshot: Optional[str] = None,
    archive: str = CORE_ARCHIVE,
    download_if_missing: bool = True,
    path: Optional[Path] = None,
    url: Optional[str] = None,
) -> Iterator[Dict[str, Any]]:
    """Yield raw row dicts (keyed by :data:`COLUMNS`) from a dump table.

    Streams bz2 → tar member → TSV one row at a time, never materialising the
    table. Source resolution order:

    - *url*: stream the archive directly over HTTP (no full download to disk);
    - *path*: read a specific local ``.tar.bz2`` (e.g. a test fixture);
    - otherwise the cached snapshot archive (downloaded on demand).

    ``limit`` caps the rows yielded — ideal for smoke tests and sampling.
    """
    if table not in COLUMNS:
        raise ValueError(f"unknown table {table!r}; choose from {sorted(COLUMNS)}")
    columns = COLUMNS[table]
    member = MEMBER[table]

    if url is not None:
        resp = transport.get(url, stream=True)
        raw = resp.raw
        raw.decode_content = True
        fileobj = bz2.BZ2File(raw)
        yield from _stream_tar(fileobj, member, columns, limit)
        return

    if path is None:
        path = local_path(snapshot or latest_snapshot(), archive)
        if not path.exists() or path.stat().st_size == 0:
            if not download_if_missing:
                raise FileNotFoundError(
                    f"{path} not cached; call download(...) first "
                    f"or pass download_if_missing=True"
                )
            download(snapshot, archive)

    with bz2.open(path, "rb") as fileobj:
        yield from _stream_tar(fileobj, member, columns, limit)


def _stream_tar(fileobj, member: str, columns: List[str], limit: Optional[int]):
    """Walk a (decompressed) tar stream, yielding rows from one member."""
    tar = tarfile.open(fileobj=fileobj, mode="r|")
    try:
        for info in tar:
            if info.name != member or not info.isfile():
                continue
            extracted = tar.extractfile(info)
            if extracted is None:
                return
            count = 0
            for line in _iter_member_lines(extracted):
                if not line.strip():
                    continue
                if limit is not None and count >= limit:
                    return
                yield _parse_line(line, columns)
                count += 1
            return
    finally:
        tar.close()


# ---- typed-row mappers -------------------------------------------------

def row_to_artist(row: Dict[str, Any]):
    from pymusicbrainz._clean import clean_or_none
    from pymusicbrainz.models import Artist

    return Artist(
        mbid=row.get("gid") or "",
        name=clean_or_none(row.get("name")),
        sort_name=clean_or_none(row.get("sort_name")),
        begin_date=_date(row, "begin"),
        end_date=_date(row, "end"),
    )


def row_to_release_group(row: Dict[str, Any]):
    from pymusicbrainz._clean import clean_or_none
    from pymusicbrainz.models import ReleaseGroup

    return ReleaseGroup(
        mbid=row.get("gid") or "",
        title=clean_or_none(row.get("name")),
    )


def row_to_release(row: Dict[str, Any]):
    from pymusicbrainz._clean import clean_or_none
    from pymusicbrainz.models import Release

    return Release(
        mbid=row.get("gid") or "",
        title=clean_or_none(row.get("name")),
        barcode=clean_or_none(row.get("barcode")),
    )


def row_to_recording(row: Dict[str, Any]):
    from pymusicbrainz._clean import clean_or_none, to_int
    from pymusicbrainz.models import Recording

    return Recording(
        mbid=row.get("gid") or "",
        title=clean_or_none(row.get("name")),
        length_ms=to_int(row.get("length")),
    )


def row_to_label(row: Dict[str, Any]):
    from pymusicbrainz._clean import clean_or_none, to_int
    from pymusicbrainz.models import Label

    return Label(
        mbid=row.get("gid") or "",
        name=clean_or_none(row.get("name")),
        sort_name=clean_or_none(row.get("sort_name")),
        label_code=to_int(row.get("label_code")),
    )


def row_to_work(row: Dict[str, Any]):
    from pymusicbrainz._clean import clean_or_none
    from pymusicbrainz.models import Work

    return Work(
        mbid=row.get("gid") or "",
        title=clean_or_none(row.get("name")),
    )


def _date(row: Dict[str, Any], prefix: str) -> Optional[str]:
    from pymusicbrainz._clean import to_int

    y = to_int(row.get(f"{prefix}_date_year"))
    if y is None:
        return None
    m = to_int(row.get(f"{prefix}_date_month"))
    d = to_int(row.get(f"{prefix}_date_day"))
    out = f"{y:04d}"
    if m:
        out += f"-{m:02d}"
        if d:
            out += f"-{d:02d}"
    return out


# ---- typed streams -----------------------------------------------------

def stream_artists(**kw: Any) -> Iterator[Any]:
    for row in stream_rows("artist", **kw):
        yield row_to_artist(row)


def stream_release_groups(**kw: Any) -> Iterator[Any]:
    for row in stream_rows("release_group", **kw):
        yield row_to_release_group(row)


def stream_releases(**kw: Any) -> Iterator[Any]:
    for row in stream_rows("release", **kw):
        yield row_to_release(row)


def stream_recordings(**kw: Any) -> Iterator[Any]:
    for row in stream_rows("recording", **kw):
        yield row_to_recording(row)


def stream_labels(**kw: Any) -> Iterator[Any]:
    for row in stream_rows("label", **kw):
        yield row_to_label(row)


def stream_works(**kw: Any) -> Iterator[Any]:
    for row in stream_rows("work", **kw):
        yield row_to_work(row)
