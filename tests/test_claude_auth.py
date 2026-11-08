"""The direct Claude API callers' sign-in: the key, or a federated exchange."""

from __future__ import annotations

import json
from typing import Any

import httpx
import pytest

from fedcourtsai import claude_auth
from fedcourtsai.claude_auth import ApiKey, ClaudeAuthError, FederatedToken

FEDERATION_ENV = {
    "ANTHROPIC_FEDERATION_RULE_ID": "fdrl_test",
    "ANTHROPIC_ORGANIZATION_ID": "00000000-0000-0000-0000-000000000000",
    "ANTHROPIC_SERVICE_ACCOUNT_ID": "svac_test",
    "ANTHROPIC_WORKSPACE_ID": "wrkspc_test",
    "ACTIONS_ID_TOKEN_REQUEST_URL": "https://oidc.invalid/token?api-version=2.0",
    "ACTIONS_ID_TOKEN_REQUEST_TOKEN": "request-bearer",
}


class _Server:
    """Answers the GitHub OIDC endpoint and the token exchange, recording both."""

    def __init__(self, exchange_status: int = 200, expires_in: int = 600) -> None:
        self.oidc: list[httpx.Request] = []
        self.exchanges: list[dict[str, Any]] = []
        self.exchange_status = exchange_status
        self.expires_in = expires_in

    def __call__(self, request: httpx.Request) -> httpx.Response:
        if request.url.host == "oidc.invalid":
            self.oidc.append(request)
            return httpx.Response(200, json={"value": f"jwt-{len(self.oidc)}"})
        assert str(request.url) == claude_auth.TOKEN_URL
        self.exchanges.append(json.loads(request.content))
        if self.exchange_status != 200:
            return httpx.Response(self.exchange_status, json={"error": "denied"})
        return httpx.Response(
            200,
            json={
                "access_token": f"sk-ant-oat01-token-{len(self.exchanges)}",
                "token_type": "Bearer",
                "expires_in": self.expires_in,
            },
        )


def test_no_rule_reads_the_key_and_nothing_names_nothing() -> None:
    assert claude_auth.from_environment({"ANTHROPIC_API_KEY": "k"}) == ApiKey("k")
    assert claude_auth.from_environment({}) is None
    assert claude_auth.from_environment({"ANTHROPIC_API_KEY": ""}) is None


def test_a_rule_without_an_organization_is_refused() -> None:
    with pytest.raises(ClaudeAuthError):
        claude_auth.from_environment({"ANTHROPIC_FEDERATION_RULE_ID": "fdrl_x"})


def test_a_named_rule_wins_over_a_key() -> None:
    credential = claude_auth.from_environment({**FEDERATION_ENV, "ANTHROPIC_API_KEY": "k"})
    assert isinstance(credential, FederatedToken)


def test_the_exchange_sends_a_fresh_oidc_token_and_the_rule() -> None:
    server = _Server()
    with httpx.Client(transport=httpx.MockTransport(server)) as client:
        credential = claude_auth.from_environment(FEDERATION_ENV, oidc_client=client)
        assert credential is not None
        headers = credential.headers(client)
    assert headers == {"Authorization": "Bearer sk-ant-oat01-token-1"}
    (oidc,) = server.oidc
    assert oidc.headers["Authorization"] == "Bearer request-bearer"
    assert oidc.url.params["audience"] == "https://api.anthropic.com"
    assert oidc.url.params["api-version"] == "2.0"
    assert server.exchanges == [
        {
            "grant_type": "urn:ietf:params:oauth:grant-type:jwt-bearer",
            "assertion": "jwt-1",
            "federation_rule_id": "fdrl_test",
            "organization_id": "00000000-0000-0000-0000-000000000000",
            "service_account_id": "svac_test",
            "workspace_id": "wrkspc_test",
        }
    ]
    assert credential.secrets() == ["sk-ant-oat01-token-1"]


def test_the_token_is_reused_until_its_refresh_margin_then_exchanged_anew() -> None:
    server = _Server(expires_in=600)
    now = [0.0]
    with httpx.Client(transport=httpx.MockTransport(server)) as client:
        credential = FederatedToken(
            rule_id="fdrl_test",
            organization_id="org",
            identity_token=lambda: claude_auth.github_identity_token(FEDERATION_ENV, client),
            clock=lambda: now[0],
        )
        credential.headers(client)
        now[0] = 600 - claude_auth.REFRESH_MARGIN_S - 1
        credential.headers(client)
        assert len(server.exchanges) == 1
        now[0] = 600 - claude_auth.REFRESH_MARGIN_S
        assert credential.headers(client) == {"Authorization": "Bearer sk-ant-oat01-token-2"}
    # Each exchange spent its own OIDC token: Anthropic accepts each one once.
    assert [exchange["assertion"] for exchange in server.exchanges] == ["jwt-1", "jwt-2"]
    assert credential.secrets() == ["sk-ant-oat01-token-1", "sk-ant-oat01-token-2"]


def test_a_refused_exchange_names_its_status() -> None:
    server = _Server(exchange_status=401)
    with httpx.Client(transport=httpx.MockTransport(server)) as client:
        credential = claude_auth.from_environment(FEDERATION_ENV, oidc_client=client)
        assert credential is not None
        with pytest.raises(ClaudeAuthError, match="HTTP 401"):
            credential.headers(client)
        assert credential.secrets() == []


def test_a_job_without_the_oidc_pair_is_told_what_it_lacks() -> None:
    env = {k: v for k, v in FEDERATION_ENV.items() if not k.startswith("ACTIONS_")}
    credential = claude_auth.from_environment(env)
    assert credential is not None
    with (
        httpx.Client(transport=httpx.MockTransport(_Server())) as client,
        pytest.raises(ClaudeAuthError, match="id-token: write"),
    ):
        credential.headers(client)
