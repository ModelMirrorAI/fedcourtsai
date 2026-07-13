# Prediction: scotus/73275174 — evt-petition-disposition

**No. 25-234, State Board of Election Commissioners, et al. v. Mississippi State
Conference of the NAACP, et al.** (appeal from the S.D. Miss. three-judge court,
No. 3:22-cv-00734-DPJ-HSO-LHS).

## Disclosure: the provisioned snapshot contains the outcome

This cell is marked `forward` in `record/context.json`, but the provisioned
snapshot (`record/snapshots/2026-07-13.json`) postdates the disposition and
contains it directly: a May 18, 2026 docket entry disposing of the appeal, and a
June 22, 2026 "Judgment Issued" entry. I could not avoid seeing it while reading
the guaranteed-common input. Per the contract, I disclose this here and in
`flags.json`, and the analysis below reasons **only from the pre-decision record**
— the docket entries through the May 14, 2026 conference distribution — plus
general legal context. The evaluation should discount this cell accordingly. I
made no retrieval calls about this case beyond the provisioned inputs, precisely
to avoid compounding the exposure.

## The legal question

This is not a discretionary cert petition but a **direct appeal** under 28
U.S.C. § 1253 from a three-judge district court (convened under 28 U.S.C.
§ 2284 for a statewide legislative-apportionment challenge). The Mississippi
NAACP plaintiffs won below: the three-judge court found that Mississippi's
legislative maps diluted Black voting strength in violation of § 2 of the
Voting Rights Act and ordered remedial districts (decision of May 7, 2025).
The State Board of Election Commissioners and the Mississippi Republican
Executive Committee appealed by jurisdictional statement filed August 26, 2025.
The State's appeal presses, among other things, whether § 2 is privately
enforceable — the question on which the Eighth Circuit had split from every
other circuit — and attacks the merits of the § 2 results finding.

Because jurisdiction is mandatory, the Court cannot simply "deny." Its realistic
menu: **note probable jurisdiction** (plenary review), **summarily affirm**,
**dismiss** for want of a substantial federal question, or **vacate and remand
in light of an intervening decision** (the appeal analogue of a GVR).

## The record signals

1. **A textbook hold.** The jurisdictional statement was fully briefed by
   October 21, 2025 (motion to affirm by appellees, opposition by appellants)
   and distributed for the **November 21, 2025** conference. Then — nothing for
   nearly six months, followed by redistribution for the **May 14, 2026**
   conference. A fully briefed JS that sits undistributed through an entire
   winter and spring is being **held for a pending merits case**, and the
   obvious lead case is *Louisiana v. Callais*, the reargued § 2 redistricting
   blockbuster pending in October Term 2025. This appeal — a § 2 vote-dilution
   ruling against a State, with a private-right-of-action challenge attached —
   sits squarely in *Callais*'s shadow.
2. **Redistribution in mid-May 2026** is the classic signature that the lead
   case has come down (or is imminent) and the held case is being cleaned up.
3. **What happens to held cases.** When the lead case decides, held cases
   overwhelmingly receive a vacate-and-remand "for further consideration in
   light of" the new decision rather than plenary review or summary
   affirmance. Summary affirmance of a § 2 plaintiff win was unlikely while the
   Court was actively reshaping § 2 doctrine; a plenary grant on private
   enforceability was possible but the Court would more likely GVR the
   redistricting cases in bulk and take that question, if at all, in a clean
   vehicle later.

## Base rates and mapping

The statpack's modern discretionary-cert anchor (~5% grant rate, TO2025 slice)
is the wrong prior for a mandatory-jurisdiction appeal that has been *held*, so
I anchor on the hold-and-redistribute pattern instead; the statpack still
tempers the plenary-grant branch. This repo's disposition instrument
(`cert_signals.py`, ingest) deliberately places GVR-family orders — petition-
stage vacate-and-remand relief — on the **granted** side of the label space, so
that is the disposition I predict.

Pre-decision probability mass, as of May 13, 2026:

- Vacate and remand in light of *Callais* (GVR family → `granted`): **~0.58**
- Note probable jurisdiction (plenary → `granted`): **~0.10**
- Summary affirmance (→ `other` in this label space): ~0.18
- Dismissal: ~0.04
- Continued hold / anything else: ~0.10

## Bottom line

**Predicted disposition: granted** (a *Callais* GVR — judgment vacated and case
remanded — being the modal specific form), **granted = 1, P(granted) ≈ 0.68**,
confidence 0.55. No per-justice votes are predicted: hold-and-GVR orders are
unsigned, and any dissent-from-GVR pattern is not predictable from this record
with useful confidence.

Inputs used: the provisioned snapshot (pre-decision entries only, as reasoned
above), `events/evt-petition-disposition/event.yaml`, `record/context.json`,
`metrics/statpack.md`, and one `fedcourts query` priors pull (see
`retrieval.md`). No filed-document text was provisioned under
`record/documents/` for this cell, so the questions presented were not
directly readable; the analysis rests on the docket record and general
knowledge of the litigation.
