"""Small normalisation helpers for MusicBrainz data."""
from __future__ import annotations

import re
import unicodedata
from typing import Optional

# An MBID is a lowercase UUID.
_MBID_RE = re.compile(
    r"[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-"
    r"[0-9a-fA-F]{4}-[0-9a-fA-F]{12}"
)


def clean(text: Optional[str]) -> str:
    """NFKC-normalise, collapse whitespace, strip."""
    if not text:
        return ""
    text = unicodedata.normalize("NFKC", str(text))
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def clean_or_none(text: Optional[str]) -> Optional[str]:
    """Like :func:`clean` but returns ``None`` for empty / placeholder values."""
    val = clean(text)
    if not val or val.lower() in ("none", "n/a", "-", "\\n"):
        return None
    return val


def to_int(value: object) -> Optional[int]:
    """Parse an int, treating the PostgreSQL ``\\N`` sentinel and junk as None."""
    if value is None:
        return None
    s = str(value).strip()
    if not s or s == "\\N":
        return None
    try:
        return int(s)
    except ValueError:
        m = re.search(r"-?\d+", s)
        return int(m.group()) if m else None


def tsv_value(value: object) -> Optional[str]:
    """Decode one Postgres COPY cell: ``\\N`` → ``None``, else the string.

    MusicBrainz dump TSV uses ``\\N`` for NULL and escapes tabs/newlines as
    ``\\t``/``\\n``; this unescapes the common ones.
    """
    if value is None:
        return None
    s = str(value)
    if s == "\\N" or s == "":
        return None
    return (
        s.replace("\\t", "\t")
        .replace("\\n", "\n")
        .replace("\\r", "\r")
        .replace("\\\\", "\\")
    )


def is_mbid(value: Optional[str]) -> bool:
    """True if *value* is exactly an MBID (UUID)."""
    if not value:
        return False
    return bool(_MBID_RE.fullmatch(value.strip()))


def extract_mbid(value: Optional[str]) -> Optional[str]:
    """Pull the first MBID (UUID) out of *value* (e.g. a MusicBrainz URL)."""
    if not value:
        return None
    m = _MBID_RE.search(value)
    return m.group(0).lower() if m else None
