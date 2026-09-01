"""Runtime settings, read from environment (prefix ``FEDCOURTS_``) or ``.env``.

Secrets (the CourtListener token) come from the environment only and are never
written to disk or committed.
"""

from __future__ import annotations

from enum import StrEnum
from pathlib import Path
from typing import Literal, Self

import yaml
from pydantic import (
    AliasChoices,
    BaseModel,
    ConfigDict,
    Field,
    field_validator,
    model_validator,
)
from pydantic_settings import BaseSettings, SettingsConfigDict

# The corpus read backends, defined here because `corpus` imports this module.
# One definition, so the setting, the type hints, and the CLI help cannot drift.
CorpusBackend = Literal["local", "ranged", "casestore", "service"]


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="FEDCOURTS_", env_file=".env", extra="ignore")

    data_root: Path = Path("data")
    config_root: Path = Path("config")
    corpus_root: Path = Path("corpus")
    metrics_root: Path = Path("metrics")
    # Recorded-cassette directory the offline `replay` engine reads instead of
    # calling a model (a captured real cell's output; see the runner). Unset in
    # production — replay is a test/dev backend — so the `replay` engine errors
    # clearly when no cassette is configured.
    replay_root: Path | None = None
    courtlistener_base_url: str = "https://www.courtlistener.com/api/rest/v4/"
    courtlistener_api_token: str | None = None
    request_timeout: float = 30.0
    # CourtListener per-token rate limits; override via FEDCOURTS_* env.
    courtlistener_rpm: int = 5
    courtlistener_rph: int = 50
    courtlistener_rpd: int = 125
    # Longest single throttle wait the client may sleep. Minute-window pacing is
    # seconds; a longer wait means an hour/day window is exhausted, and sleeping
    # it out inside a CI job reads as a hang and gets the run killed at the job
    # timeout — so the client raises instead and the caller wraps up the run.
    courtlistener_max_wait: float = 300.0
    # How read-only consumers open the corpus: "local" reads the pulled file
    # (`fedcourts corpus-pull`), "ranged" queries the immutable blob in place on
    # the corpus remote via HTTP range requests (see fedcourtsai.corpus_ranged),
    # "service" forwards query/open-events to a corpus query service on
    # localhost (see fedcourtsai.corpus_service) so the caller needs no cloud
    # credentials at all. Writers always open local.
    corpus_backend: CorpusBackend = "local"
    # The corpus remote's bucket URL, supplied out of band (never committed;
    # see SECURITY.md). corpus-pull/corpus-push and the ranged backend resolve
    # the corpus pointer against it — which pointer a read resolves is
    # `corpus_pointer` below; a push resolves only the committed one. The
    # bare workflow variable names
    # are accepted as aliases so the same runner env serves both. The workflow
    # variable is CORPUS_REMOTE_URL; the DVC_* aliases exist for the Codespaces
    # devcontainer secret, which is spelled DVC_REMOTE_URL (see
    # .devcontainer/) — new names win when both are set, and the aliases can
    # retire once that secret is renamed too.
    corpus_remote_url: str | None = Field(
        default=None,
        validation_alias=AliasChoices(
            "FEDCOURTS_CORPUS_REMOTE_URL",
            "CORPUS_REMOTE_URL",
            "FEDCOURTS_DVC_REMOTE_URL",
            "DVC_REMOTE_URL",
        ),
    )
    # The out-of-band corpus index pointer: the same JSON a publish writes to
    # the committed ``corpus/corpus.db.ref``, supplied verbatim through the
    # environment instead. When set, corpus READ paths resolve it in place of
    # the committed file — which is what lets a checkout read a corpus pair
    # whose pointer is not in git (the staging pair; see *Developer access* in
    # docs/data-pipeline.md). It passes exactly the committed pointer's
    # validation, key↔digest binding included, so it can widen nothing: it only
    # selects which already-published immutable blob is read. Writers never
    # honor it — ``corpus-push`` refuses to run while it is set — so the
    # committed pointer stays the sole pre-registration record. Unset/empty =
    # off (the committed pointer, unchanged).
    corpus_pointer: str | None = Field(
        default=None,
        validation_alias=AliasChoices("FEDCOURTS_CORPUS_POINTER", "CORPUS_POINTER"),
    )
    # Corpus split (phase 1): points the per-case content store (see
    # fedcourtsai.casestore) at ``s3://<bucket>[/<prefix>]``. When set, the writer
    # channels dual-write each mutated case there alongside the corpus blob;
    # unset/empty = off (the default), so the pipeline is unchanged. Best-effort —
    # a mirror failure only logs. Reads land in phases 3-4 (the casestore
    # provisioning backend, and `corpus_split` below).
    casestore_url: str | None = Field(
        default=None,
        validation_alias=AliasChoices("FEDCOURTS_CASESTORE_URL", "CASESTORE_URL"),
    )
    # Where the "service" backend forwards corpus queries: the base URL of a
    # `fedcourts corpus-serve` sidecar, normally on localhost. The sidecar
    # holds the actual corpus connection — and, in a cell job, the cloud
    # credentials — so the querying shell holds neither. The variable name
    # deliberately avoids the Gemini CLI's credential-name refusal regex, so
    # a cell can allowlist it like the rest of the cell contract (the
    # allowlist addition itself is a reviewed change, per the security
    # runbook).
    corpus_service_url: str | None = Field(
        default=None,
        validation_alias=AliasChoices("FEDCOURTS_CORPUS_SERVICE_URL"),
    )
    # Corpus split (phase 4): the mode switch that moves the go-forward system onto
    # the per-case content store. When on, the payload reads default to the casestore
    # (this phase routes the forward-cell provisioners there without an explicit
    # ``--corpus-backend casestore``) and a later step stops writing payloads into the
    # blob so ``corpus.db`` collapses to a small metadata index. Off by default, so the
    # pipeline is byte-for-byte unchanged until it is flipped on (at the clean-slate
    # cutover). Needs the store populated — i.e. ``casestore_url`` set.
    corpus_split: bool = False

    @field_validator("corpus_pointer", mode="before")
    @classmethod
    def _empty_corpus_pointer_is_unset(cls, value: object) -> object:
        """An empty pointer override reads as unset, not as malformed JSON.

        The same degradation ``_empty_corpus_split_is_off`` gives the split
        flag, for the same wiring: an env layer that passes an unset variable
        through raw (``scripts/corpus-env``'s prod restore, a workflow's
        ``${{ vars.… }}`` fallback) lands here as the empty string, which must
        mean "the committed pointer, unchanged" rather than fail every
        ``get_settings()`` call.
        """
        if isinstance(value, str) and not value.strip():
            return None
        return value

    @field_validator("corpus_split", mode="before")
    @classmethod
    def _empty_corpus_split_is_off(cls, value: object) -> object:
        """An empty ``FEDCOURTS_CORPUS_SPLIT`` reads as off, not as a parse error.

        Any env wiring that passes the ``prod``-environment variable (or its
        repo-level fallback) through raw — or an empty ``.env`` entry — lands
        here as the empty string, which pydantic's
        bool parser rejects. Empty must degrade to the default (off), matching
        ``casestore_url``'s documented "unset/empty = off", instead of failing
        every ``get_settings()`` call. The workflows' ``|| '0'`` fallback is
        the belt; this tested validator is the braces.
        """
        if isinstance(value, str) and not value.strip():
            return False
        return value


def get_settings() -> Settings:
    return Settings()


TRACKING_FILENAME = "tracking.yaml"


class PullConfig(BaseModel):
    """The ``pull`` section of ``config/tracking.yaml`` — the API-budget governor.

    ``config/tracking.yaml`` is the single place to tune scope and the
    CourtListener budget; this models just the keys the governor enforces (extra
    keys, like the rotation/discovery toggles, are ignored).
    """

    model_config = ConfigDict(extra="ignore")

    # Hard per-run cap on dockets refreshed (~3 requests each). Sized to the
    # active CourtListener tier and how many windows the schedule runs per day, so
    # the day's total stays under the daily ceiling and a single run stays under
    # the hourly ceiling (tier-hr ÷ ~3).
    max_cases_per_run: int = Field(default=15, ge=0)
    # Don't spend budget re-fetching closed / resolved cases.
    skip_closed: bool = True
    # Reserve up to this many of each run's slots for the stalest SCOTUS
    # dockets (the prediction scope), so the in-scope set rotates ahead of the
    # much larger general active set. Unused reserve slots fall through to the
    # normal stalest-first rotation, so it never wastes budget; 0 disables the bias.
    eligible_refresh_reserve: int = Field(default=0, ge=0)
    # Discover newly-filed dockets in the tracked courts since the last run.
    discover_new_filings: bool = True
    # Hard cap on new dockets onboarded per run (its own slice of the budget,
    # separate from the refresh cap above).
    max_new_cases_per_run: int = Field(default=10, ge=0)
    # Wall-clock budget for one `pull-all` run, in minutes, checked between
    # cases (and between courts during discovery). Sized below the workflow's
    # job timeout so a run against a degraded upstream stops, defers the rest of
    # the rotation to the next window, and still lands its queues and corpus
    # writes — instead of being killed mid-run and losing everything.
    max_run_minutes: float = Field(default=25.0, gt=0)
    # Stop the refresh rotation after this many consecutive transient REST
    # failures (timeouts / 5xx / 429): the upstream is degraded, and each doomed
    # case burns a full retry cycle of budget and wall clock. Deterministic
    # per-case errors (e.g. a 404) never trip it. Deferred cases keep their
    # stalest-first position, so the next window retries them.
    max_consecutive_transient_failures: int = Field(default=5, ge=1)


def load_pull_config(config_root: Path) -> PullConfig:
    """Read the governor's settings from ``config_root/tracking.yaml``.

    Falls back to defaults if the file or its ``pull`` section is absent, so the
    governor stays conservative rather than failing when config is missing.
    """
    path = config_root / TRACKING_FILENAME
    data = yaml.safe_load(path.read_text()) if path.exists() else {}
    return PullConfig.model_validate((data or {}).get("pull", {}))


class LiveConfig(BaseModel):
    """The ``live:`` section of ``tracking.yaml`` — the SCOTUS live channel.

    The supremecourt.gov docket JSON has no API budget, so these caps bound
    upstream politeness and coverage, not spend. At the model defaults (30/25) a
    full cycle stays around a minute; the deployed ``config/tracking.yaml`` runs a
    much larger cycle whose wall-clock is bounded by the run-pull live job's
    ``--max-run-seconds`` soft budget (it commits progress and resumes next
    cycle), so these counts are a per-cycle coverage ceiling, not a time bound.
    """

    model_config = ConfigDict(extra="ignore")

    # Pending petitions re-polled per cycle (the watchlist refresh rotation).
    max_cases_per_run: int = Field(default=30, ge=0)
    # New petitions onboarded from the Term's numbering frontier per cycle.
    max_new_cases_per_run: int = Field(default=25, ge=0)
    # Unresolved interim applications re-polled per cycle (the application
    # rotation; recent Terms first, then stalest). A changed, still-unresolved
    # substantive application in predict scope queues predict on the poll
    # (daily-debounced); the rest is ground-truth collection.
    max_applications_per_run: int = Field(default=10, ge=0)
    # Oldest October Term the refresh rotation reaches — the reachability
    # probe's floor (docs/live-sources.md): full JSON coverage OT2017+.
    term_floor_year: int = Field(default=2017, ge=1925)
    # Polite-client pacing between requests, seconds.
    throttle_seconds: float = Field(default=1.0, gt=0)
    # Consecutive 404s that mark a numbering stream's frontier (serials are
    # assigned sequentially; the tolerance bridges an occasional withheld one).
    frontier_misses: int = Field(default=2, ge=1)
    # Per-document cap on extracted text stored in the corpus: petitions
    # run 30-300 pages, and the cap is what keeps the corpus blob's growth sane.
    # ~150k characters is roughly 40 dense pages — the petition's argument in
    # full for a typical filing; a longer one is stored truncated (and flagged).
    document_text_cap: int = Field(default=150_000, ge=1_000)
    # Days after the July docket-number roll during which discovery also probes
    # the *outgoing* Term (`supremecourt.current_docket_term`). At the roll new
    # filings take the incoming Term's prefix, so the primary probe leaves the
    # outgoing Term's tail — a late filing onto it — which the historical walker
    # does not recover (it advances its cursor over the serial while still
    # pending). The window catches that tail at the source; 0 disables the grace
    # probe. A conservative default — a couple of months comfortably covers the
    # observed late-filing tail; the `le` cap keeps it a *window*, since a value
    # past ~182 would make dual-Term probing year-round.
    outgoing_term_grace_days: int = Field(default=60, ge=0, le=182)


def load_live_config(config_root: Path) -> LiveConfig:
    """Read the live channel's settings from ``config_root/tracking.yaml``.

    Falls back to defaults if the file or its ``live`` section is absent,
    mirroring :func:`load_pull_config`.
    """
    path = config_root / TRACKING_FILENAME
    data = yaml.safe_load(path.read_text()) if path.exists() else {}
    return LiveConfig.model_validate((data or {}).get("live", {}))


class HistoricalConfig(BaseModel):
    """The ``historical:`` section of ``tracking.yaml`` — the historical Term walker.

    Drives ``fedcourts historical-terms`` (the run-seed workflow): a
    sequential reverse-chronological walk of past Terms over the
    supremecourt.gov docket JSON that accumulates resolved outcomes for the
    statpack's per-Term base rates and the cert back-test set.

    **Every decided petition is ingested**, and there is deliberately no sampling
    knob: the walk must probe a serial before it can read the disposition, so
    declining to store one never saved a fetch — it only cost every rate computed
    over the result a denominator it had to reconstruct from weights. Sampling
    belongs where the cost actually is, at predict/evaluate selection, which draws
    from the corpus rather than being bounded by it, and where it is reversible.
    No API budget: the caps bound per-invocation wall clock and upstream politeness.
    """

    model_config = ConfigDict(extra="ignore")

    # Two-digit October Terms to walk, newest first. Floor OT2017 — the
    # reachability probe's full-JSON floor (docs/live-sources.md). The head
    # tracks the *docket* Term, which rolls the July before the Term opens
    # (see `supremecourt.current_docket_term`).
    terms: list[int] = Field(default=[26, 25, 24, 23, 22, 21, 20, 19, 18, 17])
    # Docket-JSON probes per invocation = the historical loop's checkpoint chunk
    # (~10 min at the polite 1 req/s; document fetches ride on top).
    max_probes_per_run: int = Field(default=600, ge=0)
    # Per-invocation wall-clock backstop, minutes, checked between serials.
    max_run_minutes: float = Field(default=20.0, gt=0)
    # Consecutive 404s that mark a (Term, stream)'s frontier — for a finished
    # Term, the end of its docket sequence.
    frontier_misses: int = Field(default=2, ge=1)
    # Polite-client pacing between requests, seconds.
    throttle_seconds: float = Field(default=1.0, gt=0)
    # Oldest two-digit Term whose ingested petitions get their filed documents
    # fetched: links are a rolling ~5-Term window upstream, near-zero
    # before ~OT2021, so older Terms load as metadata+proceedings-only rows.
    document_floor_term: int = Field(default=21, ge=0, le=99)
    # Per-document cap on extracted text stored in the corpus (see `live:`).
    document_text_cap: int = Field(default=150_000, ge=1_000)

    @field_validator("terms")
    @classmethod
    def _terms_in_served_range(cls, terms: list[int]) -> list[int]:
        # OT2017 is the probe-established floor; two-digit Term form above it.
        bad = [t for t in terms if not 17 <= t <= 99]
        if bad:
            raise ValueError(f"terms must be two-digit October Terms >= 17: {bad}")
        return terms


def load_historical_config(config_root: Path) -> HistoricalConfig:
    """Read the Term walker's settings from ``config_root/tracking.yaml``.

    Falls back to defaults if the file or its ``historical`` section is absent,
    mirroring :func:`load_live_config`.
    """
    path = config_root / TRACKING_FILENAME
    data = yaml.safe_load(path.read_text()) if path.exists() else {}
    return HistoricalConfig.model_validate((data or {}).get("historical", {}))


def load_courts(config_root: Path) -> list[str]:
    """The tracked courts from ``config_root/tracking.yaml`` (``courts:``).

    The scope ``pull`` keeps current. Returns an empty list if the file or its
    ``courts`` key is absent, so callers degrade to a no-op rather than
    crashing on missing config.
    """
    path = config_root / TRACKING_FILENAME
    data = yaml.safe_load(path.read_text()) if path.exists() else {}
    courts = (data or {}).get("courts", []) or []
    return [str(c).strip() for c in courts if str(c).strip()]


class PredictScope(StrEnum):
    """The prediction-scope gate the agentic predict/evaluate fan-out honors.

    Ingestion is always full-coverage; this restricts only the
    expensive predict/evaluate stages (see ``docs/data-pipeline.md``).
    """

    # Only SCOTUS dockets (`court == "scotus"`) are in-scope — the cost gate.
    # Originating court-of-appeals dockets are ingested for context and
    # retrieval but not predicted.
    scotus_docket = "scotus_docket"
    # No gate: every changed case with open events is in-scope (dev / back-testing).
    all = "all"


class PredictConfig(BaseModel):
    """The ``predict`` section of ``config/tracking.yaml`` — the fan-out gate.

    Models just the keys the predict/evaluate seams enforce; extra keys (the
    parallelism / skip-resolved knobs the workflow reads) are ignored.
    """

    model_config = ConfigDict(extra="ignore")

    # Which cases the agentic stages run on; `scotus_docket` is the default.
    scope: PredictScope = PredictScope.scotus_docket
    # Salience-INDEPENDENT hard cap on predict cells (predictor x case x event
    # matrix jobs) queued into one run. A backstop *below* the salience gate, not
    # part of it: it holds regardless of what selection did, so a selection that
    # fails open — the failure mode behind a past cost breach — still cannot fan
    # out an unbounded run. It bounds two things at once: GitHub's 256-job matrix
    # ceiling (a wider matrix is rejected outright, losing the whole run) and the
    # run's worst-case model spend. Enforced after scope filtering, in
    # `cap_predict_cells`, by dropping whole overflow cases (never splitting a
    # case's engines — a determinism / simplicity choice now that predict has a
    # per-predictor already-predicted skip, so a deferred case is a single clean
    # re-queue unit rather than partial admission tracked per engine) in a
    # deterministic, salience-independent order (ascending ``case_id``, a LEXICAL
    # sort over the ``court/docket`` string — numeric-ascending only within a
    # uniform docket digit width). A dropped case is deferred, never destroyed: it
    # keeps its place in the corpus predict queue and re-queues on a later cycle.
    # Default 240 = 80 fully-tournamented cases x 3 engines, 16 under the 256
    # ceiling; `ge=1` because a volume backstop that can be zeroed is not a
    # backstop.
    max_predict_cells_per_run: int = Field(default=240, ge=1)
    # The poison-pill backstop the live selection sweep's daily `predict_queued_at`
    # debounce lacks (counted from the committed `attempt.json` failure facts, see
    # `matrix.cell_failure_count`): once a (predictor, event) cell has been recorded
    # failed this many times, the sweep stops re-queuing it — so one cell that fails
    # every attempt (a persistent quota wall, a malformed record) cannot re-queue
    # forever. Keyed on cell identity, so a retry under a newer process version
    # still counts against the same cap. 0 disables the cap (every unpredicted cell
    # re-queues, as before). The predict mirror of
    # `EvaluateConfig.max_attempts_per_cell`; sized a few attempts above the
    # runner's in-request retry so a genuinely transient streak still gets several
    # cross-cycle retries before the cell is given up.
    max_attempts_per_cell: int = Field(default=5, ge=0)


def load_predict_config(config_root: Path) -> PredictConfig:
    """Read the prediction-scope gate from ``config_root/tracking.yaml``.

    Falls back to defaults (the gate on) if the file or its ``predict`` section is
    absent, so the cost gate stays conservative rather than failing when config is
    missing.
    """
    path = config_root / TRACKING_FILENAME
    data = yaml.safe_load(path.read_text()) if path.exists() else {}
    return PredictConfig.model_validate((data or {}).get("predict", {}))


class SalienceConfig(BaseModel):
    """The ``salience`` section of ``config/tracking.yaml`` — the selection knobs.

    Capacity ``N`` is the funding dial (see ``docs/budget.md``); it is a
    guaranteed *floor* of ranked picks per conference, not a hard ceiling —
    carve-outs and the sticky latch may push the realized count above it. The
    long conference (the Term's opening conference) carries a larger cap because
    it clears the summer backlog at once. ``floor`` is the always-include
    salience threshold (the relist-2 / CVSG grant-rate band).

    ``base_rate_lookback_terms`` is the one non-selection knob here: it bounds the
    segment base-rate window the evaluator and the cert back-test score skill
    against (``0`` = every prior Term). It lives beside the band knobs because the
    band is what it conditions on — but it governs **two** baselines on two
    different Term axes: the salience segment rate (docket-number Term) and the
    merits disturbed rate (grant Term,
    :func:`fedcourtsai.pipeline.base_rates.merits_base_rate`, which is not a
    salience product at all). Ten Terms means a different window on each. Moving
    this re-bases every published skill number on both stages at once, so a
    change here is a reviewable diff for figures well beyond salience.
    """

    model_config = ConfigDict(extra="ignore")

    per_conference_capacity: int = Field(default=12, ge=0)
    long_conference_capacity: int = Field(default=24, ge=0)
    floor: float = Field(default=0.28, ge=0.0, le=1.0)
    # The caption-banded arrival cohort's random-slice rate: the fraction of
    # eligible arrivals the deterministic draw (`salience.arrival_draw`,
    # keyed on the frozen draw literal, never the active version) selects at
    # docketing. The slice is load-bearing — its unbiased predicted population
    # is what makes forward skill numbers transfer to live prospective use —
    # and it is sized against that purpose, not against class measurement
    # (class rates are census quantities at the full population's n). At the
    # shipped 0.05 over ~1,500 paid arrivals/Term: ~75 cases (~$1,125 at the
    # $15/case planning rate), the reviewed sizing. Effectively frozen once
    # the cohort begins (a mid-Term change makes the realized population a
    # union across rates); 0 disables the slice (sal-v1 behavior).
    arrival_sample_rate: float = Field(default=0.05, ge=0.0, le=1.0)
    # Bounds the live cycle's selection sweep (selected petitions with open,
    # never-predicted events — the rescue/catch-up/retry path). Each swept case
    # costs one docket fetch plus document provisioning at the polite ~1 req/s,
    # so the cap keeps the sweep a small tail on the cycle; the backlog drains
    # across cycles under the sticky latch.
    sweep_cases_per_cycle: int = Field(default=25, ge=0)
    # A relist (not a first distribution) inside this many days of the case's
    # last ``predict_queued_at`` stamp is administrative churn, not a materially
    # different posture, so the live cycle suppresses re-queuing it while
    # capacity is enforced (gated scope + a salience config). The default of 1
    # suppresses only a same-day repeat (the observed failure mode: a petition
    # re-tournamented hours after its first prediction); 0 disables suppression,
    # so every relist queues unconditionally.
    relist_requeue_cooldown_days: int = Field(default=1, ge=0)
    # The lookback window for the salience-band segment base rate
    # (``fedcourtsai.pipeline.evaluate.segment_base_rate``): how many October Terms
    # immediately preceding a case's own Term may contribute to its band's pooled
    # grant rate. 0 = unbounded — every prior Term in the statpack — and is the
    # absent-file fallback only; the shipped config value is 10, matching
    # ``statpack.markdown_terms``. A bound trades variance for
    # bias: the high band carries only ~66-137 weighted-resolved petitions per Term,
    # so a short window is noisy, while a long one assumes the Court's grant
    # behaviour is stationary across the whole walked range. Per-Term high-band
    # rates measured on sal-v3 segments run 24.2%-42.4% on those counts — too thin
    # to tell drift from sampling either way, and the active sal-v4 re-reads that
    # band under a narrower distribution parse, so both the range and the counts
    # above re-base at the next statpack rebuild — which is why the window is stated rather than
    # defaulted (see docs/salience.md, *Base rates &
    # baselines for the predicted segment*). Moving this re-bases every forward
    # Brier skill number and every
    # `cert-backtest.json` per-band skill at once, which is exactly why it is config
    # rather than a constant. Counted in Term *years*, not statpack rows.
    base_rate_lookback_terms: int = Field(default=0, ge=0)
    # Cap on interim-docket tournament slots (stays, injunctions —
    # docs/salience.md, *The interim docket*), defined inside the per-conference
    # envelope (docs/budget.md). Enforced by the selection pass
    # (pipeline.salience.plan_cohorts): pending substantive applications fill up
    # to this many reserve slots per pass, and the slots in use lower the current
    # conference cohort's rank-fill limit by the same number — which costs a cert
    # pick only where the cohort's non-carve-out remainder exceeds that limit.
    interim_reserve_slots: int = Field(default=5, ge=0)

    @model_validator(mode="after")
    def _long_conference_is_not_smaller(self) -> Self:
        """Guard a fat-finger: the long conference must not carry a smaller cap."""
        if self.long_conference_capacity < self.per_conference_capacity:
            raise ValueError(
                "long_conference_capacity must be >= per_conference_capacity "
                f"({self.long_conference_capacity} < {self.per_conference_capacity})"
            )
        return self


def load_salience_config(config_root: Path) -> SalienceConfig:
    """Read the salience selection knobs from ``config_root/tracking.yaml``.

    Falls back to the field defaults if the file or its ``salience`` section is
    absent. The capacity defaults mirror the shipped ``config/tracking.yaml``
    sizing — capacities that bind at typical cohort sizes and fit the
    bootstrapping spend envelope (``docs/budget.md``) — so a config-less run
    keeps the gate a spend control rather than un-binding it. (The lookback
    keeps its deliberately conservative unbounded fallback; see the field.)
    """
    path = config_root / TRACKING_FILENAME
    data = yaml.safe_load(path.read_text()) if path.exists() else {}
    return SalienceConfig.model_validate((data or {}).get("salience", {}))


class StatpackConfig(BaseModel):
    """The ``statpack`` section of ``config/tracking.yaml`` — publication knobs.

    ``metrics/statpack.json`` always carries every Term and every bucket; these
    bound only what the Markdown artifact renders. That is not merely cosmetic:
    ``metrics/statpack.md`` is the surface the predict and evaluate prompts send
    agents to anchor on, so ``markdown_terms`` bounds the agent stratum's
    base-rate lookback *as instructed* — the sibling of
    :attr:`SalienceConfig.base_rate_lookback_terms`, which bounds the same window
    in code for the baseline those agents are scored against. The bound is
    conventional rather than a capability limit: ``statpack.json`` sits in the
    same checkout and carries every Term. Separate fields with separate defaults
    on purpose; ``docs/salience.md`` records that the two are configured to the
    same window so the scored baseline and the rendered table cannot silently
    diverge.
    """

    model_config = ConfigDict(extra="ignore")

    # How many recent Terms the per-Term detail tables in `metrics/statpack.md`
    # render (the JSON carries them all). 10 spans a decade of cert practice while
    # keeping the document prompt-sized; 0 renders every Term.
    markdown_terms: int = Field(default=10, ge=0)


def load_statpack_config(config_root: Path) -> StatpackConfig:
    """Read the statpack publication knobs from ``config_root/tracking.yaml``.

    Falls back to the shipped defaults when the file or its ``statpack`` section is
    absent, so the artifact still renders rather than failing.
    """
    path = config_root / TRACKING_FILENAME
    data = yaml.safe_load(path.read_text()) if path.exists() else {}
    return StatpackConfig.model_validate((data or {}).get("statpack", {}))


class EvaluateConfig(BaseModel):
    """Knobs for the evaluate backlog deriver (`tracking.yaml`'s `evaluate` section)."""

    model_config = ConfigDict(extra="ignore")

    # Bounds how many cases the backlog deriver queues per cycle. NOT a politeness
    # limit like the selection sweep's — the deriver reads the git ledger and the
    # corpus, no network — but a spend/PR-volume cap: each queued case fans out
    # one cell per not-yet-graded evaluator. The backlog drains across cycles,
    # stalest-stamped first, as gradings land and cases leave the level.
    backlog_cases_per_cycle: int = Field(default=25, ge=0)
    # The poison-pill backstop the `evaluate_queued_at` debounce lacks: once a
    # cell (evaluator, event) has been recorded failed this many times in the
    # committed `attempt.json` failure facts (counted by
    # `matrix.cell_failure_count`), the deriver stops
    # re-queuing it — so one cell that fails every attempt (a persistent quota
    # wall, a malformed record) cannot re-queue forever. Keyed on cell identity,
    # so a retry under a newer process version still counts against the same cap.
    # 0 disables the cap (every ungraded cell re-queues, as before). Sized a few
    # attempts above the client's in-request retry so a genuinely transient run of
    # failures still gets several cross-cycle retries before it is given up.
    max_attempts_per_cell: int = Field(default=5, ge=0)


def load_evaluate_config(config_root: Path) -> EvaluateConfig:
    """Read the evaluate backlog knobs from ``config_root/tracking.yaml``.

    Falls back to the defaults if the file or its ``evaluate`` section is absent.
    """
    path = config_root / TRACKING_FILENAME
    data = yaml.safe_load(path.read_text()) if path.exists() else {}
    return EvaluateConfig.model_validate((data or {}).get("evaluate", {}))


class SpendConfig(BaseModel):
    """The ex-post spend backstop (`tracking.yaml`'s `spend` section).

    The one control that reads what has actually been spent rather than bounding
    what a single decision or run may do — see :mod:`fedcourtsai.spend`. It gates
    both agentic stages, because the ceiling governs total inference spend rather
    than one stage's share.
    """

    model_config = ConfigDict(extra="ignore")

    # Trailing-window ceiling on measured inference spend, USD. `0` DISABLES the
    # backstop (the convention the other caps use), which is the default: adopting
    # it is a deliberate act, and a missing config can never wedge the pipeline.
    # Reaching the ceiling defers new cells — the queue is untouched and re-runs
    # next cycle — it never destroys queued work.
    ceiling_usd: float = Field(default=0.0, ge=0.0)
    # The window the ceiling applies over, days. Sized to the billing period the
    # ceiling is meant to protect rather than to a run: a per-run bound already
    # exists (`predict.max_predict_cells_per_run`), and what was missing is a
    # bound above it.
    window_days: int = Field(default=30, ge=1)


def load_spend_config(config_root: Path) -> SpendConfig:
    """Read the spend backstop's knobs from ``config_root/tracking.yaml``.

    Falls back to the defaults — i.e. **disabled** — if the file or its ``spend``
    section is absent, so a checkout without the section behaves exactly as before.
    """
    path = config_root / TRACKING_FILENAME
    data = yaml.safe_load(path.read_text()) if path.exists() else {}
    return SpendConfig.model_validate((data or {}).get("spend", {}))


class RunnerConfig(BaseModel):
    """The ``runner`` section of ``config/tracking.yaml`` — the agentic-cell retry
    governor.

    A predict/evaluate agent cell (:class:`fedcourtsai.pipeline.runner.AgenticRunner`)
    can fail on a *transient* fault — an HTTP 429 / quota-exceeded throttle, a 5xx
    upstream error, or a timeout — where a retry may well succeed. These bound the
    exponential backoff-and-jitter the runner applies before retrying such a
    failure. A *permanent* fault (a content-filter trip, a context-length blowout,
    an auth error) is deterministic and is never retried, so no cap here touches
    it — the split mirrors :func:`fedcourtsai.courtlistener.is_transient` and the
    ``pull`` governor's ``max_consecutive_transient_failures``.
    """

    model_config = ConfigDict(extra="ignore")

    # Total attempts a transient-failing cell gets (1 = the first try only, i.e.
    # retries off). A few is enough: a 429/5xx that has not cleared after a
    # handful of exponentially-spaced waits is a degraded upstream, and each
    # extra attempt re-spends a full agent invocation's tokens and minutes.
    max_attempts: int = Field(default=3, ge=1)
    # Base of the exponential backoff, seconds: the wait before retry N is
    # ``base * 2**(N-1)`` (pre-jitter), so 2.0 gives ~2s, ~4s, ~8s, ….
    backoff_base_seconds: float = Field(default=2.0, gt=0)
    # Ceiling on any single backoff wait, seconds — including one honored from a
    # server ``retry-after``. Caps the exponential growth (and a long
    # ``retry-after``) so a retrying cell cannot sleep its way into the CI job
    # timeout, the same "don't let a wait read as a hang" bound the pull
    # client's ``courtlistener_max_wait`` enforces.
    backoff_max_seconds: float = Field(default=30.0, gt=0)

    @model_validator(mode="after")
    def _max_not_below_base(self) -> Self:
        """Guard a fat-finger: the ceiling must not sit below the base wait."""
        if self.backoff_max_seconds < self.backoff_base_seconds:
            raise ValueError(
                "backoff_max_seconds must be >= backoff_base_seconds "
                f"({self.backoff_max_seconds} < {self.backoff_base_seconds})"
            )
        return self


def load_runner_config(config_root: Path) -> RunnerConfig:
    """Read the agentic-cell retry governor from ``config_root/tracking.yaml``.

    Falls back to the defaults if the file or its ``runner`` section is absent, so
    the runner retries conservatively rather than failing when config is missing.
    """
    path = config_root / TRACKING_FILENAME
    data = yaml.safe_load(path.read_text()) if path.exists() else {}
    return RunnerConfig.model_validate((data or {}).get("runner", {}))
