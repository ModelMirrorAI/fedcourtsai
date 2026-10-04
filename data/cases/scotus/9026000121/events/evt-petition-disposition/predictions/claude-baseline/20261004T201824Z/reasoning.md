# Rationale for the numbers

**P(grant) = 0.006.** The cell's frozen conditioning is band `baseline` under
`sal-v4`, Term 2026, one distribution, no CVSG, forward mode. The anchor the
prompt names is the `baseline` band's bracketed `reached` rate pooled over the
Terms the sal-v4 segment table renders strictly before 2026 (OT2017 through
OT2025). Weighting each Term's rate by its risk-set `n` gives about 5.0 percent
over roughly 12,700 petition-Terms. The 2026 row is blank, so nothing of this
Term enters the anchor.

I adjust down by nearly an order of magnitude, for reasons that stack:

- **State-court origin with an independent state ground.** The court below is
  the Supreme Court of Maryland, which granted review on an unrelated fee
  question and then dismissed the appeal per curiam under Maryland Rule 8-602.
  The federal due process claim was decided only by the intermediate Appellate
  Court of Maryland, which held the evidence (a LinkedIn post) too thin to
  decide whether the judge was practicing law. That is a fact-bound evidentiary
  ruling, not a rejection of a federal rule. The statpack's state-high-court
  buckets in the originating-court cut show grant rates at or near zero.
- **No split and no developed federal question.** The petition cites no
  conflict among courts; it argues importance and "extreme facts." Caperton
  itself stresses that its rule is reserved for extraordinary circumstances,
  and the Court has not since taken a private-party recusal petition without a
  clear record of what the judge did.
- **Question 2 is state law.** It asks for summary reversal in light of a July
  2026 Maryland Supreme Court decision on the specificity required of fee
  memoranda. The Court cannot GVR on a state decision and would not take a
  state-law question.
- **Vehicle quality.** The petition is 64 pages of reconstructed procedural
  history, with a questions-presented section that is hard to parse (the
  provisioned `questions-presented.txt` reproduces it as filed). The fee ruling
  at issue is a one-page order whose timing relative to the judge's new
  employment is contested and undeveloped. The record carries nothing a
  reviewing court could use to resolve the dispositive fact.
- **Waiver of response.** Respondents waived. A grant would require the Court
  to first call for a response, which it does for a small minority of waived
  paid petitions and which has not happened as of the snapshot. This is both a
  signal (nobody at the Court has yet asked for more) and an extra step a grant
  must pass through.
- **Counsel and stakes.** Solo practitioner; the amounts at stake are
  attorney's fees in a residential fraud suit. Neither bears on the merits of
  the due process theory, but both correlate with denial in the paid segment.

The floor of the baseline band is not zero: paid petitions with a colorable
constitutional claim from a state high court are occasionally summarily
reversed on judicial-bias grounds. That residual is what keeps the number above
a few tenths of a percent.

**Relist increment = 0.07.** From a single long-conference distribution and a
waived response, the hazard of a further distribution is mostly the chance of a
call for a response (my estimate a few percent for a petition of this shape)
plus a small reschedule/relist residual. The statpack's relist cut buckets by
terminal count and so cannot be read as this forward hazard; I used it only
for the shape (most petitions end at zero relists).

**CVSG increment = 0.002.** No federal interest of any kind.

**Summary-disposition route = 0.5 (conditional on grant).** The petition asks
for summary reversal; the Court's recent judicial-bias corrections in
fact-specific state cases have been short per curiams; but there is no
intervening decision to GVR on, and a plenary grant on a narrowed Question 1 is
conceivable. I split the conditional roughly evenly and hold no strong view.

**Dissent from denial = 0.01.** No Justice has signalled interest in this
extension of Caperton, and the state-procedural posture gives a statement
little purchase.

**Big case score = 0.05.** Stakes are personal to the petitioner. A ruling
would matter to Maryland's senior-judge recall practice, not nationally.

**Inputs used.** Snapshot `2026-10-04.json` (five docket entries: extension
application and grant, petition filed July 20, 2026, waiver of response
August 24, 2026, distribution for the September 28, 2026 conference);
`context.json`; `documents.json`; `petition.txt` (64 pages, full text,
`empty_text: false`); `questions-presented.txt`. No brief in opposition exists
because the response was waived. The event definition records
`moment: distribution`, `stage: cert`, which is the ordinary cert cell.

**Where to discount me.** I have no view of how the Court's clerks would read
the appendix exhibits on the judge's employment date; if those documents are as
clear as the petition says, a call for a response is more likely than I have
it. I also could not find this docket on CourtListener (not yet indexed), so I
have no independent check that the docket has not moved since the snapshot; in
forward mode that is not a leakage issue, only a freshness one. The corpus
priors query returned mostly application dockets rather than comparable paid
cert petitions, so it contributed shape only, not a comparable set.
