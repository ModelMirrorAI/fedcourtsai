# Reasoning — why P(grant) = 0.30

## Inputs read

Provisioned snapshot `record/snapshots/2026-09-18.json` (docket No. 25-1131,
paid, Term 2025, from the Supreme Court of Kentucky, 727 S.W.3d 400);
`record/context.json` (mode `forward`, band `elevated` under `sal-v4`,
`distribution_count` 2, no CVSG, `signals_observable` true); the event
definition (`kind: petition`, no stage recorded, so cert governs; no `moment`
recorded, so I read it as the ordinary distribution cell); and all three
provisioned documents, none flagged `empty_text` or truncated: the 51-page
petition, the QP file, and the 46-page brief in opposition. I did not have the
September 1 reply or any of the 16 amicus briefs as text; I know them only from
the docket entries and the party list.

## Anchor

Band `elevated`, Term 2025, so I anchor on the statpack's *Segment base rate by
salience band (sal-v4)* table, bracketed `reached` figure, pooled over the Term
rows strictly before 2025 that the table renders (2017 through 2024):

| pooled elevated `reached` rate | n |
| --- | --- |
| 17.2% | 2810 |

The salience version matches (`sal-v4` on both sides), so the band table is a
valid anchor. For shape only, not as the answer: the relist-count cut puts a
petition at bucket 1 at about 13% grant-family; the CVSG cut's `none` row at
about 6%; the whole modern-cert base rate at a few percent.

## Adjustments up from 17%

- **Call for a response after a waiver.** The respondents waived on April 27
  and the Court requested a response on May 14. That is an affirmative act of
  attention by at least one chambers, the cert-stage analogue of a CVSG, and
  the `elevated` band does not fully price it (the band keys on distributions
  and CVSGs). The two distributions on this docket are a CFR cycle, not a
  relist: the Court has never yet voted the petition up or down.
- **Cert-stage amicus support.** Sixteen briefs, including 20 states led by
  Kentucky (whose own high court is the court below) and a cross-faith set of
  religious organizations, plus Manhattan Institute and two law-school
  clinics. That volume is rare outside petitions the Court ends up granting.
- **Counsel.** John Bash (Quinn Emanuel, former Assistant to the Solicitor
  General) with First Liberty for the petitioner; Skadden's Supreme Court group
  for the neighbors, retained after the CFR. Both sides are treating this as a
  live grant candidate.
- **The legal question is genuinely open at the Court** and the split is
  acknowledged by the lower courts themselves (Roman Catholic Bishop of
  Springfield's survey, Thapar's Tree of Life dissent). Anash, Inc. v. Borough
  of Kingston (3d Cir. July 30, 2026), which I confirmed on CourtListener as a
  published decision with docket 25-1097, post-dates the petition, divided the
  panel, and rejects the alternative-means and self-imposed-burden factors the
  Kentucky Supreme Court relied on. The BIO has to spend a page arguing it is
  not yet binding. The reply presumably leads with it.
- **The Court's current appetite.** It granted Grand v. City of University
  Heights (No. 25-965) on June 30, 2026, a religious land-use case out of the
  Sixth Circuit, showing the subject matter has attention this Term.

## Adjustments down

- **Vehicle problems the BIO documents from the state-court briefs.**
  Petitioner's motion for discretionary review asked the Kentucky Supreme
  Court to adopt Livingston; the Court dislikes reviewing a rule the petitioner
  requested (Kibbe). The substantial-burden ruling rests partly on a
  fact-bound failure of proof about a smaller grotto on the church lot. The
  equal-terms argument was first made in the opening brief in the Kentucky
  Supreme Court, without a record on comparators, and the state court's
  treatment is two pages. A statutory-construction grant on a record this thin
  would be unusual.
- **Odd posture.** The RLUIPA claimant won before the zoning board; the
  adverse parties are private neighbors enforcing a state statute that strips
  the board of variance power. The BIO's §2000cc(a)(2)(C) argument (no
  "individualized assessment" was permitted, so the substantial-burden
  provision never applied) is not really an independent state ground, but it
  is a threshold federal question the Court would have to clear first, and it
  gives a cautious Justice a reason to wait for a conventional denied-permit
  case.
- **Track record.** Tree of Life (2019), Canaan Christian and New Harvest
  (both January 2023) and Spirit of Aloha (2025) were all denied without noted
  dissent despite the same split arguments, and Apache Stronghold (RFRA
  substantial burden) was denied over a Gorsuch dissent. The Court has been
  choosy about substantial-burden standards.
- **Small facts.** A 16-by-39-foot grotto and a neighborhood traffic dispute
  are not the stakes profile that drags a reluctant Court in; the states'
  brief supplies the national-importance argument the facts do not.

## Landing the number

The CFR plus the amicus wall would, in a clean municipal-denial vehicle, put
me near 0.45 to 0.50. The invited-error, preservation, and posture problems
are each the kind of flaw the Court has used to pass on this exact subject
before, and they pull me back hard. I land at **0.30**, a little under double
the pooled band anchor. `predicted_disposition` is `denied` because that is
still the modal outcome; `granted` is 0.

## The other claims

- `relist-increment` 0.50: from the state of two distributions with no vote
  yet taken. A grant off the long conference may come without a relist (the
  post-conference grant list) or after one; a denial may come quietly on
  October 5 or after a relist to write. Strong petitions at the long
  conference are relisted at well above the population rate, so I sit near
  even.
- `cvsg-increment` 0.10: federal statute, DOJ enforces it, but no US filing so
  far and no CVSG in the comparable recent denials.
- `summary-disposition-route` 0.05, conditional on grant: no intervening
  decision; Grand is a ripeness question and cannot supply a GVR ground.
- `dissent-from-denial` 0.30, conditional on denial: Gorsuch (Apache
  Stronghold) is the obvious author, Thomas the obvious joiner, Kavanaugh or
  Alito the plausible "statement" writers; against that, none of the four
  recent RLUIPA land-use denials drew a writing.

## Where to discount me

- I have not read the reply or the amicus briefs; my read of Anash's effect is
  inferred from the BIO's pre-emptive treatment, and my characterization of
  Grand's question is from public docket material rather than the petition.
- The CFR signal is the biggest single driver and the statpack carries no cut
  for it, so its weight is my judgment, not a measured rate.
- I know of no decision in this case; the snapshot is dated today and the
  conference is September 28. No outcome-revealing material surfaced.

## Retrieval and degradation

MCP and the corpus service both worked. `fedcourts query` is a structured
filter and carries no subject filter that reaches RLUIPA, so its priors were
generic recent grants and contributed nothing beyond confirming the tooling;
the statpack supplied the base rates. See `retrieval.md`.
