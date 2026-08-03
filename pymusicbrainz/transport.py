"""HTTP transport for MusicBrainz — the dataset backbone.

Two live data paths share one transport layer:

- the **web service** (``musicbrainz.org/ws/2``) — JSON over HTTP, no API key.
  MusicBrainz requires a *descriptive* ``User-Agent`` and enforces a hard
  **one request per second** rate limit per client. Both are honoured here: a
  ``>= 1 s`` throttle is the default, and the user agent identifies the app and
  a contact address. See <https://musicbrainz.org/doc/MusicBrainz_API>.
- the **full data dumps** (``data.metabrainz.org/.../fullexport``) — the bulk
  path; large ``.tar.bz2`` archives of PostgreSQL ``COPY`` TSV tables, streamed
  member-by-member by :mod:`pymusicbrainz.bulk`.

The session is an :class:`unblock_requests.CloudflareSession` when that package
is installed (resilient transport with Wayback fallback), falling back to
``curl_cffi`` and then plain ``requests``.
Environment knobs use the ``PYMUSICBRAINZ`` prefix.
"""
from __future__ import annotations

import time
from typing import Any, Dict, Optional

WS_BASE = "https://musicbrainz.org/ws/2"
DUMP_BASE = "https://data.metabrainz.org/pub/musicbrainz/data/fullexport"

ENV_PREFIX = "PYMUSICBRAINZ"

# MusicBrainz mandates a descriptive User-Agent identifying the application and
# a way to contact the author. Override with set_user_agent().
_user_agent = (
    "pymusicbrainz/0.0.1 ( https://github.com/LeMetadatarr/pymusicbrainz ; "
    "jarbasai@mailfence.com )"
)

_HEADERS = {
    "User-Agent": _user_agent,
    "Accept": "application/json",
}

_session: Optional[Any] = None
_last_request: float = 0.0
# The web service is capped at 1 req/sec; default to a polite >= 1 s throttle.
_min_delay: float = 1.1


def set_user_agent(user_agent: str) -> None:
    """Set the descriptive ``User-Agent`` MusicBrainz requires.

    Should identify your application/version and a contact (URL or email), e.g.
    ``"myapp/1.0 ( me@example.com )"``. Resets the session so the new header
    takes effect.
    """
    global _user_agent
    _user_agent = user_agent.strip() or _user_agent
    _HEADERS["User-Agent"] = _user_agent
    reset_session()


def set_delay(seconds: float) -> None:
    """Set the minimum delay between web-service requests (default 1.1 s).

    MusicBrainz enforces one request per second; do not set this below 1.0 for
    the live web service or you risk HTTP 503 rate-limit errors.
    """
    global _min_delay
    _min_delay = max(0.0, seconds)


def _make_session() -> Any:
    try:
        from unblock_requests import CloudflareSession

        session = CloudflareSession(env_prefix=ENV_PREFIX, wayback_fallback=True)
        session.headers.update(_HEADERS)
        return session
    except ImportError:
        pass

    try:
        import curl_cffi.requests as cffi_requests  # type: ignore
        from curl_cffi import BrowserType

        supported = {e.value for e in BrowserType}
        for candidate in ("firefox120", "firefox135", "chrome124", "chrome136"):
            if candidate in supported:
                impersonate = candidate
                break
        else:
            impersonate = next(iter(supported))
        session = cffi_requests.Session(impersonate=impersonate)
        session.headers.update(_HEADERS)
        return session
    except ImportError:
        import requests

        session = requests.Session()
        session.headers.update(_HEADERS)
        return session


def get_session() -> Any:
    global _session
    if _session is None:
        _session = _make_session()
    return _session


def set_session(session: Any) -> None:
    """Inject a custom session (tests, custom transports)."""
    global _session
    _session = session


def reset_session() -> None:
    global _session
    _session = None


def _throttle() -> None:
    global _last_request
    elapsed = time.time() - _last_request
    if elapsed < _min_delay:
        time.sleep(_min_delay - elapsed)
    _last_request = time.time()


def get(url: str, **kwargs: Any) -> Any:
    """Throttled GET returning the raw response object."""
    _throttle()
    kwargs.setdefault("timeout", 30)
    resp = get_session().get(url, **kwargs)
    resp.raise_for_status()
    return resp


def get_json(path: str, params: Optional[Dict[str, Any]] = None) -> Any:
    """GET a web-service endpoint under ``/ws/2`` and decode the JSON body.

    Args:
        path: API path relative to ``/ws/2`` (e.g. ``"artist/<mbid>"`` or
            ``"release-group"``). An absolute URL is used verbatim.
        params: Query parameters; ``fmt=json`` is added automatically.

    Returns:
        The decoded JSON body (``dict``).
    """
    query: Dict[str, Any] = dict(params or {})
    query.setdefault("fmt", "json")
    url = path if path.startswith("http") else f"{WS_BASE}/{path.lstrip('/')}"
    return get(url, params=query).json()
