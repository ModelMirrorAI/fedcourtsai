# Why P(grant) = 0.12

**Anchor.** `record/context.json` freezes this paid petition in band
`baseline` (sal-v4, matching the statpack table's heading). Pooling the
bracketed `reached` rate for `baseline` over the Terms 2017–2025 rows shown in
the statpack's "Segment base rate by salience band (sal-v4)" table gives about
**5.1%** (≈660 weighted grants over n≈12,900 in the risk set). The 2026 row is
my own Term, so I left it out.

**Adjustments up.**
- *Called-for response.* The Court requested a response after all respondents
  waived. No committed table conditions on this signal. In my judgement a
  called-for response roughly doubles a paid petition's odds, while most such
  petitions are still denied. This is the largest single adjustment, and it is
  judgement, not a published figure.
- *Amicus support.* Five amicus entries are on the record by the cutoff (NC
  Values Institute; Sutherland Institute; Independent Women's Law Center
  et al.; American College of Pediatricians; Our Duty–USA et al.). The
  snapshot's party list names several more amicus counsel. The statpack's
  amicus cut shows 18.4% granted for the 2+ bucket, but that is marginal and
  read at disposition, so it overlaps heavily with the relist signal. I give it
  only modest weight.
- *Counsel and salience.* Experienced Supreme Court counsel (Schaerr | Jaffe)
  represent the petitioner. The petition invokes four Justices' statement that
  parental rights in gender transition are "a question of great and growing
  national importance."

**Adjustments down.**
- *Vehicle.* The case arises on qualified immunity, so the Court could deny
  without reaching the parental-rights question. The Court has repeatedly
  declined petitions asking it to reshape the clearly-established-law test,
  and QP 2 asks it to revisit qualified immunity's foundations, which a
  majority has shown no appetite for.
- *Fact-bound posture.* The case is a family-court custody allocation plus
  allegations about what defendants knew. That makes it a weaker vehicle than
  a school-policy case for any broad parental-rights ruling.

- *Intervening decision.* The petition relies on *Mirabelli v. Bonta*, 607
  U.S. 492 (2026) (per curiam). Per the petition, it held that the parental
  right covers participation in mental-health decisions bearing on gender
  dysphoria, with a Barrett concurrence joined by Roberts and Kavanaugh. It
  appears to postdate the Ninth Circuit's October 21, 2025 opinion. That
  creates a GVR channel. The channel is weak because clearly-established law
  is assessed as of the conduct, but the Court GVRs loosely after a new
  per curiam.

**Net.** 0.05 → ~0.12. I put a little under half of the grant mass on a
summary route, mostly a GVR in light of *Mirabelli*. That is why
`summary-disposition-route` is 0.45.

**Other claims.** `relist-increment` is 0.97 (a post-response distribution is
all but certain, and the harness masks it on this moment anyway).
`cvsg-increment` is 0.02 (no federal interest). `dissent-from-denial` is 0.22,
reflecting Thomas's QI writings and Alito's interest in this area.
`order-writers` is consistent with that figure.

**Inputs.** I read the snapshot `2026-09-18.json` (cut at the call day),
`questions-presented.txt`, and parts of `petition.txt` (313 pages,
truncated at the cap): the statement and the reasons for granting, found by keyword search. I did not read the whole thing. No BIO exists yet. I also read the case's plain-language
summary under `summaries/`. It reports that the response deadline was extended
to November 18, 2026, which is later than my baseline. That is ordinary forward
information and says nothing about the outcome. I did no web or CourtListener
retrieval, and the one corpus query was a general sanity check of recent grants.

**Where to discount me.** The size of the response-requested uplift is my own
estimate. I have not seen the respondents' response. I also do not know the
current state of related parental-rights petitions, so the GVR channel is
speculative. I am relying on the petition's own characterisation of *Mirabelli*. I did not retrieve the opinion or its date.
