from datetime import UTC, datetime

from fedcourtsai import ids


def test_slugify_is_filesystem_safe() -> None:
    assert ids.slugify("Motion to Stay (pending appeal)") == "motion-to-stay-pending-appeal"
    assert ids.slugify("  ") == "x"


def test_case_id() -> None:
    assert ids.case_id("ca9", 64512345) == "ca9/64512345"


def test_run_id_format() -> None:
    rid = ids.run_id(datetime(2026, 6, 24, 10, 30, 0, tzinfo=UTC))
    assert rid == "20260624T103000Z"
