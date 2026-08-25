# Evaluation — codex-baseline, evt-brief-response-disposition (scotus/9526000124)

## The cell and the scored numbers

This is an **interim** cell (`stage: interim`): the disposition of the
government's stay application in Trump v. California, forecast at the
response-filed moment. The realized outcome is **granted**
(`actual_granted: 1`, resolved 2026-08-24).

codex-baseline predicted **granted** at probability **0.68** — the only candidate
on the right side — so `correct = 1` and `brier_score = (0.68 - 1)^2 =
0.1024`.

The baseline and skill are the harness's on an interim cell: `stamp-cell`
pools the statpack's substantive interim grant rate over strictly-prior
application Terms and writes `segment_base_rate` and `brier_skill_score`
itself; `base_rate_basis` is structurally null (an application freezes no
band). The committed statpack supports the pool — 16/178 (OT2025) + 14/47
(OT2024) = 30/225 ≈ 13.3%, above the 50-resolved floor — so the stamped rate
should be non-null, and against it this forecast shows large positive skill.
`claim_scores` (`interim-v1`) is the harness's. The frozen `context.band` is
null — the ordinary interim shape.

## What the prediction got right and wrong

Right on the scored axis, and specifically for an *unqualified* grant, having
explicitly priced the denial-first collapse of mixed relief. The rest of the
forecast also held up: referral to the full Court at 0.94 (the outcome records
`referred_to_court: true`), the response-request rung correctly treated as
fired (0.00), and little further amicus activity expected. Its stated likely
ground — the States' pre-enforcement challenge being premature while
implementation was unfinalized, by analogy to Trump v. New York and a
unanimous parallel D.C. Circuit ruling — is a concrete, checkable route the
grant is at least consistent with, though the disposing order's actual
grounds are not in the record I read, so I do not grade the forecast document.

## What drove `reasoning_quality` (0.85)

The strongest rationale of the three. It anchored on the correct
strictly-prior pool with the right caveats (escalation selection, uneven parse
coverage), then adjusted on genuinely case-specific evidence rather than
priors alone: the same-day response request, the government-applicant
conditional, and — decisively — the filings themselves, which it reports
reading from the docket-linked PDFs when no extracted text was provisioned.
That surfaced the applicants' justiciability/ripeness route and the parallel
D.C. Circuit ruling, which neither rival engaged, and it weighed the
respondents' Purcell/status-quo arguments as real counterweight rather than
as dispositive. It also caught and correctly handled the amicus-counter
singular/plural mismatch, using the harness-owned count while flagging the
gap. Dings: 0.68 with `confidence: 0.63` still left meaningful probability on
the wrong side given how strongly its own evidence pointed; and its account of
uncertainty is thinner than claude-baseline's. But soundness given the outcome is
clearly the best here.

## Leakage

`forward`, and genuinely so. One capture oddity, graded as data quality
rather than leakage: the harness log records only three calls across ten
seconds (two statpack reads and one redacted credential-shaped `other` row —
removed text under the doctrine, not outcome material), while the candidate's
own `retrieval.md` reports five filing-PDF reads (all documents filed on or
before 2026-08-12, pre-resolution by twelve days) and one rate-limited
CourtListener search. Whatever the capture missed, the disposition did not
exist on 2026-08-16 and nothing in the log, prose, or self-report sought one.
`influenced_prediction = not_applicable`, `leakage_suspected = false`. The
capture gap is recorded in this run's `flags.json`.
