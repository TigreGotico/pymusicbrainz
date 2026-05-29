from pymusicbrainz import entity
from pymusicbrainz.models import Artist, EntityType


def test_lookup_artist(fake_session):
    s = fake_session({"artist/5b11f4ce": "artist_lookup.json"})
    art = entity.get_artist("5b11f4ce-a62d-471e-81fc-a69a8278c7da")
    assert isinstance(art, Artist)
    assert art.mbid == "5b11f4ce-a62d-471e-81fc-a69a8278c7da"
    assert art.name == "Nirvana"
    assert art.type == "Group"
    assert art.country == "US"
    assert art.begin_date == "1987"
    assert art.end_date == "1994-04-05"
    assert art.isnis == ["0000000123486830"]
    # fmt=json was added automatically
    _, params = s.calls[-1]
    assert params["fmt"] == "json"


def test_search_artist(fake_session):
    fake_session({"artist": "artist_search.json"})
    res = entity.search(EntityType.ARTIST, "nirvana", limit=2)
    assert len(res) == 2
    assert res.count == 93
    assert res.entities[0].name == "Nirvana"
    assert res.entities[0].mbid.startswith("5b11f4ce")
    assert res.has_more is True


def test_search_empty_query_no_request(fake_session):
    fake_session({"artist": "artist_search.json"})
    res = entity.search("artist", "  ")
    assert len(res) == 0


def test_browse_uses_link_param(fake_session):
    s = fake_session({"release-group": "artist_search.json"})
    # the payload key won't match release-groups, so entities is empty, but the
    # request must carry the artist link param.
    entity.browse("release-group", artist="5b11f4ce-a62d-471e-81fc-a69a8278c7da")
    _, params = s.calls[-1]
    assert params["artist"] == "5b11f4ce-a62d-471e-81fc-a69a8278c7da"
