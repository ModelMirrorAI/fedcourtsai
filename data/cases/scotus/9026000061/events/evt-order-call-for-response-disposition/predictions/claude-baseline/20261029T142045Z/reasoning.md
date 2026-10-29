# Reasoning — P(grant) 0.08

**Inputs read.** Snapshot `record/snapshots/2026-08-17.json` (cutoff
2026-08-18, `date` cut, forward mode); `questions-presented.txt`,
`petition.txt` and `appendix.txt` (Ninth Circuit published opinion by Judge
Miller, Jan 2, 2026; district court summary-judgment order; en banc denial).
No brief in opposition exists (respondent waived; the response was only just
called for), so nothing on my desk states Paramount's side.

**Anchor.** `record/context.json` gives band `baseline` under `sal-v4`, which
matches the statpack's band table heading. Pooling the bracketed `reached`
rate for `baseline` over Terms 2017–2025 (strictly before OT2026) gives about
**5.1%** (weighted n ≈ 12,900).

**Adjustments up.** (1) The call for a response itself: some Justice or clerk
flagged the petition — no committed table conditions on it, but in my judgement
it roughly doubles a baseline rate. (2) Three amicus filings before the first
conference (statpack amicus `2+` bucket: grant family ≈ 23%, n = 1,449
resolved — a marginal, not conditional, figure). (3) Elite Supreme Court
counsel on both sides (MoloLamken for petitioners, O'Melveny for Paramount);
a cleanly framed split the petition maps as 2d/3d/5th/7th/D.C. vs. 9th/4th/8th
Circuits; a published opinion; a summary-judgment posture where the extrinsic
test was dispositive; copying and copyrightability not disputed.

**Adjustment down — the decisive one.** The petition itself discloses
(n.7) that the Ninth Circuit has granted rehearing en banc in *Sedlik v. Von
Drachenberg* to reconsider aspects of the same extrinsic/intrinsic framework.
The Court ordinarily lets a circuit reconsider its own rule en banc before
resolving a split that circuit anchors; the petitioners' fallback request to
"hold" for *Sedlik* is not something the Court usually does for a lower-court
decision. Also: the Court has repeatedly denied petitions attacking the Ninth
Circuit's test in the past (my general knowledge, not checked against the
corpus), and substantial similarity is fact-bound in application.

Net: about 8%, grant family included. `summary-disposition-route` 0.15 reflects
mainly the chance of a GVR after an en banc *Sedlik* decision. `cvsg-increment`
0.04: private-party copyright, the United States has no direct stake.
`dissent-from-denial` 0.04: a statutory-doctrine denial rarely draws a writing.
`relist-increment` 0.95 (masked; it will be redistributed after the response).

**Uncertainty / discount.** I have not seen the brief in opposition (it did not
exist at cutoff) and did not check the live docket or the status of the
*Sedlik* en banc, to avoid touching this case's later history; the en banc
grant is read from the petition only. If *Sedlik* had been decided en banc
before conference in a way that left the split intact, my number would be too
low. Corpus query returned no case-specific priors useful here.
