import json

from pymusicbrainz import dataset


def test_configs():
    assert set(dataset.CONFIGS) == {
        "artists", "releases", "recordings", "labels",
        "release_groups", "works",
    }


def test_rows_unknown_config():
    try:
        list(dataset.rows("nope"))
        assert False
    except ValueError:
        pass


def test_rows_from_dump(fixtures):
    path = fixtures / "mbdump.sample.tar.bz2"
    rows = list(dataset.rows("artists", source="dump", path=path))
    assert rows[0]["musicbrainz_id"] == "5b11f4ce-a62d-471e-81fc-a69a8278c7da"
    assert rows[0]["musicbrainz_artist_id"] == rows[0]["musicbrainz_id"]
    assert rows[0]["musicbrainz_name"] == "Nirvana"


def test_export_jsonl_from_dump(tmp_path, fixtures):
    path = fixtures / "mbdump.sample.tar.bz2"
    out = tmp_path / "artists.jsonl"
    n = dataset.export_jsonl("artists", str(out), source="dump", path=path)
    assert n == 2
    lines = out.read_text().splitlines()
    first = json.loads(lines[0])
    assert first["musicbrainz_id"] == "5b11f4ce-a62d-471e-81fc-a69a8278c7da"


def test_rows_api_search(fake_session):
    fake_session({"artist": "artist_search.json"})
    rows = list(dataset.rows("artists", query="nirvana", limit=2))
    assert rows[0]["musicbrainz_id"].startswith("5b11f4ce")
    assert rows[0]["musicbrainz_name"] == "Nirvana"
