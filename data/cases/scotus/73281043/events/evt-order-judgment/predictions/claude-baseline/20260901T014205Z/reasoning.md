# Rationale — P(disturbed) = 0.87, judgment = reversed

**Cell.** Forward merits cell at the grant moment (`evt-order-judgment`,
`moment: grant`): cert granted June 15, 2026, in Guerrero v. Johnson,
No. 25-1003 (OT2025 grant Term), a Texas capital case from the Fifth Circuit
(No. 23-70002, an interlocutory certified appeal). I worked from the docket
skeleton plus the provisioned cert-stage documents — the petition (truncated at
117 pages, text present), the brief in opposition (31 pages, text present), and
the questions-presented cut. No merits briefing exists yet at this moment; I
did not retrieve merits advocacy (none has been filed — the grant is eleven
weeks old).

**Anchor.** The committed statpack's merits section publishes an `excluded`
count, so its pooled rate is the scored baseline. My case's grant Term is 2025,
so the pool is grant Terms 2015–2024; the table carries parsed rows for
2017–2024 only (earlier Terms hold no parsed judgments and are omitted).
Pooled: disturbed 360 / parsed 516 = **69.8%**, well over the 30-judgment
floor. That is the bar my Brier skill is scored against. Coverage caveat: Term
2024's parsed 73 of 75 granted is nearly complete; the pool is not materially
censored.

**Adjustments up from 0.70 to 0.87:**

1. *Petitioner identity and posture.* A state petitioner in a capital habeas
   case. The Court's grants of state/warden petitions in AEDPA cases in the
   last decade have been reversed essentially without exception (Shinn v.
   Ramirez, Shoop v. Twyford, Brown v. Davenport, Dunn v. Reeves, Mays v.
   Hines, Thornell v. Jones). A grant to *affirm* a prisoner-favorable circuit
   rule would be highly unusual for this Court.
2. *Doctrinal alignment.* The Fifth Circuit's Cathey test — a claim "must have
   some possibility of merit to be considered available" — is a
   futility-based, atextual reading of § 2244(b)(2)(A), and its statutory
   analysis is three sentences long (the petition quotes it in full). Jones v.
   Hendrix (2023) rejected precisely this kind of futility reasoning under
   § 2255, and Bousley long ago held futility is not cause. The current
   majority's method points one way.
3. *Signals below.* The Fifth Circuit denied rehearing en banc only narrowly,
   with Judge Ho dissenting and calling Cathey "wrong" — the reviewing circuit
   itself is fractured against the rule under review.
4. *Alignment of the United States.* The Solicitor General (D. John Sauer)
   appears on the docket for the United States. Given § 2255(h)(2)'s identical
   language, the federal government's interest runs with Texas; a
   multi-state amicus brief (Louisiana et al.) also supported the petition.
5. *Grant dynamics.* Three distributions and a grant despite the BIO's lead
   vehicle objection (interlocutory posture). Taking an interlocutory capital
   case suggests the Court granted to settle the split against the outlier
   rule, not to bless it.

**Held back from going higher:** the ~10% residual covers (a) a genuine
affirmance — the Ninth Circuit's Muñoz reasoning (importing the PLRA's
practical-availability reading of "available") gives textualists a
colorable hook, and Gorsuch occasionally defects in criminal statutory cases;
(b) a DIG or unexpected procedural exit on the interlocutory posture (~3–4%);
and (c) an affirmance on an alternative ground developed in merits briefing I
cannot see yet. Choosing `reversed` over `vacated`: the certified question is
purely legal and the answer disposes of the gatekeeping issue, so I expect
"reversed" (or "reversed and remanded"), not a vacatur for reapplication of a
new standard — but the reversed/vacated label split is my largest
judgment-label uncertainty (the two together carry most of the disturbed
mass).

**Votes.** 6–3 on the Shinn/Jones v. Hendrix axis is the modal lineup; my
confidence on the exact split is moderate (a 7–2 with Kagan is plausible). The
vote block is banked ahead of its observation channel; I stated all nine
rather than trimming, since scoring is intersection-only.

**Conditioning notes.** `record/context.json`: forward mode, snapshot
2026-06-16 (truncated provenance, cutoff 2026-06-16), Term 2025,
`distribution_count` 3, `band: high` under sal-v4. Per the stage rule, the
salience band scores grant likelihood — settled history here — so I did not
anchor on it or on the cert band tables. The context's `amicus_briefs` is null
while the snapshot shows one amicus filing; that field is an interim-ladder
signal and played no role here.

**Semantic claims and big-case score.** The two propositions restate the
forecast in `predicted_reasoning.md` on their declared axes (ground:
rule-availability-as-legal-question, rejecting the merit/futility gloss;
breadth: categorical, spanning both statutes). `big_case_score` 0.42: an
entrenched split with real stakes for capital habeas practice, but a
technical gatekeeping question of moderate public salience.

**Where to discount me.** I have not seen the Fifth Circuit's opinion itself
(CourtListener's opinion index returned nothing for it; I relied on the
petition's and BIO's extensive quotation of it, which are adversarial
documents). The corpus citation lookup for a key precedent returned empty
(sparse citation coverage — a coverage gap, not absence). And the merits
briefs do not exist yet: this is a docket-skeleton-plus-cert-papers forecast,
as the grant moment defines.
