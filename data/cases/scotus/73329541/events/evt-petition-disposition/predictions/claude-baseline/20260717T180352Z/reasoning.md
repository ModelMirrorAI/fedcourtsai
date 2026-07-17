# St. Clair v. Quick, No. 25-1274 — petition disposition

**Prediction: denied. P(grant, GVR included) = 0.025.**

## The case

Michael St. Clair, serving Oklahoma life-without-parole sentences for two 1990s
murder convictions, filed a 28 U.S.C. § 2241 habeas petition in the Eastern
District of Oklahoma challenging not his convictions but his 2018 transfer from
Kentucky back to Oklahoma custody, which he says violated a 1995 Executive
Agreement between the two states' governors (the agreement required his return
to Oklahoma unless Kentucky imposed a death sentence; Kentucky's prosecution
ultimately ended in a negotiated term-of-years settlement in 2019). The
district court dismissed the petition as untimely under § 2244(d)(1)'s one-year
limitations period and denied a certificate of appealability; the Tenth Circuit
denied a COA by unpublished order (Oct. 17, 2025), and rehearing and rehearing
en banc were denied Feb. 6, 2026.

## The question presented

Whether § 2244(d)(1)'s limitations period applies to § 2241 petitions. The
petition invokes an acknowledged circuit split — the Second, Fourth, Fifth,
Ninth, and Tenth Circuits apply § 2244(d) to (at least some) § 2241 petitions
(*Burger v. Scott*, *Dulworth v. Evans*, *Shelby*, *Cook*, *Wade*,
*Kimbrell*); the Seventh Circuit holds it applies only to petitions contesting
a state-court judgment (*Cox v. McBride*) — and argues that *Bowe v. United
States*, No. 24-5438 (U.S. Jan. 9, 2026), which read § 2244's certiorari-bar
provision not to reach § 2255 proceedings on statutory-construction grounds,
undermines the majority rule. In the alternative it asks for a GVR in light of
*Bowe*. I verified via CourtListener that *Bowe* was decided January 9, 2026
(majority by Justice Sotomayor), consistent with the petition's account.

## Signals for a grant

- The split is real and was expressly acknowledged by the Tenth Circuit in
  *Dulworth*. Splits on AEDPA threshold procedure do get granted (*Banister*,
  *Jones v. Hendrix*, *Bowe* itself).
- *Bowe* is a fresh, on-theme hook: a January 2026 decision refusing to import
  a § 2244 provision into a neighboring habeas vehicle absent clear text.
- Paid (not IFP) and counseled petition; paid petitions granted at ~5.4% in
  Term 2025 (statpack fee-class detail), versus ~1.1% for IFP.

## Signals against a grant

1. **The split is old and lopsided.** The cited decisions run 2002–2006; the
   split is 5–1 and has sat unresolved for two decades. Countless petitions
   have presented it; the Court has passed every time. Nothing about this case
   makes the split newly ripe.
2. **Poor vehicle, several ways.**
   - It arises on the *denial of a certificate of appealability* by
     unpublished order — a posture the Court almost never takes up.
   - There is an antecedent question whether a state prisoner "in custody
     pursuant to the judgment of a State court" can proceed under § 2241 at
     all rather than § 2254 — many circuits recharacterize such petitions —
     so the QP may not even be reached.
   - The *Bowe* analogy is textually weak here: § 2244(d)(1) by its terms
     applies to "an application for a writ of habeas corpus by a person in
     custody pursuant to the judgment of a State court," which describes St.
     Clair (LWOP under Oklahoma judgments) regardless of the § 2241 label.
     *Bowe* turned on § 2244(b)(3)(E)'s cross-reference to § 2254
     applications, which federal-prisoner § 2255 motions are not. A
     text-focused Court could think the Tenth Circuit's result correct on
     these facts even if the Seventh Circuit is right about non-judgment
     custody challenges.
   - The underlying merits (immediate release because the Executive Agreement
     allegedly bars Oklahoma custody once Kentucky's prosecution ended without
     a death sentence) are idiosyncratic and weak — a grant would resolve the
     limitations question in a case where relief downstream is very unlikely.
3. **GVR is unlikely.** The Tenth Circuit denied panel and en banc rehearing
   on February 6, 2026 — *after* *Bowe* came down — so the lower court's last
   action postdates the intervening decision, which cuts against the standard
   GVR pattern.
4. **Docket posture is unremarkable.** Filed May 6, 2026; docketed May 12;
   distributed June 24 for the September 28, 2026 long conference. No brief in
   opposition appears on the snapshot (distribution this early implies the
   State likely waived), no call for a response yet, no amici, no relists (it
   has not yet been conferenced), no CVSG. Long-conference petitions are
   denied at above-average rates.

## Calibration

Anchors from the committed statpack (live/historical slice): modern
discretionary-cert grant rate ~2.5–3.3% per Term overall; paid-petition rate
~5.4% (Term 2025); CA10-originating petitions ~5.0%; relist-0 resolved bucket
0.8% (not directly applicable pre-conference); no CVSG here. The
salience-band table the prompt describes is not present in the committed
statpack, so I anchored on the paid fee-class rate as the closest segment.

Starting from the ~5% paid baseline, the vehicle defects (COA-denial posture,
antecedent § 2241/§ 2254 problem, textually distinguishable *Bowe* hook, weak
underlying claim), the aged lopsided split, the absence of amici, and the
long-conference distribution all point below baseline. A modest residual
covers the scenario where the *Bowe* hook catches a justice's eye and produces
a relist-then-grant or a GVR.

**P(grant incl. GVR) = 0.025; predicted disposition: denied.** Within the
grant residual I'd apportion roughly 60/40 plenary grant vs. GVR, so `denied`
is by far the modal outcome and `granted=0`.

## Big-case score

0.15 — if granted, resolving § 2244(d)'s reach over § 2241 petitions would
matter to habeas practitioners and prisoners challenging administrative or
custody decisions, but it is a technical procedural question; the case itself
(one prisoner's interstate custody-transfer dispute) has no broader
newsworthiness.

## Degradations

The corpus query sidecar (`fedcourts query` via the local service) was
unreachable, so I could not pull ranked similar priors; I relied on the
committed `metrics/statpack.md` / `statpack.json` for base rates instead. The
CourtListener MCP server worked normally. Details in `retrieval.md`.
