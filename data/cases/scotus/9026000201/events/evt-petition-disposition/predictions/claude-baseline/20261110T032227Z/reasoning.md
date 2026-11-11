# Reasoning — FTC v. National Horsemen's Benevolent & Protective Ass'n, No. 26-201

**P(grant) = 0.93.**

## Anchor
`record/context.json` freezes band `federal` (sal-v8) with `cert_anchor.rate` = 0.731 (ten prior Terms, reached rate). The statpack's per-Term `federal` column (2017–2025) ranges 47.6%–96.3%, consistent with that pooled figure. That is my starting point.

## Why well above the anchor
- **The Solicitor General is the petitioner, and a federal statute has been held unconstitutional.** The Fifth Circuit (decision-below.txt, Duncan, J., June 11, 2026, on remand after the 2025 GVR in light of *FCC v. Consumers' Research*) reissued its holding that HISA's enforcement provisions violate the private nondelegation doctrine. The Court almost always reviews a court of appeals decision that invalidates an Act of Congress when the SG asks it to.
- **Split.** The petition (petition.txt) and the decision below both acknowledge the conflict with the Sixth Circuit's *Oklahoma* decisions, which upheld the Act. A footnote in the decision below also notes the Eighth Circuit's earlier contrary *Walmsley* ruling, which was itself GVR'd.
- **Every side wants a grant.** The cert reply (cert-reply.txt) states that all respondents (Gulf Coast, Texas, National Horsemen) agree the Court should grant. The only dispute is how the QP is worded, and the SG accepts the challengers' alternative wording. Unopposed cert on a constitutional question is close to certain.
- **Companion petitions.** In `record/related/` (relation `vided-amicus`, one shared Repole Stable amicus brief each, but the dockets plainly arise from the same Fifth Circuit judgment): 26-199 (HISA's own petition from the same judgment), plus cross-petitions 26-332 and 26-335. All four are distributed for the 12/4/2026 conference. This tells me the Court is handling them as a group.

## What keeps it below ~0.97
- **The Court might take a different vehicle.** The reply flags a finality/appellate-jurisdiction concern raised by the Oklahoma petitioners (No. 25-1325, from the Sixth Circuit). The SG offers Oklahoma as a fallback. The corpus row for 25-1325 shows it distributed 2026-10-09 and still undecided as of 2026-11-02, which suggests it is being held. If the Court grants 26-199 or Oklahoma and holds 26-201, this docket would not be granted, at least not at once. I put that combined risk at roughly 5–7%. The most likely outcome is that 26-199 and 26-201 are granted and consolidated, as the SG asks.

## Increments
- Distributions shown: **1** (DISTRIBUTED for Conference of 12/4/2026). No relist yet.
- relist-increment 0.35: a grant at the first conference is the modal path. A reschedule or relist (to coordinate the four petitions plus Oklahoma, or to rewrite the QP) is plausible.
- cvsg-increment 0.01: the United States is already the petitioner.
- summary-disposition-route 0.03: there is no intervening decision to GVR on, since the remand already happened. Plenary review is the only realistic path.
- dissent-from-denial 0.2 (conditional on denial): a denial here would be odd. If it happened, it would probably come with a hold or vehicle explanation, and might draw a statement (e.g., Gorsuch or Thomas on nondelegation).

## Uncertainty and sources
I read the provisioned snapshot, context, QP, cert reply, the decision below (opening section plus grep for the split), the petition (grep), the lower-court docket record, and the related dockets. I did not read the BIO text in full, and relied on the reply's account that all respondents favor a grant. I ran one corpus lookup of 25-1325 and one generic grant query. No MCP or web retrieval was used. I know from training about the 2025 GVR of the earlier HISA petitions. I know nothing about this petition's outcome.
