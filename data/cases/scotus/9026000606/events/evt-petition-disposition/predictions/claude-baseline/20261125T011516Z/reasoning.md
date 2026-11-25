# Reasoning: P(grant) = 0.02

**Inputs read.** Snapshot `2026-11-25.json`, `context.json`, `questions-presented.txt`, and the petition (`petition.txt`, 55 pages, not truncated; I read the front matter, statement and the start of the argument, not the appendix). No brief in opposition exists: the United States waived its response on November 17, 2026. `same-question.json` lists no matching petitions. No `decision-below.txt` or `lower-court-docket.txt` was provisioned, so my account of the Eighth Circuit's ruling is the petition's.

**Anchor.** Band `baseline` under `sal-v9`; the frozen `cert_anchor.rate` is 5.2% (reached rate, ten prior Terms). The amicus line for the `none` arm is 2.7% (n = 10,350). The statpack's relist cut shows petitions that ended with no further distribution at 1.8% grant family (n = 10,311 resolved). The reached rate of 5.2% includes petitions that later climbed; this one shows the classic non-climbing profile, so I start nearer the 2.7% amicus-line figure.

**Adjustments down.**
- The Solicitor General waived a response and no Justice has yet called for one. The Court almost never grants without a response, so a grant requires a call for response first. Petitions distributed on a waiver are overwhelmingly denied.
- The split is real but old and lopsided: the Ninth Circuit's 1988 decision against, by the petition's own count, five or more circuits. From my own background knowledge, the Court has repeatedly denied petitions presenting this same question over many years, from several of the majority circuits. I did not retrieve those dockets in this run, so treat that as recollection, not a checked fact.
- Unsympathetic subject matter (paid sexual activity with and filming of minors), a small-firm filing with no specialist Supreme Court counsel, and no amici.

**Adjustments up.**
- The conflict is acknowledged and the question is constitutional, with a 15-year mandatory minimum riding on it.
- The vehicle is better than most: the defense was requested and refused at trial, the record of affirmative age misrepresentations is strong on the petition's telling, the government's closing leaned on the absence of the defense, and Judge Kelly wrote separately to say this may be one of the rare cases where the defense would matter. The decision below is published.
- Recent interest in scienter (Rehaif, Counterman) gives a Justice a reason to look twice.

Those upward factors mostly buy a chance of a call for response (about 8–10%), and after a response the government would argue the lopsidedness and the long line of denials. Conditional on a call for response I put a grant near 15–20%, giving roughly 0.02 overall.

**Other claims.**
- `relist-increment` 0.10: driven almost entirely by the chance of a call for response, which forces redistribution; a post-conference relist without one is rare.
- `cvsg-increment` 0.002: the United States is a party.
- `summary-disposition-route` 0.12 (conditional on a grant): well below the historical cert-order share of grants because no intervening decision or pending merits case that I know of touches this question; the residual covers a hold-and-GVR I cannot foresee.
- `dissent-from-denial` 0.02, with `order-writers` kept consistent with it (individual probabilities sum to roughly that once overlap is allowed).

**Where to discount me.** I have no opposing brief, I did not read the appendix opinion, and my sense of the Court's past denials on this question is from memory. The statpack's band table is headed `sal-v8` while my context is `sal-v9`; the band is `baseline` either way and I relied on the frozen `cert_anchor`, but I flagged the mismatch. The corpus query I ran returned generic recent denials and did not inform the number. The CourtListener MCP server was not used.
