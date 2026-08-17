# Rationale for the numbers — claude-baseline, 20260816T173750Z

## The anchor

P(disturbed) = 0.65, against the committed statpack's merits baseline. The
"merits docket (granted cases)" section publishes an `excluded` count (67), so
its rate is quotable and is the bar this cell's skill is scored against. My
case's grant date is 2026-06-29 (from `event.yaml`'s `opened_at`), i.e. grant
Term 2025, so the pool is grant Terms 2015–2024; the pack holds parsed rows
for 2017–2024 of that window (Terms with no parsed judgment are omitted, and
the merits table renders every Term the pack holds). Pooled:
359 disturbed / 515 parsed = **69.7%**, comfortably over the 30-parsed floor.
Coverage beside that figure: the pooled Terms' `parsed` runs close to their
`granted` (e.g. 73/75 in 2024, 52/58 in 2017), so pendency censoring in the
pool is modest.

## Adjustments

Down ~5 points from the 69.7% baseline, on two considerations:

1. **The grant was not selected for error-correction.** The government
   acquiesced in certiorari — the Solicitor General's brief in opposition
   affirmatively asked the Court to grant — while defending the judgment on
   the merits. The government lost this question in the Third and Tenth
   Circuits and was denied rehearing en banc in both (Michelin, Daley, spring
   2026), so this Court is its only route to fixing the three-circuit
   majority against it; it steered review to a vehicle where it had *won*
   below. A grant made to resolve a split both sides call intractable carries
   less of the usual selection-for-reversal signal than the baseline
   population embodies, and an affirmance here would give the government the
   nationwide rule it wants.
2. **The government's merits path is real, not makeweight.** FAA v. Cooper's
   sovereign-immunity strict-construction canon plus Schlanger v. Seamans
   (declining to read "civil action" in § 1391(e) to reach habeas, reaffirmed
   in Stafford v. Briggs) is a precedent-grounded route to affirmance, and
   the Fourth/Fifth Circuit position has attracted recent, prominent
   circuit-judge support (the Bove and Mascott dissents from the Third
   Circuit's en banc denial).

Held above 50–55% (i.e., only ~5 points below baseline) on three:

1. **The textual case for petitioner is strong.** "Any civil action" with a
   single express carve-out for tort; the Court has called habeas civil since
   Ex parte Tom Tong (1883) and Kurtz v. Moffitt (1885), recently restated in
   Banister v. Davis; and immigration detention is itself civil detention
   (Zadvydas). Cooper's canon operates only on ambiguity, and this Court's
   textualists (Barrett and Kavanaugh especially) are on record disfavoring
   canons that manufacture ambiguity against otherwise-clear text.
2. **The circuit alignment is 3–2 for petitioner** (2d, 3d, 10th vs. 4th,
   5th), with the immigration-specific narrowing giving the Court an easy
   limited ground.
3. **The Court's EAJA precedents lean claimant-friendly** (Scarborough 7–2,
   Richlin unanimous).

## Votes

7–2 reversed (Thomas, Alito dissenting) is my modal lineup; each vote is my
per-Justice best guess, not a joint draw. The genuinely uncertain votes are
Roberts, Kavanaugh, and Barrett; I put each slightly on the majority side for
the reasons in `predicted_reasoning.md`. The vote block is banked, not scored
today, and I have written it as if it graded.

## What I read, and what degraded

The provisioned inputs were unusually complete: full petition text (47 pp.),
the SG's brief for respondents (12 pp., acquiescing), the QP section, and a
current snapshot (2026-08-16) showing the full cert-stage docket — two
distributions, grant on June 29, 2026, merits-briefing extension to
August 31 / October 23, 2026. I worked from the docket skeleton plus the
cert-stage filings; no merits briefs exist yet, so there was no merits
advocacy to retrieve. This is a `forward` cell — the judgment does not exist.

Two retrieval degradations, neither blocking: a `fedcourts query` for
EAJA-related priors by citation returned empty (the citation column is
sparse — the tool's own note says missing data, not no match), and the
CourtListener MCP server returned HTTP 429 (daily rate limit exhausted) on my
first search, so I made no live CourtListener lookups; the prediction rests
on the provisioned inputs and the committed statpack, per the degrade-
gracefully rule.

`record/context.json` carries `band: "elevated"` — a cert construct on this
cert docket, settled by the grant. Per the merits-stage rule I did not anchor
on it; no flag is owed for its presence.

## Where to discount me

The 0.65 sits close to the base rate because the case-specific signals
genuinely pull both ways. If you believe respondent-acquiesced grants reverse
at materially lower rates than the granted population at large (I applied
only a modest haircut for it — I have no committed cut quantifying that
posture), shade down; if you weight the Court's textualist center harder,
shade up toward 0.70–0.75. The semantic claims assume a
narrow immigration-specific ground; a maximalist "all habeas is civil"
holding would disturb the judgment identically but grade my breadth claim
poorly.
