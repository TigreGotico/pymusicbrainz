def test_import_and_version():
    import pymusicbrainz

    assert pymusicbrainz.__version__ == "0.0.1"
    for name in (
        "lookup", "search", "browse", "get_artist",
        "stream_artists", "download", "to_extra", "dataset",
    ):
        assert hasattr(pymusicbrainz, name), name


def test_entity_types():
    from pymusicbrainz.models import EntityType, model_for

    assert {e.value for e in EntityType} == {
        "artist", "release", "recording", "release-group", "label", "work",
    }
    for et in EntityType:
        assert model_for(et) is not None
