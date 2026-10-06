# Why 0.22, and why "denied"

## Inputs read

- `record/snapshots/2026-10-06.json` (the provisioned baseline, named in `context.json`), `record/context.json` (mode `forward`, band `baseline` under `sal-v4`, `distribution_count` 1, no CVSG, Term 2026), `event.yaml` (stage `cert`, moment `distribution`).
- `record/documents/questions-presented.txt` and `record/documents/petition.txt` (45 pages, full text, not truncated). No brief in opposition exists yet; the Court requested a response on September 10 and it is due November 2, 2026, so my read of the opposition is anticipation, not text.
- `metrics/statpack.md`: the modern-cert disposition section, the relist and CVSG cuts, the circuit cut, and the `sal-v4` segment table.
- Two `fedcourts query` pulls (recent granted and GVR priors) for shape; and the repo's own event record for *RiseandShine Corp. v. PepsiCo* (`data/cases/scotus/72483489`), which shows certiorari granted June 29, 2026 and the merits event unresolved. That is public information predating my snapshot and I use it as forward signal.
- CourtListener MCP was rate-limited (HTTP 429) on both calls I made, with availability about fifty minutes out, so I did not read the Second Circuit opinion (168 F.4th 86) or the *RiseandShine* docket there and worked from the petition's account of the decision below. That is a degraded input: the petition's characterization of what the Second Circuit did is advocacy.

## Anchor

The frozen band is `baseline` under `sal-v4`, which matches the segment table's version. Pooling the bracketed `reached` figures for `baseline` over the nine Term rows strictly before 2026 (2017–2025, weighted by their `n`) gives roughly 5.0 percent (about 637 grant-family outcomes over about 12,720 reached petitions). That is the yardstick this cell is scored against, and my starting point.

Shape checks from the other cuts: the paid-segment relist cut shows a single distribution at 1.2 percent granted plus 0.5 percent GVR, rising steeply at two or more; the CVSG cut shows 4.0 percent granted and 2.3 percent GVR without a CVSG; the Second Circuit's grant family sits at about 4.9 percent, above the docket's average. The modern-cert disposition section shows GVRs are nearly half of the grant family (577 GVR against 655 granted), which matters for the route claim.

## Adjustments up from 5 percent

1. **The Court called for a response after respondent waived.** This is the strongest signal on the record. A response request is an affirmative act by at least one chambers, and the Court essentially never grants a paid petition on a waiver without one. In my experience of the docket, paid petitions with a requested response are granted on the order of one in ten, several times the rate of the undifferentiated paid segment. The frozen band does not see this: `sal-v4` keys on distributions and CVSG, so `baseline` here understates the petition's position, and I treat the response request as moving me well above the band anchor.
2. **A pending granted case the petitioner asks the Court to hold for.** *RiseandShine* (granted June 29, 2026) presents whether trademark strength is a question of fact, from the same circuit, under the same *Lakeridge* law/fact framework. A hold costs the Court nothing and a GVR after a reversal there is a conventional clean-up disposition. This is what pushes the grant family above the one-in-ten that a response request alone would suggest. The GVR query returned several hold-then-GVR priors (the Monsanto petitions, GVR'd in the 2025 Term) as examples of the shape.
3. **Counsel and amici.** Williams & Connolly (Lisa Blatt) for petitioner, Paul Weiss (William Jay) for amicus ASCAP, Latham for respondent. Elite counsel on all sides correlates with grants and signals the parties read the stakes as real.
4. **A clean, Court-friendly legal question.** The Court has repeatedly taken standard-of-review questions (*Lakeridge*, *Highmark*, *Teva*), and *RiseandShine* shows current appetite for exactly the Second Circuit's law/fact line.

## Adjustments back down

1. **Interlocutory posture.** The Second Circuit vacated and remanded for a new rate determination. The Court disfavors review while proceedings continue below, and the BIO will lead with this.
2. **The split is assembled across contexts.** Takings, tax, bankruptcy discount rates, Copyright Royalty Board deference, and RAND patent rates are not the same question as a consent-decree rate court's review of benchmark selection. The BIO will argue the Second Circuit reviews the ultimate rate for reasonableness and applied de novo review only to legal framework issues it had previously articulated, so there is no split on a shared question. Rate-court appeals arise only in the Second Circuit, which petitioner acknowledges and turns into an argument from *Exhibit Supply*, but it also means no other circuit will ever decide this precise question.
3. **One standard-of-review case from the Second Circuit is already on the merits docket.** That cuts both ways: it makes a hold likely but makes a second plenary grant on the same theme less so.
4. **ASCAP's amicus brief is an interested party's**, not a signal of broad disinterested concern.
5. **Respondent's initial waiver** suggests it read the petition as weak, though the Court's request shows at least one chambers disagreed.

## Decomposition

- Hold for *RiseandShine*: about 40 percent. Conditional on a hold, *RiseandShine* reverses the Second Circuit in a way that reaches BMI about three-quarters of the time, and the Court then GVRs rather than denies roughly half the time, giving an unconditional GVR probability near 0.13.
- Plenary grant on this petition's own force: about 0.09.
- Grant family total: 0.22. Denial (including denial after a hold): about 0.77. Dismissal or withdrawal (a global settlement during remand): about 0.01.

Since denial is the modal outcome, `predicted_disposition` is `denied` and `granted` is 0, with `probability` 0.22 carrying the grant-family belief.

## Claims

- `disposition` 0.22, equal to `probability`.
- `relist-increment` 0.96. From a state of one distribution, the response request guarantees a redistribution once the BIO (due November 2) and reply are in, unless the case settles or is withdrawn first. The residual is settlement risk and parse risk, not doubt about the Court's practice.
- `cvsg-increment` 0.08. Above the paid-segment base rate (about 1.2 percent of petitions carry a CVSG) because the response request shows interest and the United States is a party to the BMI consent decree, but the likely paths (deny, or hold for a case already granted) make an invitation unnecessary.
- `summary-disposition-route` 0.58, conditional on a grant: 0.13 GVR against 0.09 plenary. The statpack's cert-order share of the grant family is about 47 percent; I sit above it because the specific grant mechanism here is a hold.
- `dissent-from-denial` 0.05. A commercial Rule 52 question with no hook that typically draws a separate writing.

## Where to discount me

- I did not read the Second Circuit opinion itself. If it in fact reviewed the ultimate rate deferentially and faulted the district court on identifiable legal errors, the petition is weaker than I have it and the number should be lower.
- The hold probability is the swing variable, and it rests on a judgment about how liberally the Court holds for a loosely related granted case when the petitioner asks. If the Court sees *RiseandShine* as trademark-specific, the GVR path collapses and the grant family drops toward 0.10.
- The conditional grant rate after a response request is from my general knowledge of the docket, not a statpack cut; the pack publishes no response-request conditioning.
- `big_case_score` 0.35 rests on the petition's own account of the stakes (three million rightsholders, Live Nation and AEG, every future rate-court appeal); the public salience of a standard-of-review question is modest.
