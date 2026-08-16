# Rationale — P(disturbed) = 0.82, judgment `reversed`, 9–0

## Anchor

The committed statpack's "The merits docket (granted cases)" section publishes
an `excluded` count (67), so it is quotable and is the baseline my Brier is
scored against. My case's grant Term is 2025 (granted 2026-06-30, from the
event's `opened_at`). The ten-Term window is 2015–2024, strictly before; the
pack's merits table renders every Term it holds, which is 2017–2025, so the
strictly-prior pool is Terms 2017–2024: 515 parsed judgments, 359 disturbed —
**69.7%**, comfortably above the 30-parsed floor. That is the anchor.

## Adjustments up (to 0.82)

- **The grant itself is the strongest signal.** The Court called for a
  response after the respondents waived, then granted after five
  distributions over four conferences, over a BIO that led with vehicle
  objections (forfeiture, the withdrawn application, "no split"). Granting a
  *published, unanimous* Sixth Circuit affirmance — a Sutton opinion — on a
  petitioner-framed QP about whether chilling-effect doctrine is "displaced"
  by *Williamson County* reads as a grant to disagree, not to bless.
- **Doctrinal fit.** The petitioner's theory sits squarely on *SBA List v.
  Driehaus* credible-threat ripeness, and the record facts (cease-and-desist
  letter threatening citations, mayor soliciting neighbor reports, police
  patrols, prosecutor-initiated inspection) are strong for it. The Court's
  recent justiciability corrections in the land-use area (*Knick*, *Pakdel*)
  ran against finality-style barriers.
- **Case valence.** Eleven cert-stage amicus filings from a cross-ideological
  religious-liberty coalition (Agudath Israel, USCCB, Islam & Religious
  Freedom Action Team, ACLJ, Manhattan Institute, Protect the First), and the
  Court's sustained receptivity to free-exercise claimants.

## Adjustments down / what keeps me from 0.90

- **DIG risk is real.** The BIO's forfeiture argument has teeth: the Sixth
  Circuit never passed on the precise finality-exception theory the petition
  presses, and the vagueness theory was held forfeited below. A messy record
  (Grand withdrew his own application; the Commission had signaled his use
  might not even need a permit) is the classic DIG setup. A DIG counts as
  *undisturbed* on the scored binary.
- **An affirmance is not fanciful.** The panel was unanimous and carefully
  reasoned; the Court occasionally grants justiciability cases to clean up
  doctrine and affirms, and it could hold the letter from a law director with
  no zoning authority is simply not a credible enforcement threat.

Net: 0.82 against the 69.7% pooled baseline — a modest, defensible upward
tilt driven by the response-requested/relisted grant posture and doctrinal
fit, held back by DIG/vehicle risk.

## Vote block

9–0 majority for each Justice. Justiciability holdings of this shape are
usually unanimous (*SBA List* 9–0), and each Justice's modal vote is with a
disturbing majority; predicting a specific defector would lower expected
per-Justice accuracy. Scoring is intersection-only against whatever votes the
outcome record names, and no vote source is populated today — the block is
banked.

## What I anchored on, and did not

- Statpack merits section (pooled strictly-prior rate above). The cert
  salience band in `record/context.json` (`band: "high"`) is a cert construct
  whose work is done — not used, per the stage rule (no flag owed).
- Provisioned documents: the BIO (full text, 26 pp.) and the docket snapshot.
  **The petition itself was fetched but is a scanned PDF with no text layer
  (`empty_text: true`)** — my read of the petition's argument is inferred
  from the BIO's characterization, the Sixth Circuit opinion, and the QP as
  published, not from the petition's own text. Flagged in `flags.json`.
- Forward-mode retrieval: the published Sixth Circuit opinion (via
  CourtListener), the verbatim QP (via SCOTUSblog, after the Court's own QP
  PDF returned 403), and grant-coverage news. Searches surfaced only
  cert-stage material; no outcome exists (the case is pending, merits briefs
  not yet filed). No merits advocacy is on the record anywhere yet, so this
  is a forecast from the cert-stage record plus the opinion below — the
  ordinary state for a grant-moment cell.

## Uncertainty

Largest: how the Court weighs the forfeiture record (drives the DIG arm) and
whether it frames the holding as an exception to *Williamson County* or as a
narrower "this letter was final enough" ruling (drives `vacated` vs
`reversed` and the breadth claim). My semantic claims commit to the broader,
SBA-List-grounded reading; if the Court instead rules narrowly on de facto
finality under *Pakdel*, the ground claim grades poorly while the binary
still resolves disturbed.
