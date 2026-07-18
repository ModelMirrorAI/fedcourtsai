# Farr v. Grant, et al. — No. 25-1306 (petition disposition)

**Prediction: denied. P(grant) = 0.003.**

## The case

Joan E. Farr, proceeding pro se (she is her own counsel of record, with a
P.O. box address in Webb City, Missouri), petitions from the Eighth Circuit
(No. 25-1525). The underlying suit — confirmed via CourtListener (W.D. Mo.
No. 4:24-cv-00439, docket 68910257) — was a 42 U.S.C. § 1983 civil-rights
action (nature of suit "440 Civil Rights: Other") against a set of private
entertainment-industry defendants (Alexandra Grant and grantLOVE, LLC;
Scott Sims and the Ziffren Brittenham LLP law firm; WME IMG, LLC) plus
"Federal Parties." The district court dismissed on Rule 12 motions
(failure to state a claim / lack of jurisdiction) on December 16, 2024,
about five months after filing; reconsideration was denied May 19, 2025.
The Eighth Circuit affirmed on October 10, 2025 — a judgment "affirmed in
accordance with the opinion of this Court," the form of a summary
affirmance — and denied rehearing December 17, 2025.

## Why this petition will be denied

Every observable signal points the same way, and none points the other way:

1. **Pleading-stage dismissal of a § 1983 claim against private parties.**
   Section 1983 requires state action; a suit naming private individuals,
   a talent agency, and an entertainment law firm as § 1983 defendants
   fails at the threshold. A fact-bound Rule 12(b)(6)/jurisdictional
   dismissal, affirmed without a published circuit ruling, presents no
   circuit split and no question of federal law warranting review.
2. **All respondents waived response — including the Solicitor General.**
   The federal parties waived on June 18, 2026, and each private
   respondent group waived by June 24, 2026. The Court essentially never
   grants without at least calling for a response; no CFR issued before
   distribution.
3. **Single distribution to the long conference.** The petition was
   distributed on July 8, 2026 for the September 28, 2026 conference (the
   "long conference," where the summer's accumulated petitions are
   overwhelmingly denied). Zero relists; the corpus relist-0 bucket runs
   0.8% granted, and long-conference, waived, pro se petitions sit far
   below that bucket's average.
4. **Pro se petitioner, scanned petition.** The petition is a paid filing
   (which raises the base rate relative to IFP), but it is a self-filed
   scan with no text layer — not the profile of a certworthy petition.
   The provisioned `petition.txt` carries `empty_text: true` (the scan has
   no extractable text), so the questions presented could not be read;
   this is content-unavailable, not absent, and is flagged in
   `flags.json`. Nothing in the docket metadata or the lower-court record
   suggests the unread text could supply what the posture lacks.

## Base-rate anchoring

From the committed `metrics/statpack.md` (live/historical slice,
denial-reweighted): modern discretionary-cert petitions resolve ~94–95%
denied with grant rates of 2.5–3.3% per recent Term; Term 2025 paid-class
grant rate is ~5.4% (`statpack.json` per-fee-class detail); CA8-originating
petitions grant at 3.3%; relist-0 petitions at 0.8%; no-CVSG petitions at
3.0%. (The salience-band table the prompt contract references is not
present in the committed statpack, so I anchored on the relist/CVSG/circuit
cuts directly.) This petition's cell is the intersection of the weakest
buckets — zero relists, no CVSG, all waivers, pro se, pleading-stage
fact-bound dismissal, long-conference distribution — each of which sits at
or below its cut's floor. Starting from the relist-0 rate of 0.8% and
adjusting down for the waived-response, pro se, no-federal-question
profile, I set **P(grant) = 0.003**, materially below the paid-class
average and consistent with the near-zero historical grant rate for pro se
paid petitions.

Predicted disposition: **denied** at or shortly after the September 28,
2026 conference. Dismissal or withdrawal is possible but rare (~2% of
petitions); denial dominates the residual mass. A GVR is implausible — no
intervening decision plausibly bears on a state-action pleading dismissal.

## Big-case score

0.03. The respondents' celebrity adjacency may draw tabloid attention, but
the case carries no legal stakes: a denial will be unnoticed as a matter
of law, and even a (counterfactual) grant would present no question of
general significance.

## Mode note

Forward cell (`record/context.json`: `forward`); the petition is genuinely
pending — distributed for a conference ten weeks after the snapshot date —
and no retrieval surfaced any disposition of this petition. Retrieval into
the underlying district/appellate record predates the snapshot and is
legitimate forward signal.
