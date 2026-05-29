from pymusicbrainz import ids
from pymusicbrainz.models import Artist, Label, Recording


def test_canonical_mbid_from_string_and_url():
    mbid = "5b11f4ce-a62d-471e-81fc-a69a8278c7da"
    assert ids.canonical_mbid(mbid) == mbid
    assert ids.canonical_mbid(f"https://musicbrainz.org/artist/{mbid}") == mbid
    assert ids.canonical_mbid("not an id") is None


def test_artist_to_extra_anchor():
    art = Artist(
        mbid="5b11f4ce-a62d-471e-81fc-a69a8278c7da",
        name="Nirvana", type="Group", country="US",
        isnis=["0000000123486830"],
    )
    extra = ids.artist_to_extra(art)
    assert extra["musicbrainz_id"] == art.mbid
    assert extra["musicbrainz_artist_id"] == art.mbid
    assert extra["musicbrainz_name"] == "Nirvana"
    assert extra["musicbrainz_artist_type"] == "Group"
    # isni serialised as JSON array
    assert extra["musicbrainz_isni"].startswith("[")


def test_to_extra_dispatch():
    rec = Recording(mbid="af40d6b8-58e8-4ca5-9db8-d4fca0b899e2",
                    title="Smells Like Teen Spirit", length_ms=301000)
    extra = ids.to_extra(rec)
    assert extra["musicbrainz_id"] == rec.mbid
    assert extra["musicbrainz_recording_id"] == rec.mbid
    assert extra["musicbrainz_length_ms"] == "301000"

    lbl = Label(mbid="46f0f4cd-8aab-4b33-b698-f459faf64190", name="DGC")
    assert ids.to_extra(lbl)["musicbrainz_label_id"] == lbl.mbid


def test_entity_key():
    from pymusicbrainz.models import EntityType
    assert ids.entity_key(EntityType.WORK) == "musicbrainz_work_id"
