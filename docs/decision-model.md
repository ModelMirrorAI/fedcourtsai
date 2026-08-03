# The decision model

Cert, interim relief, and merits look like three prediction problems. They are
one, with two parameters. This document defines that model and pins the
aggregation rules to sources.

**Most of it is not implemented.** `pipeline/aggregation.py` carries the
thresholds and their citations, and the vocabularies exist — `Stage`, the vote
and writing values, the merits judgment axis, and the provenance block that says
how much of a vote record is there.

What is live is narrow and worth naming, because the rest of this document is
not. `Prediction.votes` carries a per-Justice vote forecast, and `vote_accuracy`
scores it against `Outcome.votes` wherever both name the same Justice, feeding
the leaderboard's `mean_vote_accuracy`. Event definitions carry a nullable
`stage` — stamped `cert` on a cert docket's petition baseline, `interim` on an
application docket's motion baseline and on SCOTUS entry-pinned
stay/injunction motions, absent everywhere the writers do not classify one —
but no aggregation rule reads it from data. Everything else is unbuilt: no artifact carries a writing role, a
judgment, or a provenance block; no schema carries a vote *margin*; and no
aggregation rule is applied to anything. That is pre-registration: the model is settled before
there is data to fit it to, which is the only order in which the choice is
credible. `docs/outcome-decomposition.md` is the companion — it defines what a
scoreable claim is and the rule that scores one, and its tests govern anything
proposed here.

## What is predicted

The **final disposition of a matter before the Court**. Everything else — vote
splits, who writes, what a concurrence splits off — decomposes that disposition
rather than replacing it.

Procedural outcomes (a dismissal as improvidently granted — a DIG — a dismissal
as moot, an affirmance by an equally divided Court) are real and have to be
handled for the methodology to be credible, but they are corner cases rather
than the object. The design records them on their own axis and routes them to
the `procedural` stratum, never blended into a cert-worthiness score. Today only
mootness practice routes there, because `Outcome.disposition_basis` carries no
other value; `metrics/README.md` governs the stratum.

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
respecting denial are censored in an open Term, and `has_opinion` is 0 on every
corpus row today — so a naive implementation would resolve "did not write" for
all nine on every case and manufacture a base rate of zero out of an empty
ingestion channel. Two more bite specifically because the claim is per-Justice:
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

**How such a forecast is scored is not settled, and is deliberately not
pre-registered here.** Three requirements any design must meet, recorded because
they are what a candidate design failed on. They **supplement** the tests in
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

[rules]: https://www.supremecourt.gov/filingandrules/2026RulesoftheCourt_WEB.pdf
[fjc]: https://www.fjc.gov/history/spotlight-judicial-history/rule-four
