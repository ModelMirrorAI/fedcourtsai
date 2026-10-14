# Why P(grant) = 0.22

**Anchor.** `record/context.json` puts this case in band `elevated` (sal-v4, Term 2025, distribution_count 2, no CVSG, forward mode). The statpack's sal-v4 band table matches that version. I pooled the bracketed `reached` figures for `elevated` over the Terms strictly before 2025 (2017–2024), weighting each by its n: about 484 grants out of n≈2810, which is **≈17.2%**. Single Terms range from 13.8% to 20.5%. For shape, the relist-count cut shows that a petition's chances rise steeply between bucket 1 (8% grant, 5% GVR) and bucket 2 (28% grant, 13% GVR). That table is bucketed by terminal count, so I used it for shape only. Nearly all of this case's grant probability is plenary review. A GVR has no basis here.

**Adjustments up.**
- QP 2 is the question the Court left open in *Centro de Periodismo* (2023), where it said that case was a poor vehicle only because Puerto Rico was absent. That defect is cured here. The BIO's only real vehicle point on QP 2 is that the First Circuit followed its own circuit precedent, which is exactly what review would examine.
- The case has been relisted after a conference.
- Three amicus briefs were filed at the cert stage. Counsel is a repeat public-interest litigator.

**Adjustments down.**
- QP 1 is weakened by the petitioners' own litigation choices: they disclaimed Penn Central, and the First Circuit treated other theories as waived (BIO 8–10). The BIO also argues credibly that the First Circuit assumed a cognizable property interest and decided narrowly. The split is soft: a Federal Circuit case, a Texas Supreme Court case, and a concurrence.
- Puerto Rico's immunity has few practical consequences elsewhere. The Lanham Act abrogation question may be easier for the Court to sidestep.
- A single relist is also consistent with a Justice writing a dissent from denial, which on QP 2 seems plausible to me (Justice Thomas). That drags the grant share of relisted outcomes below the pooled band rate. The supplemental brief rests only on a USPTO speech, which is weak.

I land slightly above the anchor, at 0.22. The QP 2 vehicle is unusually clean for a question the Court has called open, and that roughly offsets the dissent-from-denial reading of the relist.

**Other claims.** relist-increment 0.4: a dissent or hold path vs. disposal on 10/16. cvsg-increment 0.08: the petitioner asked, but the Court rarely calls for the SG's views after relisting. summary-route 0.05. dissent-from-denial 0.35: relist plus Justice Thomas's stated view in *Centro*.

**Inputs used.** The snapshot `2026-10-14.json`; the QP file; the petition (truncated, appendix cut); the BIO (read in full where relevant: vehicle and split sections); the cert reply (pp. 1–8). I fetched the 9/21 supplemental brief, which was not provisioned, directly from supremecourt.gov. It cites a USPTO Director speech and asks for a CVSG in the alternative.

**Uncertainty.** I cannot tell whether the 10/16 redistribution is a relist for a grant, a hold, or a writing. That is the main swing factor. I made no CourtListener MCP calls and no corpus queries.
