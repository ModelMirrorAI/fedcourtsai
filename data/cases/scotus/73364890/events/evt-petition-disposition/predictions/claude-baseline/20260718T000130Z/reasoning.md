# F.E.B. Corp. v. United States, No. 25-1294 — cert petition disposition

**Prediction: denied. P(any grant, GVR included) = 0.008.**

## The case

F.E.B. Corp. petitions from the Eleventh Circuit's third decision (unreported,
Nov. 5, 2025; rehearing denied Jan. 30, 2026) in the long-running quiet-title
fight over Wisteria Island, a dredge-spoil island off Key West. After a bench
trial on remand from *FEB II*, 52 F.4th 916 (11th Cir. 2022), the district
court found the United States created the island "for its own use" within the
meaning of the Submerged Lands Act exception, 43 U.S.C. § 1313(a), and the
court of appeals affirmed the findings as "plausible and supported by the
record" under clear-error review.

The questions presented ask (1) whether the Court should take up Justice
Blackmun's *concurrence* in *Anderson v. City of Bessemer City*, 470 U.S. 564,
581–82 (1985), which questioned the majority's "broad dictum" applying Rule
52(a) clear-error review to findings resting purely on documentary evidence,
and (2) whether "plausible" is the correct clear-error touchstone in a
historical-document case under § 1313(a).

## Why denial is near-certain

1. **The legal premise is foreclosed by the rule's own text.** The 1985
   amendment to Rule 52(a) — now Rule 52(a)(6) — provides that findings of
   fact, "whether based on oral or other evidence," must not be set aside
   unless clearly erroneous. The very question Justice Blackmun reserved was
   answered by the rulemaking process forty years ago, and *Anderson* itself
   (a unanimous judgment on this point) has been settled law since. Changing
   the standard would be a Rules Enabling Act project, not a cert-worthy
   circuit-law question. The petition never engages this text.

2. **No conflict alleged.** The petition cites exactly one case — *Anderson* —
   in its Table of Authorities. There is no claimed circuit split, no
   competing line of authority, and no assertion that any court of appeals
   reviews documentary-record findings de novo today. "Plausible" as the
   clear-error touchstone is *Anderson*'s own vocabulary (a finding must stand
   if it is a "plausible" account of the record), so QP2 attacks standard
   doctrine, not an outlier.

3. **Fact-bound, splitless error correction.** The decision below is
   unpublished, unanimous, and turns on record-specific inferences about
   1940s dredging operations. This is the paradigm of a petition the Court
   denies without comment.

4. **The respondent waived.** The Solicitor General filed a waiver of the
   right to respond (June 16, 2026) — the government sees no prospect of a
   grant. The Court essentially never grants without at least calling for a
   response, and no CFR had issued as of the snapshot; the petition was simply
   distributed for the September 28, 2026 long conference, the setting in
   which the vast bulk of summer petitions are denied in a single order list.

5. **Base rates.** From the committed statpack (modern discretionary-cert
   slice): overall grant rate ~2.5–3.3% per recent Term; petitions with zero
   relists grant at 0.8%; Eleventh Circuit petitions at 4.4%; no CVSG here.
   This petition sits well below the average never-relisted paid petition on
   the qualitative factors above (waiver, no split, single-authority
   petition, unpublished decision below), so I adjust below the 0.8%
   relist-zero anchor to **0.008**. A GVR is implausible — no intervening
   decision is identified or pending on the QP.

Modest grant-side weight: it is a paid petition by experienced Supreme Court
counsel, the Submerged Lands Act question has some intrinsic interest, and the
case has a colorful subject. None of that offsets the structural signals.

## Disposition call

`denied`, `granted = 0`, probability 0.008. Predicted mechanics: denial from
the September 28, 2026 conference or shortly after, without recorded dissent.

## Inputs used

- Snapshot `data/cases/scotus/73364890/record/snapshots/2026-07-17.json`
  (docket: filing, SG waiver, distribution; paid case type, Term 2025).
- Provisioned `questions-presented.txt` and `petition.txt` (full petition body
  read; the appendix tail of the 178-page PDF is truncated, which does not
  affect the analysis).
- Committed `metrics/statpack.md` base rates (modern cert slice, relist/CVSG/
  circuit cuts, per-Term table).
- CourtListener MCP (one opinion search) to confirm the FEB I / FEB II
  published history; the corpus query sidecar was unreachable this run (see
  `retrieval.md` and `flags.json`), so no `fedcourts query` priors — the
  statpack and provisioned inputs carried the base-rate anchoring instead.
  This degrades nothing material for a petition this clearly deny-shaped.

Mode is `forward`; no `DECIDED_BEFORE` clock applies. No outcome-revealing
material was encountered.
