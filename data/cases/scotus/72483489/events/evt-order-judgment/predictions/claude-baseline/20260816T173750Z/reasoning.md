# Rationale for P(disturbed) = 0.80, judgment = vacated

**The committed baseline.** The statpack's "The merits docket (granted cases)"
section publishes an `excluded` count (67), so its rate is quotable and is the bar
my Brier skill is scored against. This case's grant Term is 2025 (petition GRANTED
June 29, 2026, from the event's `opened_at`; the docket-number Term, 2024, is not
the axis). Pooling `disturbed` over `parsed` across the grant Terms strictly
before 2025 that the pack holds (2017–2024; the pack carries nothing earlier, so
the ten-Term window truncates to eight): 359/515 = **69.7%**, comfortably past the
30-parsed floor. That is the anchor.

**Adjustments up from 69.7%:**

- **The Court granted to resolve a 12–1 split, and the case comes from the
  outlier.** The QP is exactly the Second Circuit's solo position (strength as a
  question of law); the petitioner lost below under that position. When the Court
  takes a lopsided split from the lone outlier circuit, the modal outcome is
  adoption of the majority rule and a remand — which disturbs this judgment.
- **The United States is against the decision below on the merits.** The CVSG
  brief (May 20, 2026) recommended denial but agreed the Second Circuit
  "mischaracterized the inquiry" (Patently-O's summary of the SG brief; the brief
  PDF itself was 403-blocked to my fetch tool). The SG's merits read is a strong
  predictor of the Court's.
- **The grant itself absorbed the vehicle objections.** The Court granted over an
  SG deny-on-vehicle recommendation, after both parties filed supplemental briefs
  (June 8, 2026) on those objections — so the vehicle problems were known and
  discounted at the grant, which lowers the DIG residual below its base rate.
- The Court's precedent leans petitioner's way: Hana Financial (consumer-
  perception inquiries are for the jury) and Booking.com (a mark's character
  depends on consumer meaning) are the petition's two lead authorities and are a
  comfortable doctrinal fit.

**Adjustments down (why not 0.90):**

- **The BIO's outcome-independence argument is the real affirmance path.**
  PepsiCo argues a ruling for Rise "would not change this case's outcome given the
  reasoning below, unchallenged Second Circuit precedent, and the record" — i.e.,
  even treated as fact, no reasonable jury could find the RISE marks strong, and
  other confusion factors independently support summary judgment. The SG evidently
  credited some of this. If the Court agrees, it can hold for petitioner on the
  characterization yet still `affirm` — undisturbed on the scored binary. I price
  affirmance ≈ 0.15.
- **Unpreserved-argument and reverse-confusion complications** (the BIO's second
  vehicle point) keep a DIG live at ≈ 0.04, and an equally divided affirmance is
  ≈ 0.01 absent any visible recusal.

Rough decomposition consistent with my number: vacated ≈ 0.55, reversed ≈ 0.22,
affirmed-in-part ≈ 0.03 (disturbed ≈ 0.80); affirmed ≈ 0.15, DIG ≈ 0.04, equally
divided ≈ 0.01. `judgment = vacated` is the modal single label; `probability =
0.80` is the disturbed mass; `granted = 1` states the same binary;
`predicted_disposition = other` per the merits-stage contract.

**What I worked from.** This is a `forward` cell at `moment: grant` — no merits
briefing exists yet (petitioner's merits brief is due August 31, 2026), so there
is no merits advocacy to retrieve. I worked from the provisioned snapshot (docket
skeleton through August 10, 2026), the provisioned cert-stage documents
(`questions-presented.txt`, `petition.txt` [truncated: true, but the body and
appendix excerpts I needed were present], `brief-in-opposition.txt`), the
committed statpack, and open-web retrieval for the SG's CVSG position
(supremecourt.gov and justice.gov both refused my fetch tool with 403s; a
Patently-O summary supplied the SG's bottom line — deny on vehicle, but the
Second Circuit "mischaracterized the inquiry"). A corpus `fedcourts query`
citation lookup for Hana Financial returned no rows (citation coverage is sparse:
161 of 590,339 SCOTUS rows), so priors came from the statpack alone.

**Where to discount me.** (1) My read of the SG brief is secondhand — a blog
summary, not the brief text; if the SG's merits agreement was narrower than
"mischaracterized the inquiry" suggests, my upward adjustment overshoots.
(2) The vacated-vs-reversed split within the disturbed mass is genre judgment
(mischaracterization cases usually vacate), not case-specific evidence. (3) The
9–0 vote forecast is a prior from recent trademark unanimity; nothing in this
record individuates any Justice. (4) The salience band in `record/context.json`
(`high`, sal-v3) is a cert construct — per the stage rules I did not anchor on it,
and no flag is owed for its presence.

**Band/context note.** `band: high` under `sal-v3`, `distribution_count: 3`,
`cvsg_date: 2025-10-06`, all frozen at provisioning; cert signals are spent at
this stage and were used only as case history (the CVSG-then-grant path), not as
an anchor.
