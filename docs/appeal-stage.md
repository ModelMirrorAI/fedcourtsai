# The appeal stage

What a court-of-appeals forecast is, before any is committed: the moments an
appeal passes, what each predicts, when each opens, and how each resolves. The
stage is court-agnostic, so every slice that reaches a circuit reuses it. The
first to use it is the AI-case watchlist (`config/ai-watchlist.yaml`), whose
listed appeals sit in several circuits; the D.C. Circuit slice
([milestones.md](milestones.md)) adds its panel moments to the same stage. The
last section says what happens when a listed case reaches the Supreme Court.

**Status: designed, not registered.** Nothing here is forecast yet. The stage
registers with the process version that opens the prediction scope to the
watchlist slice, beside the trial stage ([trial-stage.md](trial-stage.md)).
That version adds `appeal` to `Stage` and the two moments below to `Moment`
(`schemas.py`), declares their claims in `pipeline/moments.py`, and dates the
entry in [freeze-record.md](freeze-record.md). Until it lands, this page is
the design that entry cites, and a change to it needs no re-bless. The reader
for `appeal-disposition` is built as library code (`pipeline/appeal_resolver.py`,
rule `appeal-resolver-v1`), read by a dry-run command and wired into nothing
else; none is built for `appeal-permission`.

## The moments

| Moment | Predicts | Outcomes |
| --- | --- | --- |
| `appeal-permission` | the ruling on a petition for permission to appeal | granted, denied |
| `appeal-disposition` | the court's disposition of the appeal | affirmed, reversed, vacated, mixed, dismissed, no merits decision |

`appeal-permission` also resolves **withdrawn** (the petitioner withdrew it)
or **mooted** (the case below closed before a ruling), the trial stage's two
words for the same two ends.

**Which appeals.** An appeal is in the stage when a slice lists its docket: for
the watchlist, a `relation: appeal` docket under a listed case. One event per
listed docket and moment. Where a court consolidates several appeals, the
slice lists the lead docket, and the consolidated set is one event. A petition
for permission usually sits on a docket of its own and a granted appeal on a
new one, so each is forecast only once its own docket is listed.

**A petition for permission** is one under Federal Rule of Civil Procedure
23(f) (a class-certification ruling) or 28 U.S.C. § 1292(b) (a certified
interlocutory order). It is a moment of its own because the court of appeals
decides it separately, and a grant opens an appeal that gets its own
`appeal-disposition` event on the docket the court then assigns.

**The disposition's outcomes.** *Affirmed*, *reversed* and *vacated* are the
court's judgment on the whole of what was appealed, with or without a remand.
*Mixed* is any judgment that does different things to different parts
(affirmed in part and reversed in part, affirmed in part and vacated in part).
*Dismissed* is the court's own dismissal of the appeal, for want of
jurisdiction or as moot. *No merits decision* is an appeal the parties ended:
a voluntary dismissal, a stipulated dismissal, a settlement. The split between
the last two is who ended the appeal, which the docket states.

**Not forecast in the first registration:** which judges sit, how each votes,
and whether anyone dissents. The panel moments and the vote claims belong to
the D.C. Circuit slice, whose court names its panel well before argument. A
court that names its panel only days before argument leaves no window in
which a forecast could use it, so an appeal in such a court has this stage's
two moments and no more.

## When each moment opens

`appeal-disposition` opens when the **briefing closes**: the appellant's reply
brief is on the docket, or its deadline has passed with none. The deadline is
the one the court's scheduling order set where it set one, and otherwise the
one the Federal Rules of Appellate Procedure give. The forecast's information
set is the complete briefing. It does not wait for argument, which is often
set months later or not held.

`appeal-permission` opens when the **answer** to the petition is on the docket
or its deadline has passed with none.

**An appeal already open when the stage registers** follows the trial stage's
rule: briefing closed and no disposition yet opens it on the day the slice is
switched on, as a forward event; a disposed appeal opens nothing.

**No horizon.** An appeal can sit for a year after argument. The event stays
open until the court acts.

## How each moment resolves

**Nothing is voided.** An appeal dismissed on the parties' stipulation, mooted
by a ruling below, or ended by a settlement resolves as such, and the forecast
prices that in.

The event resolves on the **panel's judgment**. A petition for rehearing, a
rehearing en banc and a later judgment of the Supreme Court do not reopen it:
each is a later proceeding, and the forecast was of what the panel would do.

The resolver is to be deterministic, to run no agent, and to miss rather than
misread, on the trial resolver's terms: the docket text decides, the opinion's
or order's own decretal line only checks it, a disagreement between the two or
a text that cannot be read is an unrecorded outcome for the maintainer's
triage, and every resolution cites the entry it read. The court's opinion is
its own work and public domain ([data-sources.md](data-sources.md)). The
stage does not register until that resolver exists and its triage rate has
been measured on appeals already decided (*Measuring the reader*, below).

### The reader as built

`pipeline/appeal_resolver.py` reads one appellate docket for
`appeal-disposition`, and `fedcourts appeal-events` runs it over the stored
listed appeals ([cli.md](cli.md)). It reads the docket text only; the check
against the opinion's own decretal line is not built.

- **A disposition is read only from the court's own entry**, named by its
  leading words: a judgment, an opinion, a memorandum, a summary order, or an
  order whose own words dismiss the appeal. A mandate, a document received
  from another court, a party's filing, the Supreme Court's judgment and an
  entry the clerk has marked vacated, stricken, withdrawn or entered in error
  dispose of nothing. Neither does an order that only speaks of a dismissal:
  one to show cause, one that defers the question, one that dismisses unless
  a party acts.
- **The result is read in four forms**: a judgment entry that leads with it
  ("Judgment, Affirmed") and speaks of no other result; the court's capitals
  in an opinion or memorandum entry ("we VACATE … and REMAND", "AFFIRMED"); a
  judgment "that the judgment of the District Court be affirmed"; and an entry
  "affirming the judgment of the district court". Outside those forms,
  lower-case prose is not read, because an opinion's summary speaks of what
  the court below did. A remand is not an outcome. An opinion entry that
  states no result is passed over for the judgment beside it.
- **Result words beside another subject go to triage.** Where the entry also
  speaks of a dissent or a concurrence, a cross-appeal, rehearing en banc, a
  stay or injunction pending appeal, a certified question, fees or sanctions,
  or a result "as to" a part, the rule cannot say the words are the panel's
  disposition of the whole appeal.
- **Mixed** is two different results with at least one stated in part.
  Two results with no "in part" (reversed and vacated), and one result in
  part with no other, go to triage.
- **A dismissal is split by who ended the appeal.** A voluntary or stipulated
  dismissal, a settlement or Rule 42(b) is *no merits decision*; a dismissal
  for want of jurisdiction, as moot or as untimely is *dismissed*. A
  dismissal that states neither, both, or another reason (a failure to
  prosecute) goes to triage, and so does one that reaches less than the whole
  appeal: in part, one of several appellants, one of several consolidated
  appeals, a cross-appeal. The reader does not otherwise tell the members of
  a consolidated set apart.
- **A petition for review is triage.** Its outcomes (granted, denied) are not
  this stage's, so a judgment on one is reported and never mapped.
- **The first entry that reads as a disposition resolves the event.** Entries
  the rule could not settle are triage only where none reads. A petition for
  rehearing and what follows it are not read.
- **The event opens on the appellant's reply brief as filed**: the first
  entry that leads with the brief and names the appellant or petitioner as
  its filer. A deadline, an extension, a deficiency notice, a stricken brief,
  a paper copy received, a supplemental reply, a reply on a motion and
  another party's reply are not it. The deadline path is not built: an appeal
  whose reply deadline passes with no reply waits under this rule, because
  the courts state that deadline in forms too varied to read safely.
- **A docket that speaks of a cross-appeal opens nothing**, because the last
  brief there is not the appellant's reply.
- **A disposition the rule read with no reply read before it opens
  nothing.** That covers an appeal decided before its briefing closed, one
  decided the day the reply arrived, and one whose reply the rule could not
  read. An entry the rule could not settle closes nothing.
- **Entries with no date, or dated after the day of the reading, are not
  read.**

### Measuring the reader

The listed appeals already decided are too few to measure a triage rate on,
so the measurement is a sample: `fedcourts appeal-sample` draws civil appeals
from CourtListener, 25 from each of the Second, Third, Ninth and D.C.
Circuits, filed in one fixed twelve-month window old enough that most have
ended, in a seeded random order so each court's draw repeats. It reads each
with the reader above and reports three counts: appeals with a disposition
read, appeals with an entry sent to triage, and appeals on which nothing was
read. The triage rate is the second over the first two together. The third is
split by whether CourtListener records a termination date, because an ended
appeal on which the reader read nothing is where a disposition in a form the
rule does not know would be; those rows, and a hand check of the dispositions
read, are what say whether the reader misses or misreads. The sample holds
what RECAP holds: a docket with few stored entries reads as nothing read, and
is not evidence about the rule.

## Documents

A cell reads the docket, the principal briefs, the reply and the order or
judgment under review, staged by the pipeline like every other input
([document-provisioning.md](document-provisioning.md)). Appellate filings are
covered less completely in the RECAP archive than district filings are, so
this stage is where a purchase from PACER through RECAP Fetch is most likely
to be needed ([live-sources.md](live-sources.md)). No purchase path is built:
the stage registers only with a per-run spend cap that fails closed and a log
of every purchase. An appendix is never bought.

## Base rates

The corpus stores no court-of-appeals base rate for dispositions. The first
registration states, per moment, either a published figure with its source and
population, read before registration, or that the first year runs **without a
base rate**, in which case no skill-over-base-rate figure is reported until
the slice's own resolved events can supply one. The Administrative Office of
the U.S. Courts' published tables of appeals terminated on the merits are the
candidate source; none is adopted yet, and a general civil-appeal rate would
describe a different population from a hand-picked list.

## A listed case at the Supreme Court

**Status: designed, not built.** What exists is a monitoring readout:
`fedcourts ai-watchlist-check` (`pipeline/ai_follow_ons.py`) reports each
SCOTUS corpus row whose lower court and docket number are a listed docket's
own. Nothing records a link, tags the petition or plans a forecast from it.
The rule below registers with the watchlist slice.

**The link.** A petition for certiorari or an application to the Court arises
from a listed case when the lower court and docket number it names are a
listed docket's own. The match is on the listed docket's number, so a petition
from an appeal the watchlist does not list is found once that appeal is
listed. A petition linked after one of its events has resolved opens nothing
for that event: only an event still open on the day of the link is forecast,
so a listing made with the Court's action in view cannot select into the
population.

**The rule.** A linked petition is forecast whether or not the salience gate
selects it. The gate ([salience.md](salience.md)) is not changed, the link is
no input to it, and the deterministic exclusions that run before it still
apply; a linked petition they exclude is reported by the check as linked and
not forecast. What the link adds is a second route to a forecast, and a second
population for the cells it produces:

- A linked petition the gate has **selected** is a SCOTUS case like any other.
  Its cells are SCOTUS cells, planned when the gate would plan them and
  counted where it would count them, as if no watchlist existed.
- A linked petition the gate has **not selected** is forecast on the Court's
  moments under the **watchlist's own process label**, and its cells belong to
  the watchlist's population. No SCOTUS leaderboard, claim board, big-case
  board, window record or public export reads them, and the gate's own
  bookkeeping (cohort completion, the re-predict rule, the interim reserve's
  slots in use) does not either: to the gate, such a cell is not there.
- The gate's selection is a one-way latch on the case and can come late. From
  the pass that selects a linked petition, the gate owes its open and later
  events as SCOTUS cells in the ordinary way, including an open event that
  already holds watchlist cells. Those earlier cells stay where they are. One
  event can then carry a forecast in each population, and each cell is still
  counted in exactly one.

The SCOTUS population is therefore exactly the one its registered selection
produces: every SCOTUS cell is one the gate ordered, made when the gate
ordered it, and the gate orders nothing because of a link.

**What the watchlist's Supreme Court figures are.** They cover the linked
petitions the gate passed over, which is by construction the remainder the
gate ranked low, less any it later selected. They are reported with their
count beside them, against the same base-rate anchor a SCOTUS event of the
same band scores against, labelled as Supreme Court events, and never pooled
with the trial or appeal stages' figures, which answer different questions. A
view of every linked petition across both populations is a descriptive cut of
cells already counted, never a second count.

**What the registration has to change.** Population is a docket-level
membership as built (`prediction_slices.py`, `store.in_population`): every
cell under `data/cases/scotus/` is a SCOTUS cell, a slice refuses a `scotus`
docket, and no docket is in two populations. This rule needs a population
recorded per cell and read by every figure reader
([process-version.md](process-version.md) lists them), the watchlist's process
to carry the Court's moments and prompt text under its own digest and counting
windows, and those three invariants restated for a linked petition. None of
that is built, and each is part of the change that switches the slice on.

## Out of scope

Petitions for a writ of mandamus, motions for a stay or an injunction pending
appeal, rehearing and rehearing en banc, and the amount of any fee or cost
award.
