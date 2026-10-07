# Evaluation — codex-baseline, scotus/73500241, evt-petition-disposition

**Outcome.** Cert stage (`event.yaml` stage `cert`, moment `distribution`). The
petition was denied on 2026-10-05 after one distribution for the 2026-09-28
conference, no call for a response, no separate writing (`outcome.json`:
`actual_disposition` denied, `actual_granted` 0).

**Scores.** `predicted_disposition` denied matches, so `correct` 1. Probability
0.015 against 0 gives a Brier of 0.000225. The baseline is the `baseline` band's
bracketed `reached` figure pooled resolved-weighted over OT2017 through OT2024
from the sal-v4 table in `metrics/statpack.md`, 0.0512 on the `risk_set` basis
(frozen band `baseline` under `sal-v4`, matching the table heading; the in-code
pooler returns 0.051209 on the same context, and the candidate's own figure of
593 / 11,580 from the pack's prefix fields is the same number). Ten of ten Terms
are rendered, so no window divergence. Brier skill is
1 - 0.000225 / 0.0512^2 = 0.9142.

**Leakage.** Forward mode, `not_applicable`, checked: prediction created
2026-09-17, denial 2026-10-05. The log carries 30 calls at coverage 0.87. The
external retrievals are four unobserved fetches of the petition's own appendix
PDF (a filing dated 2026-05-28 and linked in the provisioned snapshot, so
pre-resolution by construction), one captured shell fetch of the same PDF parsed
in memory, a CourtListener lookup of Asinor (decided 2024) with a passage search,
and an empty citation search for the opinion below. Nothing reaches this
petition's disposition. One call's text contains `data/qp-topics/`: a `find` for
`AGENTS.md` with that path as a `-not -path` exclusion. The prompt's literal rule
counts a file-search whose query names that path, but an exclusion pattern keeps
the directory out of the search rather than reading it, and the results could not
have carried qp-topic membership. I read it as not a read and grade the cell
clean, and I have recorded the reading in `flags.json` so a maintainer can
overrule it. `retrieved_outcome_material` false.

**Reasoning quality: 0.82.** The best-evidenced analysis in the cell. The anchor
is computed from the pack's own prefix fields rather than rounded percentages, the
candidate correctly keeps the reached rate rather than the terminal one, and it
correctly reads the Term as 2025 and the caption class off the private
petitioners. The decisive work is reading the Kansas Court of Appeals opinion out
of the filed appendix, which no other candidate managed: that is where the
defendant-status, official-capacity immunity, and pleading grounds come from,
and they are exactly the barriers that make the abstract constitutional question
unable to change the judgment. Checking Asinor's actual text against the
petition's characterization of the split, and catching the petition's
misattribution of Federal Circuit cases to this Court, are both sound and both
grounded in cited sources.

Two things hold it under claude-baseline. First, the candidate declines to weigh the
waiver with no call for a response, treating it as "evidence about the docket's
present posture, not an adjudication of the petition's strength." That is true
but beside the point: a paid petition sitting three months on a waiver without a
call for a response is the single strongest denial signal on the docket, and the
analysis reaches 0.015 while explicitly setting it aside. Second, the opening
move that "the subject warrants attention" and the 0.34 stakes score give the
underlying retention issue more weight than this damages-only vehicle can carry;
the number itself is not scored here, but the framing pulls against the rest of
the analysis. The tool-limitations section is candid and useful. The forecast
document and the claims block were read for context only and are not scored.

**Big case.** My own read, formed before looking at the candidate's score, is
0.06.
