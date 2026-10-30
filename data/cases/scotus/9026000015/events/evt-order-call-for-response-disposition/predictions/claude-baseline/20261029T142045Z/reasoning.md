# Why P(grant) = 0.14

**Inputs read.** Snapshot `2026-07-31.json` (cut at the response-requested day),
`context.json` (mode `forward`, band `baseline` under `sal-v4`,
distribution_count 1, no CVSG, term 2026), and the provisioned
`questions-presented.txt`, `petition.txt` (truncated at the cap) and
`appendix.txt` (truncated). No brief in opposition exists yet.

**Anchor.** The sal-v4 segment table's `baseline` bracketed `reached` rate,
pooled over Terms 2017–2025 (strictly before OT2026), is about 5%
(roughly 660 grants over ~12,900 weighted petitions; per-Term 4.0%–5.9%).
The band is the weakest one and was frozen before the call for response.

**Adjustments up.**
- The Court *called for a response* after the City waived. No committed table
  conditions on this; my judgement is that a call roughly doubles-to-triples
  the paid-petition rate, though most called-for petitions are still denied.
- Amicus support is heavy: the live docket (forward-mode retrieval, past my
  baseline) shows twelve amicus briefs filed Aug 3–31, 2026, from religious
  liberty groups across faiths and tribal organizations. The statpack's
  `2+` amicus bucket (n≈1,449 resolved) grants ~18% plus ~4.5% GVR — a
  population shape, not a conditional on my state.
- Six Fifth Circuit judges noted dissent from denial of rehearing en banc
  (Judge Oldham writing), and Judge Higginson dissented at the panel stage
  three times. The petition alleges two circuit splits (substantial burden
  where alternative locations exist; least-restrictive-means after
  pre-litigation notice). Religious liberty is an area this Court takes up
  regularly. Counsel is a law-school religious-liberty clinic.

**Adjustments down.**
- **Vehicle.** The ruling is on a preliminary injunction (interlocutory), and
  the panel's principal analysis is under Texas RFRA — state law. The petition
  argues the federal Free Exercise analysis was incorporated, but the Court can
  easily see the state-law ground as independent. The City will press both.
- Possible mootness or changed facts if the park work (tree removal,
  anti-nesting deterrence) has proceeded; I did not verify the project's status.
- The Court denied review in the Apache Stronghold sacred-site case (2025)
  over a written dissent, which suggests a majority does not want this line of
  sacred-site cases now. QP 1 framed as "courts overriding theological judgment"
  is broad and less tidy than a clean statutory split.

Net: roughly 3× the anchor, giving 0.14. The grant family includes a GVR, which I
rate unlikely (no obvious intervening decision).

**Other claims.** relist-increment 0.97 (redistribution after the BIO is
essentially mechanical; the harness masks it on this moment). cvsg-increment
0.02 (no federal interest). summary-disposition-route 0.08 conditional on a
grant. dissent-from-denial 0.40 conditional on a denial. Gorsuch wrote the
Apache Stronghold dissent and this petition's twelve amici and en banc dissent
make a written dissent more likely than usual. order-writers is consistent
with that: Gorsuch 0.32, with smaller weights on Thomas, Alito and Sotomayor
(Sotomayor has written on Native American religious claims).

**Where to discount me.** I have not read the City's brief in opposition, which
is not filed yet. I relied on the petition's characterization of the record. The
call-for-response uplift is judgement, not a committed figure. I recognize the case
from the 2024 Fifth Circuit proceedings but have no knowledge of a disposition
of this petition. The live docket (fetched 2026-10-29) shows it still pending.
