"""How the harness's own Claude API calls sign in.

The case summaries and the AI-ruling summaries call the Messages API directly,
one request per summary, with no engine CLI between them and the API. Their
credential is one of two kinds, read from the environment:

- **Workload identity federation**, once the job's environment names a
  federation rule and organization: the job's GitHub OIDC token is exchanged at
  the Claude API's token endpoint for a short-lived access token, sent as a
  bearer token. Each exchange asks GitHub for a fresh OIDC token, since
  Anthropic accepts each one once and GitHub's expire in minutes, and the
  access token is exchanged again shortly before it expires, so a run of hours
  never holds a credential older than one token lifetime.
- **The API key**, otherwise: a local run, or a workflow whose environment
  names no rule.

A throttle, a server error or a dropped connection at either endpoint is raised
as the ``httpx`` error it is, so the caller's bounded retry covers the sign-in
as it covers the call; any other refusal is a :class:`ClaudeAuthError`.

The federation identifiers are identifiers, not credentials. The key wins only
where no rule is named: a workflow that names one withholds the key.
"""

from __future__ import annotations

import os
import time
from collections.abc import Callable, Mapping
from dataclasses import dataclass, field
from typing import Protocol
from urllib.parse import quote

import httpx

KEY_ENV = "ANTHROPIC_API_KEY"
RULE_ENV = "ANTHROPIC_FEDERATION_RULE_ID"
ORGANIZATION_ENV = "ANTHROPIC_ORGANIZATION_ID"
SERVICE_ACCOUNT_ENV = "ANTHROPIC_SERVICE_ACCOUNT_ID"
WORKSPACE_ENV = "ANTHROPIC_WORKSPACE_ID"
REQUEST_URL_ENV = "ACTIONS_ID_TOKEN_REQUEST_URL"
REQUEST_TOKEN_ENV = "ACTIONS_ID_TOKEN_REQUEST_TOKEN"

TOKEN_URL = "https://api.anthropic.com/v1/oauth/token"
OIDC_AUDIENCE = "https://api.anthropic.com"
JWT_BEARER_GRANT = "urn:ietf:params:oauth:grant-type:jwt-bearer"

#: How long before its stated expiry an access token is replaced. Wide enough
#: that a request started just before the margin still completes on a live
#: token, since one summary call can take minutes.
REFRESH_MARGIN_S = 180

#: The token lifetime assumed when the exchange states none: the shortest the
#: federation rules here are configured for.
DEFAULT_LIFETIME_S = 600


class ClaudeAuthError(RuntimeError):
    """The run cannot obtain a credential: a misconfiguration or a refused exchange."""


class ClaudeCredential(Protocol):
    """A credential a direct Messages API call carries."""

    def headers(self, client: httpx.Client) -> dict[str, str]:
        """The auth headers for the next request, exchanging first if due."""
        ...

    def secrets(self) -> list[str]:
        """Every credential value this run has sent, for containment scans."""
        ...

    def invalidate(self) -> None:
        """Drop a credential the API refused, so the next request signs in afresh."""
        ...


@dataclass(frozen=True)
class ApiKey:
    """A static API key, sent as ``x-api-key``."""

    key: str = field(repr=False)

    def headers(self, client: httpx.Client) -> dict[str, str]:
        return {"x-api-key": self.key}

    def secrets(self) -> list[str]:
        return [self.key]

    def invalidate(self) -> None:
        """A key has nothing to refresh."""


@dataclass
class FederatedToken:
    """An access token exchanged from a GitHub OIDC token, sent as a bearer token."""

    rule_id: str
    organization_id: str
    identity_token: Callable[[], str]
    service_account_id: str | None = None
    workspace_id: str | None = None
    clock: Callable[[], float] = time.monotonic
    _token: str = field(default="", init=False, repr=False)
    _refresh_at: float = field(default=0.0, init=False, repr=False)
    _issued: list[str] = field(default_factory=list, init=False, repr=False)

    def headers(self, client: httpx.Client) -> dict[str, str]:
        if not self._token or self.clock() >= self._refresh_at:
            self._exchange(client)
        return {"Authorization": f"Bearer {self._token}"}

    def secrets(self) -> list[str]:
        return list(self._issued)

    def invalidate(self) -> None:
        self._token = ""

    def _exchange(self, client: httpx.Client) -> None:
        assertion = self.identity_token()
        _mask(assertion)
        body = {
            "grant_type": JWT_BEARER_GRANT,
            "assertion": assertion,
            "federation_rule_id": self.rule_id,
            "organization_id": self.organization_id,
        }
        if self.service_account_id:
            body["service_account_id"] = self.service_account_id
        if self.workspace_id:
            body["workspace_id"] = self.workspace_id
        try:
            response = client.post(TOKEN_URL, json=body)
            response.raise_for_status()
            data = response.json()
            token = data["access_token"]
            lifetime = int(data.get("expires_in") or DEFAULT_LIFETIME_S)
        except httpx.HTTPError as exc:
            if _is_transient(exc):
                raise
            # The reason a rule refused an exchange is in the Console's
            # authentication history; the response says only the status.
            status = exc.response.status_code if isinstance(exc, httpx.HTTPStatusError) else 0
            raise ClaudeAuthError(f"the federation token exchange answered HTTP {status}") from exc
        except (ValueError, TypeError, KeyError) as exc:
            raise ClaudeAuthError("the federation token exchange returned no access token") from exc
        if not isinstance(token, str) or not token:
            raise ClaudeAuthError("the federation token exchange returned no access token")
        _mask(token)
        self._token = token
        self._refresh_at = self.clock() + max(lifetime - REFRESH_MARGIN_S, 0)
        self._issued.append(token)


def _is_transient(exc: httpx.HTTPError) -> bool:
    """A fault the caller's bounded retry should see as it is: a throttle,
    a server error, or a request that got no response."""
    if isinstance(exc, httpx.HTTPStatusError):
        status = exc.response.status_code
        return status == 429 or status >= 500
    return isinstance(exc, httpx.RequestError)


def _mask(value: str) -> None:
    """Register a credential with the Actions log masker, when running in Actions.

    The runner masks the secrets a job names, but not a token minted inside a
    step, and a traceback that prints a request's headers would otherwise
    show it in a public run log.
    """
    if os.environ.get("GITHUB_ACTIONS") == "true":
        print(f"::add-mask::{value}", flush=True)


def _env(environ: Mapping[str, str], name: str) -> str:
    return environ.get(name, "").strip()


def github_identity_token(environ: Mapping[str, str], client: httpx.Client) -> str:
    """A fresh GitHub Actions OIDC token for the Claude API's audience."""
    url, bearer = _env(environ, REQUEST_URL_ENV), _env(environ, REQUEST_TOKEN_ENV)
    if not url or not bearer:
        raise ClaudeAuthError(
            "a federation rule is named, but this job cannot request a GitHub OIDC "
            "token: the job needs `id-token: write`"
        )
    separator = "&" if "?" in url else "?"
    try:
        response = client.get(
            f"{url}{separator}audience={quote(OIDC_AUDIENCE, safe='')}",
            headers={"Authorization": f"Bearer {bearer}"},
        )
        response.raise_for_status()
        value = response.json().get("value")
    except httpx.HTTPError as exc:
        if _is_transient(exc):
            raise
        status = exc.response.status_code if isinstance(exc, httpx.HTTPStatusError) else 0
        raise ClaudeAuthError(f"the GitHub OIDC endpoint answered HTTP {status}") from exc
    except (ValueError, AttributeError) as exc:
        raise ClaudeAuthError("the GitHub OIDC endpoint returned no token") from exc
    if not isinstance(value, str) or not value:
        raise ClaudeAuthError("the GitHub OIDC endpoint returned no token")
    return value


def from_environment(
    environ: Mapping[str, str] | None = None,
    oidc_client: httpx.Client | None = None,
) -> ClaudeCredential | None:
    """The credential the environment names, or None when it names none.

    ``oidc_client`` fetches the GitHub OIDC tokens; a short-lived client of its
    own per fetch by default.
    """
    env = os.environ if environ is None else environ
    rule = _env(env, RULE_ENV)
    if rule:
        organization = _env(env, ORGANIZATION_ENV)
        if not organization:
            raise ClaudeAuthError(f"{RULE_ENV} is set without {ORGANIZATION_ENV}")

        def identity_token() -> str:
            if oidc_client is not None:
                return github_identity_token(env, oidc_client)
            with httpx.Client(timeout=30.0) as client:
                return github_identity_token(env, client)

        return FederatedToken(
            rule_id=rule,
            organization_id=organization,
            identity_token=identity_token,
            service_account_id=_env(env, SERVICE_ACCOUNT_ENV) or None,
            workspace_id=_env(env, WORKSPACE_ENV) or None,
        )
    key = env.get(KEY_ENV, "")
    return ApiKey(key) if key else None
