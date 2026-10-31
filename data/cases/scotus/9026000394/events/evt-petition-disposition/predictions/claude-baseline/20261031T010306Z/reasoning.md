# Reasoning — Herlihy v. DBMP, LLC (No. 26-394)

**P(grant) = 0.18.**

## Inputs read
- Snapshot `record/snapshots/2026-10-31.json` (forward mode, no cutoff).
- `record/documents/questions-presented.txt`, `petition.txt` (read the QP, introduction and reasons section), `appendix.txt` present (Fourth Circuit opinion, 167 F.4th 142, with Judge King dissenting; en banc denied) — not read in full.
- No brief in opposition: DBMP **waived** response on Oct 22, 2026; the Court then **requested a response** on Oct 30, 2026 (due Nov 30).
- `same-question.json`: empty list (nothing above the 0.5 threshold).
- `context.json`: band `baseline` (sal-v4), `cert_anchor.rate` = 0.0509 (10-Term lookback), distribution_count 1, no CVSG.

## Anchor
The frozen band anchor is ~5.1% (baseline band's `reached` rate, pooled). I start there.

## Adjustments up
- **Response requested** after a waiver: some chambers flagged the petition. Most such petitions are still denied, but it is a real step up from a baseline paid petition.
- **Amicus support**: five amicus filings at the petition stage (bankruptcy law professors, the asbestos claimants' committee, Prof. Rave, Public Justice, and a **coalition of states led by North Carolina**). The statpack's paid-segment amicus cut shows the 2+ bucket resolving granted 18.2% / gvr 4.5% (n=1,446 resolved), vs ~2% for 0. That cut is marginal and overlaps the relist/response signals, so I don't stack it fully on top of them.
- **Claimed circuit split** with the Third Circuit's *In re LTL Management* (2023) on whether a non-distressed Two-Step debtor files in good faith; the panel had a sharp dissent; top-tier Supreme Court counsel (Gupta Wessler); a national-importance issue that follows *Purdue Pharma* (2024) and *Truck Insurance* (2024), so the Court is engaged with mass-tort bankruptcy.

## Adjustments down
- **Posture**: this is a denial of stay relief under § 362(d) in a Chapter 11 case that is still pending (filed 2020). That is interlocutory, and the respondent will argue it is a poor vehicle for a good-faith question usually raised on a § 1112(b) motion to dismiss.
- **The split is debatable**: *LTL* dismissed under § 1112(b) on financial-distress grounds, on facts (J&J's funding agreement) the Fourth Circuit can distinguish. The BIO will say there is no square conflict, and the Fourth Circuit's § 524(g) reasoning was specific to asbestos.
- As I recall it, the Court has previously declined review in a Fourth Circuit Two-Step matter (*Bestwall*). I am not certain of the details and did not verify it here.

Net: about 18%. Roughly the 2+ amicus bucket's grant-only rate, and above the band anchor because of the response request, but held down by the vehicle and split problems.

## Increments
- Distributed once (for the 11/13/2026 conference). Because a response was requested and is due Nov 30, the petition will almost surely be redistributed once the response and any reply are in, so relist-increment = 0.95.
- CVSG: private parties only, but the U.S. Trustee/United States has an interest in bankruptcy-abuse questions and has litigated Two-Step matters. 0.10.

## Uncertainty
I have not read the response, because it doesn't exist yet. If the response concedes a real conflict, or if the Court relists after the response comes in, the odds rise sharply. Corpus query retrieval returned nothing on point. No MCP or web lookups.
