# Why 0.78: Nelsen v. Pike, No. 26A428

## What the cell is

Interim stage, `moment: response-filed`, forward mode. Snapshot
`2026-09-30.json` (cutoff 2026-10-01, `date` cut); context carries
`band: null`, `response_requested: false`, `referred_to_court: false`,
`amicus_briefs: 0`, Term 2026. So no cert band is in play and none is
derived. The provisioned document is the State's 15-page application
(`application.txt`, not truncated, text extracted). The docket at snapshot
shows three same-day entries: the application submitted to Justice Kavanaugh,
Pike's response filed, and the State's reply filed. The response and reply
texts were not provisioned; I read the application and, via CourtListener, the
Sixth Circuit's published stay order and dissent (see `retrieval.md`).

## The anchor

The statpack's "The interim docket (applications)" section publishes per-Term
substantive counts. Pooling the resolved substantive slice over Terms strictly
before 2026 (Terms 2024 and 2025 are the only prior Terms with parsed rows;
Terms 2016–2023 show `unparsed` only): granted 14 + 17 = 31 over resolved
70 + 226 = 296, a pooled rate of about 10.5%, which clears the 50-resolved
floor. That is the scored baseline. The section's caption already describes
the rate as grounding the scored base rate, so I read the current caption, not
a descriptive-only predecessor. I note the caveats the section carries: Term
2024 rests on 972 unparsed rows, and the pooled cohort is not selected on the
escalation ladder the way predicted cells are.

## Why I sit far above the anchor

The pooled rate is over every substantive application, most of them prisoners'
or private parties' stay requests, which the Court denies at a very high rate.
This application is the mirror image: a **State** asking the Court to **vacate**
a lower-court stay of an execution. That sub-population behaves very
differently, and my number rests on it:

1. **Applicant class.** In the corpus rows I pulled, every capital application
   by a prisoner (twelve rows across Terms 2026) was denied, and the one
   capital State application to vacate a circuit stay (Guerrero v. Busby,
   25A1235, filed 2026-05-11, decided 2026-05-14) was granted, referred to the
   Court, with no response requested and no amici. That matches the pattern I
   carry from general knowledge of the Court's practice since roughly 2017:
   State applications to vacate execution stays are granted far more often
   than not (Price v. Dunn, Dunn v. Ray, Barr v. Lee, Hamm v. Reeves, Hamm v.
   Miller, Hamm v. Smith), with the rare denial (Dunn v. Smith, a religious
   liberty claim) coming where the prisoner's claim had real merit.
2. **The stay order's shape.** The Sixth Circuit majority (Stranch, Moore;
   Griffin dissenting) stayed the execution "until further order" so it could
   "properly analyze the parties' fully briefed arguments," with no finding of
   a significant possibility of success. Hill v. McDonough requires that
   showing for any stay, and Price v. Dunn vacated an Eleventh Circuit stay on
   exactly the "we need time to consider a difficult question" rationale. The
   present Court majority has been consistent on this point.
3. **The merits of the underlying motion.** Pike's Rule 60(b) motion argues
   that the State's August 13, 2026 hearing remark ("the State does not dispute
   the terrible things that Ms. Pike suffered") undermines the state
   post-conviction court's rejection of her sentencing ineffective-assistance
   claim. Under Gonzalez v. Crosby that is an attack on the prior merits
   ruling, so a successive petition, and the same claim was already presented
   in her first petition, so § 2244(b)(1) bars it. Griffin's dissent lays this
   out; the majority order does not answer it. The Court's majority is likely
   to see it the same way.
4. **Delay and posture.** The motion was filed 47 days after the remark and the
   day before the execution, after the Court had denied Pike's own stay
   application and cert petition (26A414, 26-5696) on September 29. The
   equitable presumption against last-minute claims (Bucklew, Nelson) cuts
   against the stay, and the Court has already looked at this execution once
   this week and declined to stop it.

## Why not higher

- **Mootness before disposition.** The Sixth Circuit could decide the remand
  motion and dissolve its own stay before the Court acts, or resolve it in
  Pike's favor and change the posture. A stay entered to permit a decision on
  "fully briefed" papers may be short-lived by design. If the stay disappears
  first, the application is denied as moot or withdrawn, either of which scores
  as ungranted. I put this around 10%.
- **Partial or qualified relief** collapses to `denied` under the interim
  resolver. A conditioned order (vacate but direct the Sixth Circuit to rule by
  a date) is unusual on this docket but not impossible.
- **A genuine denial.** Three Justices will almost certainly vote to leave the
  stay; a fourth or fifth could see a short, published, 2–1 panel stay on a
  jurisdictional question as within the panel's discretion. I give this
  roughly 8–10%.

Net: 0.78.

## The ladder claims

- `response-requested-increment` 0.03: the response and the reply are both on
  the docket; nothing remains to be called for.
- `referral-increment` 0.88: the Court's practice on State vacatur applications
  is referral and a full-Court order, and every capital application row I
  retrieved carried `referred_to_court: true`. The complement is mostly the
  mootness/withdrawal branch, in which no referral is recorded.
- `amicus-increment` 0.05: zero entries now, hours to disposition, and amici
  seldom appear on the State's vacatur docket (Pike's own stay docket drew one).

## Votes and stakes

The votes are a forecast, unscored at this stage: six to vacate, three to deny.
`big_case_score` 0.45: the case is highly newsworthy (a capital case with
national attention, a woman facing execution, a published 2–1 circuit stay) but
the legal question is a routine application of Hill and Gonzalez and will
produce no majority writing.

## Where to discount me

- I did not read Pike's response or the State's reply; my reading of her
  argument comes from the Sixth Circuit order's summary and the application.
- This cell ran at about 21:30 UTC on the execution date with the matter fully
  briefed by 20:11 UTC. The Court may already have acted. I did not look up the
  26A428 docket's current state, per the rule against retrieving this case's
  disposition, so the cell may be overtaken by events rather than mis-provisioned.
- The corpus's interim parse coverage is two Terms deep; the State-applicant
  sub-population I lean on has one corpus row, so the rest of that prior is
  general knowledge rather than a committed figure.
- The CourtListener docket for the Sixth Circuit matter was current as of
  14:34 UTC and showed the stay still in force; no outcome-revealing material
  surfaced in any retrieval.
