# Reasoning for P(disturbed) = 0.70

**Inputs.** Snapshot `2026-09-29.json` (forward mode, date cut 2026-09-29).
I read the provisioned questions-presented, petition, BIO, appendix, and both
merits briefs: petitioner's brief (Aug 6, 2026, WilmerHale) and Florida's
respondent brief (Sep 28, 2026). All of them came with `empty_text: false` and
untruncated. I read none of the ~28 amicus briefs. The snapshot lists the
United States among amicus counsel, but its brief does not appear in the
proceedings by the cutoff, so I do not know which side it supports. I did no
retrieval beyond the provisioned inputs and the committed statpack.

**Anchor.** The statpack's merits section publishes an `excluded` column, so
it can be quoted. The grant date is 2026-06-15 (OT2025), so the pool is grant
Terms 2015–2024. The table shows rows for 2017–2024 only, since Terms with no
parsed judgment are omitted. Pooled: 360 disturbed / 516 parsed ≈ **69.8%**.
Coverage is high in those Terms: parsed against granted is close to 1 except
OT2020 (69/79) and OT2024 (73/75). This is the bar I am scored against.

**Adjustments.** I end close to the anchor, but the signals pull both ways.
- *Up:* The Court took this question after five distributions and a called-for
  response, by IFP grant, and chose this vehicle over the companion petitions
  (Parada, Minor). The respondent's own statement of the QP is "whether the
  Court should overrule Williams". Granting a case framed that way suggests at
  least four Justices doubt Williams. Ramos's originalist method points toward
  the petitioner, and Gorsuch is on record (Khorrami v. Arizona dissent from
  denial) wanting to reconsider Williams. The vehicle is clean: Florida
  conceded preservation at the cert stage.
- *Down:* Reliance is unusually concrete. Florida cites about 5,200 pending
  direct appeals, at least seven States use smaller felony juries, and 13+
  States appear as amici for Florida. Florida also argues that overruling
  Williams would unsettle Rule 48 civil juries and other non-originalist
  precedents. Roberts, Alito and (in Ramos) Kagan weigh stare decisis heavily,
  and Barrett and Kavanaugh have voiced reliance-sensitive views. Five votes
  to overrule are not guaranteed even if four voted to grant.
- These roughly cancel, so I settle at 0.70, a hair above the base rate.

**Judgment label.** Ramos's disposition was "reversed", so I predict
`reversed`. A "vacated and remanded" judgment (e.g., so the state court can
take up harmless error) would also count as disturbed and costs nothing on the
Brier axis.

**Where to discount me.** My vote assignments, especially Barrett, Kavanaugh
and Kagan, are educated guesses from past alignments. I did not read the
amicus briefs, including the United States' (side unknown). I do not know the
argument date or how the argument went; it had not happened by the cutoff.
I do not know this case's outcome.
