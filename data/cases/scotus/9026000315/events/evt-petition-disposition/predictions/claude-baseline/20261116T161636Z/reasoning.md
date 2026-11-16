# Reasoning — Goldman v. Phillips, No. 26-315 (cert, distribution moment)

**P(grant) = 0.17; call: denied.**

## What I read
- Snapshot `2026-11-16.json`: paid petition from an en banc Ninth Circuit decision (May 7, 2026); one amicus brief (four retired bankruptcy judges and a law professor) filed Sept. 24; distributed once, for the Nov. 13 conference; on Nov. 4 the Court **requested a response** (due Dec. 4, 2026). No brief in opposition, no waiver entry, no CVSG.
- `questions-presented.txt`, `petition.txt` (read the front matter, introduction and statement), `appendix.txt` (skimmed the en banc opinion). No BIO exists yet, so I have only one side.
- `context.json`: band `baseline`, `distribution_count` 1, `cert_anchor.rate` 0.052, `cert_amicus_line` (arm `some`) 0.163. `same-question.json` lists no matching petitions.

## Anchor and adjustments
- Anchor: the frozen baseline-band reached rate, 5.2%.
- Up: the Court called for a response. That removes the large mass of petitions denied without anyone looking twice; my own rough sense is that called-for-response paid petitions are granted at something like twice the paid rate. No committed table conditions on it, so this is judgement.
- Up: the petition's features are those of a credible grant candidate — a claimed three-way split (negligence: CA9 and three others; willful and deliberate: four circuits; gross negligence: CA5) that courts and treatises have acknowledged for decades; an en banc decision below; an experienced Supreme Court specialist as counsel of record; a cert-stage amicus brief from retired bankruptcy judges. The harness's amicus-arm reference rate (16.3%, n=2,315) points the same way, though the prompt warns it likely runs high for a weak band.
- Down: vehicle. The en banc opinion, as I read it, is mostly about the immunity framework (quasi-judicial and "derived" immunity) and reverses a pleading-stage dismissal and remands; the negligence standard is restated as longstanding circuit law rather than being the centre of the decision. The case is interlocutory, and the trustee may still win on remand. A competent BIO will press all of that, and will likely argue the split is stale and shallow in practice (many of the cited cases are from the 1970s–1990s, and the split has survived a long time without the Court taking it). The QP is also worded broadly ("whether ... and if so, under what standard"), which is not fatal but is not tidy.
- Down: a real chance of a CVSG (the U.S. Trustee Program supervises Chapter 7 trustees), which delays and does not by itself mean a grant.

Net: about 17%, roughly three times the band anchor and in line with the amicus-arm reference. I would not go above ~25% without seeing the BIO; I would not go below ~10% given the response request plus an acknowledged split and en banc posture.

## Other claims
- `relist-increment` 0.97: the petition must be redistributed once the response is in; only a withdrawal/dismissal before then avoids it.
- `cvsg-increment` 0.12: bankruptcy questions with a federal programme interest draw CVSGs more than most, but the base rate is about 1% of paid petitions.
- `summary-disposition-route` 0.05 (given a grant): no intervening decision to GVR on; a grant here would be plenary.
- `dissent-from-denial` 0.03 and low `order-writers` numbers: a technical bankruptcy question rarely draws a writing on denial.

## Retrieval and limits
One corpus query (generic recent grants; not informative for this case) and the committed statpack. No CourtListener or web lookups. I did not check the petition's characterisation of the other circuits' case law independently; my read of split depth rests on the petition alone, which is advocacy. Discount accordingly.
