# Reasoning — P(grant) = 0.07

**Inputs read.** Snapshot `record/snapshots/2026-10-10.json` (forward mode,
no cutoff), `record/context.json` (band `baseline` under `sal-v4`,
distribution_count 1, no CVSG, Term 2025), and `record/documents/petition.txt`
plus `questions-presented.txt` (text extracted, not truncated). No BIO has been
provisioned because none has been filed: the response is due 2026-10-30.

**Anchor.** In the statpack's "Segment base rate by salience band (sal-v4)"
table, the `baseline` column's bracketed `reached` rate for Terms strictly
before 2025 (2017–2024) runs from 4.5% to 5.9%. The pooled figure is about 5.3%,
on roughly 1,200–1,700 weighted petitions per Term. The heading's version
matches my context, so this is my anchor.

**Adjustments up.**
- The Court *requested a response* after the first conference. That means at
  least one chambers looked at the petition. Requests are common, though, and
  apparently not enough by themselves to lift the band above `baseline`.
- The petitioner is represented by Sidley's appellate group, and the American
  Bankers Association filed an amicus brief in support.
- The issue sits in the Court's own Kindred/Concepcion/Imburgia line. A
  facially arbitration-only rule is the kind of target the Court has reversed
  before, in Kindred and Imburgia.
- The petition claims a lopsided split: the Fourth Circuit against the First,
  Second, Third, Sixth and Eighth Circuits.

**Adjustments down.**
- The opinion below is an **unpublished** per curiam that simply applies circuit
  precedent (*Johnson*, *Noohi*). That makes it a thin vehicle.
- The split is less clean than the petition presents it. The cited cases are
  old (1989–2011), several of them only say a separate-consideration rule
  "might risk" preemption, and the Fourth Circuit's holding rests partly on the
  change-of-terms clause making the arbitration promise illusory. Respondents
  can frame that as a generally applicable contract defense.
- **The companion petition is gone.** *Johnson v. Continental Finance*
  (No. 25-34) was the published Fourth Circuit decision applying the same rule.
  A web search turned up the parties' joint stipulation to dismiss it under Rule
  46.1, filed on the supremecourt.gov docket on 2026-05-05. That predates my
  snapshot, so it is legitimate forward signal. The same week (May 4–5), this
  case's respondents asked for and received a near-six-month extension "with
  petitioner's consent." The two cases appear to share plaintiff-side posture
  and the same Maryland rule. My reading is that settlement talks are under way
  here too, and I put about 30% on this petition ending in a Rule 46 dismissal.
  That counts as no grant. This is inference from docket timing, not a
  disclosed fact.
- If the case does go forward, P(grant) is perhaps 10%. Combined with the
  dismissal risk, that gives about 0.07.

**Claims.**
- *relist-increment, 0.65.* If a BIO is filed, the petition will be
  re-distributed, which is near-certain conditional on the case proceeding.
  The main risk is settlement.
- *cvsg-increment, 0.03.* This is private-party FAA litigation with no federal
  interest flagged.
- *summary-disposition-route, 0.10.* This is conditional on a grant. A summary
  reversal of an unpublished per curiam applying binding circuit precedent is
  possible but unlikely, and there is no intervening decision to support a GVR.
- *dissent-from-denial, 0.04.* Statements on a denial in a private arbitration
  case are rare.

**Uncertainties and discounts.** I have not seen the BIO, which does not exist
yet. My settlement inference rests on timing alone. My big-case score is
moderate: the rule affects consumer-credit arbitration in Maryland and
possibly other states, but it is one state's doctrine.

**Retrieval degradation.** CourtListener's docket-entries endpoint returned no
entries for No. 25-34, so I took its status from a web search result.
