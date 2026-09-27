# Why P(grant) = 0.006

## Inputs read

- `record/snapshots/2026-09-18.json`: one docket entry, "Petition for a writ of
  certiorari filed. (Response due October 19, 2026)"; paid case type; docketed
  September 17, 2026; lower court CA9 No. 24-5020, decided March 20, 2026,
  rehearing denied June 30, 2026. Petitioner is John Torsten Loop, listed as his own
  attorney (pro se); respondents "Washington, et al."
- `record/context.json`: `mode: forward`, `band: baseline`, `salience_version:
  sal-v4`, `distribution_count: 0`, `cvsg_date: null`, `term: 2026`,
  `signals_observable: true`, `cut_kind: date`, cutoff 2026-09-18.
- `record/documents/`: `petition.txt` (39 pages, text extracted, not truncated) and
  `questions-presented.txt`. No brief in opposition exists yet. I read the whole
  petition body; the appendix (the CA9 memorandum) was not in the extracted text, so
  my knowledge of the decision below comes from the petition's own description of
  it.
- `metrics/statpack.md`: the sal-v4 "Segment base rate by salience band" Term
  table, the relist / CVSG / circuit cuts, and the per-Term table.

## Anchor

The context's band is `baseline` under `sal-v4`, which matches the statpack table's
version, so the table is a valid anchor. This is an arrival cell, so the anchor is
the caption class's floor: the petitioner is a private individual, so `baseline`'s
bracketed `reached` rate. Pooling every prior Term the table renders (OT2017 through
OT2025, strictly before this case's OT2026) by weighted n gives 637.4 / 12,720 =
**5.0%**. That is the whole private-class arrival population's grant-family rate and
is the yardstick the evaluator scores against. I did not use the relist-count cut's
relist-0 figure (1.2% granted), which the prompt warns understates an arrival.

## Adjustments from the anchor

Every case-specific signal points down, and several point down hard.

1. **Pro se petitioner.** The 5.0% pool is dominated by counseled paid petitions.
   Pro se paid petitions are granted at a small fraction of that rate; plenary
   grants of pro se petitions are a handful per decade. This is the single largest
   adjustment.
2. **Unpublished, non-precedential decision below.** The CA9 disposed of the appeal
   by memorandum. The Court treats an unpublished affirmance of a jurisdictional
   dismissal as a poor vehicle, and it creates no circuit-level law to correct.
3. **No circuit split alleged.** The petition claims conflict with *Exxon Mobil*,
   *Lance*, and *Skinner*, and cites CA9 and CA3 cases as *agreeing* with the
   petitioner's reading. That is an error-correction argument, not a split.
4. **Domestic-relations posture with alternative grounds.** The federal defendants
   are the State of Washington (sovereign immunity), JAMS and a retired-judge
   arbitrator (arbitral/judicial immunity), and the Attorney General. Even if
   Rooker-Feldman were wrongly applied, the complaint faces independent
   jurisdictional and immunity bars, so a grant would likely change nothing.
5. **QP2 was not decided below.** The delegation-to-arbitrator due process question
   is the more interesting one, but the district court dismissed for lack of
   jurisdiction and the CA9 affirmed on that ground, so QP2 is unreviewable here.
6. **T.M. cuts the wrong way for a GVR channel.** I checked the syllabus of *T.M. v.
   University of Maryland Medical System Corp.*, No. 25-197 (decided June 18,
   2026, after the CA9 decision and before this snapshot). It held that
   Rooker-Feldman applies regardless of whether the state judgment remains subject
   to further state review. It did not narrow the doctrine in a way that would
   prompt a GVR of this affirmance, and the Court having just spoken on
   Rooker-Feldman lowers the odds it takes a second, fact-bound case the same year.
   This is pre-snapshot public information used as ordinary forward signal, not
   leakage.

Nothing pushes up. The petition is competently printed and formally compliant, and
the parental-rights framing is articulate, but the Court does not grant on
framing.

Result: I place P(any grant) at **0.006**, roughly an order of magnitude below the
class anchor. The residual mass is mostly a hold-and-GVR contingency should an
unforeseen Rooker-Feldman or parental-rights case be decided this Term, which is why
`summary-disposition-route` (conditional on grant) sits at 0.6 rather than at the
Term tables' 30 to 59% GVR share of grants.

## Other claims

- `relist-increment` 0.96: from zero distributions, "at least one more" means simply
  "gets distributed at all." Nearly every docketed paid petition is; the residual is
  a Rule 46 withdrawal or a dismissal before distribution.
- `cvsg-increment` 0.003: no federal interest.
- `dissent-from-denial` 0.01: pro se, jurisdiction-dismissed family-law vehicle.

## Uncertainty and where to discount me

- I have not read the CA9 memorandum itself (not in the extracted appendix and not
  on CourtListener), so its reasoning, and whether it rested on any alternative
  ground, is known only through the petition's characterization.
- No BIO exists yet; I assume waiver. A requested response would not change the
  number much.
- The statpack carries no pro se cut, so the size of the largest adjustment rests on
  my general knowledge of the Court's practice rather than on a committed figure.
- Two `fedcourts query` calls were run for priors; both returned rows dominated by
  substantive applications rather than cert petitions when filtered by
  `--disposition`, so they informed nothing beyond confirming the corpus service was
  reachable. Retrieval was otherwise well within budget (5 MCP calls).
