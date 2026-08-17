# Rationale — claude-baseline, evt-order-judgment (moment: grant), run 20260816T173750Z

**P(disturbed) = 0.85, judgment `vacated`, 9-0.**

## Anchor

The committed statpack's "The merits docket (granted cases)" section
publishes an `excluded` count (67), so its rate is quotable and is the
baseline this cell is scored against. Grant date is the event's `opened_at`,
2026-07-20, i.e. grant Term OT2025; the pool is grant Terms 2015-2024,
strictly before mine. The pack's table holds Terms 2017-2025, so the
available pool is 2017-2024: disturbed 50+34+49+46+57+42+50+31 = 359 over
parsed 73+55+72+65+69+54+75+52 = 515 → **69.7%** (n=515, comfortably past
the 30-parsed floor). Terms 2015-2016 hold no parsed judgments in this pack,
so the shown window is the window.

## Adjustments up from 69.7%

- **Posture.** The petitioner lost below and asks the Court to correct the
  legal standard; the Court grants overwhelmingly to disturb, and the pooled
  base rate already reflects that. This case is a stronger-than-average
  member of that class: affirming would entrench the Alaska/Eleventh Circuit
  "abstract" approach against the Ninth Circuit — the split the grant
  presumably exists to resolve — and would put federal and state courts in
  Alaska under conflicting Eighth Amendment regimes.
- **Deliberateness of the grant.** Alaska waived response; the Court called
  for one (Sep 17 2025), distributed the petition three times, held it from
  the 12/12/2025 conference to the 6/29/2026 conference, and granted after a
  supplemental brief. That is a Court that saw the BIO's vehicle objections
  and took the case anyway.
- **Doctrinal alignment.** Bajakajian's own application was
  defendant-specific (actual harm, actual sentence, culpability "relative to
  other potential violators"); the decision below compared the plane to the
  theoretical maximum fine and charged Jouppi with legislative-history harms
  — moves Bajakajian expressly discounted. Timbs (2019), the nearest
  analogue, was 9-0 to vacate. Recent separate writings (Toth, Culley,
  Leonard) show sustained cross-ideological appetite for policing fines and
  forfeitures, and no sitting Justice is an evident defender of the abstract
  approach.
- **Facts.** A $95,000 airplane forfeited over a six-pack, first offense,
  minimum sentence — maximally sympathetic, and the Alaska Supreme Court
  resolved all factual disputes in Jouppi's favor, leaving a pure question
  of law.

## Adjustments down / uncertainty

- The State's best argument — that the "split" is really disagreement over
  emphasis within a shared multi-factor framework, making this
  error-correction — could support a narrow affirmance if a majority reads
  the decision below charitably (it did nominally examine Jouppi's specific
  facts). I weight this low but not at zero.
- A DIG remains possible if the merits briefing exposes the culpability
  fact-disputes the Alaska Court of Appeals wanted found; a DIG counts as
  undisturbed. Small (~3%) but it belongs in the complement.
- This forecast is made from the **docket skeleton plus cert-stage
  documents** (petition, BIO, QP — all provisioned with clean text) and
  public post-grant coverage. No merits briefs exist yet (moment: grant;
  the docket shows only a joint-appendix motion after the grant), so
  nothing here reflects merits advocacy.

Netting: start ~0.70, add the posture/alignment/deliberate-grant evidence,
subtract the DIG/narrow-affirmance mass → **0.85**.

## Other fields

- `judgment` = `vacated` over `reversed`: the petition itself asks for
  correction-and-remand, and unresolved fact issues make the Court unlikely
  to hold the forfeiture excessive itself.
- Votes: 9-0 majority, per Timbs and the cross-ideological writings above;
  intersection-only scoring means the full list costs nothing. Authorship
  guess (Gorsuch) is unscored.
- `big_case_score` 0.6: first excessiveness-standard case since Bajakajian,
  nationwide forfeiture stakes, heavy coverage — but a methodological QP,
  not a blockbuster.
- The salience band in my context (`high`) is a cert construct; per the
  prompt's merits-stage rule I did not anchor on it.
- The cert-stage guidance's relist/CVSG claims are spent here; the declared
  set is `merits-v1`'s single `judgment-disturbed`, restated from
  `probability`.

Where to discount me: I cannot see why the petition was held for six months
(Dec 2025 → Jun 2026) or what the June 2026 supplemental brief said; if the
hold was for a related case whose decision reshapes the question, my
adjustment is blind to it. My corpus prior retrieval returned nothing
(sparse citation coverage), so the 69.7% anchor plus general legal knowledge
carries more weight than case-matched priors would.
