# Rationale — P(grant) = 0.07

**Anchor.** `record/context.json` freezes `band: elevated` under `sal-v3`,
Term 2025, `mode: forward`, `distribution_count: 2`. The statpack's "Segment
base rate by salience band (sal-v3)" table matches the context's salience
version, so per the contract I anchor on the elevated band's bracketed
`reached` rate pooled over Terms strictly before 2025. Pooling 2017–2024
(denominators 3419, numerators ≈ 693) gives ≈ **20.3%**. That is the
yardstick my skill is scored against.

**Why I sit well below the anchor.** I committed 0.07 — roughly a third of
the band rate — for reasons specific to this record:

1. **The elevated band appears to rest on an inflated distribution count.**
   The frozen `distribution_count` of 2 counts the May 26 distribution of
   the *sealing motion* (25M86) alongside the petition's own June 24
   distribution for the September 28 long conference. The petition has never
   been considered at a conference and never relisted; the conference it is
   distributed for postdates the snapshot. A true once-relisted elevated
   petition carries real Court-attention signal; this one carries none yet.
   I use the frozen band as instructed (it is the scoring baseline) but
   discount the underlying signal heavily. Flagged in `flags.json`.
2. **Respondents waived their response.** The Court does not grant against a
   waiver, so a grant requires the extra step of a CFR, and Vizient's
   sophisticated counsel judged the petition low-threat enough to waive. No
   CFR has issued in the eight weeks since.
3. **The asserted split is soft.** The petition's split rests on the two
   fractured majority opinions in *Whole Foods* (D.C. Cir. 2008) — which the
   Fifth Circuit expressly noted are "nonbinding even within that Circuit" —
   plus *Newcal* (9th Cir. 2008), a Third Circuit case that affirmed a
   market *rejection*, district-court decisions, and the Merger Guidelines.
   That is an approach-level tension, not a crisp holding-level conflict,
   and it has persisted since 2008 without the Court taking it.
4. **Vehicle problems.** Fact-heavy summary-judgment posture where the
   question is how to weigh record evidence; a partially sealed record; a
   private dispute with a single amicus filed by a solo practitioner.

**What pushes the other way** (and keeps me at 0.07 rather than the ~2%
whole-docket paid rate): the CA5 opinion is published and precedential
(164 F.4th 405) and expressly declines to follow the D.C. Circuit's
core-consumer approach, which is the kind of acknowledged methodological
divergence that occasionally draws a CFR and a look; market definition is
outcome-determinative across modern antitrust litigation and the Court has
not spoken to Brown Shoe submarkets in decades; competent appellate counsel;
paid petition. The Court's June 2026 grant in *Apple v. Epic Games*
(25-1311, surfaced in my corpus query) shows appetite for antitrust, though
on different questions — I read it as roughly neutral for a second,
lower-profile market-definition case.

**Claim numbers.**
- `disposition` 0.07 — as above; essentially all grant mass is plenary.
- `relist-increment` 0.30 — P(any distribution past the frozen count of 2).
  Dominated by the CFR path (~25%) plus a conference relist without CFR
  (~5%). The statpack's relist cut (74% of the paid scored segment ends at
  relist-0) buckets by terminal count, so I treated it as shape, not as this
  state's forward hazard; being in the elevated band argues for somewhat
  more attention than the raw segment.
- `cvsg-increment` 0.04 — private antitrust suit, no response even called
  for yet; the paid-segment CVSG cut shows how rare CVSGs are (173 of
  ~13.6k), and I sit modestly above that unconditional rate because
  antitrust/market-definition is a recurring CVSG subject.
- `summary-disposition-route` 0.03 (conditional on grant) — no intervening
  decision to GVR against; not a summary-reversal shape.
- `dissent-from-denial` 0.05 (conditional on denial) — above the background
  rate for silent denials but low; no Justice has been writing at the
  denial stage on market definition.

**Uncertainties / where to discount me.** I have not seen the Fifth
Circuit's opinion itself, only the petition's characterization of it — if
the panel's rule is less absolute than the petition claims, the split
argument weakens further; if it is as stark as claimed, a CFR is more
likely than my 25%. The sealed portions of the record are redacted in the
provisioned petition text, so I cannot judge how strong the core-customer
evidence actually is. My relist-increment number is the least anchored: no
published cut conditions on "distributed for the long conference with a
waiver on file," so 0.30 is judgment, not arithmetic. Retrieval was light
by choice (one corpus query beyond the provisioned inputs); the MCP server
was available but I did not use it.
