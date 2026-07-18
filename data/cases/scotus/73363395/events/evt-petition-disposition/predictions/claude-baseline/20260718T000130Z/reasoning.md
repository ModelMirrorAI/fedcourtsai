# Campo v. Uber Technologies, Inc. (No. 25-1292) — petition disposition

**Prediction: denied. P(grant, GVR included) ≈ 0.008.**

## The case

Yesit Campo, as personal representative of the Estate of Arlevys Molina, sued
Uber Technologies and its Rasier subsidiaries for wrongful death in Florida
state court (Miami-Dade Circuit Court). The trial court granted the Uber
defendants summary judgment in April 2023; Florida's Third District Court of
Appeal affirmed (Campo v. Uber Techs., Inc., 407 So. 3d 503 (Fla. 3d DCA
2025)); and the Florida Supreme Court declined discretionary jurisdiction on
October 24, 2025. The paid cert petition was docketed May 19, 2026 (Term
2025 numbering, No. 25-1292).

## The questions presented

Both QPs ask the same thing in two constitutional wrappers: whether, under
(1) the Seventh Amendment and (2) Fourteenth Amendment due process, the
demanded jury trial should have proceeded against the Uber defendants so a
jury could weigh the record evidence and draw adverse inferences —
i.e., whether summary judgment wrongly displaced the jury.

## Why this petition is a near-certain deny

1. **The lead theory is foreclosed at the threshold.** The Seventh Amendment
   has never been incorporated against the states (Minneapolis & St. Louis
   R.R. v. Bombolis, 241 U.S. 211 (1916); reaffirmed as an acknowledged
   non-incorporated right in McDonald v. City of Chicago). A Seventh
   Amendment challenge to a *Florida state court's* summary judgment fails
   without reaching any question the Court would need to resolve. The
   petition itself quotes Florida cases acknowledging the Amendment "is only
   binding upon federal courts."
2. **No split, no question of federal importance.** The reasons-for-granting
   section cites almost exclusively Florida authority (Hollywood, Inc.,
   1978 Chevrolet Van, Printing House) plus general jury-trial dicta (Jacob,
   Beacon Theatres, Dimick). It alleges no conflict among circuits or state
   high courts and articulates no legal rule in dispute — it asks for
   fact-bound error correction of a state summary judgment, the paradigmatic
   cert-denial profile under Rule 10.
3. **Docket signals all point to denial.** Respondents (represented by Wilson
   Elser) filed a waiver of the right to respond on June 10, 2026, and the
   petition was distributed for the September 28, 2026 long conference on the
   waiver alone. The Court's uniform practice is to call for a response
   before granting; a first distribution with a waiver, no CFR, no relist,
   no CVSG, and no amici is the lowest-salience posture a paid petition can
   occupy.
4. **Base rates.** From the committed `metrics/statpack.md`: modern
   discretionary-cert petitions resolve overwhelmingly as denials (11,115
   denied vs. 367 granted in the denial-reweighted slice); the relist-0
   bucket runs **denied 97.3% / granted 0.8%**; Term 2025's estimated grant
   rate is 2.5% (paid petitions grant more than IFP, but this one carries
   none of the paid-docket quality markers); and no-CVSG petitions grant at
   3.0%. Petitions from Florida's courts in the selected slice show no
   grants (Supreme Court of Florida bucket: denied 70.4%, dismissed 29.6%,
   granted 0%). Conditioning the ~1–3% anchors on the foreclosed lead
   theory, the absence of any split, and the response waiver pushes this
   petition well below the relist-0 rate.

## Calibration

- **P(grant) = 0.008** — slightly below the relist-0 base rate (0.8%),
  because the petition combines a legally foreclosed lead question,
  no-split fact-bound error correction, and a respondent waiver posture.
- **Predicted disposition: denied.** A GVR is implausible (no candidate
  intervening decision), and nothing suggests dismissal or withdrawal.
- **Expected path:** denied at or shortly after the September 28, 2026 long
  conference, likely on the October 2026 order list.
- **Votes:** none predicted — cert denials issue without recorded votes, and
  nothing here suggests a dissent from denial.
- **big_case_score = 0.10.** A private wrongful-death dispute; even the
  latent Uber-driver control/independent-contractor issue is presented only
  as record evidence a jury should have weighed, not as a legal question.
  If decided, the ruling would be narrow and little-noticed.

## Inputs and degradations

I used the provisioned snapshot (`record/snapshots/2026-07-17.json`), the
provisioned `questions-presented.txt` and full `petition.txt` (58 pp.; no
brief in opposition exists — respondents waived), the event definition, and
the committed `metrics/statpack.md` base rates. The corpus query sidecar was
unreachable in this cell (`fedcourts query` timed out), so I could not pull
ranked corpus priors; the statpack and provisioned inputs were sufficient
for this low-variance call. Mode is `forward` — no disposition exists yet
(first conference is September 28, 2026), so no further retrieval was
needed and none surfaced any outcome.
