# The decision model

Cert, interim relief, and merits look like three prediction problems. They are
one, with two parameters. This document defines that model and pins the
aggregation rules to sources.

**Much of it is not implemented.** `pipeline/aggregation.py` carries the
thresholds and their citations, and the vocabularies exist — `Stage`, the vote
and writing values, the merits judgment axis, and the provenance block that says
how much of a vote record is there.

What is live is worth naming precisely, because the rest of this document is
not. `Prediction.votes` carries a per-Justice vote forecast, and `vote_accuracy`
scores it against `Outcome.votes` wherever both name the same Justice — on a
declared **merits** moment only, the stage gate below — feeding the
leaderboard's `mean_vote_accuracy`. Event definitions carry a nullable
`stage` — stamped `cert` on a cert docket's petition baseline, `interim` on an
application docket's motion baseline and on SCOTUS entry-pinned
stay/injunction motions, `merits` on the minted merits event, absent
everywhere the writers do not classify one. The merits **cell contract** is
implemented end to end: a cert grant that
opens a merits proceeding mints an open `evt-order-judgment` (kind `order`,
stage `merits`, target the judgment); the granted docket keeps polling toward
its decision; the live channel latches the parsed judgment onto the corpus
row (`pipeline/judgment.py`, the shared parser the offline backfill also
uses), and outcome detection resolves the merits event from those columns —
`Outcome.judgment` carries the result, `actual_disposition` records `other`
(no cert label applies, by the axis-separation rule below), and
`actual_granted` carries the **declared merits binary**, whether the judgment
below was disturbed. A merits *prediction* carries `judgment` plus a mandatory
non-empty vote block (schema-enforced; the `validate` gate holds a
merits-stage event's scored prediction to the judgment), and its
`probability` is P(disturbed), scored by the same Brier formula against the
strictly-prior pooled disturbed rate (*Scoring a merits forecast*, below).
The merits **cell** runs: both prompts carry a merits section, the fan-out
admits the merits event on a row whose grant opened a merits proceeding
(`store.forecastable_events`), and the provisioning guard is keyed on the
event, so the grant order that opened the cell does not refuse it.
What remains unbuilt: no artifact carries a
writing role or a real vote record with provenance (the outcome writer
records no votes, for the reason given below); no schema carries a vote
*margin*; and no aggregation rule is applied to anything. The scoring design
was settled before any merits outcome existed to fit it to, which is the only
order in which the choice is credible. `docs/outcome-decomposition.md` is the
companion — it defines what a scoreable claim is and the rule that scores
one, and its tests govern anything proposed here (the declared `merits-v1`
claim set was chosen against them).

## What is predicted

The **final disposition of a matter before the Court**. Everything else — vote
splits, who writes, what a concurrence splits off — decomposes that disposition
rather than replacing it.

Procedural outcomes (a dismissal as improvidently granted — a DIG — a dismissal
as moot, an affirmance by an equally divided Court) are real and have to be
handled for the methodology to be credible, but they are corner cases rather
than the object. The design records them on their own axis, never blended into
a cert-worthiness score. Mootness practice routes to the `procedural` stratum
(`Outcome.disposition_basis` carries no other value; `metrics/README.md`
governs the stratum); a DIG and an equally divided affirmance are recorded on
the judgment axis and count as **undisturbed** on the merits binary — both
leave the judgment below standing — staying in the scored merits pool because
the pooled baseline's denominator includes them (the `Judgment` docstring
carries the argument).

## The model

For one event with participating set `P` — nine Justices minus recusals:

```
R_j   the latent reasoning of Justice j
V_j = vote(R_j)               a vote; one vocabulary spans every stage
W_j = writing(R_j, V_j, D)    none | majority | plurality | concurrence |
                              concurrence-in-judgment | dissent | statement
D   = A_stage(V_1 … V_|P|)    the disposition
```

Two things vary by stage, and nothing else does:

- **`A_stage`** — how votes aggregate into a disposition.
- **`O_stage`** — what an outside observer gets to see.

That is the whole claim. A cert grant and a merits reversal are the same object
counted differently and observed differently.

| | cert | interim | merits |
| --- | --- | --- | --- |
| `A_stage` | grant iff at least **four** Justices vote to grant | relief iff a **majority**; a Circuit Justice may act alone before referring to the full Court | judgment by a **majority** of participating; the *opinion* may command fewer, which is a plurality |
| `D` observed | always | always | always |
| `V_j` observed | almost never, **and selectively** | partially | fully, with a vote source |
| `W_j` observed | rarely non-`none` — but **absence is observed for every participating Justice** once the order list is final | sometimes | fully |
| `R_j` observed | iff `W_j ≠ none` | iff `W_j ≠ none` | iff `W_j ≠ none` |

The last row is the one that is easiest to lose: reasoning censoring is
**within-stage**, not a property of the stage. Even at merits, a Justice's
reasoning is observed only if that Justice wrote — which is why the writing role
is recorded per Justice rather than inferred from the stage.

## Where the aggregation rules come from

The thresholds are load-bearing for anything derived from a vote forecast, so
they carry citations and live in exactly one place in code
(`pipeline/aggregation.py`). No prompt, docstring, or agent restates them.

**The finding that shapes this whole section: every threshold is Court practice,
not enacted law.** The only statutory number involved is the quorum. That is
worth stating plainly, because a reader will otherwise assume a code section
stands behind numbers this load-bearing.

### Cert: four votes, and the Rules do not say so

Rule 10 is captioned *Considerations Governing Review on Certiorari* and states
only:

> Review on a writ of certiorari is not a matter of right, but of judicial
> discretion. A petition for a writ of certiorari will be granted only for
> compelling reasons.

Searched in full, the [Rules][rules] contain no certiorari vote count anywhere.
The string `vot` does not occur in the document **at all**, and `majority`
occurs exactly once — in Rule 44.1, governing rehearing: "A petition for
rehearing … will not be granted except by a majority of the Court." That is the
only vote-count provision in the Rules, and it is not about certiorari.

This is a negative claim about a document, the one kind a reader cannot
spot-check from the citation, so the provenance is part of it: the 2026 Rules
PDF, all 86 pages extracted to text (187,779 characters) and searched
case-insensitively, on 2026-07-30.

The Federal Judicial Center's [The Supreme Court's Rule of Four][fjc] records the
custom as predating the Judiciary Act of 1925 — it "began in the early
nineteenth century as an informal—perhaps even unstated—practice" — and coming
into public focus during the hearings on that Act, where Justice Van Devanter
testified:

> We always grant the petition when as many as four think that it should be
> granted and sometimes when as many as three think that way.

**That "sometimes three" is history, not a live exception.** The same source
records that the Court "gradually adopted the view that four votes should serve
as a hard minimum to ensure discretionary review, irrespective of the strength
of feeling of those in the minority", and that the standard "has proven
remarkably durable … to the present day". Van Devanter was describing the
practice that view superseded. (The same source records the shift being "softened
to some extent" by "join-three" votes from the early 1970s — which does not
disturb the count, since a join-3 vote *is* a fourth vote to grant, and is decent
corroboration that the votes are correlated.) Treating four as a hard floor is
therefore right for any petition this pipeline predicts; hanging an approximation
on a 2026 forecast from testimony about the pre-1925 Court would be the repo's
own cross-era incomparability caution run backwards.

### Interim relief

Once an application is before the full Court it is decided by majority. A single
Circuit Justice may instead act alone (Sup. Ct. R. 22; 28 U.S.C. § 2101(f)); the
rule in code describes the referred posture only and does not model that.

*Hollingsworth v. Perry*, 558 U.S. 183, 190 (2010) (per curiam), is worth reading
here but is **not** the source of the vote count:

> To obtain a stay pending the filing and disposition of a petition for a writ of
> certiorari, an applicant must show (1) a reasonable probability that four
> Justices will consider the issue sufficiently meritorious to grant certiorari;
> (2) a fair prospect that a majority of the Court will vote to reverse the
> judgment below; and (3) a likelihood that irreparable harm will result from the
> denial of a stay.

That states what an applicant must **show** — a legal standard — not how many
Justices must vote to grant the stay. What makes it interesting for this model is
different and worth keeping separate from the aggregation rule: the standard is
*about* two other forecasts. A stay applicant must establish a probability over a
cert grant and a probability over a merits reversal, so an interim forecast
contains a cert forecast and a merits forecast as components. That nesting is a
property of the standard, not of the counting.

### Merits

A majority of those participating carries the judgment. This is practice too — no
statute states it. 28 U.S.C. § 1 supplies the nine seats and the six-Justice
quorum and nothing more; § 2109 is captioned *Quorum of Supreme Court justices
absent* and borrows the equally-divided phrase by reference rather than enacting
it. The doctrine is judge-made, and splits across two cases: *Durant v. Essex
Co.*, 74 U.S. (7 Wall.) 107 (1868) holds that an equally divided Court affirms
and that the affirmance is the judgment of the entire Court — "the division of
opinion between the judges was the reason for the entry of that judgment; but
the reason is no part of the judgment itself" — while *Neil v. Biggers*, 409
U.S. 188, 192 (1972) is the authority for its carrying no precedential weight.
An equally divided Court reaches a judgment; what it does not reach is a
precedent.

Below six participating there is no quorum and the Court cannot act, so the code
raises rather than returning a threshold: a clamped number would answer an
invalid question confidently, and pre-register that answer.

## Observation, and what it forecloses

Which quantities can ever be scored is a function of **the outcome record
alone** — never of what a predictor attempted, and never of how well it did.

**An individual cert vote is never scored, even when visible.** This is the
sharpest consequence of the model and the one most easily gotten backwards. A
cert vote becomes public only when a Justice **chooses** to note it —
overwhelmingly a dissent from denial. Observation is therefore very nearly a
deterministic function of the value being scored: a noted cert vote is almost
always a vote to grant. Observation is selected on the very outcome being scored,
and the deny-and-silent stratum has zero probability of observation — so no
inverse-probability weight is identified there and no reweighting can rescue the
estimate. This forecloses the "adjust for it" response, which is why
the rule is *never score*, whatever a particular record happens to contain.

**Whether a Justice writes at all does not have that problem.** Absence is itself
an observation: once the order list is final, every participating Justice is
observed. It is not
disclosed by the pre-decision docket, and it is an increment from the
prediction's vantage point — so it clears tests 1 and 2 of the five the
withdrawn cert-signal set failed (`docs/outcome-decomposition.md`). It does **not** yet
clear the rest, and the gaps are specific: a per-Justice baseline would have to
be conditioned on what the predictor is shown rather than pooled unconditionally,
it would have to be weighted for the corpus's legacy denial-subsampled rows, writings
respecting denial are censored in an open Term, and opinion bodies reach fewer
than ten corpus rows (the operator-run channel that fills them, `fedcourts
enrich-opinions`, is scoped to the cert-granted slice and converges only the
grants whose docket links a published cluster upstream, so the denial side
stays empty by construction) — so a naive implementation would resolve "did
not write" for all nine on all but a few cases and manufacture a base rate of
zero out of an all-but-unpopulated column. Two more bite specifically because the claim is per-Justice:
nine claims per event are not nine independent bets — writing is strongly
correlated across Justices within a case, so summing them weights the writing
dimension nine to one against the disposition and reports an event count nine
times the effective one; and at a per-Justice write rate of well under one
percent, a single called positive dominates the whole set's total, which
`docs/outcome-decomposition.md` requires to be reported beside it. Those are
conditions on the claim, not details of it.

## Recording the outcome

A vote list carries its own censoring rather than leaving it to be inferred:
the source it came from, the participating count that is the aggregation
denominator, whether every participating Justice's vote is present, — the votes themselves sit beside it,
on the outcome.

Presence carries meaning, the discipline `ResolutionSignals` already
established: an absent record means **nobody looked**; a record present but
incomplete, with two entries, means exactly two votes are on the public record
and the other seven genuinely are not. Collapse that distinction and no import
can restore it.

## Vocabulary

`Stage` is the primary cut, and an event may carry none — which is exactly true
of a circuit motion, and makes the rule lookup total rather than partial.

Stage is the right cut and event kind is not: an event kind names *what filing
opened the event*, and a merits decision is not a filing. The problem it solves
is the within-SCOTUS version of one `metrics/README.md` already names across
courts (there, `granted` means cert on a SCOTUS row and a motion granted on a
court-of-appeals docket); within SCOTUS the same word means cert on a petition
and relief on a stay application. Stage says which in the record instead of in
prose.

Procedural outcomes get their own **axis**, not their own bucket in the
disposition vocabulary. A DIG has no coherent binary grant value: cert *was*
granted, and the merits event resolved to nothing. Forcing it onto the cert
binary would corrupt the comparability anchor every grant-rate figure rests on.
A summary reversal is the opposite case and belongs in the cert vocabulary,
because it *is* a grant — the Court disposing of the merits without argument. It
counts on the granted side of the binary axis, which is what keeps
`actual_granted` comparable across every rate the project publishes. No resolver
rule reads one off an order, so nothing produces the label.

## What a forecast carries — open

The model says a forecast is over per-Justice votes. *If* such a forecast
carries a distribution over the vote margin — which no schema requires today —
a disposition probability follows from it:

```
p_implied  =  Σ_{k ≥ threshold} p_margin[k]
```

Carrying an explicit margin distribution rather than nine marginals is what keeps
that aggregation exact without an independence assumption — which would be badly
wrong for a Court whose votes are strongly correlated. It relocates the
assumption into the predictor rather than removing it: nothing verifies that a
submitted margin is the law of any joint distribution over nine votes. Linearity
of expectation gives one free check, `Σ_j P(V_j = for-relief) = Σ_k k · p_margin[k]`,
and it is worth knowing how weak that check is — it pins the first moment and
nothing else, so forecasts with identical per-Justice marginals and identical
mean margin can still differ in `p_implied` across the whole plausible range.

The identity is **binary by construction**: every bin below the threshold falls
into the complement. That is right for a single-question, two-outcome vote and
wrong wherever part of the mass belongs to a procedural outcome on its own axis.
At merits the equally divided bin is exactly that case — it is not a "denial" of
anything — so the complement of `p_implied` is not itself a claimable quantity
there.

## Scoring a merits forecast — pre-registered

Three requirements any design must meet, recorded because they are what an
earlier candidate design failed on. They **supplement** the tests in
`docs/outcome-decomposition.md` rather than standing in for them; a design must
pass those too.

- **The floor must be conditioned the way the predictor is conditioned.** Not a
  base rate coarser than the disclosed conditioning, and not a window
  difference — both were tried and both failed. A segment base rate printed with
  its band cut and lookback window satisfies the letter of "a floor was
  reported" while repeating the failure, so reporting one is not compliance.
- **No scored total may include any part of a cert-stage vote forecast beyond
  the disposition scalar.** Levels below the disposition are unavailable at cert,
  so the remaining bins of a margin distribution are unfalsifiable there.
  Eliciting them anyway is permitted; scoring them, or presenting them as
  evidence of rigor, is not.
- **A scoring rule must be proper over its whole domain.** A rule proper only on
  the subset where one of its terms is inert is not proper. A consistency term
  between two submitted numbers additionally drives them toward equality, so any
  design carrying one must ship a test that distinguishes a genuinely coherent
  forecast from a field copied to avoid the penalty.

The registered design, chosen against those constraints:

**The scored axis is one probability: P(disturbed).** A merits prediction
carries `judgment` (the full vocabulary, `Prediction.judgment` mirroring
`Outcome.judgment`) and its headline `probability` denotes P(the judgment
below is disturbed: reversed, vacated, or the mixed affirmed-in-part
outcome) — the merits
meaning of the field whose cert meaning is P(granted), exactly as `granted`
already denotes cert on a petition and relief on an application, with the
stage saying which. The outcome writer records the same binary in
`actual_granted` (`pipeline.judgment.judgment_disturbed` is the single
projection), so `(probability − actual_granted)²` is the Brier score at every
stage, and one formula serves both. The binary is **declared over the full
judgment vocabulary**, not derived from a two-outcome vote question: a DIG and
an equally divided affirmance are declared *undisturbed* (both leave the
judgment below standing), so the complement is well-defined even though it
pools an affirmance with two procedural exits — the equally-divided caveat
above is answered by declaration, not ignored. They stay in the scored pool
because the baseline's denominator holds them too (next paragraph), keeping
the scored population and its baseline the same population. The
mechanical-claim mirror is the `merits-v1` set (`pipeline.claims`): one
declared claim, `judgment-disturbed`, restating the headline probability the
way the cert set's `disposition` claim does; the per-Justice vote, split, and
authorship claims were tested against `docs/outcome-decomposition.md`'s eight
tests and **failed** (no committed resolution channel, no conditioned
strictly-prior baseline, and nine-to-one re-encoding of one correlated
insight), so they are deliberately not declared.

**The baseline is the strictly-prior pooled disturbed rate.** The statpack's
merits section publishes per-grant-Term counts;
`pipeline.base_rates.merits_base_rate` pools its `disturbed` over its `parsed`
across Terms strictly before the case's, under the identical
leakage rule the segment base rate applies (the case's own and later Terms
never contribute), and it is **version-free** because the section is not a
salience-band product: there is no scorer version to pin. Skill is
`brier_skill` against that baseline, so parroting the historical disturbed
rate earns ~0.

The baseline's population is the scored population, and that is the first
constraint doing real work rather than being recited. A merits cell exists
only where the grant opened a merits proceeding
(`corpus.opens_merits_proceeding` — the rule that mints the event); a GVR and
a summary reversal terminate at the cert order and mint nothing, so the merits
section does not admit them either. GVRs run at roughly forty percent of
grants and are near-certain vacaturs, so a merits population holding them
would sit well above the rate the scored cases actually face — a baseline
coarser than the disclosed conditioning, which is exactly what
`docs/outcome-decomposition.md`'s third test forbids, and it would manufacture
apparent lift for a forecaster who knew only the argued rate. It would also
double-count: a GVR's vacatur is a *cert*-stage disposition, already carried by
the cert sections, and describing it again under a merits heading is the
stage-axis confusion the axis exists to prevent. If a finer committed cut ever
lands (originating circuit, question presented), the same constraint requires
re-deriving the baseline at that conditioning before any skill number is
published against it.

**Where that exclusion is only as good as the label, and what is owed.** The
predicate reads the row's cert `disposition`, and the label cannot carry the
exclusion alone. The
`gvr` label is a **forward convention** (the `Disposition` docstring), and a
row's label can lag its own cert order — measured on the walked corpus, the
stale labels sit on *recent* IFP GVRs, not only on Terms resolved before the
convention existed — so such rows pass `opens_merits_proceeding`, their
cert-order
"Judgment VACATED and case REMANDED" parses as `vacated`, and they would enter
the pooled rate at near-certain disturbance. `summary-reversal` has no
resolver at all, so that class is excluded in name only. Both would
inflate the pooled rate, and
differential parseability aggravates it — a cert-order vacatur parses the day
it is granted, an argued judgment six to eighteen months later, so the
*parsed* slice is enriched in the escapees beyond their population share.
The standing constraint, restated: **no merits skill number may be published
against an unguarded pool** — one whose escapees are not removed. The
**label-independent guard** that discharges it is the deterministic one this
constraint always admitted — the grant→judgment gap, since a disposition
riding in the cert order carries the grant's own date, while the nearest
genuine judgment observed sits a full month after its grant — and it is
applied where the pool is built
(`pipeline.judgment.judgment_rode_the_grant_order`, at the statpack merits
accumulator's admission): a row whose parsed judgment is dated on or before
its own grant is excluded from the cohort entirely, exactly as a labeled GVR
is, and counted in the section's published `cert_order_excluded` — a guard
that stops firing and a guard with nothing to fire on must not render the
same artifact. A pack parsed from a build the guard never ran on publishes
`null` there, never a zero, for the same reason. A parsed judgment carrying
**no** date cannot be gap-tested:
its membership is unknown, so it stays in `granted` as a visible coverage
gap while its judgment stays out of the parsed slice and the rate. A granted
case recorded as `merits_terminated` sits in `granted` on the same footing,
whichever of the two shapes it carries: a post-grant Rule 46 dismissal has no
judgment to place, because nobody reached the merits; a bare mandate notation
has one the corpus never captured. Folding either into the vocabulary as a
seventh value would score it as undisturbed — asserting for the first that the
decision below survived a merits ruling no one made, and for the second that it
survived a ruling whose direction the record does not state. The
invariant the pool publishes under is therefore exact: **every judgment in
the parsed slice provably postdates its grant**, and `brier_skill_score` is
computed on merits cells against that guarded pool — the prohibition is
discharged by the guard, not waived. What the guard does not reach, stated
rather than implied: a summary reversal issued in a *later* order than the
grant, and an unparsed cert-order vacatur sitting in `granted` as coverage —
both residues of the parse, visible in the coverage columns, neither able to
touch the rate. Detecting the contaminated Terms per cell was considered and
rejected — the escapees show up as a partly-labelled Term rather than an empty
one, and the cert Term table an evaluator can read is keyed on the
docket-number Term, so the test would pass exactly the Terms the pack's own
caveat names; the guard therefore lives at the pool, where one predicate
cleans every consumer at once (the merits base rate and the harness's
`judgment-disturbed` claim baseline pool the same per-Term counts). `segment_base_rate` is
recorded on a merits cell as the baseline its skill is scored against; the
harness's `judgment-disturbed` claim baseline reads the same guarded pool, so
both carry the guard by construction — and because they are one quantity
computed twice, the leaderboard cross-checks the evaluator's recorded rate
against the harness's and drops a merits cell whose two disagree
(`metrics/README.md`, the merits skill column), rather than ranking it on a
rate only the evaluator pooled.

**Three guards on the pool, all stated rather than implicit.** The window is
the same Term-year band and the same knob the cert baseline uses —
`salience.base_rate_lookback_terms`, ten Terms as shipped — so the pool is
`grant_term - 10 <= entry < grant_term`, and moving that knob re-bases every
published skill number, cert and merits alike, at once; any merits figure is
published with the window stated. The pool must clear a **stated minimum
sample** (`MERITS_BASE_RATE_MIN_PARSED`, 30 parsed judgments as shipped)
before it returns a rate at all. That
floor is not decoration: the merits section exists from its first parsed
judgment, so without it a single prior-Term row would hand out a degenerate
0 or 1 baseline — and `brier_skill` returns `None` exactly where such a
baseline was *right*, so a published mean would be taken only over the cells it
got wrong. And the pool refuses **build provenance it cannot vouch for**: a
Term whose `cert_order_excluded` is null comes from a statpack build the
cert-order guard above never ran on, so its parsed counts may still carry the
class the rate must exclude — one such Term inside the pooled window and the
whole pool returns no baseline, rather than a narrowed window nobody stated
or a rate over contaminated counts. (The window knob therefore has a second
effect beside the level it sets: it decides which Terms' provenance can make
a merits baseline exist at all.) The window alone re-bases rather than
refuses; behind the floor or the provenance refusal there is no baseline, the
claim goes unscored, and no substitute rate is invented.

**The Term axis is the grant Term, on both sides.** The statpack merits
section is keyed on the October Term certiorari was granted in, and so is the
baseline lookup — read from the merits event's `opened_at`, which *is* the
grant date. The docket-number Term is not a stand-in for it: the two disagree
for a petition docketed into the incoming Term and granted before that Term
opens, where the docket Term runs one *later* and would admit the case's own
cohort into its own baseline. Keying both sides on the grant Term also keeps
cohort-mates comparable — two cases granted in the same Term are scored
against the same pool, which a docket-keyed lookup would not guarantee.

**Censoring, which the fifth test requires answering.** An argued case's
judgment lands six to eighteen months after the grant, so a recent, still-open
grant Term contributes a slice skewed toward the quicker dispositions — its
parsed rows are thinner and earlier-resolving than that Term's eventual
cohort. Its sharpest version — a cert-order vacatur parsing the moment it is
granted — is what the population predicate is meant to remove, and removes
only where the label is present (above). The strictly-prior guard keeps a
case's own Term out, the minimum-sample floor keeps a thin pool from scoring at
all, and the statpack's `parsed`/`granted` coverage is published beside the
rate so the residue stays visible rather than assumed away.

**The vote block is mandatory, and scored intersection-only.** Every merits
prediction must carry a non-empty per-Justice `votes` block — the schema
enforces "judgment set ⇒ votes non-empty" on the artifact, and the `validate`
gate enforces "merits-stage event ⇒ the scored prediction carries a judgment"
from the committed `event.yaml`, the two halves meeting because a prediction
does not carry its event's stage. The block is scored by `vote_accuracy`
alone: over the Justices the outcome record actually names, under
`vote_provenance` — never over what the predictor attempted, and never
entering any total beyond that per-cell fraction. Today the merits outcome
writer records **no** votes, deliberately: the terminal docket entry's
authorship recital names at most the opinion's author and never the
participating count `VoteProvenance` requires as the aggregation denominator,
so no honest provenance block can be built from docket text, and a vote list
without one is illegible. The mandatory block is therefore elicitation ahead
of its observation channel — banked, unscored — until a real vote source (an
order list, the opinion, SCDB) populates `Outcome.votes` with provenance.
That is the permitted side of the second constraint's line, and the
constraint's own prohibition stands untouched: a *cert*-stage vote is never
scored.

**A check holds that prohibition, not the absence of a data source.**
`pipeline.moments.scores_votes` is the gate, and it lives on the moments
register because that table is the authority on an event's stage. It admits
only the declared **merits** moments: `vote_accuracy` returns null on
everything else before it reads either vote list, and `mean_vote_accuracy`
re-applies the same predicate to each cell's own event as it aggregates, so a
committed `Evaluation` that carries the figure anyway — written by an evaluator
that computed the field itself — is dropped from the mean rather than averaged
into it. Both seams key on the **event's declared moment**, not on the stage the
board's join assigned the cell, so the two cannot disagree about which cells are
scorable. Denial is the default rather than the cert stage being named: an id the
register does not declare has no stage this code can state, so it is one that
cannot be shown *not* to be cert. The consequence is that an ingestion channel
populating `Outcome.votes` at the cert stage — noted dissents from denial are
published on the order list and are the obvious candidate — changes nothing
about what is scored. That is what makes the rule structural rather than a
property of what a particular record contains, and the tests that fail when the
gate is removed sit beside the scorer and the board (`tests/test_evaluate.py`,
`tests/test_leaderboard.py`).

**`judgment_correct` is descriptive, not a score.** The exact-match bit on the
full vocabulary (`Evaluation.judgment_correct`) reports
whether the predicted judgment label was the realized one — a `reversed` call
against a `vacated` outcome is 0 even though both disturb. It carries no
probability and is never presented as a proper score; the Brier on the
disturbed binary is the scored quantity. It is also the merits accuracy axis
outright: `correct` on a merits cell *is* this comparison
(`pipeline.evaluate.is_correct`), because a merits outcome's
`actual_disposition` is always the off-vocabulary `other` and comparing
dispositions there would score every cell against a constant the merits
contract never defines. Both are computed by the shared helpers, but on a real
cell they are the evaluator's field to write, like `brier_score` — the harness
stamps only `claim_scores` and the base-rate basis record.
This keeps the third constraint trivially satisfied: the design's one scored
rule is the Brier score on one submitted probability, proper over its whole
domain, with no consistency term between submitted numbers anywhere (the
`merits-v1` claim must *equal* the headline probability — a well-formedness
check that voids a divergent block, not a penalty that shapes it).

**What remains unbuilt, and stays outside every scored total.** No schema
carries a margin distribution and none is scored; `p_implied` and the margin
identity above remain analysis, and eliciting a margin in prose remains
permitted and unscored. The writing-role claims
keep the conditions recorded under *Observation* above.

[rules]: https://www.supremecourt.gov/filingandrules/2026RulesoftheCourt_WEB.pdf
[fjc]: https://www.fjc.gov/history/spotlight-judicial-history/rule-four
