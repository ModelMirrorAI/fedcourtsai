# Rationale for the numbers

**P(grant) = 0.47; predicted disposition `denied` (the modal single label), with `gvr` the second most likely label at about 0.41.**

## Anchor

The frozen conditioning is `band: baseline` under `sal-v4`, which matches the statpack's segment table heading, and `distribution_count: 1` with no CVSG. Pooling the baseline band's bracketed `reached` figure over the nine rendered Terms strictly before OT2026 (OT2017 through OT2025, weighted by the bracketed `n`) gives about 5.0% (roughly 637 grants over 12,720 risk-set petitions). That is the yardstick the evaluator scores this cell against, and it is the right prior for a once-distributed paid petition with nothing else known about it. The relist-count cut (bucket 1: granted 8.2% plus gvr 5.1%) and the CA5 originating-circuit cut (granted 1.6%, gvr 2.1%) sit in the same neighbourhood. I read the statpack's modern-cert section for the overall gvr-to-granted split (577 to 655), which is the uninformed prior for the summary-disposition-route claim.

## Why I move far above the anchor

The adjustment is almost entirely one fact, which predates my snapshot and is public: the corpus row for No. 26-104, *Rhoney v. Barbosa da Cunha* (CA2, docketed July 23, 2026, distributed for the same September 28 conference, counsel D. John Sauer for the government and Michael Tan and Matt Adams for the respondent, the same lawyers as in this case), records `date_cert_granted: 2026-10-01`. That is the government's petition on exactly this question, from the circuit that ruled against it. The Second Circuit's September 25, 2026 order denying rehearing en banc (which I read via CourtListener) describes the split as the Fifth and Eighth Circuits for the government against the Second, Seventh, Sixth, Eleventh, Tenth, Ninth, First and Third for the noncitizens, cites *Buenrostro-Mendez v. Bondi*, 166 F.4th 494 (5th Cir. 2026) with Judge Douglas dissenting, and notes that the Supreme Court had granted and then dismissed per stipulation another detention case (*Genalo v. Black*) in June and September 2026. The petitioners' September 25 letter "re DC" on this docket is almost certainly about that en banc order in *Da Cunha*.

Given the companion grant, this petition's fate is a held-case problem rather than an ordinary cert question:

- P(the Court holds or relists rather than denying outright) ≈ 0.85. Petitioners lost below on the question the Court has just taken, so a hold is the near-reflexive treatment; an outright denial on October 5 is possible but would forfeit the petitioners' remedy for no reason I can see on the record. The Fifth Circuit judgment (reversal of district-court habeas grants, rehearing en banc denied April 9, 2026) is in a GVR-able posture.
- P(the Court rules for the noncitizens in *Rhoney*) ≈ 0.50. The lower-court consensus is lopsided and includes thirty years of consistent executive practice and *Jennings*'s description of section 1225(b) as the border provision, but the deeming clause in section 1225(a)(1) is a strong textual hook, the dissents and the two pro-government circuits are written by judges whose method the current majority shares, and the government won the grant it asked for. I treat it as a coin flip.
- P(GVR | held, noncitizens win) ≈ 0.95; P(GVR | held, government wins) ≈ 0.02.
- P(plenary grant and consolidation, or replacement vehicle if *Rhoney* becomes moot) ≈ 0.07. The Court declined to take both cases on October 1, which argues against consolidation, but the government's filing here is docketed as "Brief of Federal Respondents filed" rather than a brief in opposition, which reads as acquiescence, and detention vehicles are fragile.

Arithmetic: 0.85 × (0.50 × 0.95 + 0.50 × 0.02) + 0.07 ≈ 0.48, which I round to 0.47. Conditional on any grant, the GVR share is about 0.41 / 0.48 ≈ 0.85, which is the summary-disposition-route number.

## The other claims

- `relist-increment` 0.88: a hold ends with a redistribution before disposal, a relist on October 5 is itself an increment, and a plenary grant also comes off a redistribution; only an outright October 5 denial leaves the count at one. Note that the snapshot carries two "DISTRIBUTED for Conference of 9/28/2026" entries around a "Rescheduled" entry; the harness counts them as one distribution and I forecast from that count.
- `cvsg-increment` 0.01: the Solicitor General is counsel of record for the federal respondents, so no invitation can issue.
- `dissent-from-denial` 0.08: a denial would follow a government merits win in *Rhoney*; held petitions denied in that posture rarely draw writings.

## Uncertainties and where to discount me

- The snapshot was generated October 2, 2026 and the Court's October 5 order list has already issued. I deliberately did not look up this docket's own current state. If the petition was denied on October 5, my 0.47 is badly wrong in the direction of over-prediction; if it was relisted, the relist claim is already true.
- My read of the companion grant comes from a corpus row, not from the Supreme Court's order list itself, and the Fifth Circuit opinion text was not available on CourtListener (both the Fifth Circuit's *Sosnava Rodriguez v. Ortega* and the Second Circuit en banc order returned no text through `read_document`; the en banc order's text came through the opinions endpoint instead). I did not read *Buenrostro-Mendez* itself.
- No filed-document text was provisioned (`record/documents/` does not exist), so I have not read the questions presented, the petition, the government's brief, or the two letters; the characterization of the brief as non-opposing rests on the docket entry's wording alone.
- The merits coin flip is the dominant driver and is my own judgment, not a base rate. A reader who believes the Court will side with the government on the text should move toward 0.10; one who believes the circuit consensus will hold should move toward 0.80.
- The `big_case_score` of 0.75 reflects the stakes of the question (detention policy for a very large population), not the odds of this petition being the vehicle that decides it.
