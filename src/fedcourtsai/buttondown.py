"""Deliver a rendered update to the email list as a Buttondown **draft**.

The one write this module makes is ``POST /v1/emails`` with ``status: draft``:
nothing here sends, schedules or edits an email, so every send is a person
pressing send in Buttondown after reading the draft. The key it is handed can
do more than that, which is why the request is built here, in one place, with
the status fixed rather than passed in.

Three rules shape the rest:

* **A draft always targets one tag.** The recipients are the subscribers
  carrying one tag, given by its id — the form Buttondown's filter takes, and
  one that needs no permission beyond emails — or by name, resolved to the id
  by listing the account's tags before anything is written. An empty id, or a
  name that matches no tag or several, refuses the post: a draft without a
  filter would go to the whole list when sent.
* **One draft per subject.** The subject names the week, so before creating a
  draft the module looks for any email with that exact subject that is not
  deleted — a draft, a scheduled send or one already sent — and returns it
  instead. Re-running a week therefore never makes a second draft, unless
  someone has since edited the draft's subject in Buttondown.
* **A draft's audience is confirmed, not assumed.** Buttondown echoes the
  filters an email carries; a draft whose echo does not name the tag — one
  just created, or one a re-run finds — fails the run, so a filter Buttondown
  dropped or renamed surfaces before anyone presses send.
* **Reads retry, the write does not.** The lookups are retried on a transport
  error, a server error or a rate limit; the create is attempted once, because a retried
  ``POST`` whose first attempt reached Buttondown would make a duplicate. A
  failed create fails the run, and running it again is safe, since the subject
  lookup finds whatever the first attempt made.
"""

from __future__ import annotations

import json
import time
from collections.abc import Callable, Iterator, Mapping
from dataclasses import dataclass
from typing import Any, Final

import httpx

#: Buttondown's API root.
API_BASE: Final = "https://api.buttondown.com/v1"

#: The environment variable the key arrives in. Read by the caller, never logged.
API_KEY_ENV: Final = "BUTTONDOWN_API_KEY"

#: The only status this module ever writes.
DRAFT_STATUS: Final = "draft"

_READ_ATTEMPTS: Final = 3
_RATE_LIMITED: Final = 429
_SERVER_ERROR: Final = 500
_BACKOFF_SECONDS: Final = (2.0, 5.0)
_MAX_PAGES: Final = 20
_TIMEOUT_SECONDS: Final = 30.0


class ButtondownError(RuntimeError):
    """A Buttondown request failed, or its answer does not allow a safe post."""


@dataclass(frozen=True)
class Draft:
    """The email a post produced or found, and whether this call created it."""

    email_id: str
    status: str
    created: bool
    url: str | None


def make_client(api_key: str, *, transport: httpx.BaseTransport | None = None) -> httpx.Client:
    """An HTTP client for the Buttondown API, authenticated with ``api_key``."""
    if not api_key.strip():
        raise ButtondownError("no Buttondown API key")
    return httpx.Client(
        base_url=API_BASE,
        headers={"Authorization": f"Token {api_key.strip()}", "Accept": "application/json"},
        timeout=_TIMEOUT_SECONDS,
        transport=transport,
    )


def _get(
    client: httpx.Client,
    path: str,
    params: Mapping[str, Any],
    *,
    sleep: Callable[[float], None],
) -> dict[str, Any]:
    """One GET, retried on a transport error, a 5xx or a 429; any other failure raises."""
    last: str = ""
    for attempt in range(_READ_ATTEMPTS):
        try:
            response = client.get(path, params=dict(params))
        except httpx.TransportError as exc:
            last = type(exc).__name__
        except httpx.HTTPError as exc:
            raise ButtondownError(f"GET {path} failed ({type(exc).__name__})") from exc
        else:
            code = response.status_code
            if code < _SERVER_ERROR and code != _RATE_LIMITED:
                if code != httpx.codes.OK:
                    raise ButtondownError(f"GET {path} returned {code}{_reason(response)}")
                return _object(response, f"GET {path}")
            last = f"HTTP {code}"
        if attempt < _READ_ATTEMPTS - 1:
            sleep(_BACKOFF_SECONDS[min(attempt, len(_BACKOFF_SECONDS) - 1)])
    raise ButtondownError(f"GET {path} failed after {_READ_ATTEMPTS} attempts ({last})")


def _object(response: httpx.Response, what: str) -> dict[str, Any]:
    """A response's JSON object body, or a :class:`ButtondownError` naming ``what``."""
    try:
        body = response.json()
    except ValueError as exc:
        raise ButtondownError(f"{what} returned a body that is not JSON") from exc
    if not isinstance(body, dict):
        raise ButtondownError(f"{what} returned a non-object body")
    return body


_REASON_MAX: Final = 300


def _reason(response: httpx.Response) -> str:
    """Buttondown's own account of a refusal, bounded, for the run log.

    A refused request's JSON body names the field or rule it failed, which a bare
    status code cannot. The request carried no secret in its body: the key
    travels in the Authorization header, which error bodies are assumed not to
    echo, and everything else sent is the public update. The one-line,
    bounded cut is the backstop on that assumption, and a body that is not JSON
    contributes nothing.
    """
    try:
        body = response.json()
    except ValueError:
        return ""
    if isinstance(body, Mapping):
        parts = [
            str(body[key]) for key in ("code", "detail", "message") if body.get(key) is not None
        ]
        text = " — ".join(parts) if parts else json.dumps(body, sort_keys=True)
    else:
        text = json.dumps(body, sort_keys=True)
    text = " ".join(text.split())
    if not text:
        return ""
    if len(text) > _REASON_MAX:
        text = text[: _REASON_MAX - 1] + "…"
    return f": {text}"


def _results(
    client: httpx.Client,
    path: str,
    params: Mapping[str, Any],
    *,
    sleep: Callable[[float], None],
) -> Iterator[dict[str, Any]]:
    """Every object a paginated listing returns, page by page, up to a bound."""
    seen = 0
    for page in range(1, _MAX_PAGES + 1):
        body = _get(client, path, {**params, "page": page}, sleep=sleep)
        results = body.get("results")
        if not isinstance(results, list):
            raise ButtondownError(f"GET {path} returned no results list")
        for item in results:
            if isinstance(item, dict):
                yield item
        seen += len(results)
        count = body.get("count")
        if not results or not isinstance(count, int) or seen >= count:
            return
    raise ButtondownError(f"GET {path} did not finish within {_MAX_PAGES} pages")


def tag_id(client: httpx.Client, name: str, *, sleep: Callable[[float], None] = time.sleep) -> str:
    """The id of the tag named exactly ``name``; refuses an absent or ambiguous one."""
    matches = [tag for tag in _results(client, "/tags", {}, sleep=sleep) if tag.get("name") == name]
    if not matches:
        raise ButtondownError(f"no Buttondown tag named {name!r}; refusing an untargeted draft")
    if len(matches) > 1:
        raise ButtondownError(f"{len(matches)} Buttondown tags named {name!r}")
    found = matches[0].get("id")
    if not isinstance(found, str) or not found:
        raise ButtondownError(f"Buttondown tag {name!r} has no id")
    return found


def existing_email(
    client: httpx.Client, subject: str, *, sleep: Callable[[float], None] = time.sleep
) -> dict[str, Any] | None:
    """The non-deleted email whose subject is exactly ``subject``, if there is one."""
    params = {"subject": subject, "-status": "deleted", "excluded_fields": "body"}
    for email in _results(client, "/emails", params, sleep=sleep):
        if email.get("subject") == subject:
            return email
    return None


def tag_filter(tag: str) -> dict[str, Any]:
    """Buttondown's recipient filter for the subscribers carrying one tag id."""
    return {
        "filters": [{"field": "subscriber.tags", "operator": "contains", "value": tag}],
        "groups": [],
        "predicate": "and",
    }


def targets(email: Mapping[str, Any], tag: str) -> bool:
    """Whether an email's echoed filters address the subscribers carrying ``tag``."""

    def walk(group: object) -> bool:
        if not isinstance(group, Mapping):
            return False
        rules = group.get("filters")
        nested = group.get("groups")
        return any(
            isinstance(rule, Mapping)
            and rule.get("field") == "subscriber.tags"
            and rule.get("operator") == "contains"
            and rule.get("value") == tag
            for rule in (rules if isinstance(rules, list) else [])
        ) or any(walk(sub) for sub in (nested if isinstance(nested, list) else []))

    return walk(email.get("filters"))


def _draft(email: Mapping[str, Any], *, created: bool) -> Draft:
    email_id = email.get("id")
    if not isinstance(email_id, str) or not email_id:
        raise ButtondownError("Buttondown returned an email with no id")
    url = email.get("absolute_url")
    return Draft(
        email_id=email_id,
        status=str(email.get("status") or ""),
        created=created,
        url=url if isinstance(url, str) and url else None,
    )


def post_draft(
    client: httpx.Client,
    *,
    subject: str,
    body: str,
    tag_name: str | None = None,
    tag_id_value: str | None = None,
    sleep: Callable[[float], None] = time.sleep,
) -> Draft:
    """Create the week's draft for one tag's subscribers, or return the one already there.

    The tag is given by id (``tag_id_value``), which needs no read beyond
    emails, or by name (``tag_name``), which lists the account's tags to
    resolve it. Exactly one of the two.
    """
    if (tag_name is None) == (tag_id_value is None):
        raise ButtondownError("name exactly one of a tag name or a tag id")
    if body.lstrip().startswith("---"):
        raise ButtondownError("the body opens with a front-matter fence, which Buttondown refuses")
    if tag_id_value is not None:
        if not tag_id_value.strip():
            raise ButtondownError("an empty tag id; refusing an untargeted draft")
        tag = tag_id_value.strip()
    else:
        assert tag_name is not None  # the exactly-one check above
        tag = tag_id(client, tag_name, sleep=sleep)
    label = tag_name if tag_name is not None else tag
    found = existing_email(client, subject, sleep=sleep)
    if found is not None:
        if found.get("status") == DRAFT_STATUS and not targets(found, tag):
            raise ButtondownError(
                f"the week's draft {found.get('id')!r} is not addressed to {label!r}; "
                "fix or delete it in Buttondown before sending"
            )
        return _draft(found, created=False)
    payload = {
        "subject": subject,
        "body": body,
        "status": DRAFT_STATUS,
        "filters": tag_filter(tag),
    }
    try:
        response = client.post("/emails", json=payload)
    except httpx.HTTPError as exc:
        raise ButtondownError(
            f"creating the draft failed ({type(exc).__name__}); re-running is safe, "
            "since the subject lookup finds a draft the attempt may have made"
        ) from exc
    if response.status_code != httpx.codes.CREATED:
        raise ButtondownError(
            f"creating the draft returned {response.status_code}{_reason(response)}"
        )
    created = _object(response, "creating the draft")
    if created.get("status") != DRAFT_STATUS:
        raise ButtondownError(
            f"Buttondown answered status {created.get('status')!r} for a draft request"
        )
    if not targets(created, tag):
        raise ButtondownError(
            f"Buttondown created draft {created.get('id')!r} without the {label!r} "
            "filter in its answer; fix or delete it in Buttondown before sending"
        )
    return _draft(created, created=True)
