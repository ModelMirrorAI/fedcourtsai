# Reasoning — scotus/9026000199 (No. 26-199), evt-petition-disposition

**P(grant) = 0.90.**

## Anchor
`record/context.json` freezes band `baseline` (sal-v8), distribution_count 1, no CVSG, forward mode,
with `cert_anchor.rate` = 0.0516 (10-Term lookback). The statpack band table shows the same
`baseline` reached rate of roughly 4–6% across prior Terms. The band captures the docket's shape:
one distribution and a private petitioner (the Authority is a private nonprofit, so the caption reads
`private`). It cannot see what moves this petition far off that anchor.

## Why far above the anchor
- **A federal statute held facially unconstitutional.** The Fifth Circuit (June 11, 2026, on remand
  after this Court's GVR in light of *FCC v. Consumers' Research*) reissued its holding that HISA's
  enforcement provisions facially violate the private-nondelegation doctrine (petition; appendix).
  The Court almost always reviews a decision invalidating an Act of Congress.
- **An acknowledged split.** The Sixth Circuit upheld the same provisions (*Oklahoma v. United
  States*, 163 F.4th 294 (6th Cir. 2025)), and the Eighth Circuit divided 2–1. Every brief agrees.
- **Every party asks for review.** The Solicitor General filed a parallel petition (No. 26-201,
  in `record/related/`). In the combined BIO file, the Horsemen "acquiesce to certiorari," Texas
  "does not oppose granting certiorari," and Gulf Coast "acquiesce[s]" (cert reply at 1–2 collects
  the quotes). The only dispute is whether to add the questions in the respondents'
  cross-petitions (26-332, 26-335 and a third). That affects the scope of the grant, not whether
  there is one.
- **Earlier interest.** The Court granted the Authority's stay of the mandate in 24A287 and later
  GVR'd. Texas's response says several Justices have shown interest.
- **The companion dockets move together.** 26-201, 26-332 and 26-335 were all distributed for the
  same 12/4/2026 conference (`related/`, rows marked `vided-amicus` with one shared Repole Stable
  brief; their own dockets also mark the BIOs VIDED, so they really are companions). A corpus lookup
  of the Sixth Circuit petition, *Oklahoma* No. 25-1325, shows it distributed in October 2026 with
  no disposition. That fits a hold pending these petitions.

## Residual risk (about 10%)
- The main path to an ungranted outcome for *this* docket: the Court grants the SG's 26-201 alone
  (or the *Oklahoma* petition) and holds 26-199. I think that is unlikely. When a federal agency
  and a private co-party both petition from one judgment, the Court usually grants both and
  consolidates (as it did in *Consumers' Research*, 24-354 and 24-422). Here the Authority is the
  regulated entity whose powers are at stake.
- A small chance of a GVR or summary route (claim 0.04 conditional on a grant). There is no
  intervening decision this time, because the remand already took account of *Consumers'
  Research*.

## Other claims
- relist-increment 0.60: the docket shows one distribution (12/4 conference). The Court usually
  relists before granting plenary review, and the cross-petitions' scope question adds a reason to
  wait. Still, a clean grant at the first conference of a case everyone agrees on is plausible.
- cvsg-increment 0.01: the United States is already a party and petitioner.
- dissent-from-denial 0.35 (conditional on a denial, which I find unlikely): a denial that leaves a
  federal statute invalid in one circuit could draw a writing. Justices Gorsuch, Thomas and Alito
  are the most likely writers. The order-writers figures are low because a grant order carries no
  writings.

## Inputs used
Snapshot 2026-11-10.json; questions-presented.txt, petition.txt (skimmed), brief-in-opposition.txt
(combined responses; grep for acquiescence and vehicle sections), cert-reply.txt (read),
appendix.txt (not read in depth); `related/` 26-201, 26-332, 26-335; statpack band table; corpus
lookups listed in retrieval.md. No MCP or web retrieval.
