# Rodriguez-Montes v. Texas, No. 25-7286 — cert petition disposition

**Prediction: denied. P(granted) = 0.002.**

## The case

Fabian Aldair Rodriguez-Montes, a Texas state prisoner proceeding pro se and in
forma pauperis, petitions for certiorari from the Court of Appeals of Texas,
Twelfth District (No. 12-24-00161-CR, decided April 23, 2025, unpublished). The
Texas Court of Criminal Appeals refused discretionary review on August 20, 2025
and denied rehearing on October 9, 2025. He was convicted after a warrantless
motel-parking-lot detention and frisk in Cleburne, Texas that produced a firearm
and a meth pipe, and was sentenced to sixty-five years on two counts.

The petition (13 pages, handwritten on the Court's pro se form) presents four
questions: (1) whether an anonymous tip plus ambiguous non-criminal conduct
supports a Terry stop, citing *Florida v. J.L.*; (2) whether the frisk exceeded
*Terry*/*Ybarra*/*Dickerson* limits absent individualized armed-and-dangerous
suspicion; (3) whether due process requires a jury instruction (Texas's Art.
38.23 vehicle) when suppression facts are disputed; and (4) whether appellate
courts may credit officer testimony over body-camera video, invoking *Scott v.
Harris*.

## Why denial is near-certain

**Base rate.** This is a paid-no, IFP-yes prisoner petition (docket type `IFP`,
Term 2025). Modern discretionary cert is granted at a few percent overall, and
IFP prisoner petitions run far below that — on the order of one in a thousand or
worse per Term. The committed statpack's SCOTUS cut (denied 4.4%, granted 1.4%
of resolved) blends historical merits-era labels and overstates the modern IFP
grant rate; the prompt's own guidance puts the modern discretionary grant rate
at a few percent, and this petition sits in the weakest stratum of that pool.

**Rule 10 posture.** Every question is fact-bound error correction: the petition
argues the Texas courts *misapplied* settled standards (*Terry*, *J.L.*,
*Dickerson*, *Scott v. Harris*) to this record, not that courts are divided on
what the standards are. No circuit or state-court split is alleged. The Court
does not sit to review whether one anonymous tip was sufficiently corroborated
or whether one body-cam video contradicts one officer's testimony.

**Vehicle problems.** The decision below is an unpublished intermediate-court
opinion; the TCCA refused review without a reasoned decision. Question 3 is
entangled with a state-law procedural rule (Art. 38.23's statutory suppression
instruction), and the federal due-process framing (via *Jackson v. Virginia*,
which governs evidentiary sufficiency, not suppression instructions) is
doctrinally shaky. The video-versus-testimony question (the only one with any
general interest, as a possible *Scott v. Harris* extension) arrives on disputed
facts — the worst posture for it.

**Docket signals.** The State's response was due June 1, 2026; the snapshot
shows no brief in opposition and no waiver entry, and the petition was
distributed June 18 for the September 28, 2026 conference — the "long
conference," where the summer's accumulated IFP petitions are denied en masse.
The Court essentially never grants without first calling for a response; a
petition going to the long conference without a CFR is on the standard denial
track. A GVR is implausible: no pending merits case obviously implicates these
questions.

**Timing.** Expect an order denying the petition on the orders list following
the September 28, 2026 conference (early October 2026).

The residual 0.2% covers the small chance of a relist, a call for a response
that revives the petition, or a summary disposition — none of which the current
record signals.

## Inputs and caveats

Anchored on the provisioned snapshot (`record/snapshots/2026-07-10.json`) and
the provisioned petition text (`record/documents/petition.txt`; the QP section
is included in it — no separate `questions-presented.txt` or
`brief-in-opposition.txt` was provisioned, consistent with no BIO on the
docket). Mode is `forward` (pending case). The CourtListener MCP server was
down for this cell (every call returned a server-side session-store error), so
no live retrieval supplemented the record; `fedcourts query` returned no
matching priors (the resolved SCOTUS slice of the corpus is small). Neither gap
materially affects the call — the prediction is driven by the petition itself
and the well-known cert base rates. See `retrieval.md` and `flags.json`.
