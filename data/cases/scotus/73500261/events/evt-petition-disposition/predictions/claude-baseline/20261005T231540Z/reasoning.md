# Rationale for P(grant) = 0.20

## What this petition is

The provisioned petition text makes the posture unusual, and the posture drives the number. Louisiana *won* in the en banc Fifth Circuit (Feb. 20, 2026, 170 F.4th 292): the court vacated the preliminary injunction against H.B. 71 on ripeness grounds without rendering the dismissal Louisiana asked for. Louisiana then filed a "conditional petition for writ of certiorari," expressly conditioned on the Court granting a petition arising out of the Texas companion case, *Nathan v. Alamo Heights ISD* (en banc, Apr. 21, 2026, upholding Texas's S.B. 10 on the merits and rendering dismissal). Section I of the petition argues at length that review is *unwarranted*; Section II says only that if the Court grants *Nathan* it should grant *Roake* too, invoking *Forney v. Apfel* for a prevailing party's right to seek the "other half of the loaf."

Retrieval established the cluster's state: the Texas plaintiffs' petition is docketed as No. 26-257 (filed Aug. 17, 2026; Texas's response extended to Oct. 28, 2026; one amicus brief so far). The Louisiana plaintiffs obtained an extension to June 20, 2026 to petition from the *Roake* judgment (No. 25A1239) but I found no petition of theirs on any docket, and they waived a response here on July 6. So this docket is the only vehicle from the *Roake* judgment, and both sides of it would rather the Court not take it.

The snapshot's one striking entry is the July 28 **"Response Requested"** after the waiver, followed by two extensions pushing the response to Oct. 19, which lines up with the Oct. 28 response date in 26-257. I read that as the Court wanting the full cluster briefed together, which is a mild positive signal about the Court's interest in the cluster rather than about this petition on its own.

## Anchors

- `record/context.json` freezes `band: state` under `sal-v4`, `distribution_count: 1`, no CVSG, Term 2025, mode `forward`. Per the prompt, the yardstick is the state band's bracketed `reached` rate pooled over Terms strictly before OT2025. Pooling the eight prior rows the table renders (2017 to 2024) gives roughly **23%** (weighted n = 392). That rate is the grant family, GVRs included.
- Modern discretionary-cert base rate: a few percent; relist-count cut at one distribution: granted 8.2%, GVR 5.1%; no-CVSG cut: granted 4.0%, GVR 2.3%. The relist cuts bucket by terminal count, so I used them for shape, not as the answer.

## Adjustments

Starting from about 23%, I moved **down** because this is a derivative petition: it can be granted essentially only if 26-257 is granted, and even then the Court may simply hold it and deny it after decision. My decomposition:

- P(the Court grants 26-257) about **0.45**. For: the issue is of obvious national importance (Louisiana, Texas, Arkansas, Alabama, and Tennessee have enacted classroom-display laws); the en banc Fifth Circuit held that *Stone v. Graham* did not survive *Kennedy*, which only this Court can say; the Court's recent appetite for Religion Clauses cases (*Kennedy*, *American Legion*, *Mahmoud*). Against: no circuit split (the Fifth Circuit aligned itself with the Third and Fourth Circuits' *Kennedy* methodology); active percolation, with the Eighth Circuit having argued *Stinson* on Sept. 22, 2026; facial, pre-enforcement posture; and the strategic-denial dynamic, in which the three Justices most likely to want *Stone* reaffirmed may not supply the votes to grant, while the majority may be content to let the Fifth Circuit's rule stand.
- P(this petition granted | 26-257 granted) about **0.45**: roughly 0.35 for a consolidated plenary grant (the Fifth Circuit consolidated the cases, and Louisiana's ripeness win is entangled with the Article III questions the Court would face in *Nathan*) plus roughly 0.10 for a hold followed by a GVR if Texas prevails.
- Product about 0.20, with a small residual for paths I have not enumerated. I did not add for the response request beyond what is already in the 26-257 estimate.

The number sits slightly below the band's pooled reached rate, which is where a state-captioned petition whose own petitioner asks for denial belongs.

## Claims

- `disposition` 0.20, as above.
- `relist-increment` 0.96: one distribution shown; the called-for response is not yet filed, so redistribution is close to certain. The residual is withdrawal or an unexpected summary denial on the existing distribution.
- `cvsg-increment` 0.05: no federal party; the SG would file as amicus uninvited.
- `summary-disposition-route` 0.22: of the grant mass, roughly 0.045 is a hold-then-GVR and 0.155 plenary; the conditional share is about 0.22, which is below the docket-wide cert-order share of grants because a consolidated plenary grant is the natural form here.
- `dissent-from-denial` 0.08: a writing would attach to 26-257, not to the prevailing state's conditional petition.

## Uncertainties and where to discount me

- The whole number is a product of two judgment calls about a companion docket. If the Court grants 26-257, the realized probability here jumps to something like 0.45; if it denies 26-257, this petition is denied with near certainty.
- The event may stay open for a long time: a hold behind 26-257 would resolve this docket only after a merits decision in 2027.
- I did not read Texas's brief in opposition in 26-257 or any brief in opposition here, since none has been filed; the respondents' position on this petition is unknown beyond their initial waiver.
- `documents.json` shows the petition fetched with `truncated: true` (292 pages); the appendix opinions were cut, but the petition's full argument section was present and read.
- I know of no decided outcome for this case; nothing retrieved disclosed one, and today's order list from the Sept. 28 conference could not have acted on a petition whose response is due Oct. 19.
