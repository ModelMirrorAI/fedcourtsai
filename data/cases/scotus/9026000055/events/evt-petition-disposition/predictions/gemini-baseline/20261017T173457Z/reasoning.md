P(grant) 0.015. This is a paid immigration petition from the Fifth Circuit (`baseline` salience band, P(reached) ~ 5% across prior terms). The case has been distributed for its first conference (count=1), which puts it in the relist-0 bucket (overall grant rate ~1.2%). Because we lack the text of the petition, the BIO, and the CA5 opinion (the `documents/` directory was empty and my CourtListener searches returned no results for the CA5 decision or docket), I must rely entirely on the docket skeleton.

Immigration petitions from the Fifth Circuit are common and heavily denied unless there is a well-developed circuit split. Without evidence of a split, the base rate dominates. I set P(grant) near the relist-0 bucket's historical rate.

P(cvsg-increment) is 0.0 because the United States (via the Attorney General / Solicitor General) is already the respondent, having filed a Brief in Opposition. The Court does not invite the SG's views when the SG is already participating.

I set P(summary-disposition-route) at 0.4 conditional on a grant, as immigration petitions are frequently held for and then GVR'd in light of recent merits decisions.

No retrieval beyond the provisioned inputs yielded case-specific text.
