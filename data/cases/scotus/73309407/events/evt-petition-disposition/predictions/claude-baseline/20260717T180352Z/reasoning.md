# Patterson v. Michigan, No. 25-1263 — cert prediction

**Prediction: denied. P(grant, GVR included) ≈ 0.002.**

## The case

Ricky Darnell Patterson faces a pending Michigan prosecution under MCL
257.625(5)(a) (operating while intoxicated causing serious impairment) arising
from a September 2024 motorcycle-car collision in Jackson, Michigan. His blood
draw showed 4.6 ng/ml active Delta-9 THC; the responding state trooper
testified at the preliminary exam that Patterson passed all field sobriety
tests. The trial court nonetheless bound the case over, finding probable cause
of marijuana impairment. The Michigan Court of Appeals denied interlocutory
leave "for lack of merit in the grounds presented" (Sept. 8, 2025), and the
Michigan Supreme Court denied leave (Nov. 21, 2025). The petition (paid,
counseled by the Jackson County Public Defender) was docketed May 7, 2026;
respondent's brief was due June 8, 2026; the docket shows no response and the
case was distributed for the September 28, 2026 long conference.

## Questions presented

As framed in the petition: (I) "On the night in question did Petitioner have
actual notice of what is an acceptable level of THC he could have in his
bloodstream when he was operating his motor vehicle?" and (II) "Is the case at
hand capable of repetition yet evading judicial review?"

## Why this petition is a near-certain denial

1. **Interlocutory, likely jurisdictionally defective posture.** There is no
   final judgment: the prosecution is still pretrial. 28 U.S.C. § 1257(a)
   grants review only of final judgments of the highest state court, and the
   petition makes no argument for a *Cox Broadcasting* finality exception. A
   state high court's discretionary denial of interlocutory leave is about the
   weakest possible vehicle. If convicted, Patterson can raise everything on
   direct appeal — the "capable of repetition, yet evading review" framing (QP
   II) is a mootness doctrine that has no application to a live prosecution
   headed for trial.

2. **Fact-bound framing.** QP I is expressly tied to "the night in question" —
   a case-specific factual question about one defendant's notice, not a
   recurring legal question. The Court denies fact-bound QPs as a matter of
   course; petitions framed this way rarely even reach a conference discussion
   list.

3. **No split alleged.** The petition cites no conflict among state high
   courts or federal circuits on any legal rule. Its core complaint — that no
   national per se THC-impairment threshold exists — is a legislative/policy
   gap, and the petition candidly asks the Court to *adopt a mathematical
   formula* (>8.2 ng/ml ≈ 0.05% BAC, from one 2019 simulator study) as a
   national standard. Setting scientific per se thresholds for state DUI law
   is quintessentially a legislative task; the Court does not grant cert to do
   it, and vagueness/notice challenges to state statutes of this kind come up
   through final judgments.

4. **State-law heart.** Whether MCL 257.625's "under the influence" element
   requires proof of actual impairment, and whether the MRTMA (MCL 333.27954)
   displaces it, are questions of Michigan statutory interpretation on which
   the state courts have the last word. The federal hook (due-process notice
   under *Cramp*) is thin and undeveloped.

5. **Docket signals.** Paid case, but: no amici, no response filed by
   Michigan, distribution to the long conference, zero relists. Petitions
   distributed without a requested response are denied at an extremely high
   rate. Nothing in this record suggests the Court will call for a response.

## Base-rate anchoring

From the committed `metrics/statpack.md` (modern discretionary-cert slice,
denial-reweighted): recent Terms' overall grant rate runs ~2.5–3.3%; petitions
with **zero relists** grant at ~0.8% (denied 97.3%); no CVSG here (CVSG cases
grant at 27%, none-CVSG at 3.0%). State-court petitions in the selected slice
skew heavily to denial (the Michigan appellate bucket in the
originating-court table is 100% denied on its small sample). This petition
sits well below the average petition in that already-low-grant population on
every quality dimension (posture, split, QP framing), so I adjust down from
the 0.8% zero-relist anchor to **0.2%**. The residual probability mostly
covers tail scenarios (an unexpected CFR followed by relists); no plausible
GVR source exists, so `predicted_disposition` is a flat `denied`.

## Inputs used

Provisioned snapshot (`record/snapshots/2026-07-17.json`), the provisioned
`questions-presented.txt` and full `petition.txt` (32 pp., read in full), the
event definition, and the committed statpack. One CourtListener MCP lookup
confirmed the docket is still pending (no `date_terminated`) — the forward
cell is correctly provisioned. The corpus query sidecar was unreachable
(`fedcourts query` timed out), so no corpus priors were retrieved; the
committed statpack supplied the base rates instead. This degraded the cell
only marginally — the statpack anchors were sufficient for a petition this
far from the grant zone.
