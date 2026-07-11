# Mizrahi v. United States, No. 25-1238 — cert-petition disposition

**Prediction: denied, P(granted) = 0.15.** A live (`forward`-mode) petition,
distributed but undecided as of the 2026-07-10 snapshot; the government's
requested response is due July 15, 2026, so the disposition will likely come at
the September long conference or an early OT2026 conference.

## The legal question

The petition asks one clean question: whether *Libretti v. United States*, 516
U.S. 29 (1995) — which said "the right to a jury verdict on forfeitability does
not fall within the Sixth Amendment's constitutional protection" — should be
overruled. Petitioner was convicted of money laundering (18 U.S.C. § 1956) on a
general verdict that did not specify which of three predicate theories (bank
fraud, wire fraud, or narcotics proceeds) the jury found; the district court
then found by a preponderance that $3.85M was narcotics proceeds and ordered
$4.5M in criminal forfeiture under § 982(a)(1), over a preserved
Fifth/Sixth-Amendment objection. The Second Circuit affirmed in an unpublished
summary order (Nov. 7, 2025; rehearing denied Jan. 30, 2026), bound by its own
precedent (*Fruchter*) that only the Supreme Court can overrule *Libretti*.

## The governing standard

Cert is discretionary and the base rate is very low (a few percent for paid
petitions). The Rule 10 drivers here are not a circuit split — the circuits
uniformly follow *Libretti* — but (a) the importance of a recurring federal
constitutional question (DOJ obtained ~$2.5B in criminal forfeitures across
~8,300 completed cases in FY2024, per the petition), and (b) the argument that
*Libretti* is irreconcilable with the *Apprendi* line, which only the Court
itself can resolve.

## Signals from the snapshot pointing toward grant

1. **Call for response after waiver.** The SG waived on May 21; the case was
   distributed June 2 for the June 18 conference; on June 15 the Court
   **requested a response** (due July 15). A CFR means at least one chambers
   wants the government's views — petitions that draw a CFR are granted at a
   far higher rate than the baseline, though still well under half.
2. **Two coordinated cert-stage amicus briefs** — Washington Legal Foundation
   joined by the Due Process Institute, NACDL, and NAPD (Milbank), and a brief
   of Former Federal Judges (Arnold & Porter). Cert-stage amici correlate with
   grants and signal an organized campaign to tee this question up.
3. **Doctrinal momentum.** *Erlinger* (2024) celebrated that the Court "ha[s]
   now overruled several decisions inconsistent" with *Apprendi*; *Southern
   Union* (2012) already applies *Apprendi* to criminal fines, and forfeitures
   are "fines" for constitutional purposes (*Bajakajian*). Most recently,
   *Ellingburg v. United States* (Jan. 20, 2026, 9-0) held MVRA restitution is
   criminal punishment for Ex Post Facto purposes, with a Thomas concurrence
   joined by Gorsuch — the incremental fines → restitution → forfeiture path
   the petition invites is visibly underway.
4. **Public Justice-level interest.** Gorsuch (joined by Sotomayor) dissented
   from denial in *Hester* (2019) on the twin restitution question; Gorsuch
   dissented from denial again in *Rimlawi* (2025) and *Burnett* (2026). Every
   case *Libretti* cited for its Sixth Amendment remark (*McMillan*, *Cabana*,
   *Spaziano*) has since been overruled or repudiated.
5. **A preserved, outcome-dispositive objection** and experienced Supreme
   Court counsel (Winston & Strawn on the petition; Steptoe as counsel of
   record on the docket).

## Signals pointing toward denial

1. **The Court has denied this exact question at least seven times** —
   *Tedder* (2005), *Braun* (2005), *Dantone* (2006, 2015), *Leahy* (2006),
   *Stevenson* (2017), *Esformes* (2023) — all post-*Apprendi*, several
   post-*Southern Union*, and *Esformes* recently. The petition itself
   catalogues these. The Court also denied *Rimlawi* (2025) and *Burnett*
   (2026) in the adjacent Apprendi space this and last Term.
2. **No split and no percolation pressure**: every circuit to decide the issue
   follows *Libretti*, so there is no disuniformity to resolve — only an
   invitation to overrule, which the Court grants sparingly and usually only
   after noted dissents accumulate. The publicly signaled votes (Gorsuch,
   Sotomayor, plausibly Thomas) still fall short of the four needed.
3. **Vehicle wrinkles.** The judgment below is an unpublished summary order;
   the duplicitous counts and general verdict give the government harmless
   error and alternative-ground arguments (the jury did convict on the bank
   fraud counts underlying $690K of the forfeiture); and the sympathetic-facts
   narrative (severe ASD, comparative sentencing disparity with the
   cooperator) is orthogonal to the QP.
4. **Base rate.** Even CFR'd, amicus-supported paid petitions are more often
   denied than granted. The corpus statpack confirms grants are rare (SCOTUS
   resolved base rate: granted ~1.4%; modern discretionary cert grants run a
   few percent), though the resolved SCOTUS sample in the corpus is small
   (296) and largely historical.

## Weighing

The CFR after waiver is the strongest single signal — it separates this
petition from its seven denied predecessors, none of which (so far as the
record shows) arrived with this combination of a fresh 9-0 "monetary sanctions
are criminal punishment" precedent, organized amicus support, and an explicit
*Erlinger* roadmap for overruling pre-*Apprendi* outliers. I start from a
CFR-conditional grant rate around 8–12%, adjust upward for the amici, the
momentum, and the clean preserved objection, and back down for the repeated
prior denials, the absence of any split, and the vehicle wrinkles. That lands
at **P(granted) ≈ 0.15**. The single most likely disposition remains **denied**
— quite possibly with a dissent from, or statement respecting, denial by
Gorsuch and Sotomayor, which is how the last several of these have ended.

## Predicted votes

Cert votes are mostly unobservable; the `votes` array encodes the modal
denial scenario — Gorsuch and Sotomayor publicly noting they would grant
(as in *Hester*), Thomas plausibly joining after his *Ellingburg*
concurrence, and no fourth vote. If the SG's response (due July 15)
concedes the question's importance or the Court relists repeatedly after
the response arrives, the grant probability would rise materially.

## Inputs and caveats

Anchored on the provisioned questions-presented and petition text and the
2026-07-10 docket snapshot (no brief in opposition existed yet — the response
is due July 15). The CourtListener MCP server was unavailable in this cell
(server-side `REDIS_URL` configuration error on every call), so retrieval fell
back to the committed statpack, `fedcourts query` (zero matching priors
returned), and two engine web searches — see `retrieval.md` and `flags.json`.
The outcome of this petition does not yet exist; nothing outcome-revealing was
(or could be) retrieved.
