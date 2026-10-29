# Rationale for the forecast

## Information set

This is a **cert-stage, response-requested** cell, not a prediction of whether
the Court will request a response: that request already occurred. I read the
case-level snapshot `record/snapshots/2025-11-07.json`, the event definition,
`record/context.json`, the document manifest, the question presented, the
substantive portions of the petition, relevant appendix opinions and the
rehearing order, and the October 8 party letter. The manifest marks all staged
documents nonempty, untruncated, and not OCR-derived.

The frozen context says `forward`, Term 2025, `baseline`, `sal-v4`, one
distribution, no CVSG, and a date cutoff of November 7, 2025. I retain that mode
rather than inferring a disposition from the age of the record. The snapshot
contains entries through November 6, including the response request. There is
no brief in opposition on this information set, as expected at this moment.
I do not infer the eventual response's arguments. No current Supreme Court
docket, this petition's disposition, other cells' predictions, or topic-label
artifacts were consulted; I do not know this petition's outcome.

## Anchor and adjustments

The matching `sal-v4` table in the committed `metrics/statpack.md` is the
anchor. Pooling **all eight displayed Terms strictly before 2025**, OT2017
through OT2024, gives **607 grant-family outcomes / 11,599 denial-reweighted
resolved risk-set observations = 5.2332%** for private petitions that reached
`baseline`. I computed the numerator from `prefix_est_grant_rate` times
`prefix_weighted_resolved` in the companion JSON, not by averaging rounded
percentages or using the terminal-band rate. Neither OT2025 nor OT2026 enters
the anchor. These figures describe the committed pack supplied in this
checkout, not a newly refreshed corpus census. The pack exposes no build or
latest-pull timestamp; corpus-wide freshness and this case's `last_pulled` were
not established, and I make no current-population claim from the live lookups.

The paid-segment terminal cuts provide context, not forward hazards. At zero
relists the pack has 10,203 resolved observations, with about 1.8% in the grant
family; at one relist, 2,538 and about 13.7%; at two, 495 and about 41.2%; at
three or more, 484 and about 37.4%. Those are endpoints, not this petition's
probabilities of subsequently reaching them. The no-CVSG cut has 13,556
resolved observations and approximately 6.4% grants plus GVRs; the CVSG cut
has 164 and about 34.8%. None establishes a called-for-response rate.

One actual amicus brief, from the American Bankers Association on October 17,
is visible on the docket even though frozen `amicus_briefs` is null. The
one-amicus terminal bucket has 1,162 resolved observations and about 15.1%
grants plus GVRs. I treat it as a marginal stakes signal, not an independent
multiplier on the band rate or evidence that the final amicus count is one.
The corpus-wide cert table's low overall grant-family share and Fourth Circuit
cut likewise do not supersede the matching risk-set anchor.

I move from the 5.23% anchor to **24%** for three case-specific reasons:

- The Court affirmatively requested a response after the initial distribution.
  That is a positive attention signal, but the prompt identifies its low
  threshold and provides no measured response-requested adjustment.
- The petition, especially pp. 10-13, articulates a concrete conflict between
  the Fourth Circuit's separate-consideration rule and decisions of five
  other circuits. Its federal preemption theory fits the equal-treatment
  precedents discussed at pp. 13-17. This is stronger than a bare assertion
  that a lower court misapplied state contract law.
- The banking association's filing and Spring Oaks' Rule 12.6 letter support
  practical importance and sustained party interest. Spring Oaks is an aligned
  co-defendant, however, not an adverse party conceding the question.

Substantial offsets keep denial the modal result. Appendix A, pp. 1a-3a,
shows a short, **unpublished**, unanimous affirmance applying existing circuit
law. The preemption issue was expressly rejected in a footnote, so I do not
treat it as unpreserved; nevertheless, the earlier Johnson petition, No.
25-34, identified in the provisioned petition could supply a lead vehicle.
I have not retrieved its later history. Appendix B, particularly pp. 12a-17a
and 33a-34a, also shows genuine formation and unilateral-amendment questions,
including Maryland/Utah choice-of-law issues. Those could make the dispute
look narrower and more contract-specific than the petition's five-circuit
framing. Appendix C says rehearing was denied as untimely, not that the en
banc court considered and rejected the federal argument. That is not asserted
as a bar to Supreme Court review, but it provides no fresh en banc endorsement.

The circuit split is the petitioner's characterization. The appendix confirms
the actual federal issue and rationale below, but independent verification of
the other circuits' holdings was unavailable. I therefore discount, rather
than fully credit, the claimed clean five-to-one conflict. The upward adjustment
is a judgment call, not a fitted likelihood ratio or a measured CFR base rate.

## Other probabilities and limitations

The 99% distribution increment largely reflects routine redistribution after
a requested response, not a 99% chance of substantive reconsideration or a
grant. It is written despite being masked for this moment. The 2% new-CVSG
probability reflects the absence of a clear governmental stake. The 40%
summary-route number is conditional on any grant, not an unconditional 40%
forecast; plenary treatment remains more likely within the grant branch.
The 6% writing-on-denial probability leaves a plain denial overwhelmingly
likely within the denial branch. The nine independent writing probabilities
allow rare writings on other dispositions too and do not sum to one.

The stakes score of 0.56 concerns the reach of consumer arbitration and class
litigation, not the chance of certiorari. It does not predict the validity of
Ford's underlying lending claims.

Retrieval was degraded: the CourtListener precedent lookup was throttled
(HTTP 429); three web-tool calls returned no usable content. A broad corpus
query produced unrelated selected grants, including decisions after this
snapshot because its year filter keys on docket Term. Those rows supplied
neither a time-specific prior nor an estimate and were not used to adjust the
forecast. A targeted historical docket query returned an uninformative masked
row. I made no REST fallback and obtained no external opinion text. The
forecast therefore rests on the provisioned filings and committed pack; see
`retrieval.md` for every attempted external lookup and transfer line.
