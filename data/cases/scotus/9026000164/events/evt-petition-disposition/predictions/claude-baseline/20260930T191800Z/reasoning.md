# Why 0.29, and where to discount me

## Inputs read

- `record/snapshots/2026-09-30.json` (the provisioned baseline, read in full).
- `record/context.json`: mode `forward`, band `elevated` under `sal-v4`,
  `distribution_count` 2, no CVSG, Term 2026, `signals_observable` true.
- `record/documents/questions-presented.txt`, `petition.txt` (393 pages,
  `truncated: true`, the text ends inside the Virginia Supreme Court majority
  opinion at App.38a, so the appendix's due-process section, the dissent, the
  U.S. amicus brief, and the trial-court orders were not on my desk beyond what
  the petition's own body quotes), and `brief-in-opposition.txt` (43 pages,
  complete). I had two subagents summarize the two briefs and then
  spot-checked their key claims against the text (the waiver footnote at
  App.48a n.27 and its *Harris v. Reed* framing, the *Genalo* citation, the
  withdrawn U.S. amicus brief, the related No. 26-226 petition).
- `metrics/statpack.md`: the modern discretionary-cert section, the relist and
  CVSG cuts, and the segment base rate by salience band (`sal-v4`).

## The anchor

The context band is `elevated` and the statpack's band table is rendered under
`sal-v4`, so the versions match and the bracketed `reached` figure is the
yardstick. Pooling the nine Term rows strictly before OT2026 (OT2017 through
OT2025) gives a risk-set grant-family rate of **16.9%** (521.5 of 3,085
weighted). That is my starting point. For shape only: the relist cut puts
once-relisted paid petitions at 8.2% granted plus 5.1% GVR and twice-relisted
ones near 41% combined, and the CVSG cut puts petitions without a CVSG at 4.0%
granted plus 2.3% GVR. The Supreme Court of Virginia row in the
originating-court cut shows no plenary grants among 121 resolved petitions,
which I read as a weak negative rather than a real prior, because that row is
dominated by IFP criminal petitions unlike this one.

## Adjustments up

- **The Court asked for a response after respondents waived.** That is an
  affirmative act of attention by at least one chambers, and it is what the
  seven amici filed against. Some of this is already priced into `elevated`.
- **Seven cert-stage amicus briefs, all supporting petitioners**, including a
  former U.S. Ambassador to Afghanistan and two former officials, adoption-law
  scholars, Afghan-law scholars, the Young Center, and adoptee organizations.
  For a private petition from a state court this is heavy support and a strong
  stakes proxy.
- **Counsel and posture.** Roman Martinez of Latham is counsel of record. The
  state supreme court split 4-3, and the intermediate appellate court and both
  trial judges had gone the other way (on state-law and due-process grounds
  respectively).
- **An acknowledged open question.** *Smith v. OFFER* reserved whether
  nonparent caretakers hold a liberty interest, and the petition assembles a
  real division (Tenth and Fifth Circuits and several state courts applying a
  case-by-case test; Sixth, Seventh, Second Circuits and Colorado applying a
  bright-line rule; a further split on biological kin). The Virginia rule
  (only legal or biological parents) is the strictest end.
- **Extraordinary facts and sustained press attention**, plus the federal
  government's own prior filings calling the adoption a fraud on the court.

## Adjustments down

- **Waiver as an adequate and independent state ground.** The Virginia
  Supreme Court said petitioners waived any "nonparent caretaker" theory
  distinct from their de facto parent theory "given the paucity" of their
  argument (App.48a n.27). Respondents lead with this, and it is their best
  point. The court did rule on the federal due-process claim across the board,
  which gives the Court a route around the footnote, but the Court dislikes
  spending a grant on a vehicle where a threshold bar is contestable.
- **The record is messy and the equities cut both ways.** The trial court found
  petitioners did not prove kinship, that they had lied on three occasions,
  rejected the trafficking narrative, and credited the Masts; a DNA order is
  unfulfilled. The child has lived with respondents for five years. Petitioners
  were foreign nationals abroad when the orders issued, and respondents preview
  an extraterritoriality argument. Any relief would unsettle a 2020 adoption of
  a seven-year-old. These are the kind of facts that keep a majority from
  coalescing on a clean legal question.
- **The Court's caution in this doctrinal area.** *Troxel* produced no majority
  opinion, and the Court has avoided the *Smith* reservation for nearly fifty
  years. The petition itself describes "entrenched disarray" rather than a
  square split on judgments, which the BIO turns into a percolation argument.
- **The federal government has stepped back.** DOJ withdrew its Virginia
  Supreme Court amicus brief in March 2025; the current Solicitor General is
  unlikely to support the petition, and a CVSG that comes back unfavorable
  would hurt rather than help.

Net: I move from 16.9% to **0.29**. The point prediction is therefore a denial
(`granted` 0, `predicted_disposition` denied), with grant a substantial
minority outcome. About a quarter of my grant mass is the hold-and-GVR route
in light of *Genalo v. Black*, which is why `summary-disposition-route` is
0.25 conditional on a grant; a per curiam reversal on these facts is not
realistic.

## The other claims

- **relist-increment 0.60.** The two distributions shown are not two
  considerations: the first was pulled by the response request, so the
  petition has never been to conference. A grant, a hold, a CVSG, and most
  denials with a writing all produce at least one more distribution. Only a
  clean first-conference denial does not, and I put that near 0.40 for a
  petition with this profile.
- **cvsg-increment 0.15.** Well above the population rate because the federal
  role here (State, Defense, DOJ filings, the Afghan government and the ICRC)
  is unusually deep, but held down because the question is a state family-law
  due-process question and the government has already withdrawn.
- **dissent-from-denial 0.30.** Sympathetic facts, a 4-3 court below, seven
  amici, and the fraud findings make a statement or dissent plausible; most
  denials of even high-profile petitions are silent.
- **big_case_score 0.7.** A merits decision would define whether kinship and
  foster caretakers hold procedural-due-process rights before adoption, a
  question touching child-placement practice in every state, and the dispute
  is already a national story.

## What I know from outside the record, and its limits

I recognize this case from training data: the Afghan-orphan dispute between
the Masts and the couple identified as the child's relatives was widely
reported through 2024 and 2025, and I was aware of the Virginia Supreme Court's
February 2026 ruling. I do not know the disposition of this petition, which
cannot exist yet: the cell is `forward`, the first live conference is October
16, 2026, and no retrieval surfaced any disposition. My prior familiarity may
make me overweight the case's prominence relative to how the Justices weigh it;
discount the upward adjustments accordingly.

## Retrieval and its limits

CourtListener MCP calls (four) located the related federal matters (the W.D.
Va. tort suit *Doe v. Mast*, 3:22-cv-49, still open, and the Fourth Circuit
appeal 24-1900, terminated April 22, 2026, which underlies respondents' own
pending petition No. 26-226 on a gag order) and failed to surface the Virginia
Supreme Court opinion or *Genalo v. Black*, so the *Genalo* route rests on the
petition's description alone. `fedcourts query` returned recent SCOTUS grants
but no topically similar prior, and the citation filter has no coverage for
*Smith v. OFFER* or *Troxel*. The corpus priors did not move my number.

## Where to discount me most

The single largest uncertainty is how the Court weighs the waiver footnote.
If the Court reads the federal question as fully decided below, my number is
low by perhaps ten points; if it treats the footnote as an adequate state
ground, it is high by about the same. Second, I could not read the appendix's
due-process section or the dissent, so my account of the Virginia court's
reasoning is filtered through the parties' briefs.
