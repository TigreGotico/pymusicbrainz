from pymusicbrainz import bulk


def test_stream_artists_fixture(fixtures):
    path = fixtures / "mbdump.sample.tar.bz2"
    artists = list(bulk.stream_artists(path=path))
    assert len(artists) == 2
    nirvana = artists[0]
    assert nirvana.mbid == "5b11f4ce-a62d-471e-81fc-a69a8278c7da"
    assert nirvana.name == "Nirvana"
    assert nirvana.begin_date == "1987"
    assert nirvana.end_date == "1994"


def test_stream_limit(fixtures):
    path = fixtures / "mbdump.sample.tar.bz2"
    assert len(list(bulk.stream_artists(path=path, limit=1))) == 1


def test_stream_releases(fixtures):
    path = fixtures / "mbdump.sample.tar.bz2"
    rels = list(bulk.stream_releases(path=path))
    assert rels[0].mbid == "b84ee12a-09ef-421b-82de-0441a926375b"
    assert rels[0].title == "Nevermind"
    assert rels[0].barcode == "720642442526"


def test_stream_recordings(fixtures):
    path = fixtures / "mbdump.sample.tar.bz2"
    recs = list(bulk.stream_recordings(path=path))
    assert recs[0].title == "Smells Like Teen Spirit"
    assert recs[0].length_ms == 301000
    assert recs[0].length_str == "5:01"


def test_stream_labels(fixtures):
    path = fixtures / "mbdump.sample.tar.bz2"
    labels = list(bulk.stream_labels(path=path))
    assert labels[0].name == "DGC"
    assert labels[0].mbid == "46f0f4cd-8aab-4b33-b698-f459faf64190"


def test_unknown_table():
    try:
        list(bulk.stream_rows("nope", path="x"))
        assert False
    except ValueError:
        pass


def test_archive_url_shape():
    url = bulk.archive_url(snapshot="20260527-002102")
    assert url.endswith("/20260527-002102/mbdump.tar.bz2")
    assert str(bulk.local_path("20260527-002102")).endswith(
        "20260527-002102-mbdump.tar.bz2"
    )
