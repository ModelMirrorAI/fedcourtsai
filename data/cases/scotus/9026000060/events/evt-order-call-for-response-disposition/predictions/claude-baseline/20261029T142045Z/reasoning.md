# Reasoning — P(grant family) = 0.17

**Inputs read.** Snapshot `record/snapshots/2026-08-27.json` (cutoff
2026-08-27, `date` cut, forward mode); `record/context.json` (band
`baseline` under `sal-v4`, distribution_count 1, no CVSG, term 2026);
`record/documents/questions-presented.txt` and `petition.txt` (truncated at
the cap; read the QP, statement, reasons and vehicle sections). No BIO was
provisioned — it did not exist at the cutoff. Forward-mode retrieval: the
live supremecourt.gov docket shows an extension of the response time, an NRA
amicus brief (Sep 24) and the BIO filed Oct 26, 2026, and no disposition, so
the cell is correctly pending. I did not read the BIO's text.

**Anchor.** Band `baseline` (sal-v4) — the table's heading matches my
context's salience version. Pooling the bracketed `reached` figures for
OT2017–OT2025 (every rendered Term strictly before OT2026) gives roughly
660 grants over ~13,100 weighted petitions ≈ **5.0%**. That is the
yardstick. The band does not register the call for a response (sal-v4 keys
on relists/CVSG/caption class), and no committed table conditions on one, so
how far that moves me is judgement.

**Adjustments up.**
- The Court called for a response a week after first distribution, before
  the long conference — a Justice wanted the case briefed. Called-for
  responses on paid petitions historically grant materially above the paid
  base (my recollection, not a committed figure: on the order of 10%).
- Elite Supreme Court counsel (Clement & Murphy), a 22-State amicus brief
  (West Virginia et al.), NSSF's motion, and later an NRA/SAF brief — the
  statpack's amicus cut puts 2+ amicus petitions at ~18% granted vs 2% for
  zero (n≈1,449 resolved), a marginal shape, not an additive adjustment.
- A divided panel (Quattlebaum, J., dissenting) on third-party
  traceability, an area this Court has taken repeatedly (*California v.
  Texas*, *Alliance for Hippocratic Medicine*, *Murthy*, *Diamond
  Alternative Energy*), and it follows the Court's unanimous skepticism of
  industry-liability theories in *Smith & Wesson v. Mexico* and *Taamneh*.

**Adjustments down.**
- Interlocutory posture: the Fourth Circuit reversed a standing dismissal
  and remanded, leaving PLCAA and proximate cause undecided. Defendants can
  still win on remand, the ordinary reason to deny.
- The "split" is about how to phrase the standard (determinative/coercive
  vs. predictable effect), and the panel said it would find standing under
  either — a vehicle point respondents will press.
- Fourth Circuit originating-circuit cut: ~1.3% granted, unremarkable.

Net: from ~5% to the low-to-high teens; I settle at **0.17** for the grant
family, including a summary reversal. Main uncertainty: whether the BIO's
interlocutory/vehicle arguments land (I did not read it), and how much the
response request reflects one Justice's interest rather than four.

**Other claims.** relist-increment 0.97 (redistribution after the response
is near-certain; the harness masks it on this moment). cvsg-increment 0.02
(private parties, Article III question). summary-disposition-route 0.20
conditional on grant (the petition expressly asks for summary reversal;
plenary review is still the norm for a standing-doctrine question).
dissent-from-denial 0.17 conditional on denial: a called-for, amicus-backed
petition on a Second Amendment-adjacent industry-liability question draws
more separate writing than average, but an interlocutory denial is easy to
let pass silently. order-writers puts the most weight on Thomas and Alito,
then Gorsuch, with Jackson and Sotomayor carrying the summary-reversal
dissent path.

**big_case_score 0.6**: consequential for firearms-industry liability and
third-party standing doctrine generally, but procedural and at the pleading
stage.

**Where to discount me.** The "called-for response" uplift is from memory,
not a committed table. The petition was truncated at the cap (the appendix
was cut), so I read the Fourth Circuit opinion only through the petition's
characterization of it.
