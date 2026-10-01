# Rationale for the numbers (claude-baseline, run 20260930T191800Z)

**P(grant) = 0.08; predicted disposition denied.**

**Anchor.** `record/context.json` freezes `band: elevated` under `sal-v4`, Term 2026, `distribution_count: 2`, no CVSG, mode `forward`. The statpack's "Segment base rate by salience band (sal-v4)" table matches the context's salience version, so the band anchor applies. Pooling the bracketed `reached` figures for `elevated` over the nine rendered Terms strictly before 2026 (OT2017 through OT2025) gives roughly 521 grants over a weighted risk-set denominator of about 3,085, or about 16.9%. That is my starting point, and the yardstick the evaluator will score this cell against.

**Why I move far below the anchor.** The case-specific evidence is unusually strong and points one way.

1. *Slaughter decided the question presented.* The provisioned brief in opposition reports, and I confirmed from the opinion text via CourtListener, that Trump v. Slaughter (decided June 29, 2026) overruled Humphrey's Executor and held that enforcing statutes through in-house adjudication "is executive." The petition was filed two days earlier and asked, in the alternative, for the Court to wait for Slaughter. The wait is over and the answer cuts against petitioner. The majority even cited the district court's Wilcox opinion as an example of Humphrey's indeterminacy ("Does it protect all multimember agencies?").
2. *The companion petition was denied.* Harris v. Bessent, No. 25-1110, arose from the same consolidated D.C. Circuit opinion, concerned the MSPB (a body at least as adjudicatory as the NLRB), made the same "purely adjudicatory" and "sever the tipping powers" arguments, and was denied on June 30, 2026, the day after Slaughter, without a GVR. This is the closest possible comparator and it resolved as a denial.
3. *The judgment below already agrees with Slaughter.* A GVR asks a lower court to reconsider in light of a decision that might change its result. The D.C. Circuit ruled for the government; Slaughter reinforces that ruling. There is nothing to remand for.
4. *The Court's own prior words.* In staying the district court's judgment in May 2025 the Court said the NLRB wields "considerable executive power." The BIO quotes that line back.
5. *The Solicitor General opposes.* The government waived, then, when asked, filed a 12-page BIO asking for denial or, alternatively, summary affirmance, and arguing expressly against a GVR.

**Why I do not go to the floor.** Three things keep the number above the low single digits.

- *The Court called for a response.* After the government waived, the Court requested a response on August 13. A CFR means at least one Justice wanted the SG's post-Slaughter position on file before acting, which is more attention than a routine denial gets. I read it mostly as the Court's care with a case it has now seen four times (stay, cert before judgment, Slaughter amicus, this petition), not as appetite for a grant, but it is a real signal.
- *Slaughter reserved an adjudicatory question.* The majority said tenure protections for "non-Article III courts, such as the Tax Court and the Court of Federal Claims" pose "a different set of questions" and left them for another day. The petition's whole theory is that the Board, bifurcated from the General Counsel by Taft-Hartley, is a court-like adjudicator. Four Justices could in principle want to define that boundary now; the Sotomayor dissent explicitly names the NLRB as an open case. I think the Harris denial shows the Court does not want to, but the door is not fully shut.
- *Summary affirmance.* The SG invited a grant-and-summarily-affirm, which would register as a grant on the binary axis. The Court very rarely does this on a cert petition, but the invitation is on the record.

Netting these, I land at 0.08, roughly half the anchor's distance to zero from the band rate, weighted heavily by the Harris comparator. I would not defend anything above 0.15.

**Claims.**
- `disposition` 0.08, restating the above.
- `relist-increment` 0.35. The docket shows two distributions, but the second is a redistribution after the requested response, so the petition has not yet been to conference. The forward hazard from this state is mostly the chance of a one-cycle relist while a Justice writes about the denial, plus a small chance the Court holds it for something. The statpack's relist cut buckets by terminal count and is not a lookup for this hazard; I used it only for shape (most petitions never relist).
- `cvsg-increment` 0.01. The SG is the respondent.
- `summary-disposition-route` 0.7 conditional on a grant, because both sides' alternative asks are summary forms and a plenary grant is the least likely grant path.
- `dissent-from-denial` 0.25 conditional on denial; reasoning in `predicted_reasoning.md`. I am least sure of this number: the Slaughter dissenters flagged the NLRB question but also let Harris go, and I could not learn whether Harris's denial carried a writing.

**Big case score 0.5.** Stakes if decided are real (the independence of the agency that adjudicates private-sector labor law, in a case the Court has already stayed once), but the marginal doctrinal significance after Slaughter is a carve-out question, and the practical outcome is largely foreordained. Not grant likelihood.

**Inputs used.** Snapshot `record/snapshots/2026-09-30.json` (the file `context.json` names). Provisioned documents: `questions-presented.txt`, `petition.txt` (29 pp., full text), `brief-in-opposition.txt` (12 pp., full text); `documents.json` shows none empty or truncated. No reply brief or Rule 15.8 supplemental brief appears on the docket as of the snapshot, although the petition promised one after Slaughter. Statpack: modern-cert base rate, relist and CVSG cuts, originating-circuit cut (CADC petitions grant at about 5.5% plus 2.3% GVR, the highest of any circuit, consistent with an elevated anchor), and the sal-v4 band table. Corpus queries and CourtListener retrieval are listed in `retrieval.md`.

**Where to discount me.** I could not confirm whether any Justice wrote on the Harris denial, and I did not retrieve the Court's June 30 order list. The Slaughter opinion text I read came from the CourtListener opinions endpoint's plain-text field after the MCP document reader reported no text; I read the syllabus and keyword passages, not the full 227,000-character opinion. If the Court's practice is to grant-and-summarily-affirm more often than I believe in mop-up cases after a landmark, my grant number is too low. Everything I relied on predates the September 30 snapshot; the petition's disposition does not yet exist (the conference is October 16, 2026), so nothing outcome-revealing was available to leak.
