# Rationale for the probabilities

## Record and information boundary

This is the cert-stage arrival event for United States v. Office of the
New York State Attorney General, Supreme Court No. 26-348. I used
`record/snapshots/2026-09-15.json`, the event definition, `record/context.json`,
and the provisioned `documents.json`, `questions-presented.txt`, and
`petition.txt`. The snapshot contains the September 15 petition entry,
with a response due October 15, 2026. The context is forward, with a
September 16 baseline cutoff, zero distributions, no CVSG, Term 2026, and
the federal band under sal-v4. These are arrival-time facts, not evidence
that the petition failed to attract attention.

The main petition, printed pages 1-12, and selected portions of the appended
Second Circuit majority opinion supply the substantive record; the petition
also summarizes Judge Park's dissent. The
142-page source is marked truncated; its provisioned text stops during the
district-court appendix. The main petition and the relevant Second Circuit
material are available, but I do not assume the later appendices were read.
No brief in opposition is provisioned, so this is not a comparison of both
sides' Supreme Court advocacy. The appended adverse majority opinion does
provide counterarguments. The missing BIO is consistent with the early
posture, not a response waiver or concession.

I did not seek this petition's current docket, its disposition, subsequent
history, or the current status of Jackson. Jackson's existence and the
requested hold come from the provisioned petition itself. I have no known
outcome for this event and encountered no outcome-revealing material. Two
generic statutory web-retrieval attempts returned no usable content and
added nothing to the forecast; they are recorded in `retrieval.md`.

## Base-rate anchor

The committed `metrics/statpack.md` sal-v4 table matches the frozen context.
For this federal-petitioner arrival cell I use the federal class floor's
bracketed reached rate, not the private baseline, the once-distributed
population, or the terminal zero-relist bucket. Pooling every displayed
strictly prior Term, 2017-2025, gives **143 estimated grants / 202 weighted
resolved petitions = 0.7079207921**. I calculated this using the corresponding
unrounded `prefix_est_grant_rate` and `prefix_weighted_resolved` fields in
`metrics/statpack.json`. Term 2026 is excluded. The individual denominators
are small and the rates vary substantially across Terms, so this is an
anchor, not a precise case-specific frequency.

These are the committed pack's figures as read on September 27, 2026, not
a fresh live-corpus estimate. I did not query or refresh the corpus and
cannot supply a newest-pull stamp for its underlying blob. The provisioned
case snapshot and document fetch dates are September 15, 2026.

## Why 0.74, and why GVR

The strongest case-specific fact is the government's explicit request that
the Court hold this petition for Jackson and then dispose of it as
appropriate (petition pp. 10-12 and conclusion). This sharply separates
P(any grant) from P(plenary review of this particular case). A relatively
poor lead vehicle can still be a strong candidate for a later GVR.

Factors favoring review or a grant-family disposition:

- The Solicitor General is the petitioner, already captured in the federal
  anchor; I do not count that status a second time as an independent boost.
- The questions concern authority to staff vacant Senate-confirmed offices
  and delegate their duties, rather than a purely record-specific error.
  The petition connects the questions to ongoing prosecutorial leadership
  and executive practice (pp. 10-11).
- The delegation conflict is supported by the adverse opinion itself, not
  merely counsel's characterization. At Appendix pp. 33a-34a, the Second
  Circuit expressly rejects the Federal Circuit's Arthrex reasoning that
  limits the FVRA to nondelegable duties. On the first-assistant question,
  the petition describes agreement among the Second, Third, and Ninth
  Circuits; I do not incorrectly characterize that agreement as a split.
- The petition's summary of Judge Park's dissent supplies developed opposing
  readings on both statutory issues (petition p. 9, describing Appendix
  pp. 41a-65a). Those readings,
  together with the identified companion petition, make substantive
  reconsideration plausible without requiring this case to lead.

Factors restraining the estimate:

- Jackson must itself produce a disposition that warrants further action
  here. A hold request is advocacy, not an order granting a hold or a grant
  of certiorari in either case. Denial or an adverse companion decision
  could leave this petition facing denial as well.
- The issuing grand jury was discharged and the subpoenas became
  unenforceable. The Second Circuit relied on repetition/evading-review
  and continuing disqualification grounds to retain a live controversy
  (Appendix pp. 13a-14a). The Supreme Court could disagree; the government
  acknowledges this complication (petition pp. 11-12).
- The majority treated an independent challenge to disqualification as
  forfeited and affirmed that remedy (Appendix pp. 38a-39a). This is a real
  obstacle to complete relief, not a basis to assume that a favorable
  statutory holding automatically restores the government's position.
- The majority's distinction between Section 3347's exclusivity language
  and Section 3348's section-specific definition offers a developed
  contrary statutory argument (Appendix pp. 33a-34a). I do not equate a
  circuit disagreement or executive interest with certain merits success.

Balancing these points yields a modest increase from the approximately
71% federal arrival anchor to **74% for any grant**. Most of that probability
belongs to a follow-on GVR. The vehicle problems reduce the likelihood of
independent plenary review much more than they eliminate the possibility
of a remand after a relevant companion ruling. A jurisdictional vacatur is
another possible grant-family route but not my modal forecast.

## Other declared claims

The paid-segment relist and CVSG cuts in `metrics/statpack.md` were read as
population context. Their terminal buckets do not estimate forward hazards:
the relist-0 group has 9,892 resolved petitions and approximately 1.7%
grant-family outcomes, while relist-1 is approximately 13.3%, relist-2
40.9%, and relist-3+ 36.8%. These are not substitutes for the federal
arrival anchor. In particular, zero distributions today does not imply
membership in the terminal no-relist population.

- **Relist increment, 0.98:** from the frozen count of zero, ordinary first
  distribution suffices. My forecast of a hold and later reconsideration
  does not require frequent true relists or count a silent hold as one.
- **CVSG increment, 0.005:** the pack's CVSG population has a much higher
  grant-family share than its no-CVSG population, but that selection does
  not estimate the chance of a call here. The Solicitor General already
  speaks for the petitioner, leaving little reason for an invitation.
- **Summary route conditional on grant, 0.95:** the express request for
  companion treatment and acknowledged vehicle difficulties concentrate
  grant probability in a cert-order GVR rather than separate argument.
  This is conditional, not the joint probability of grant and summary action.
- **Dissent/statement conditional on denial, 0.10:** the statutory and
  institutional stakes support a nonzero chance of a writing, but a denial
  after companion treatment could be routine. This is an aggregate
  existence prediction, not a per-Justice forecast.

The **0.82 stakes score** reflects the potentially broad consequences for
vacancy management, federal prosecution, and federal-state institutional
relations. It is not the grant probability. The follow-on posture and
case-specific remedies keep it below the very highest significance tier.
