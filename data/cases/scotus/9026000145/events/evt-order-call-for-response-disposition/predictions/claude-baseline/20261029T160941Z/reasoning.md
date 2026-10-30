# Reasoning — P(grant) 0.47

**Inputs read.** Snapshot `record/snapshots/2026-10-06.json` (forward mode, date cut
at 2026-10-06), `context.json` (band `baseline` under sal-v4, distribution_count 1,
no CVSG), `documents/questions-presented.txt` and `documents/petition.txt` (truncated
at the cap; the body and the opinion below were within it). No brief in opposition
exists — the Court has just requested one.

**What decides it.** The petition (filed by the Solicitor General for the warden of a
federal immigration-detention facility) asks only that it be held for *Montoya Palacios
v. Liggins*, No. 25-1223. A corpus `--docket-number` lookup confirms that case: granted
2026-06-29, from CA4, petitioner the detainee, SG as respondent, and the respondents'
counsel here (Tutt, for Michelin) filed as amicus there. So P(grant) here ≈ P(the
government wins *Montoya Palacios*) — a win produces a GVR of the Third Circuit's
contrary judgment, which counts as a grant — plus a small allowance for a mixed or
narrow ruling that still prompts a GVR.

**Estimate of the companion's outcome.** For the government: the sovereign-immunity
clear-statement rule (*Lane v. Peña*, *Ardestani v. INS* construing EAJA narrowly), a
recognized split (CA4/CA5 vs CA2/CA9/CA10/CA3), and a four-plus-one-judge dissent from
rehearing en banc below. Against: the Court granted the *detainee's* petition, and
its reversal rate on granted cases is roughly two-thirds; "any civil action" is broad
text, and in *Kirtz* (2024) the Court found a waiver in plain statutory text without a
special clear statement. I put a government win at ~0.45, and add ~0.02 for a
narrow/mixed decision still yielding a GVR: **0.47**.

**Why not the band rate.** The frozen band is `baseline` (reached ~4–6% across prior
Terms), apparently because the caption names a warden with no federal marker. The
petitioner is in substance federal (federal class reached rates ~50–90%), but neither
describes a hold petition whose fate is tied to a granted lead case. I deviate sharply
from the baseline anchor deliberately; this is where a reader should judge me.

**Claims.** relist-increment 0.97 (masked on this moment; a held petition is
redistributed many times). cvsg-increment 0.003 (the SG is the petitioner).
summary-disposition-route 0.93 given a grant (GVR is the overwhelmingly likely grant
route; small residual for plenary grant or a different outcome). dissent-from-denial
0.04 given denial (denials of held petitions rarely draw writings). Order-writers kept
small and consistent with that.

**Uncertainties.** The merits of *Montoya Palacios* are genuinely close and I have not
read its briefs; the Court could also decide it on a ground (e.g. limited to §2241
detention challenges vs. all habeas) that leaves the GVR call debatable. The
respondents could also concede/settle (fees here are ~$16k and ~$18k), leading to a
withdrawal or dismissal — small.

**Retrieval.** Four corpus query attempts, two successful (see `retrieval.md`); no CourtListener MCP or web
calls. Nothing found reported a disposition of this petition.
