# Reasoning — scotus/9026000293 (No. 26-293, Ashton v. The Taliban), CVSG moment

**P(any grant) = 0.37; label `denied`.**

## What I read
- Snapshot `2026-11-16.json`: paid petition from the Second Circuit (No. 23-444), filed 31 Aug 2026; one amicus brief (Afghanistan's UN chargé d'affaires, VIDED); distributed for the 6 Nov and 13 Nov conferences; on 16 Nov the Court invited the Solicitor General's views, Justice Kagan taking no part. No respondent has appeared and no brief in opposition is on the docket, so there is no opposition text to weigh.
- `questions-presented.txt` and `petition.txt` (truncated at the cap; I read the body, not the appendix). The petition asks for one thing only: a GVR of the Second Circuit's FSIA holding in light of *Exxon Mobil v. Corporación CIMEX* (decided 23 June 2026, after rehearing was denied below). It expressly joins the plenary arguments of the Havlish petition (No. 26-292) on the TRIA "blocking date" rule and asks to be consolidated if any petition from the judgment is granted.
- `record/related/`: 26-292 (Havlish, relation `Vide`) and 26-294 (Owens, relation `vided-amicus`, one shared brief). I read both dockets; both are from the same judgment and both drew a CVSG the same day, so I treat all three as one package. Havlish has an amicus brief from Iowa and 30 other States and a supplemental brief.
- `lower-court-docket.txt` says no en banc petition was found and no opinion was on CourtListener. The petition says rehearing en banc was denied over dissents by Judges Sullivan (joined by three) and Menashi. I rely on the petition's account; I did not have the decision below itself, and my description of its holdings is the petitioners' characterisation.
- `same-question.json`: empty list, nothing to rest on.

## Anchor
- `context.json`: band `high` (sal-v8), `cert_anchor.rate` 0.350; `cert_amicus_line` 0.352 (arm `some`, 543 resolved).
- Statpack CVSG cut (paid scored segment): 166 resolved, granted 29.5% + gvr 6.0% = 35.5% grant family. All three figures agree at about 0.35.

## Adjustments
Up:
- Reported en banc dissents from five judges, a divided panel, an asserted conflict with the First/Third Circuits (FSIA) and Ninth/Eleventh (TRIA timing), 31 States as amici on the lead petition, and very large stakes. That is a stronger package than the median CVSG petition.
- A grant-family outcome for this docket has several routes: consolidated grant with Havlish; a hold followed by a GVR if the Court disturbs the judgment in Havlish; or a direct GVR in light of *Cimex*.

Down:
- This petition is derivative. Its own ask is a GVR, and the *Cimex* link is the petitioners' reading: by their own description *Cimex* is about whether the Helms-Burton Act displaces FSIA exceptions, not about who is a "foreign state". A court that sees a loose fit will not GVR on it.
- The United States has institutional interests against the petitioners (the recognition power, control of blocked assets), so the invited brief may well recommend denial, and the Court follows the SG's recommendation most of the time. I do not know what the SG will say and did not assume it.
- If Havlish is granted and the judgment affirmed, this petition ends in a denial.

Rough decomposition: P(plenary grant on the lead petition) about 0.38; given that, about 0.35 this docket is granted alongside it and 0.65 it is held, with about 0.68 of held cases ending in a GVR; plus about 0.07 for a GVR of the package in light of *Cimex* without plenary review. That gives about 0.37.

## Other claims
- `relist-increment` 0.97: after the SG files, the petition is distributed again as a matter of course; the only miss is a withdrawal or dismissal first.
- `cvsg-increment` 0.02: a CVSG is already on the docket; the claim is vacuous here.
- `summary-disposition-route` 0.62 (conditional on a grant): most of the grant mass for this docket is a GVR, either direct or after a hold.
- `dissent-from-denial` 0.12 (conditional on denial): the subject and the en banc dissents make a noted dissent or statement more likely than usual, but still uncommon.
- `order-writers`: small numbers, highest for Thomas, Alito and Gorsuch; Kagan near zero because she is recused.

## Where to discount me
- No decision-below text and no opposition; the petition is my only account of the holdings.
- I know little about *Cimex* beyond the petition's description (it postdates most of what I know).
- The outcome depends heavily on an SG brief that does not exist yet, and resolution may be far off if the petition is held.
- Corpus queries returned only generic rows and did not move the number. I made no CourtListener MCP or web calls.
