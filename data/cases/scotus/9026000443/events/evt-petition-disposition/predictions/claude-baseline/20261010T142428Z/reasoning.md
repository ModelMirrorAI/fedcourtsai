# Rationale for the numbers

## What the record shows

- Paid petition from the Eleventh Circuit's published opinion in *Drummond v.
  Southern Co. Services*, 177 F.4th 1076 (May 26, 2026), rehearing denied
  August 6, 2026, which **reversed** a Rule 12(b)(6) dismissal and sent the
  class action back for further proceedings. Interlocutory posture.
- Petitioner is a private employer and its plan (Jones Day as counsel), so the
  caption class is `private` and `context.json`'s band is `baseline`,
  `distribution_count` 1, no CVSG, forward mode, `sal-v4`.
- Respondents (Stris & Maher) **waived** a response on October 2; distributed
  October 7 for the November 6 conference.
- The petition's own lead request is a **hold** pending *FedEx v. Watt*,
  No. 26-360, and *Kellogg/Reichert*, No. 26-387, both from the Sixth
  Circuit's divided decision in *Reichert v. Kellogg Co.*, 170 F.4th 473
  (6th Cir. Mar. 16, 2026) (Stranch, Bush; Nalbandian dissenting; en banc
  denied May 15, 2026). The alternative request is a plain grant.
- The questions-presented file and the full petition text were provisioned
  (`documents.json`: both `empty_text: false`, 25 pages, not truncated). No
  brief in opposition exists because of the waiver.

## Anchor

Cert stage, `band: baseline` under `sal-v4`, which matches the statpack's
"Segment base rate by salience band (sal-v4)" table, so the anchor is the
**bracketed `reached`** figure for `baseline` pooled over the Terms strictly
before OT2026 that the table renders (OT2017 to OT2025): the per-Term figures
run 3.8% to 5.9% on denominators of roughly 1,200 to 1,700 each, pooling to
about **5%**. For reference only: the relist-count cut's relist-0 bucket (a
terminal count, not my state) shows grant 1.2% plus GVR 0.5%, the relist-1
bucket grant 8.2% plus GVR 5.1%; the CVSG-none bucket grant 3.9% plus GVR 2.3%;
the ca11 originating-circuit cut grant 1.6% plus GVR 1.9%.

## Adjustments

**Up, and the only thing that matters: the hold linkage.** This petition's
disposition is mechanically coupled to Nos. 26-360 and 26-387. In this
pipeline a GVR is a grant, so P(grant here) is roughly
P(lead petitions granted) x [P(consolidation) + P(reversal) x P(GVR follows)].
I retrieved both lead dockets from supremecourt.gov (forward mode, public
information predating my snapshot): respondents waived in both (September 24
and 25), no distribution or amicus entries showed yet, counsel are Morgan Lewis
and Jenner & Block for petitioners, Motley Rice and Stris & Maher for
respondents. The corpus also carries both as open `evt-petition-disposition`
events, so their cells are being predicted in parallel.

My estimate of the lead petitions' grant chance is about **0.17**. For: a
recurring pure statutory question, a dissent below, two circuits now imposing
the requirement, heavyweight counsel, very large aggregate stakes, and a Court
that has recently taken ERISA text cases (*Cunningham v. Cornell*, *M&K
Employee Solutions*). Against, and heavier: **no circuit split** (the Sixth and
Eleventh Circuits agree; the only contrary rulings are district-court, e.g.
the April 2026 *Intel* summary judgment in the Northern District of
California, which could ripen into a Ninth Circuit split the Court might
prefer to wait for); **interlocutory posture** in all three cases (reversals of
dismissals); and **waivers from every respondent**, which means the Court would
first have to call for a response before any grant, a step it takes in a
minority of waived paid petitions. Conditional on a lead grant, I put reversal
at about 0.57, a GVR of this docket following a reversal at about 0.9, and a
consolidation grant at about 0.1. That yields about 0.17 x 0.56 = 0.095, plus a
sliver for an independent grant of this petition, so **P(grant) = 0.10**, about
twice the band anchor.

**Down, relative to the petition's own framing.** The petition presents no
split and asks principally for a hold, which concedes it is not the vehicle.
The Eleventh Circuit opinion is long (sixty-odd pages in the appendix) and
reasons from actuarial practice, IRS interpretation and purpose, so a
summary reversal of this docket on its own is not a realistic route.

## The other claims

- `relist-increment` 0.60: the leads waived in late September and will reach a
  conference in the same window as this petition's November 6 conference. If
  the Court denies all three off the first conference that holds them all,
  the count here stays at one; if the leads land a week or two apart from this
  one, or the Court calls for a response in the leads, this docket is
  redistributed before disposition. The corpus GVR priors I pulled (OT2025
  held-then-GVR'd petitions) all carry two to four distributions, which is
  the shape of the hold branch.
- `cvsg-increment` 0.04: a CVSG, if any, issues in the lead dockets; the
  Court only occasionally lists companion petitions in the same order.
- `summary-disposition-route` 0.80: conditional on any grant, the GVR branch
  dominates the consolidation branch by about four to one on the arithmetic
  above.
- `dissent-from-denial` 0.05: any writing would attach to the lead docket,
  and no-split denials of this kind rarely draw one.

## Uncertainty and where to discount me

- The biggest sensitivity is P(lead grant). A reader who believes the Court
  will take the actuarial-equivalence question this Term without a circuit
  split should roughly double my number; one who weighs the waivers and the
  interlocutory posture more heavily should halve it.
- I could not see whether amicus briefs supporting the lead petitions are
  coming (due around October 16 and 22); a wave of industry amici would raise
  the lead grant chance and hence this one.
- The merits-reversal probability (0.57) is a judgment call about a
  textualist majority facing a term-of-art argument; it only matters inside
  the grant branch.
- No MCP degradation: CourtListener answered, but it holds no SCOTUS dockets
  for these numbers, so the lead-docket facts came from supremecourt.gov via
  web fetch.
- I did not encounter this case's own disposition anywhere; the petition is
  eight days old and undistributed until October 7.
