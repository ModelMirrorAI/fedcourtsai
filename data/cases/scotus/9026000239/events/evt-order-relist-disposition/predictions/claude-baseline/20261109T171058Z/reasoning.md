# Rationale: P(grant) = 0.90

**Anchor.** `record/context.json` freezes band `federal` under `sal-v8`. Its `cert_anchor.rate` is 0.731, the pooled `reached` rate for federal-petitioner paid petitions over the 10 prior Terms. The statpack's sal-v8 table shows Term rates between 47.6% and 96.3% (n between 12 and 43 per Term). The relist-count cut, pooled across all Terms, is a cross-check. The grant family (granted + gvr) is about 41% in the 2-distribution bucket (n=495 resolved) and about 37% in the 3+ bucket (n=483). That covers all paid petitioners and counts reschedules as relists, so it reads low for an SG petition.

**Upward adjustments:**
- The SG is seeking review of a published D.C. Circuit decision that invalidated a presidential proclamation and left nationwide classwide relief in place. The Court grants nearly every SG petition in which a court of appeals has struck down a major federal policy.
- The petition draws real support: 22 States and three other amici.
- The posture already reflects split views below. A stay panel partially stayed the district court's order over Judge Pillard's separate writing (petition, around text lines 640–680), and the mandate has been stayed. The remedial questions (1252(f)(1), Rule 23(b)(2) classes after Trump v. CASA) recur.
- The corpus query shows the current Court's pattern of granting after a single relist. For example, DOJ v. McNutt (26-204), an SG petition, was granted 10/19/2026 at distribution_count 2.

**Main risk.** The Court might prefer to wait or hold, or use a related vehicle. I found no Vide-linked or same-question petitions: `same-question.json` lists none above threshold. The BIO argues the statutory question is easy and the remedial questions are fact-bound. Neither argument usually defeats an SG petition of this magnitude. There is a small chance of a narrowed grant. That would still count as a grant.

**Inputs read:** the snapshot (2026-11-09.json), context.json, the QP, petition and BIO (QPs, table of contents and argument structure), lower-court-docket.txt (rehearing en banc denied with no noted dissent) and the statpack. I did not read decision-below.txt in depth and relied on the petition's account of the proceedings below. There was no MCP or web retrieval.

**Claims.**
- relist-increment 0.20: a grant at the 11/13 conference ends distributions.
- cvsg-increment ~0: the federal government is the petitioner.
- summary route 0.04.
- dissent-from-denial 0.65: conditional on a rare denial, a dissent from the government-aligned Justices is likely.
