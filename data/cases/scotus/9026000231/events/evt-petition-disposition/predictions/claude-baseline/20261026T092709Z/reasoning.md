# Rationale — P(grant) = 0.22

**Anchor.** `context.json` freezes band `baseline` (sal-v4), with
distribution_count 1 and no CVSG. Pooling the statpack's "Segment base rate by
salience band (sal-v4)" bracketed `reached` figures for `baseline` over Terms
2017–2025, which are strictly before OT2026, gives roughly 5% (Term values
3.9–5.9%, n≈1,200–1,700 each). That is my starting point. The band reflects a
single distribution. It does not capture the strong case-specific signals
below, which is why I move well off it.

**Upward adjustments (from the provisioned petition, QP and snapshot):**
- **Response requested** (Sep 4, 2026) after the SG waived. At least one
  Justice wanted a closer look. Called-for responses are well known to raise
  grant odds severalfold above the paid-docket rate.
- **An acknowledged, outcome-determinative split.** The petition (pp. 11–17)
  quotes the government's court-of-appeals brief. The government urged the
  Sixth Circuit to reject the Ninth and Tenth Circuits' approach, and the Sixth
  Circuit acknowledged the conflict with *Vega* (Pet.App.25a). The government
  also did not dispute that the battery predicate fails under the Ninth and
  Tenth Circuit rule. That makes it a clean vehicle on the question as framed.
- **Elite counsel** (Lisa Blatt, Williams & Connolly, with the federal
  defender) and a cert-stage **NACDL amicus**.
- **The Court's appetite for ACCA questions.** It has granted many recent
  ACCA cases (*Borden*, *Wooden*, *Brown*, *Erlinger*, *Delligatti*).

**Downward adjustments:**
- The Court denied *Gomez* (No. 25-7193) in May 2026. The petition says the
  denial was "on other grounds", but it still shows a recent pass on adjacent
  terrain.
- The split runs across *different* state statutes. The SG will probably argue
  there is no square conflict on Florida § 784.041, and that *Delligatti* and
  *Stokeling* answer the question. Justice Thomas's *Borden* concurrence
  (which turns on intentional "use" of force) could also make the Court see
  little practical difference.
- The BIO has not been filed. I have no text of the government's actual
  position, and that is the largest single source of uncertainty. A BIO that
  concedes the split and importance would push me toward 35–40%. A strong
  vehicle or no-conflict argument would push me toward 10%.

**Increments.** relist-increment 0.96: a called-for response almost always
leads to redistribution after the BIO. cvsg-increment 0.005: the SG is a party,
so a CVSG is structurally near-impossible. summary-disposition-route 0.06: I
see no intervening decision, so any grant would be plenary.
dissent-from-denial 0.10: possible in a criminal-sentencing split case, but
most denials carry no writing. The order-writers figures are kept consistent
with that.

**Inputs read.** The snapshot `2026-10-26.json`, `context.json`,
`questions-presented.txt` and `petition.txt` (full, not truncated). I did not
read `appendix.txt` in depth. No BIO or reply exists yet. Figures quoted from
the petition are the petitioner's characterization and were not independently
verified.
