# Rationale for the numbers

**P(grant) 0.30; predicted disposition `denied`.**

## Anchor

`record/context.json` freezes `band: elevated` under `sal-v4`, Term 2025,
`distribution_count: 2`, no CVSG, mode `forward`. The statpack's "Segment
base rate by salience band (sal-v4)" table matches the context's salience
version, so I anchor on the elevated band's bracketed `reached` rate pooled
over the Terms strictly before OT2025 that the table renders (OT2017–OT2024):
**17.2% (n=2810)**. The relist-count cut (bucket 1: granted 8.2%, gvr 5.1%;
bucket 2: granted 27.8%, gvr 13.1%) and CVSG cut (`none`: granted 4.0%, gvr
2.3%) were read for shape only; they bucket by terminal count and this
petition's two distributions are not two conference considerations (below).

## Adjustments up

- **Response requested.** Respondents waived; the Court called for a
  response on April 30. That is an affirmative act of attention and the
  strongest single signal on the docket.
- **Companion vehicle on the same conference.** The BIO itself discloses
  United Biologics v. Amerigroup, No. 25-1388 (Sixth Circuit, the other side
  of the Illinois Brick lost-profits split); I confirmed from the public
  docket that it was distributed for the same 9/28/2026 conference (BIO filed
  Aug 17, reply Sep 2). The Sixth Circuit's rehearing denial carried a
  statement (Judge Bush) calling the disharmony appropriate for Supreme
  Court review and a concurrence (Judge Murphy, joined by Sutton and
  Kethledge) saying any change must come from this Court. A paired pair of
  petitions from opposite sides of an acknowledged split is the classic grant
  setup.
- **Counsel and amici.** Noel Francisco, Allon Kedem, John O'Quinn, Ashley
  Parrish for petitioners; two business amici (Chamber/NAM, EPSA) at the cert
  stage.
- **Stakes.** Four dominant manufacturers, a putative nationwide class, and
  the 340B contract-pharmacy channel the government itself litigated over
  (Novartis v. Johnson, Sanofi v. HHS).

## Adjustments down

- **The BIO's vehicle arguments are substantial.** On QP2 the panel used
  joint lobbying/PhRMA membership only as "further support" fifteen paragraphs
  into a holistic Twombly analysis that petitioners do not otherwise contest;
  every circuit including the Second agrees mere opportunity to conspire is
  not a plus factor. The amici brief only QP2, and the BIO makes that point.
  On QP1 respondents argue there was no overcharge at any level (petitioners
  "refused to transfer drugs to contract pharmacies" at any price), so the
  case may not present the relabeling question cleanly, and there is a
  preservation footnote.
- **Interlocutory posture and complexity.** Reversal of a Rule 12 dismissal
  in a 340B-structured market; the Court may prefer the cleaner Sixth
  Circuit vehicle and hold or deny this one.
- **Two vehicles, one grant.** If the Court takes only 25-1388, this docket
  is most likely held and later GVR'd or denied. A hold produces no
  disposition for months and, on this docket, a GVR (which counts as a grant)
  or a denial depending on how *Amerigroup* comes out.

Netting these, I move from 17% to 0.30. The single most likely outcome is
still non-grant, so `predicted_disposition` is `denied` and `granted` is 0.

## Claims

- `disposition` 0.30 (equals `probability`).
- `relist-increment` 0.55. The context's `distribution_count` of 2 counts the
  superseded 5/14 distribution (pulled by the response request) and the
  post-reschedule redistribution; the petition has not yet been considered at
  any conference. From a first-real-conference state with a CFR, amici, and a
  companion case, a further distribution is more likely than not, but a
  silent hold for 25-1388 (no new entry) or a clean October 5 denial are real
  paths, so I stay near even.
- `cvsg-increment` 0.20. Federal-program antitrust question, government
  litigated the underlying policies; but if a CVSG issues it may go to the
  companion only, and the pair is already positioned for decision.
- `summary-disposition-route` 0.25 (conditional on grant). Priced on the
  hold-then-GVR path; plenary is the likelier grant form.
- `dissent-from-denial` 0.12 (conditional on denial). Gorsuch's Illinois
  Brick skepticism in *Apple v. Pepper* makes a statement conceivable;
  paired-vehicle denials usually issue silently.

## Big case score 0.6

Stakes are real (multi-billion-dollar 340B channel, four major manufacturers,
Illinois Brick's scope) but the questions are pleading-stage antitrust
doctrine, not a constitutional headline.

## Inputs used and uncertainties

Snapshot `record/snapshots/2026-09-17.json` (14 docket entries, paid case,
Second Circuit No. 24-598, decision Aug 6, 2025, rehearing denied Dec 5,
2025); `documents.json` shows petition (39 pp.), BIO (44 pp.), and the QP
section all fetched with text, none truncated or `empty_text`. I read the QP,
the petition's Reasons for Granting and vehicle section in full, and the BIO's
Introduction, Statement summary, and both argument parts including the
"should not be held" section. I did not read the reply brief (not
provisioned) or the amicus briefs beyond their docket entries.

Main uncertainties: whether the Court sees 25-1388 or this case as the better
Illinois Brick vehicle; whether the hold path (which delays resolution and
may end in a GVR) dominates; and how much weight the CFR carries when the
respondent-side BIO is as strong on vehicle grounds as this one. Discount me
most on the relist claim, where the `distribution_count` semantics (two
entries, zero conference considerations) make the increment unusually hard
to price. Mode is `forward`; the 9/28 conference has not occurred, so no
disposition exists and nothing I retrieved touched this case's outcome.
