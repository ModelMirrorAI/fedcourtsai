"""The Buttondown draft poster, against a fake API: what it writes, and what it refuses."""

from __future__ import annotations

import json
from collections.abc import Callable
from pathlib import Path
from typing import Any

import httpx
import pytest
from typer.testing import CliRunner

from fedcourtsai.buttondown import (
    API_KEY_ENV,
    DRAFT_STATUS,
    ButtondownError,
    make_client,
    post_draft,
    tag_filter,
)
from fedcourtsai.cli import app

from .test_public_update import _base, _event, _forecast, _week_of

runner = CliRunner()

SUBJECT = "FedCourtsAI weekly update: October 5 \N{EN DASH} October 11, 2026"
TAG_ID = "sub_tag_0123456789abcdefghijklmn"


class FakeButtondown:
    """A minimal in-memory Buttondown: tags, emails, and a log of every request."""

    def __init__(
        self,
        *,
        tags: list[dict[str, Any]] | None = None,
        emails: list[dict[str, Any]] | None = None,
        fail_gets: int = 0,
        post_status: int = 201,
        answer_status: str = DRAFT_STATUS,
    ) -> None:
        self.tags = tags if tags is not None else [{"id": TAG_ID, "name": "weekly-scotus"}]
        self.emails = emails or []
        self.fail_gets = fail_gets
        self.post_status = post_status
        self.answer_status = answer_status
        self.requests: list[httpx.Request] = []

    def __call__(self, request: httpx.Request) -> httpx.Response:
        self.requests.append(request)
        if request.method == "GET" and self.fail_gets:
            self.fail_gets -= 1
            return httpx.Response(503)
        path = request.url.path
        if request.method == "GET" and path == "/v1/tags":
            return httpx.Response(200, json={"results": self.tags, "count": len(self.tags)})
        if request.method == "GET" and path == "/v1/emails":
            wanted = request.url.params.get("subject", "")
            hits = [e for e in self.emails if wanted in e["subject"]]
            return httpx.Response(200, json={"results": hits, "count": len(hits)})
        if request.method == "POST" and path == "/v1/emails":
            if self.post_status != 201:
                return httpx.Response(self.post_status, json={"detail": "refused"})
            payload = json.loads(request.content)
            email = {
                **payload,
                "id": "em_new",
                "status": self.answer_status,
                "absolute_url": "https://buttondown.com/fedcourtsai/archive/new",
            }
            self.emails.append(email)
            return httpx.Response(201, json=email)
        return httpx.Response(404)

    def posts(self) -> list[dict[str, Any]]:
        return [json.loads(r.content) for r in self.requests if r.method == "POST"]


def _client(fake: Callable[[httpx.Request], httpx.Response]) -> httpx.Client:
    return make_client("test-key", transport=httpx.MockTransport(fake))


def _no_sleep(_seconds: float) -> None:
    return None


def test_creates_one_draft_addressed_to_the_tag_by_id() -> None:
    fake = FakeButtondown()
    with _client(fake) as client:
        draft = post_draft(
            client, subject=SUBJECT, body="Body.", tag_name="weekly-scotus", sleep=_no_sleep
        )
    assert draft.created
    assert draft.email_id == "em_new"
    (payload,) = fake.posts()
    assert payload["status"] == "draft"
    assert payload["subject"] == SUBJECT
    assert payload["filters"] == tag_filter(TAG_ID)
    assert all(r.headers["Authorization"] == "Token test-key" for r in fake.requests)


def test_a_week_already_drafted_or_sent_is_returned_not_duplicated() -> None:
    for status in ("draft", "sent", "scheduled"):
        fake = FakeButtondown(emails=[{"id": "em_old", "subject": SUBJECT, "status": status}])
        with _client(fake) as client:
            draft = post_draft(
                client, subject=SUBJECT, body="Body.", tag_name="weekly-scotus", sleep=_no_sleep
            )
        assert not draft.created
        assert draft.email_id == "em_old"
        assert draft.status == status
        assert fake.posts() == []


def test_a_subject_that_only_contains_the_weeks_subject_is_not_a_match() -> None:
    fake = FakeButtondown(
        emails=[{"id": "em_x", "subject": SUBJECT + " (copy)", "status": "draft"}]
    )
    with _client(fake) as client:
        draft = post_draft(
            client, subject=SUBJECT, body="Body.", tag_name="weekly-scotus", sleep=_no_sleep
        )
    assert draft.created


def test_a_missing_or_ambiguous_tag_refuses_before_any_write() -> None:
    for tags in ([], [{"id": "a", "name": "weekly-scotus"}, {"id": "b", "name": "weekly-scotus"}]):
        fake = FakeButtondown(tags=tags)
        with _client(fake) as client, pytest.raises(ButtondownError, match="weekly-scotus"):
            post_draft(
                client, subject=SUBJECT, body="Body.", tag_name="weekly-scotus", sleep=_no_sleep
            )
        assert fake.posts() == []


def test_reads_retry_a_server_error_and_the_write_is_attempted_once() -> None:
    fake = FakeButtondown(fail_gets=2)
    with _client(fake) as client:
        assert post_draft(
            client, subject=SUBJECT, body="Body.", tag_name="weekly-scotus", sleep=_no_sleep
        ).created

    refused = FakeButtondown(post_status=500)
    with _client(refused) as client, pytest.raises(ButtondownError, match="500"):
        post_draft(client, subject=SUBJECT, body="Body.", tag_name="weekly-scotus", sleep=_no_sleep)
    assert len(refused.posts()) == 1


def test_reads_give_up_after_their_attempts() -> None:
    fake = FakeButtondown(fail_gets=10)
    with _client(fake) as client, pytest.raises(ButtondownError, match="3 attempts"):
        post_draft(client, subject=SUBJECT, body="Body.", tag_name="weekly-scotus", sleep=_no_sleep)
    assert fake.posts() == []


def test_an_answer_that_is_not_a_draft_is_reported_as_a_failure() -> None:
    fake = FakeButtondown(answer_status="about_to_send")
    with _client(fake) as client, pytest.raises(ButtondownError, match="about_to_send"):
        post_draft(client, subject=SUBJECT, body="Body.", tag_name="weekly-scotus", sleep=_no_sleep)


def test_a_front_matter_body_and_an_empty_key_are_refused_locally() -> None:
    fake = FakeButtondown()
    with _client(fake) as client, pytest.raises(ButtondownError, match="front-matter"):
        post_draft(client, subject=SUBJECT, body="---\nx: 1\n---\n", tag_name="t")
    assert fake.requests == []
    with pytest.raises(ButtondownError, match="key"):
        make_client("  ")


def test_cli_dry_run_prints_the_untitled_body_and_contacts_nothing(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    data = tmp_path / "data"
    base = _base()
    _event(data, 101, "Alpha v. Beta")
    _forecast(data, 101, at=base, probability=0.4)
    week = _week_of(base.date())
    monkeypatch.delenv(API_KEY_ENV, raising=False)
    env = {"FEDCOURTS_DATA_ROOT": str(data)}

    result = runner.invoke(
        app, ["post-public-update", "--tag", "weekly-scotus", "--week", week, "--dry-run"], env=env
    )
    assert result.exit_code == 0, result.output
    assert result.output.startswith("Subject: FedCourtsAI weekly update: ")
    assert "Tag: weekly-scotus" in result.output
    assert "\n# FedCourtsAI" not in result.output
    assert "Alpha v. Beta" in result.output

    no_key = runner.invoke(
        app, ["post-public-update", "--tag", "weekly-scotus", "--week", week], env=env
    )
    assert no_key.exit_code == 2
    assert API_KEY_ENV in no_key.output

    empty = runner.invoke(
        app, ["post-public-update", "--tag", "weekly-scotus", "--week", "2026-W01"], env=env
    )
    assert empty.exit_code == 3
