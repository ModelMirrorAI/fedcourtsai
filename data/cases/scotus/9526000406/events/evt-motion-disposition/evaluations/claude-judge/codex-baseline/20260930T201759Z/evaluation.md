# Evaluation of codex-baseline — DHS v. D.V.D., No. 26A406 (`evt-motion-disposition`)

## Stage and what is mine to write

This is an **interim** cell: the government's application to stay the District of
Massachusetts's February 25, 2026 order and judgment pending certiorari. The event
resolved on 2026-09-29: the full Court, on referral from Justice Jackson, **granted**
the stay in full, treated the application as a petition for certiorari, granted it
(No. 26-426) on three stated questions, and set the case for the December 2026
argument session; Justices Sotomayor, Kagan, and Jackson would have denied. The
outcome record carries `actual_disposition: granted`, `actual_granted: 1`, and the
three interim signals (response requested, referred, two amicus briefs) all fired.

On an interim cell the baseline and skill are the harness's: `segment_base_rate` and
`brier_skill_score` are stamped by `stamp-cell` from the statpack's interim pool
(application-Terms strictly before 2026, floor 50 resolved) and `base_rate_basis`
stays null because the interim pool is no salience-band product. I wrote none of the
three. The pool the harness will read is, on the committed pack, 31 granted of 296
resolved substantive applications across Terms 2024 and 2025 (10.5%), so I expect a
non-null stamp; if it comes back null the pack's interim section is the place to look.
`claim_scores` is likewise the harness's (`interim-v1`, four claims), and no
`vote_accuracy` is written on an interim cell (this candidate predicted no votes in
any case). No `semantic_grades`: no semantic set is declared off the merits stage.

## Quantitative

- `predicted_disposition: granted` vs `actual_disposition: granted` → `correct = 1`.
- Probability 0.86 vs `actual_granted = 1` → `brier_score = (0.86 − 1)² = 0.0196`.

## Reasoning quality: 0.84

A disciplined rationale, graded on `reasoning.md` alone. Its strengths:

- **Information set stated precisely.** It names what it read, treats the September 24
  submission as the arrival state, notes that the application is the government's
  brief and not the appendix so the lower courts' reasoning is known only through the
  applicant's account, and says a missing response at arrival is not evidence of weak
  opposition. It defines its 0.86 as the probability of an *unqualified* grant of the
  substantive stay, distinct from administrative relief.
- **Anchor handled correctly.** 31/296 = 0.1047 over Terms 2016–2025 with the
  coverage caveats stated (Term 2024's 972 unparsed rows; the escalation-based
  selection of scored cells), and the statpack's vintage recorded as artifact vintage
  rather than corpus freshness. I verified the figures against the committed pack and
  against the cited vintage; they match.
- **Drivers and counterweights both argued.** The two 2025 grants in this case as
  legitimate pre-decision evidence (and explicitly not the target's outcome); the
  final-judgment posture and the alleged operational disruption as urgency; the
  § 1252(f)(1) / vacatur route with Biden v. Texas's reservation acknowledged; the
  First Circuit's distinctions as described in the brief; and the risk of removal to
  persecution or torture taken seriously rather than adopting the applicant's
  no-cognizable-harm framing. The 14% residual is allocated (denial and mixed relief
  first) and candidly labelled a judgment rather than a fitted subgroup rate.
- **The legal standard verified**, not recited: Hollingsworth v. Perry's stay-pending-
  certiorari factors checked through CourtListener.

What holds it below claude-baseline: the applicant-class effect, which turned out to be
decisive, is asserted without any data or even a stated prior for Solicitor General
applications, and the case-specific analysis is somewhat thinner (nothing on the
Circuit Justice's handling, nothing from the prior application's own docket). Against
that, its epistemic discipline about what came from where is the best of the three.
The forecast document and the claims block were read for context only and are not
scored here.

## Leakage: forward, not applicable

`mode: forward`; the prediction was created 2026-09-27 and the event resolved
2026-09-29, so the case was genuinely pending. The log (38 calls, capture 0.95) is
local reads of the provisioned inputs, prompt, schemas and statpack; two web searches
marked `unobserved`, graded on their queries, which seek only the general stay
standard (Nken and a Cornell LII page) and name neither this case nor its docket
number; and three CourtListener calls resolving Hollingsworth v. Perry, 558 U.S. 183.
No `retrieved_doc_date` anywhere. One shell `find` carries the literal `data/qp-topics/`
only inside a `-not -path` exclusion while locating `AGENTS.md`, so nothing under that
path was read or listed; I grade that as not a read, and note it here because the
rule keys on a query naming the path. The candidate's `retrieval.md` matches the log.
`retrieved_outcome_material = false`, `influenced_prediction = not_applicable`,
`leakage_suspected = false`.

## Big case: 0.85 (my read)

Formed from the record and the outcome: a nationwide removal policy on its third
emergency trip to the Court, now converted into a merits case on jurisdiction,
§ 1252(f)(1)'s reach over classwide declaratory relief and vacatur, and the legality of
the Guidance under § 1231(b), due process, and FARRA/CAT. The candidate's 0.93 is not
graded here; the panel's rank-agreement does that at leaderboard time.
