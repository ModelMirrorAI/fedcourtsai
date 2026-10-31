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
briefing. A motion to dismiss that asks for other relief in the alternative
(to transfer, to stay, to compel arbitration) is not a `trial-dismissal`
event, because a grant of it need not dismiss anything.

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
  adopting a magistrate judge's recommendation; never a party's filing, the
  recommendation itself, or a court of appeals' order or mandate) whose docket
  text rules on the motion. A ruling is the CM/ECF form: a ruling verb standing
  right after the entry's head (`ORDER granting`, `MEMORANDUM OPINION AND
  ORDER denying`, `ORDER ADOPTING 58 REPORT AND RECOMMENDATIONS and granting`)
  or opening a later clause after a semicolon, a comma or "and", with the
  motion's entry number directly after it and going straight on to name a
  motion (`ORDER granting 45 Motion to Dismiss`, `denying [45]`, `granting 45
  and 47 Motions`). A verb anywhere else is a reference to a ruling, not one:
  `ORDER granting 70 Motion for Reconsideration of Order granting 45` rules on
  70, `ORDER vacating 60 Order granting 45` rules on nothing about 45, and
  `granting 45 days` rules on nothing. An entry that cites no entry number
  never rules, because a docket can hold several motions of one kind.
- **Anything that could limit the ruling is triage.** The ruling's run goes
  from the motion's number to the next ruling verb, across sentences, and
  stops at the clerk's trailer ("Signed by Judge ..."). A verb that carries
  its own qualifier reads as it says (`denying as moot` reads mooted,
  `granting in part and denying in part` reads granted in part). Otherwise
  the run goes to triage when it holds a limit (`moot`, `in part`, `partial`,
  `as to`, `only`, `except`, `but`, `to the extent`, `insofar`, `with respect
  to`), other relief (`or`, `alternative`, a stay, a transfer, arbitration, a
  remand, a severance), a second ruling word (`denied` after `granting`,
  `terminated`), or another entry's number, whether the word limits the
  ruling, belongs to the motion's own title ("Motion to Dismiss in Part"),
  names a party ("Moot Holdings LLC") or speaks to another motion; the rule
  cannot tell which. A bare "terminating" is triage.
- **Leave is read from the docket text only**, from the motion's ruling up to
  the next ruling, and only for a dismissal granted in whole or in part.
  Leave-to-amend and prejudice phrases are read after a warning of what
  follows a failure to file or amend ("failure to file will result in
  dismissal with prejudice") is struck, which a motion's own title ("for
  Failure to State a Claim") is not; leave stated both ways (some counts with prejudice,
  others with leave) reads `mixed`, and no phrase reads `unstated`.
- **The order's text only checks.** Where it is given, its decretal language
  (the final run of "it is ordered" paragraphs, from the last concluding
  anchor where one leads them) is read for a clause whose subject is the
  motion itself (`the Motion to Dismiss (ECF No. 45) is DENIED`) or whose verb
  takes it by name (`the Court GRANTS Defendants' Motion to Dismiss (Dkt.
  45)`). A clause that conditions or anticipates a ruling ("should not be
  granted", "will be granted", "show cause"), or whose subject is another
  matter about the motion (an extension, leave, a hearing, a reply), reads
  nothing. A reading that disagrees with the docket text, a clause citing
  several entries, and a ruling with an exception or a limit are triage;
  agreement records the source as both. The order's text never resolves an
  event on its own: an opinion that cites the motion with no ruling its
  docket text states is triage.
- **A closure without a merits decision** is read from its leading noun: a
  stipulation or notice of dismissal, an order granting one, an order granting
  final approval of a settlement, or a consent judgment, followed by nothing
  but prejudice words, the whole action or all claims, a filer named only
  generically (all parties, the parties, plaintiffs, defendants), the rule it
  rests on, "and judgment", the clerk's initials, a filer's trailer, and a
  judge's signature line; a signature by the parties is not read past. Anything else
  after it (a named party, a claim, a cause of action, a crossclaim, an
  appeal, a related case) leaves it unread, and so does a motion for voluntary
  dismissal, a preliminary approval or a notice of settlement. A closure
  resolves `trial-judgment` as no merits decision and any motion still open as
  mooted. A closure that follows a judgment the resolver passed over (a
  partial or default judgment) is triage, since the merits may already be
  decided in part.
- **A withdrawal notice** naming the motion as the first entry it cites, with
  no limit ("as to", "only", "in part", "partial"), resolves the motion withdrawn, unless
  the motion was a joint one, which one party's notice cannot withdraw.
- **A final judgment** is an entry whose leading noun is a judgment. Its docket
  text must name the side, by "in favor of", "judgment against" or "plaintiff
  take nothing"; mixed needs both sides named "in favor of", and the
  judgment's own text, where given, must not contradict it. A judgment whose
  lead marks it partial or default, one under Rule 54(b) or Rule 55 anywhere
  in its text, one for costs, and a court of appeals' judgment are passed
  over. A judgment that any later entry amends, vacates, sets aside, reopens,
  reverses or remands, or reopens for a new trial or under Rule 59 or 60, or
  that a later judgment follows, is triage.
- **Every resolution cites the entry it read**: its CourtListener entry id,
  entry number and filing date.
- **What goes to triage**, as an unrecorded outcome with the reason and the
  entries weighed: the docket text and the order disagreeing; a qualifier in
  the ruling's clause, two docket rulings that disagree, or a bare
  "terminating"; an order clause citing several entries, or ruling with an
  exception or on part only; an opinion with no docket-text ruling; a final
  judgment whose docket text names no side, names both in different forms, is
  limited to some parties or claims (`as to`, `except`), leaves a claim
  pending, remaining or remanded, decides liability with damages still to be
  determined, rules on a counterclaim, crossclaim or third-party claim, or
  has the defendant take nothing too; a judgment a later entry may replace; and a closure after
  a passed-over judgment.

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
