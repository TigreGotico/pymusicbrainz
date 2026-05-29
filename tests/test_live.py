"""Live smoke test against the MusicBrainz web service (no-key path).

Respects the descriptive User-Agent and the one-request-per-second rate limit
(the default throttle). Skipped automatically when the network is unreachable.
Run explicitly with::

    pytest tests/test_live.py -m live
"""
import pytest

import pymusicbrainz

pytestmark = pytest.mark.live

NIRVANA = "5b11f4ce-a62d-471e-81fc-a69a8278c7da"


def test_live_lookup_artist():
    try:
        art = pymusicbrainz.get_artist(NIRVANA)
    except Exception as e:  # pragma: no cover - network-dependent
        pytest.skip(f"network unavailable: {e}")
    assert art.mbid == NIRVANA
    assert art.name == "Nirvana"


def test_live_search_artist():
    try:
        res = pymusicbrainz.search("artist", "nirvana", limit=3)
    except Exception as e:  # pragma: no cover - network-dependent
        pytest.skip(f"network unavailable: {e}")
    assert len(res), "search returned no hits"
    assert res.entities[0].mbid
