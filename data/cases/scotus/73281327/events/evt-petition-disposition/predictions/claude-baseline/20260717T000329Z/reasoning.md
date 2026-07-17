# Pileggi v. Washington Newspaper Publishing Co., LLC (No. 25-1040) — petition disposition

**Prediction: GVR (granted=1), P(any grant, GVR included) = 0.52.**

## The legal question

Whether "goods or services from a video tape service provider," in the Video
Privacy Protection Act's definition of "consumer" (18 U.S.C. § 2710(a)(1)),
covers **all** of a provider's goods or services or only its **audiovisual**
goods or services. Pileggi subscribed to the Washington Examiner's free email
newsletter; the site's Meta Pixel allegedly disclosed her video-viewing URLs
plus Facebook ID to Facebook. The district court dismissed and the D.C.
Circuit unanimously affirmed (146 F.4th 1219, Aug. 12, 2025; rehearing denied
Sept. 30, 2025), adopting the narrow "audiovisual goods or services" reading —
joining the Sixth Circuit (*Salazar v. Paramount Global*, 133 F.4th 642)
against the Second (*Salazar v. NBA*, 118 F.4th 533) and Seventh (*Gardner v.
Me-TV*, 132 F.4th 1022).

## Why this cell is really a prediction about *Salazar*

The controlling fact — stated on the face of both provisioned briefs — is that
the Court **granted certiorari on this exact question on January 26, 2026, in
*Salazar v. Paramount Global*, No. 25-459**. Both sides ask for a hold:

- The petition (filed Feb. 27, 2026) expressly requests hold-then-GVR in light
  of *Salazar* (Pet. 1, 11–13).
- The brief in opposition (Apr. 3, 2026) **agrees the petition should be
  held**, asking for denial if the Sixth Circuit is affirmed and conceding a
  GVR is appropriate if it is reversed (BIO 1, 11), with remand for its
  preserved alternative grounds (including Judge Randolph's
  not-a-video-tape-service-provider concurrence).

The docket behavior confirms the hold: distributed April 22 for the **May 14,
2026 conference**, and — as of the July 16, 2026 snapshot — no order issued.
A petition considered at a mid-May conference that neither appears on the next
order lists nor by the Term's end cleanup is being **held** for the lead case.
*Salazar* (granted late January) will be argued in fall 2026 and decided by
roughly June 2027; this petition will then be disposed of in its light.

So the disposition space collapses to:
- **Salazar (petitioner) wins** (broad reading) → GVR of the D.C. Circuit's
  judgment, which rests solely on the "consumer" holding. Both parties agree
  this is the right disposition in that branch, and GVR of held
  same-question petitions is standard practice.
- **Paramount wins** (narrow reading affirmed) → outright denial: the D.C.
  Circuit already applied the narrow rule, so there is nothing to reconsider.
- Small residual: dismissal (settlement), a DIG or fractured non-decision in
  *Salazar* (likely followed by denial here or a further hold).

## Handicapping *Salazar*

- **Reversal prior:** the Court reverses in roughly two-thirds of plenary
  merits cases, and it took the case from the narrow-reading side of the split
  while leaving the Second and Seventh Circuits' broad-reading decisions in
  place. Petitioner Salazar also has a straightforward plain-text argument:
  § 2710(a)(1) says "goods or services," where Congress elsewhere in the same
  statute said "audio visual materials" when it meant that (the
  meaningful-variation point).
- **Countervailing lean:** the current Court has repeatedly refused to read
  penalty-laden statutes to cover sweeping modern applications (*Van Buren*,
  *Dubin*, *Fischer*, *Snyder*). The broad reading turns any newsletter
  sign-up at any video-carrying website into a $2,500-per-disclosure class
  claim — exactly the "general internet privacy statute" transformation the
  D.C. Circuit's five textual/structural reasons resist. That gives the
  respondent side a better-than-usual shot at affirmance.

Netting these, I put *Salazar* reversal (petitioner-favorable) at ~0.55.
P(grant here) ≈ 0.55 × ~0.95 (GVR follows reversal; small tail for
settlement/DIG paths) ≈ **0.52**, with predicted disposition **gvr** as the
single likeliest label. Note the distribution is bimodal — essentially
GVR-or-denied — so `gvr` is a plurality call, not a high-confidence mode.

Base-rate context from the committed statpack: the modern discretionary-cert
grant rate is ~2.5–3%, and D.C. Circuit-originating petitions grant at ~12%
(denial-reweighted). This petition sits far above those anchors because the
hold is already observable and the grant channel (GVR) does not require four
votes for plenary review of this case on its own — only that the lead case
come out petitioner's way.

## Votes and stakes

No per-justice votes predicted: a GVR/denial-of-a-held-petition is an
unsigned, typically unanimous order, and the meaningful vote split belongs to
*Salazar*, not this docket. Big-case score 0.2: the underlying VPPA question
has real commercial stakes for the media/advertising industry, but this
petition itself is a companion whose disposition will be a one-line order.

## Inputs used

Provisioned snapshot (2026-07-16), `questions-presented.txt`, `petition.txt`
(truncated at 137 pp.; QP, introduction, statement, and reasons sections
read), and `brief-in-opposition.txt` (full 17 pp.). The BIO's concession that
a hold is proper — and that a GVR should follow a *Salazar* reversal — is the
single most probative fact in the record. Corpus statpack consulted for base
rates; corpus `query` retrieval returned no topical priors (see
`retrieval.md`).
