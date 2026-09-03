# Rationale for the numbers

**P(unqualified grant) = 0.05; predicted disposition: denied.**

## What I worked from

The provisioned snapshot (2026-09-02), the full application text
(`record/documents/application.txt`, 43 pages, extracted cleanly), the frozen
context (`mode: forward`, `band: null`, `response_requested: true`,
`referred_to_court: false`, `amicus_briefs: 0`, term 2026), the committed
`metrics/statpack.md` interim section, and one `fedcourts query` over recent
application priors. I deliberately ran no live CourtListener/web search on this
controversy: the applicants asked for a ruling by September 3 — the day of my run —
so any live search would have had a high chance of surfacing this application's own
disposition, which the leakage rule tells me not to seek. The forecast therefore
rests on the record as of the September 2 snapshot; if the Michigan Supreme Court
acted on September 2–3, I could not see it, and that is my largest blind spot.

## The anchor

This is an application-Term 2026 cell. Per the statpack's interim-docket section,
the scored baseline is the substantive resolved grant rate pooled over strictly
prior application-Terms: Term 2025 (17/226) + Term 2024 (14/70) = **31/296 ≈ 10.5%**,
which clears the pre-registered 50-resolved floor — so unlike earlier packs, a
published baseline exists for this cell, and I anchored on it. (The kickoff prompt's
worked figure of a 44-application pool describes an older pack; I computed from the
committed section as instructed.) Caveats carried with it: the pooled rate is
right-censored on the escalation columns, blends uneven parse coverage, and the
scored population is selected up the escalation ladder relative to the cohort behind
the rate.

## Adjustments

Up from 10.5%: a response was requested by the Circuit Justice within a day of
docketing — the strongest escalation rung short of referral, and the pack's
response-requested applications (55 of 340 substantive) are a selected, stronger
slice. The equities are unusually concrete: the Board conceded on the record that
the rejected affidavits would have cured a three-signature deficiency. Counsel
(John Bursch) is an experienced Supreme Court advocate.

Down, and decisively: (1) the ask is a mandatory injunction ordering state officials
to certify an initiative for the ballot — a materially rarer grant than a stay, and
the interim baseline is dominated by stays; (2) § 1257 jurisdiction rests on a
"constructive denial" of a mandamus petition the Michigan Supreme Court has had for
five business days, an aggressive extension of A.A.R.P. v. Trump (a federal-court
case); (3) the Court's consistent practice is to avoid injecting itself into
state-election mechanics on the eve of ballot finalization, and denying (or waiting
out) this application costs it nothing doctrinally since the state court can still
act; (4) the merits are deeply entangled with state signature-canvass law, with the
federal due-process/equal-protection overlay untested in this posture. A quick
response request is also routine diligence on any deadline-bound emergency
application — the Justice needs both sides before doing anything, including denying —
so I discount that signal well below its unconditional selection effect.

Net: roughly half the baseline, **0.05**. Residual disposition mass: denied ~0.82,
dismissed ~0.08, withdrawn ~0.05 (the latter two mostly the Michigan-Supreme-Court-
acts-first scenarios), granted 0.05.

## The increment claims

- `response-requested-increment` 0.02: the rung already fired (September 1 entry);
  the harness will mask the claim as vacuous. Nominal number for completeness.
- `referral-increment` 0.55: contested, salient, response-requested applications are
  usually referred, but the ~1–2-day horizon leaves real mass on an in-chambers
  denial or a mooting event before any referral entry appears. No published
  conditioned cut exists; this banks.
- `amicus-increment` 0.12: zero amici on the docket and roughly a one-day window;
  organized interest in the subject is high but same-day application amici are
  uncommon. Banks.

## Where to discount me

The pooled 10.5% baseline is not conditioned on the escalation ladder, so my
halving of it against a response-requested application is a judgment call pulling
against the selection direction; if the Court treats the Board's on-record
concession as making the right "indisputably clear," 0.05 is too low. Conversely, if
the Michigan Supreme Court granted relief on September 2–3 (which I could not
observe), the true grant probability here is near zero and the withdrawn/dismissed
mass is understated. I have no visibility into intra-Court appetite for the
citizen-only-voting subject beyond the public record.
