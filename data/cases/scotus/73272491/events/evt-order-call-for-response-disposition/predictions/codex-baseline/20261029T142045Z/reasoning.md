# Predictor rationale

## Information set

I assign **P(any grant) = 0.20** and predict denial of certiorari. This is the
cert-stage, response-requested moment, not a forecast of whether the Court will
request a response: that already happened on June 15, 2026.

I read the provisioned `2026-06-16.json` snapshot, `context.json`,
`documents.json`, `questions-presented.txt`, and the petition's substantive
argument and relevant lower-court appendix. The frozen state is `baseline`
under `sal-v4`, October Term 2025, one distribution, and no CVSG. The docket
shows two amicus briefs, filed June 1, followed by distribution June 2 for the
June 18 conference. The United States waived a response May 21; the Court
subsequently requested one, due July 15. No opposition is in this moment's
record. Its absence is expected, not a provisioning defect, and I do not infer
its arguments or recommendation.

The mode is `forward`, but I deliberately use the supplied moment's record
rather than refresh this case's docket. The October 29 engine execution date
does not establish what happened after June 15. Timing forecasts below are
relative to that information set, not a claim that July 15 is still in the
future or that the petition remains pending today. I neither know nor retrieved
this petition's disposition. The provisioned filings' later download dates are
not later substantive evidence: their filing date is April 27.

## Calibration

The committed `metrics/statpack.md` has a matching `sal-v4` band table. I pooled
the bracketed **baseline reached** rates for every displayed Term strictly
before 2025: OT2017 through OT2024, with a combined weighted resolved denominator
of **11,599**. Weighting the displayed rounded rates by those denominators
gives approximately **5.23%**. This is an approximation from the printed table,
not an exact numerator reconstructed from the corpus. I exclude OT2025 and
OT2026 and do not use the much lower terminal-baseline rate. These are the
committed pack's historical estimates, not a fresh corpus query or a claim
about today's corpus inventory.

The pack's paid-segment signal cuts provide useful shape checks, not independent
likelihood multipliers. The terminal zero-relist bucket has 10,203 resolved
weighted petitions and about 1.8% grants including GVRs; one relist has 2,538
and about 13.7%; two relists has 495 and about 41.2%. This petition has only
one distribution, **not** a completed true relist. A routine redistribution
after the requested response must not be mistaken for the same degree of
interest as repeated consideration at conference. In the CVSG cut, 164 resolved
weighted petitions with a CVSG have about 34.8% grants including GVRs, versus
6.4% among 13,556 without one. This record has no CVSG and should not receive
that population's premium.

The two-or-more-amicus bucket has 1,449 resolved weighted petitions and about
22.9% grants including GVRs. The snapshot really has two such entries, but that
terminal, marginal association overlaps other selection signals; it is not a
conditional grant rate for this moment. I use the support as corroboration of
institutional importance rather than directly transplanting that percentage.
No published cut conditions on a called-for response, so the movement from
5.23% to 20% is case-specific judgment, not a measured response-request hazard.

## Case-specific adjustments

The substantial upward adjustment rests on three things. First, requesting a
response after the United States waived one is affirmative attention from the
Court. It shows sufficient interest to obtain adversarial briefing, although
not necessarily the four votes needed to hear the case. Second, the petition
presents a recurring constitutional question about jury findings for criminal
forfeiture, with support from former federal judges and a second coalition of
legal organizations. Third, its argument links a specific older precedent,
Libretti, to the later Apprendi, Southern Union, and Erlinger line. Those cases
are discussed here as presented in the filing, not as newly verified holdings.
The question is not merely whether the sentencing judge misweighed evidence.

The petition's appendix improves the vehicle assessment: the Second Circuit's
November 7, 2025 summary order expressly rejects the jury-right claim under
Libretti and circuit authority. The sentencing excerpt reproduced in the
petition records a constitutional objection. Thus this is not an issue that
appears unpreserved or unaddressed below. The court imposed a roughly $4.55
million forfeiture based on judicial findings, making the procedural question
consequential. I do not adopt the petition's disputed account of the underlying
transactions as established fact.

Important downward considerations keep denial the modal result. The petition
acknowledges **no circuit split**, because lower courts uniformly follow
Libretti. That does not prevent review of the Court's own precedent, but removes
a conventional reason for immediate intervention. The petition itself lists
earlier requests to reconsider the same issue, indicating that doctrinal tension
has not automatically forced a hearing. The decision below is a summary order,
not a developed new appellate treatment. Although the constitutional issue was
addressed, I cannot rule out government vehicle or harmless-error arguments
without the response. Reconsidering an older precedent is a more substantial
step than correcting an obvious departure from settled controlling law.

The combined result is a meaningful minority chance of review rather than a
coin flip. My uncertainty is concentrated in the government's forthcoming
position and whether the Justices see this forfeiture question as ready for
review now, not in the merits of the underlying criminal conviction.

## Other probabilities and stakes

- **Further distribution, 0.99:** ordinary processing after a called-for
  response strongly favors another distribution. This increment is masked on
  this moment by the harness; it does not mean a 99% chance of a substantive
  post-conference relist.
- **New CVSG, 0.005:** the United States is already the respondent, and its
  requested response supplies the Solicitor General's position without a
  separate invitation to participate as amicus.
- **Summary route given a grant, 0.07:** overruling or materially restricting
  Libretti calls for plenary consideration. The supplied record identifies no
  intervening decision requiring a routine GVR. This is conditional on a grant,
  not a 7% unconditional probability of summary relief.
- **Dissent or statement given denial, 0.22:** the petition's discussion of
  Gorsuch's writings concerning jury factfinding in related sentencing settings
  supports a meaningful, but still minority, chance of a separate writing.
  Most denials should still be silent. His 0.14 order-writing probability is
  unconditional; the other Justice-specific probabilities are also
  unconditional, do not imply joining another Justice is authorship, and need
  not sum to one. No individual cert votes are forecast.
- **Stakes, 0.57:** a ruling could change jury practice and burdens of proof
  in criminal forfeiture nationwide. It would not necessarily invalidate
  forfeiture generally or change civil forfeiture, so the stakes should not be
  inflated to encompass those distinct questions.

## Retrieval limits

An attempted CourtListener MCP lookup of Erlinger by its supplied reporter
citation returned HTTP 429, so I did not retry or use a REST fallback. A general
official-site Rule 10 web search and attempted rules-PDF open returned no
usable content. Accordingly, no external lookup supplies substantive facts
here. The forecast rests on the provisioned filings and the committed
statpack; `retrieval.md` records the attempts. The petition text is marked
truncated but not OCR-derived; its question and substantive argument, plus
the relevant appellate disposition, are readable. I do not assume the
unread or omitted remainder of the appendix resolves every vehicle question.
