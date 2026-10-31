# The trial stage

What a district-court forecast is, before any is committed: the moments a
trial-court case passes, what each predicts, when each opens, and how each
resolves. The stage is court-agnostic, so every later district slice reuses it
rather than minting its own. The first slice to use it is the AI-case watchlist
(`config/ai-watchlist.yaml`), whose district dockets the corpus already keeps
current ([data-pipeline.md](data-pipeline.md)).

**Status: designed, not registered.** Nothing here is forecast yet. The stage
registers with the process version that opens the prediction scope to the
watchlist slice. That version adds `trial` to `Stage` and the four moments
below to `Moment` (`schemas.py`), declares their claims in
`pipeline/moments.py`, and dates the entry in [freeze-record.md](freeze-record.md).
Until it lands, this page is the design that entry cites, and a change to it
needs no re-bless. The resolver below is built as library code and is wired
into nothing.

## The moments

| Moment | Predicts | Outcomes |
| --- | --- | --- |
| `trial-dismissal` | the ruling on a motion to dismiss | granted, granted in part, denied; for a grant in whole or in part, with or without leave to amend |
| `trial-class` | the ruling on a motion for class certification | certified (granted), certified in part, denied |
| `trial-summary-judgment` | the ruling on one party's motion for summary judgment | granted, granted in part, denied |
| `trial-judgment` | the case's final disposition | judgment for plaintiff, for defendant, mixed, or no merits decision |

Each of the three motion moments also resolves **withdrawn** (the movant
withdrew it) or **mooted** (the court denied or terminated it as moot, or the
action closed before any ruling on it).

**One event per motion.** A motion event is named by the docket entry that
filed it. Cross-motions for summary judgment are two events, one per moving
party, so "per moving party" needs no extra outcome. Two defendants' separate
motions to dismiss are two events. A motion renewed after an amended complaint
is a fresh event: the first resolves mooted, the second opens on its own
briefing.

**Partial rulings are outcomes, not ambiguity.** Most rulings in these cases
grant some claims and deny others, so "in part" is a registered outcome on
every motion moment, and the resolver records which. Which claims survived is
not part of the outcome: a count-by-count record is a later claim family, not
this stage's.

**Leave to amend** is recorded only on a dismissal granted in whole or in part:
`with-leave` where the order grants leave or invites an amended complaint,
`without-leave` where it dismisses with prejudice, denies leave, or calls
amendment futile, `mixed` where it does both for different claims, and
`unstated` otherwise. "Without prejudice" alone reads as unstated, because a
dismissal without prejudice does not by itself grant leave.

## When each moment opens

A motion moment opens when the motion is **fully briefed**: the opposition and
the reply are both on the docket, or the reply deadline has passed with no
reply. The deadline is the one the court set by order where it set one, and
otherwise the district's local rule, recorded per court in the slice's config
when the slice registers; a court whose rule the config does not carry opens on
the reply alone. The forecast's information set is therefore the complete
briefing, as the merits stage's `briefed` moment is for the Court.

`trial-judgment` opens with the slice: a listed case's final disposition is
forecast once, when the case enters the slice, and again at no later point in
the first registration. A later re-forecast (after the dismissal ruling, say)
is a second moment, registered on its own.

**No horizon.** A ruling can sit for months. The event stays open until the
court acts, and the forecast prices the wait in no way: it predicts what the
court does, not when.

**The judge is known** at every moment, since assignment is public on the
docket, so there is no panel-style comparison here. A reassignment between the
opening and the ruling changes nothing about the event.

## How each moment resolves

**Nothing is voided**, the same rule the D.C. Circuit slice's design carries
([milestones.md](milestones.md)). A motion
withdrawn, mooted by an amended complaint, or overtaken by settlement resolves
as such, and the forecast prices that in. A forecaster who thinks a motion will
be mooted puts weight on that outcome.

The resolver is `pipeline/trial_resolver.py` (rule `trial-resolver-v1`). It is
deterministic, runs no agent, and is built to miss rather than misread: a text
it cannot read leaves the event open, or sends it to triage, and never records
a guessed outcome.

- **The docket text decides.** The disposing entry is the first court entry
  after the motion (an order, opinion, ruling or minute order, or an order
  adopting a magistrate judge's recommendation; never a party's filing or the
  recommendation itself) whose docket text rules on the motion. A ruling is
  the CM/ECF form: a ruling verb with the motion's entry number directly after
  it, going on to name a motion (`ORDER granting 45 Motion to Dismiss`,
  `denying [45]`, `granting 45 and 47 Motions`). A number anywhere else names
  a motion's subject rather than the one ruled on, so `ORDER granting 46
  Motion for Leave to File Excess Pages re 45 Motion to Dismiss` rules on 46,
  and `granting 45 days` rules on nothing. An entry that cites no entry number
  never rules, because a docket can hold several motions of one kind.
- **The rest of the motion's phrase qualifies the verb.** `as moot` reads
  mooted and `in part` reads granted in part, wherever in the phrase they
  stand; `as to`, `only`, `to the extent`, `insofar` and `with respect to` are
  triage, as is a bare "terminating".
- **The order's text only checks.** Where it is given, its decretal language
  (the final run of "it is ordered" paragraphs, from the last concluding
  anchor where one leads them) is read for a clause whose subject is the
  motion itself (`the Motion to Dismiss (ECF No. 45) is DENIED`) or whose verb
  takes it by name (`the Court GRANTS Defendants' Motion to Dismiss (Dkt.
  45)`). A clause that conditions or anticipates a ruling ("should not be
  granted", "will be granted", "show cause"), or whose subject is another
  matter about the motion (an extension, leave, a hearing, a reply), reads
  nothing. A reading that disagrees with the docket text, a clause citing
  several entries, and a ruling with an exception or a limit are triage. The
  order's text never resolves an event on its own: an opinion that cites the
  motion with no ruling its docket text states is triage.
- **"In part" is stated, not inferred.** A ruling in part is one the text calls
  so, or one predicate that grants and denies (`GRANTED as to Count I and
  DENIED as to Count II`); a grant beside a separate denial of something else
  is not one. Leave-to-amend and prejudice phrases are read before the ruling
  verb and struck, as is a warning of what follows a failure to amend
  ("failure to file will result in dismissal with prejudice"); leave stated
  both ways (some counts with prejudice, others with leave) reads `mixed`.
- **A closure without a merits decision** is read from its leading noun: a
  stipulation or notice of dismissal, an order granting one, an order granting
  final approval of a settlement, or a consent judgment, followed by nothing
  but prejudice words, the whole action or all claims, the filer, the rule it
  rests on and the clerk's trailer. Anything else after it (a party, a claim,
  a cause of action, a crossclaim, an appeal, a related case, a settlement
  with one defendant) leaves it unread, and so does a motion for voluntary
  dismissal, a preliminary approval or a notice of settlement. A closure
  resolves `trial-judgment` as no merits decision and any motion still open as
  mooted. A stipulation filed by named parties that drops only some of them
  without saying so is read as a closure; the docket text cannot tell the two
  apart, which is a known limit of the rule.
- **A withdrawal notice** naming the motion as the first entry it cites, with
  no limit ("as to", "only", "in part"), resolves the motion withdrawn.
- **A final judgment** is an entry whose leading noun is a judgment. Its docket
  text must name the side, by "in favor of", "judgment against" or "take
  nothing"; mixed needs both sides named "in favor of", and the judgment's own
  text, where given, must not contradict it. A judgment whose first sentence
  marks it partial, Rule 54(b), default, or for costs or fees, and the court of
  appeals' judgment, are passed over.
- **Every resolution cites the entry it read**: its CourtListener entry id,
  entry number and filing date.
- **What goes to triage**, as an unrecorded outcome with the reason and the
  entries weighed: the docket text and the order disagreeing on the ruling or
  on leave; a docket ruling with a limit, two docket rulings that disagree, or
  a bare "terminating"; an order clause citing several entries, or ruling with
  an exception or on part only; an opinion with no docket-text ruling; a final
  judgment whose docket text names no side, names both in different forms, is
  limited to some parties or claims, or rules on a counterclaim; and a
  judgment a later entry amends, vacates or sets aside.

The order's text, where the resolver uses it, is the court's own order read
from the RECAP archive. A court order is a work of the federal government and
public domain; CourtListener's CC BY-ND covers its own curation, not the order
([data-sources.md](data-sources.md)).

## Base rates

The corpus stores no district-court base rate, and none is built for this
stage. The watchlist is a hand-curated selection of AI cases, so a general
civil-docket rate would describe a different population in any case. The
first registration therefore states, per moment, either a published figure
with its source and population, read before registration, or that the first
year runs **without a base rate**, in which case no skill-over-base-rate
figure is reported for the slice until its own resolved events can supply
one. The Federal Judicial Center's studies of motion-to-dismiss and
summary-judgment practice are the candidate published sources; none is
adopted yet.

## Out of scope

Discovery motions, preliminary injunctions (a candidate later moment, with a
horizon of its own), jury verdict detail and damages amounts. The salience gate
does not apply: the slice is the selection.
