# Reasoning — scotus/9526000686, evt-motion-disposition (interim, arrival)

**P(stay granted in whole or in part | decided, not mooted) = 0.01.**

## What I read
- Snapshot `2026-11-14.json`: application 26A686, marked capital, from the Supreme Court of Florida (SC2026-1724, SC2026-1725), linked with cert petition 26-6154, a single entry: the application for a stay of execution submitted to Justice Thomas on Nov 14 2026. No response requested, no referral, no amicus entries (`context.json` agrees: all three ladder rungs at zero).
- `record/documents/application.txt` (4 pages, not truncated). It asks for a stay of a Florida execution set for Nov 19 2026 pending the concurrently filed cert petition. Its grounds are stated only by reference to the petition: Florida's warrant and clemency process is said to violate separation of powers, due process and equal protection, with general Eighth Amendment language. The application is brief and generic; it even leaves a "[date]" placeholder for the Florida Supreme Court's ruling. The cert petition itself was not provisioned, so I know the questions only as the application describes them.

## Base rates
- Scored yardstick: the statpack's interim section, pooled over the ten application-Terms before OT2026 (finer counts), bottom-right cell of the applicant-class table: 156/1337 = 11.7%. The pool clears the 50-resolved floor.
- The cell that actually describes this application is `private` × `capital`: 3.5% (10/288). I leaned on that cell, not the margin, and then went well below it.

## Why below the capital-private cell
- That cell pools every kind of capital stay request, including ones with substantial method-of-execution, competency, or religious-liberty claims and ones arriving from federal habeas with a lower-court dissent. This application is the weakest sub-type: an end-stage, under-warrant challenge from state successive postconviction proceedings, where the Florida Supreme Court's ruling very likely rests at least partly on state procedural bars, and where the federal claim (clemency/warrant-selection process) has been repeatedly rejected and has never drawn the Court's interest. Clemency due-process claims face *Woodard*'s minimal-safeguards standard.
- From general knowledge (not retrieved): the Court has denied the stay applications accompanying Florida's long run of executions under recent death warrants essentially without exception, normally without noted dissent.
- The application itself shows no sign of a claim built to attract four votes; it does not articulate a split or a specific legal question.
- I keep 1% rather than less for unknowns: the petition's actual content is not in front of me, and courtesy/administrative developments are possible.

## Other claims
- `response-requested-increment` 0.04: in capital warrant cases the State files its opposition unprompted; a formal request on the docket is unusual.
- `referral-increment` 0.93: the standard disposition of such applications is "presented to Justice Thomas and by him referred to the Court." Residual is for a single-Justice denial, a withdrawal, or a state-court/gubernatorial event mooting the matter first.
- `amicus-increment` 0.02: no amicus activity is typical in a five-day warrant window on this kind of claim.
- `order-writers`: small numbers; Sotomayor and Jackson are the likeliest to write or note a dissent on a capital denial, but in the recent Florida warrant cases writings have been rare.

## Retrieval and limits
- One corpus query (see `retrieval.md`); it returned recent rows, mostly extension applications, and gave no usable capital-stay priors, so the forecast rests on the statpack table and the record. No CourtListener or web retrieval; I did not look at the live docket.
- Discount me on: not having the cert petition; reliance on training-era knowledge of Florida warrant litigation outcomes.
