# Rationale for the probabilities

## Record and decision target

This is a forward, cert-stage arrival cell. I read event.yaml,
record/context.json, record/snapshots/2026-10-30.json, documents.json,
questions-presented.txt, the petition's complete main body, and selected
parts of its appendix, including the Ninth Circuit opinion's opening and
its discussion of Jennings. The snapshot filename and cutoff are October
30, 2026; the actual supplied docket contains only the October 28 petition
entry, with a November 30 response deadline. I do not treat the filename as
evidence of any future docket development. The frozen conditioning is
sal-v4, federal, Term 2026, zero distributions, and no CVSG.

There is no brief in opposition in the supplied materials, which is ordinary
at arrival rather than a provisioning defect. The petition PDF is 253 pages
and its staged text is capped; documents.json marks it truncated but not
empty or OCR-derived. Its main argument and requested relief are readable.
Several appendix sections have explicit pipeline omission markers. I did
not infer that the omitted portions contain no counterarguments. The
appended majority opinion supplies an actual opposing legal rationale,
but it is not a substitute for a respondent's Supreme Court brief.

## Anchor and adjustment

The committed statpack's sal-v4 federal band is the appropriate caption-class
arrival population, not the whole petition population or a terminal
zero-relist bucket. Pooling every displayed Term strictly before 2026
(2017 through 2025), using statpack.json's federal prefix_weighted_resolved
and prefix_est_grant_rate, gives 151 grant-family outcomes over 206 resolved
petitions: 73.30%. The current Term's three resolved federal petitions are
excluded. This is a calculation from the committed statpack in this
checkout, not a newly measured live-corpus rate; the sample remains modest
and nearest-Term completion is uneven.

I raise P(any grant) to 0.82 principally because of unusually direct
hold-and-remand evidence, not because the petition has acquired docket
attention. Petition pages 10-11 say the Court granted the same statutory
question in Rhoney v. Barbosa da Cunha on October 1, 2026, and expressly
request a hold followed by an appropriate disposition. They also report that
the Ninth Circuit withdrew its en banc briefing order and stayed its mandate
pending the lead decision. The separate corpus lookup for No. 26-104
corroborated the lead case's cert grant and date. That is a different case's
pre-existing grant, not the disposition this cell predicts. I did not
retrieve this petition's outcome or subsequent history.

The government can therefore obtain a grant-family outcome without persuading
the Court that this particular class action should occupy a separate
argument slot. A remand can be appropriate even if the lead opinion does not
fully endorse the government's broad position. On the other hand, the lead
Court could affirm the relevant bond-hearing entitlement or draw a line that
leaves this judgment intact. The local class and the named respondent's
departure also make this less attractive as an independent vehicle. These
considerations preserve substantial denial risk rather than making a GVR
certain. My approximate outcome allocation is 0.7954 GVR/other cert-order
grant, 0.0246 plenary grant, 0.17 denial, and 0.01 dismissal or withdrawal.
Within the cert-order category, GVR overwhelmingly dominates summary reversal.

The legal dispute is genuine. The petition's argument emphasizes the
statutory treatment of people present without admission as applicants for
admission. The appended Ninth Circuit majority instead reads the additional
seeking-admission language, Section 1226's structure, and longstanding practice
as preserving bond eligibility for interior arrests. Its account of Jennings
supports that historical distinction. Judge Bea's dissent, as summarized in
the petition, adopts the government's textual reading. I lean toward a lead
decision requiring reconsideration here, but I do not treat the majority's
contrary construction or the long prior practice as frivolous. No separate
forecast of the lead case's exact judgment or vote is required to recognize
the derivative remand route.

## Remaining claims and stakes

The statpack's paid-segment terminal relist cut has resolved n=10,203 at zero,
2,538 at one, 495 at two, and 484 at three or more; the CVSG cut has n=13,556
without and n=164 with a CVSG. These describe where petitions ended, not the
hazard of moving from this arrival's zero distributions. They do not replace
the federal arrival anchor. The amicus cut is similarly terminal: n=11,109
at zero, 1,162 at one, and 1,449 at two or more. No amicus entry appears in
the baseline, and that absence at docketing is not a reason to lower the
stakes or impute terminal lack of support.

The 0.98 distribution increment reflects expected initial conference
processing and possible post-hold processing; no actual conference is
invented. The 0.005 CVSG increment reflects that the Solicitor General is
already the petitioner. The 0.97 summary-route figure is conditional on a
grant; its product with 0.82 is approximately 0.7954, not the number to put
in the conditional claim. The 0.08 denial-writing figure is conditional on
denial. All nine order-writer probabilities are small and unconditional:
a follow-on disposing order is unlikely to carry its own writing even when
the underlying subject is contentious. Those probabilities are judgmental,
not estimates from a published writing baseline.

The big-case score is 0.90 because the underlying question can determine
bond-hearing access for a broad population detained inside the country.
This concerns significance if decided, not the chance of review or the
likelihood that this derivative petition receives its own opinion.

## Retrieval limits

A five-case structured corpus query supplied general grant examples, not
matched controls or a numerical estimator. The lead-case lookup was much
more useful. I attempted official-source web research on the detention
statute and Jennings; the web tool returned no usable content. A
CourtListener MCP citation search for Jennings was throttled with HTTP 429.
I did not use a REST fallback or seek credentials. Consequently, the legal
assessment rests on the provisioned argument and appended opinion rather
than an independently retrieved Jennings opinion. This limits confidence in
the merits assessment, not access to the dispositive hold request. All
retrieval attempts are listed in retrieval.md. No disposition of this
petition was encountered, and I have no known outcome to disclose.
