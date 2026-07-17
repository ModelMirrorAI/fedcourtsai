# Pestarino v. Pestarino, No. 25-1249 — petition disposition

**Prediction: denied. P(any grant, GVR included) ≈ 0.002.**

## The case

Bart Pestarino, proceeding pro se (paid docket), petitions from the Washington
Supreme Court's October 8, 2025 denial of review of an unpublished Washington
Court of Appeals, Division 1 decision (No. 86578-1-I, Apr. 21, 2025) affirming a
civil protection order entered against him in Skagit County Superior Court in a
dispute with his ex-spouse. The petition attacks Washington's civil protection
order statute, RCW 7.105, and the federal statutes that give such orders
nationwide effect.

## The question presented and the governing standard

The QP is a sprawling compound question: whether a State may impose
"punishment-like" consequences (firearm prohibition, loss of parental rights,
warrantless-arrest exposure, movement restrictions, stigma) through civil
proceedings on a preponderance standard without criminal procedural safeguards,
and whether the federal statutes that nationalize such orders — 18 U.S.C.
§ 922(g)(8), 18 U.S.C. § 2265, and the VAWA self-petition provisions (8 U.S.C.
§§ 1101(a)(51), 1367) — operate as bills of attainder. The body of the petition
adds Second Amendment (Heller/Bruen/Rahimi), Supremacy Clause/immigration
preemption, and due process theories.

Certiorari is governed by Rule 10: the Court grants for genuine, developed
splits of authority or questions of exceptional national importance presented in
clean vehicles, almost never for asserted error correction in a fact-bound
two-party dispute.

## Why this petition will be denied

1. **Vehicle.** A pro se petitioner litigating against his ex-spouse over a
   state protection order, on review of an *unpublished* intermediate state
   appellate decision that the state supreme court declined to hear. There is no
   respondent with institutional stakes, no amici, and the state-court record
   (per the petition's own framing) is dominated by case-specific findings.
2. **No split.** The petition alleges no circuit or state-court split on any of
   its questions; it argues first-principles unconstitutionality. Rule 10
   petitions of this shape are denied as a matter of course.
3. **Rahimi forecloses the core federal theory.** United States v. Rahimi, 602
   U.S. 680 (2024), upheld § 922(g)(8) against facial Second Amendment
   challenge just two Terms ago. A pro se petition asking the Court to revisit
   the civil-protection-order-to-firearm-disability pipeline so soon, in a
   domestic-relations posture, has essentially no chance.
4. **The bill-of-attainder theory is not seriously contestable.** Statutes of
   general applicability triggered by individualized judicial findings are the
   opposite of legislative punishment of named individuals (Nixon v.
   Administrator; United States v. Brown); no court of appeals has held
   otherwise for § 922(g)(8) or § 2265.
5. **Docket signals are all baseline.** Filed Jan. 6, 2026 (docketed May 5,
   2026); a short 12-page brief in opposition was filed June 2, 2026; the case
   was distributed once, on June 17, 2026, for the September 28, 2026 long
   conference. No relist (the conference has not yet occurred), no CVSG, no
   amici. The long conference is where the summer's accumulated petitions are
   overwhelmingly denied.
6. **Base rates.** The committed statpack's modern discretionary-cert slice
   puts the overall grant rate near 3%, but the 0-relist bucket — this case's
   bucket — grants at 0.8%, petitions with no originating federal circuit skew
   lower still, and state-court petitions in the statpack's
   originating-court table are dominated by denials. Pro se petitions,
   even paid ones, grant at a small fraction of the paid-docket average. This
   petition sits well below the average member of even the 0-relist bucket
   (family dispute, unpublished decision below, no split, kitchen-sink QP), so
   I set P(grant) at 0.002 — a fifth of the 0-relist base rate — rather than at
   the whole-docket 2.5–3%.
7. **No GVR hook.** No pending merits case suggests a hold: Rahimi is already
   decided and cuts *against* the petitioner, and nothing in the QP tracks a
   granted case this Term. A GVR is therefore not the likeliest grant-side
   outcome either; the residual probability mass is nearly all plain denial,
   with dismissal (procedural default) the distant second.

## Inputs used

- Snapshot `record/snapshots/2026-07-17.json` (docket 25-1249, proceedings
  through the June 17, 2026 distribution).
- `record/documents/questions-presented.txt` and `record/documents/petition.txt`
  (52 pp., full text) — the QP, related-proceedings list, table of authorities,
  and statement summarized above.
- `record/documents/brief-in-opposition.txt` was provisioned but is
  content-unavailable (`empty_text: true` in `documents.json` — a 12-page
  scanned filing with no text layer). I did not infer anything from the blank
  file; its existence and date come from `documents.json` and the snapshot. Its
  content could only have moved this prediction toward denial, so the gap is
  immaterial to the call (flagged in `flags.json`).
- Committed base rates in `metrics/statpack.md`; corpus priors and a
  CourtListener docket search per `retrieval.md`. This is a forward-mode cell —
  the conference date (Sept. 28, 2026) postdates today, so the petition is
  genuinely pending and no outcome exists to leak.

## Big-case score

0.05. The abstract subject matter (civil protection orders, § 922(g)(8), VAWA)
touches nationally salient debates, but as a vehicle this is a two-party
domestic dispute whose denial — the near-certain outcome — will be noticed by
no one beyond the parties, and even a hypothetical merits decision would arrive
through a record too idiosyncratic to carry broad doctrine.
