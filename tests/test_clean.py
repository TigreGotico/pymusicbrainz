from pymusicbrainz._clean import (
    clean,
    clean_or_none,
    extract_mbid,
    is_mbid,
    to_int,
    tsv_value,
)


def test_clean_normalises_whitespace_and_unicode():
    assert clean("  Nirvana   Band  ") == "Nirvana Band"
    assert clean(None) == ""
    assert clean("") == ""


def test_clean_or_none_treats_placeholders_as_missing():
    assert clean_or_none(None) is None
    assert clean_or_none("") is None
    assert clean_or_none("  ") is None
    assert clean_or_none("N/A") is None
    assert clean_or_none("-") is None
    assert clean_or_none("\\N") is None
    assert clean_or_none("Nirvana") == "Nirvana"


def test_to_int_handles_null_sentinel_and_junk():
    assert to_int(None) is None
    assert to_int("\\N") is None
    assert to_int("") is None
    assert to_int("42") == 42
    assert to_int(7) == 7
    # junk with an embedded number falls back to a regex extraction
    assert to_int("42 (approx)") == 42
    assert to_int("no digits here") is None


def test_tsv_value_null_and_empty():
    assert tsv_value(None) is None
    assert tsv_value("\\N") is None
    assert tsv_value("") is None


def test_tsv_value_unescapes_tab_newline_carriage_return():
    assert tsv_value("a\\tb") == "a\tb"
    assert tsv_value("a\\nb") == "a\nb"
    assert tsv_value("a\\rb") == "a\rb"


def test_tsv_value_escaped_backslash_before_letter_stays_literal():
    """Regression: a real backslash immediately followed by a literal letter.

    Postgres COPY TEXT format escapes a literal backslash as ``\\\\``. If that
    literal backslash happens to be followed by a plain ``t``/``n``/``r``
    (unescaped, ordinary character), the encoded bytes on the wire are
    ``\\\\`` + ``t`` == three characters: backslash, backslash, t. A correct
    decoder must resolve escapes left-to-right in one pass and must NOT let
    the second backslash of the ``\\\\`` pair combine with the following
    literal ``t`` into a bogus ``\\t`` (tab) escape.
    """
    encoded = "\\\\t"  # backslash, backslash, t
    assert tsv_value(encoded) == "\\t"  # literal backslash + literal 't'


def test_tsv_value_double_backslash_alone():
    assert tsv_value("a\\\\b") == "a\\b"


def test_is_mbid():
    assert is_mbid("5b11f4ce-a62d-471e-81fc-a69a8278c7da") is True
    assert is_mbid(" 5b11f4ce-a62d-471e-81fc-a69a8278c7da ") is True
    assert is_mbid("not-an-mbid") is False
    assert is_mbid(None) is False
    assert is_mbid("") is False


def test_extract_mbid_from_url_and_plain_text():
    mbid = "5b11f4ce-a62d-471e-81fc-a69a8278c7da"
    assert extract_mbid(f"https://musicbrainz.org/artist/{mbid}") == mbid
    assert extract_mbid(f"prefix {mbid} suffix") == mbid
    assert extract_mbid("no id here") is None
    assert extract_mbid(None) is None
