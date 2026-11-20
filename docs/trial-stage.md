# The trial stage

What a district-court forecast is: the moments a
trial-court case passes, what each predicts, when each opens, and how each
resolves. The stage is court-agnostic, so every later district slice reuses it
rather than minting its own. The first slice to use it is the AI-case watchlist
(`config/ai-watchlist.yaml`), whose district dockets the corpus already keeps
current ([data-pipeline.md](data-pipeline.md)).

**Status: registered and switched on.** The stage is registered under the
watchlist slice's own process label, `ai-watchlist-v1`, in the sequence
*How the stage registers* sets out below, and the slice is enabled
(`predict.slices` in `config/tracking.yaml`). `trial` is a `Stage` and the
five moments below are `Moment` values (`schemas.py`). All five are switched
on in the stage's own table (`pipeline/moments.py`) from the day
`TRIAL_SWITCH_ON` names, the outcome record has the stage's three fields, and
`validate` holds a trial record to both. Each moment names its claim set
(`pipeline/claims.py`). Six actors of the slice read its two prompts: the
predictors `claude-trial`, `codex-trial` and `gemini-trial` read
`.github/prompts/predict-trial.md`, and the judges `claude-trial-judge`,
`codex-trial-judge` and `gemini-trial-judge` read
`.github/prompts/evaluate-trial.md`. The registration's entry is dated in
[freeze-record.md](freeze-record.md). This page is the design that entry
cites, so a change to a rule here is a change to a registered process and
needs a re-bless under [process-version.md](process-version.md). The opener
and the resolver below run in the watchlist refresh's pass
(`pipeline/trial_events.py`), which writes an event only of a moment that is
switched on by the day it runs: from `TRIAL_SWITCH_ON` on it writes every
moment's events, and on an earlier day it reports what it would open and
writes nothing. Provisioning's forward gates read a trial event by the stage's
own rules (`provision-snapshot`).

## The moments

| Moment | Predicts | Outcomes |
| --- | --- | --- |
| `trial-dismissal` | the ruling on a motion to dismiss | granted, granted in part, denied; for a grant in whole or in part, with or without leave to amend |
| `trial-class` | the ruling on a motion for class certification | certified (granted), certified in part, denied |
| `trial-summary-judgment` | the ruling on one party's motion for summary judgment | granted, granted in part, denied |
| `trial-preliminary-injunction` | the ruling on a motion for a preliminary injunction | granted, granted in part, denied |
| `trial-judgment` | the case's final disposition | judgment for plaintiff, for defendant, mixed, or no merits decision |

Each of the four motion moments also resolves **withdrawn** (the movant
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

**One docket owns a motion.** A motion belongs to the docket whose entry filed
it. Where one motion is docketed on a multidistrict proceeding's lead docket
and again on a member docket, the lead docket's entry names the event and the
member's entry opens none, so one motion is never forecast twice.

**A temporary restraining order is not an event.** It is decided in days, often
before the other side is heard, which leaves no forecast window. A motion that
asks for both a restraining order and a preliminary injunction is a
`trial-preliminary-injunction` event for its injunction half: a ruling on the
restraining order alone does not resolve it, so the resolver passes over a
ruling whose text names the restraining order and keeps reading for one that
names the injunction. A ruling on such a motion that names neither half goes
to triage, since the rule cannot say which half it decides. An injunction the court enters on
the parties' stipulation resolves the motion mooted, because the court decided
nothing, and so does an order consolidating the injunction hearing with the
trial on the merits.

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
the reply are both on the docket, or the opposition is and the reply deadline
has passed with no reply. The deadline is the one the docket states (the response and reply
dates a clerk enters on the motion, or on a later entry that sets or resets
them), and otherwise the district's local rule, recorded per court in
`config/trial-local-rules.yaml`; a court whose rule the config does
not carry opens on the reply alone. A statement of non-opposition opens
nothing by itself: the motion waits for its ruling like any motion with no
opposition the rule can read. The forecast's information set is
therefore the complete briefing, as the merits stage's `briefed` moment is for
the Court.

**The local rules.** Each row of `config/trial-local-rules.yaml` is one
district's default briefing periods, read from the court's own published
rules, with the rule's citation, the page it was read on, the day it was read
and the day that version took force. A row gives the days for an opposition
(from the motion's filing) and for a reply (from the opposition's filing, or
from the day the opposition was due where the rule says so), the motion
moments the rule gives other periods, and no reply period where the district
allows no reply without leave: there a motion opens on a reply the court
permitted, or on a date the docket states. A period is counted in calendar
days, and a last day on a weekend or a federal legal holiday runs to the next
day that is neither, as Federal Rule of Civil Procedure 6(a) counts it. A
motion filed before the recorded version took force gets no counted
deadline, since it may have been briefed under a version the file does not
carry. A state holiday and a day declared a holiday are not read, so a period
that ends on one is counted a court day short. A motion for a preliminary
injunction gets a counted deadline only where a row names that motion: courts
set its briefing by order, in words the opener does not read as a schedule,
and no row names it.
The rows are the rules' defaults: a judge's individual practices or a
scheduling order can set other dates, which is why a counted deadline is
distrusted once any briefing schedule on the docket moves (below). The rows
cover every district the watchlist's own, member and companion dockets sit
in, and a test holds them to that.

The opener is `pipeline/trial_opener.py` (rule `trial-opener-v2`),
deterministic like the resolver and built the same way: a motion it cannot
name or briefing it cannot date opens nothing and is reported with its reason.

- **A motion is its own entry's leading phrase**, and the event is named by
  that entry's number. A motion re-filed as a correction is the later entry's
  event.
- **Briefing is a party's filing that leads with what it is** (an opposition,
  a response, an answering brief, a reply) and cites the motion as the first
  entry it refers to. A declaration, a notice, a request for argument, an
  amicus filing and a motion about the briefing are not briefing, and neither
  is briefing on a motion about the motion.
- **Briefing cites its motion directly.** The motion's number follows the
  brief's name with nothing but the reference between them; a filing that
  names a second motion, request or objection first is briefing on that one.
- **A deadline is distrusted once any briefing schedule on the docket
  moves.** After a later entry that speaks of an extension, a stipulation, a
  continuance or a schedule for a brief, whichever motion it cites, neither
  the docket's stated dates nor the local rule opens the motion; the reply
  itself still does. An entry that sets or resets this motion's deadlines
  restores only the deadline it states.
- **A reply deadline that falls before the opposition opens nothing.** It was
  stated for a schedule the opposition did not keep.
- **Entries dated after the day of the reading are not read**, so a reading
  as of a past day sees what the docket showed then.
- **A motion with no opposition the rule can read stays unopened.** The
  opposition may be a cross-motion, which this rule does not read as one, so a
  clerk's default reply date alone opens nothing.
- **A motion the court rules on before its briefing closes opens nothing.**
- **A transferred-from docket opens nothing.** It repeats the entries of the
  docket the case was transferred to, which owns the events.

`fedcourts trial-events` runs the opener and the resolver over the stored
watchlist dockets and prints what each read ([cli.md](cli.md)).

`trial-preliminary-injunction` opens earlier, when the **opposition** is on
the docket, or its response deadline has passed with none: the date the
docket states, or the local rule's where the docket states none, no
schedule has moved and the district's row names this motion, which no row
does. These motions are heard on a compressed schedule, and a
court often rules without waiting for a reply or allowing one, so a rule that
waited for the reply would open many of them after their ruling or never.

**A motion already open when the stage registers.** A motion that these rules
would have opened before the registration, and that the court has not ruled
on, opens on the day its moment is switched on: its outcome does not exist yet,
so the forecast is a forward one like any other. A motion the court has
already ruled on opens nothing.

`trial-judgment` opens with the slice: a listed case's final disposition is
forecast once, when the case enters the slice, and again at no later point in
the first registration. The event is written by the first pass that reads the
case's own docket with the moment switched on, opens that day, and is written
only while the docket shows no final disposition: a case already closed, or
whose closing the resolver cannot read, gets none. A later re-forecast (after the dismissal ruling, say)
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

The resolver is `pipeline/trial_resolver.py` (rule `trial-resolver-v3`). It is
deterministic, runs no agent, and is built to miss rather than misread: a text
it cannot read leaves the event open, or sends it to triage, and never records
a guessed outcome. It reads the four motion moments and the final
disposition.

- **The docket text decides.** The disposing entry is the first court entry
  after the motion (an order, opinion, ruling or minute order, or an order
  adopting a magistrate judge's recommendation; never a party's filing, the
  recommendation itself, or a court of appeals' order or mandate) whose docket
  text rules on the motion. A ruling is the CM/ECF form: a ruling verb standing
  right after the entry's head (`ORDER granting`, `MEMORANDUM OPINION AND
  ORDER denying`, `ORDER ADOPTING 58 REPORT AND RECOMMENDATIONS and granting`,
  `ORDER by Judge Rita F. Lin granting`)
  or opening a later clause after a semicolon, a comma or "and", with the
  motion's entry number directly after it and going straight on to name a
  motion (`ORDER granting 45 Motion to Dismiss`, `denying [45]`, `granting 45
  and 47 Motions`). A verb anywhere else is a reference to a ruling, not one:
  `ORDER granting 70 Motion for Reconsideration of Order granting 45` rules on
  70, `ORDER vacating 60 Order granting 45` rules on nothing about 45, and
  `granting 45 days` rules on nothing. An entry that cites no entry number
  never rules, because a docket can hold several motions of one kind.
- **A ruling that cites the motion after its title is read in three plain
  shapes**, each only in the capitals the court wrote its ruling in: a
  first-person sentence that ends on the citation (`I GRANT Plaintiffs' Motion
  for Summary Judgment on Fair Use (D.I. 672).`); a passive sentence on the
  citation (`Defendant's Motion to Dismiss (Doc. No. 54) is GRANTED.`); and a
  capitalised title with one trailing entry number (`ORDER GRANTING MOTION
  FOR PRELIMINARY INJUNCTION 6 .`). The sentence must stand where a sentence
  starts, and its title must be the movant, one of the stage's four motions,
  and at most what the motion is "on": a request, an objection or a motion
  about the motion is not that title, and neither is one with a limit or an
  alternative in it. The passive shape reads granted, denied, and granted in
  part and denied in part, and no other wording.
- **A ruling on the cited motion in any other shape is triage**, and so is a
  plain one beside anything that could change it: a second ruling in the
  court's capitals that the rule cannot tie to another motion, a limiting
  word after the ruling ("however", "as to", "otherwise"), a text that states
  a ruling it does not make (a tentative ruling, a recommendation, a
  condition, an order to show cause), two readings that disagree, or leave
  granted or denied in an order that rules on several motions. `ORDER ON 166
  215 CROSS MOTIONS` is triage too: it names the motions and leaves the
  ruling to the order. Triage here stops the reading at that entry, so an
  order about the motion written in one of these shapes (a request for
  argument on it that "is DENIED") holds the event for the maintainer even
  where a later entry rules on it plainly.
- **Anything that could limit the ruling is triage.** The ruling's run goes
  from the motion's number to the next ruling verb, across sentences, and
  stops at the clerk's trailer ("Signed by Judge ..."); the rest of the text
  up to the trailer is read for limits too, since one on this motion can
  follow another motion's ruling. A verb that carries
  its own qualifier reads as it says (`denying as moot` reads mooted,
  `granting in part and denying in part` reads granted in part). Otherwise
  the run goes to triage when it holds a limit (`moot`, `in part`, `partial`,
  `as to`, `only`, `except`, `but`, `to the extent`, `insofar`, `with respect
  to`), other relief (`or`, `alternative`, a stay, a transfer, arbitration, a
  remand, a severance), a claim or count that proceeds, survives, remains or
  is not dismissed, a second ruling word (`denied` after `granting`,
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
  judge's dated signature line ("Signed by Judge X on 2/1/2026"); nothing
  after a signature is read past but the entry date and the initials. Anything else
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
civil-docket rate describes a different population. The first registration
therefore states two published figures as **references** and runs the other
three moments with none:

| Moment | Published reference | Source and population |
| --- | --- | --- |
| `trial-dismissal` | granted 46%, granted in part 29%, denied 25%; of the orders that granted anything, 47% gave leave to amend at least some claims | Cecil, Cort, Williams and Bataillon, *Motions to Dismiss for Failure to State a Claim After Iqbal* (Federal Judicial Center, March 2011), Table 4 and note 26: 1,221 orders on Rule 12(b)(6) motions in 23 districts in 2010, prisoner and pro se cases excluded |
| `trial-summary-judgment` | granted 48%, granted in part 15%, denied 36% | Cecil and Cort, *Report on Summary Judgment Practice Across Districts with Variations in Local Rules* (Federal Judicial Center, August 13, 2008), Table 3: the 18,831 motions granted or denied in civil cases terminated in fiscal year 2006 |
| `trial-class` | none | The Center's class-action study holds 36 contested certification motions, from diversity cases filed before 2005 |
| `trial-preliminary-injunction` | none | No published grant rate for contested motions was found |
| `trial-judgment` | none | The federal courts' tables report how cases end, not which side prevailed |

A reference is context beside a forecast and nothing more. It counts orders
that ruled, so it says nothing of a motion withdrawn or mooted, and it
describes general civil litigation in 2006 and 2010. **No
skill-over-base-rate figure is reported for the slice** from it: such a
figure waits until the slice's own resolved events can supply a rate.

## How the stage registers

The registration is a sequence, and only its last step moves a process digest
([process-version.md](process-version.md)). Before that step a moment is
declared and switched off, the pattern the Court's later moments followed.
All five trial moments are past it: the step registered the slice's label and
actors and switched each moment on from `TRIAL_SWITCH_ON`.

**The first registration is the trial stage alone.** The appeal stage
([appeal-stage.md](appeal-stage.md)) registers after it, under the same slice.

**Events.** A motion event is `evt-motion-trial-<motion>-<entry number>`:
kind `motion`, the filing that opened it, and a label made of the moment's
motion word (`dismissal`, `class`, `summary-judgment`,
`preliminary-injunction`) and the number of the docket entry that filed the
motion, so `evt-motion-trial-dismissal-45` is the motion to dismiss at entry
45. The case's final disposition is the one event `evt-order-trial-judgment`.
The stage keeps a table of its own beside the Court's declared moments, with
a row per moment: a motion moment's row names a **family** of ids, one per
motion, where a Court row names one event. The two are separate because the
Court's table orders one question asked at several moments, and a null moment
there reads as the first; the trial stage's moments are five different
questions and none is first. Only the trial mint seam writes an id on the
`trial-` label: the entry-pinned extractor prefixes `re-` to a subject that
would begin with it, and `validate` fails an event on the label that is not a
declared trial event. The record, not the id, carries the stage and the
moment, as everywhere else.

**Outcomes.** The outcome record carries three fields no other stage may carry:
the motion's ruling (granted, granted in part, denied, withdrawn, mooted),
leave to amend on a dismissal granted in whole or in part (with leave, without
leave, mixed, unstated), and the final disposition (judgment for plaintiff,
for defendant, mixed, no merits decision). Each cites the entry the resolver
read, in the record's `source`. The disposition label the Court's stages
share has no member for any of these, so a trial outcome records it as
`other`, as a merits outcome does, and the stage's binary is its own: 1 where
a motion was granted in whole or in part, and 1 on the judgment event where
judgment was for the plaintiff or mixed. A trial outcome carries exactly one
result and no field of the Court's stages, and `validate` fails a trial field
on any other event.

**Claims.** The stage asks a different question at its moments, so it
declares a claim set per question
([outcome-decomposition.md](outcome-decomposition.md), *The trial sets*):

- `trial-motion-v1`, on a class, summary-judgment or preliminary-injunction
  motion: the headline claim `trial-ruling-granted`, that the motion is
  **granted in whole or in part**, and the distribution claim `trial-ruling`,
  which spreads the forecast over the five rulings. The headline resolves on
  every resolved event, a withdrawn or mooted motion included, since nothing
  is voided.
- `trial-dismissal-v1`, on a motion to dismiss: the same two, and the
  distribution claim `trial-leave` over leave to amend's four values. It
  resolves only where the motion was granted in whole or in part, and is
  masked otherwise.
- `trial-judgment-v1`, on the final disposition: the headline claim
  `trial-judgment-for-plaintiff`, a **judgment for the plaintiff or a mixed
  judgment**, and the distribution claim `trial-judgment` over the four
  dispositions.

A distribution's mass on the headline's side is the headline probability
stated again, and a forecast whose two numbers disagree states no
distribution. No claim has a baseline, so none is scored under the claim
rule: the headline is resolved and reported, and the distributions are
collected and resolved. A forecast is **correct** where its side of the
headline binary is the side the outcome fell on, the same event its Brier
score reads.

There is no vote claim and no authorship claim: one judge decides, and is
known. The decision model's aggregation rules are the Court's and declare
nothing for this stage ([decision-model.md](decision-model.md)).

**Opening and resolving.** The watchlist refresh opens and resolves events in
the pass that stores the dockets (`pipeline/trial_events.py`): after the
dockets are refreshed, the opener and the resolver read every listed district
docket as stored, a newly briefed motion's event is written, and a ruling the
resolver reads closes its event with the outcome. Each declared moment
carries the day it was switched on. The pass writes no event of a moment that
has none and reports what it would open; a motion event it writes opens on
the day its briefing closed, or on the day the moment was switched on where
that is later, and the final-disposition event opens on the day the pass
first writes it. A motion the court ruled on before the pass first read it is never
written, and a member docket opens no motion while its lead docket is not
stored. Nor is an event written while an entry may already decide it, by the
net a forward cell on it would be refused on (*The docket a cell reads*,
below): the resolver passes over a ruling it cannot read exactly, such as one
stated in a hearing's minute entry, and an event opened past such an entry
would carry a decided motion as open. That holds for a motion and for the
final disposition alike, and only for an event not yet written: one the pass
already wrote stays open until the resolver or an adjudication closes it. The
pass lists each event it held that way, with the entry weighed, in the
refresh's report. A reading the resolver sends to triage writes no outcome: the event
stays open, and the pass lists it, with the reason and the entries weighed,
in the refresh's report and its log. So does a result dated before its event
opened or read from an undated entry, and a stored motion event the opener no
longer reads. A maintainer
settles a triaged event by a pull request that records the result, the entry
it rests on and that entry's date in the committed adjudication list
(`config/trial-adjudications.yaml`), which the pass reads ahead of the
resolver's own rule for an event it wrote and has not closed. An outcome's
`source` names the docket entry it rests on, and says so where the entry was
adjudicated.

**Scope.** With the slice switched on, the predict and evaluate queues admit
the slice's dockets beside the Court's, and the fan-out admits a trial event
that is open, switched on and in the slice. A lower-court docket's stage-less
baseline event is not forecast. The fan-out's half is built
(`store.forecastable_event_ids`): a docket an enabled slice names is forecast
on the events of a trial moment switched on by that day and on nothing else,
whether the request names the event or leaves it to the corpus, and no docket
outside a slice is asked for a trial event. The queues' half is built too
(`pipeline/slice_backlog.py`): beside the Court's backlog, and outside its
per-cycle case cap, a scheduled predict round is owed every enabled slice's
open, switched-on trial event that some predictor of the slice has not
forecast, and a scheduled evaluate round every resolved trial event of the
slice that holds a forecast and lacks some judge of the slice. A forecast is
owed only where provisioning would mint it: a docket last read longer ago
than the backlog's staleness bound is held until the refresh reads it again,
and an event the stored docket may already decide is not owed, because that
refusal records nothing and the cell would be minted again every round. A
cell that has failed the per-cell attempt cap is not owed again, and a docket
out of the predict scope is owed nothing. The slices' cells share the run's
cell cap with the Court's, which admits whole cases in case-id order, so a
round over that cap keeps a district docket ahead of the Court's. A slice
event that resolves with no forecast is reported by no monitor: the
missed-forecast read is the Court's. With no slice enabled, no moment switched
on, or no actor of the slice, nothing is owed.

**The docket a cell reads.** The refresh stamps the day it last read each
docket even where nothing changed, and a district docket is fresh for a cell
when that stamp is inside the bound the predict job enforces, since an
unchanged docket stores no new snapshot. The Court's pre-mint poll has no
counterpart: the event is opened by the same pass that just read the docket.
A cell's record carries the docket, the motion's briefing, the judge, and the
listed case's related dockets; none of the Court's fields (the term, the
salience band, the cert anchor) is written for it.

The last three are one file, `record/trial.json`
(`pipeline/trial_record.py`), written for a forward cell and read off the
cell's own snapshot and the watchlist. A replay cell gets none, since the
watchlist is undated and a docket it lists can postdate the cell's cutoff. The
judge is the one the snapshot's header names as assigned, with the magistrate
judge it names as referred to. The briefing is the opener's reading of the
event's motion on that snapshot: the entry that filed it, the first
opposition and the first reply after it, each by entry number and filing
date, and the day and basis the opener reads the event as opening on, read
as of the day the cell is provisioned, as the pass that opened the event read
it: a deadline counts as passed over the days since the snapshot. It is
a pointer into the docket: a filing's own text is in the snapshot, on its
entry's document, where the RECAP archive holds it, and no separate copy is
staged. A cell that wants a brief the snapshot lacks retrieves it under its
mode's rule. The
judgment event names no motion and has no briefing, and neither has a motion
the opener does not read on the snapshot. The related dockets are the listed
case's other dockets (its appeal, the docket it was transferred from, the
panel's docket, its member and companion dockets), each by court, docket
number and relation, with the listed case's own docket among them for a cell
placed on a member or companion docket. None of their snapshots is staged.

The gates are built (`provision-snapshot`). A forward cell on a trial event is
refused when the docket was last read longer ago than the bound, when the
record already holds the event's outcome or the corpus records the docket
decided, or when the trial resolver reads the snapshot as ruling on the
event's motion, as finally disposing of the action for the judgment event, or
as moving on either in a form it would send to triage. The resolver is built
to miss a ruling rather than misread one, so a cell is held to a wider net as
well, whose bias is the opposite: a pending motion it refuses costs one
forecast, and a ruling it misses hands a forecast its answer
(`trial_resolver.motion_disposal_signal`, `action_over_signal`). A motion's
cell is refused when the snapshot lacks the motion's own entry; when an entry
after the motion may show the action over (a closure, a judgment, or the
court's or the clerk's notation that the case is closed, terminated,
dismissed, remanded or transferred out, unless stated as a condition); when a
party withdraws the motion or voluntarily dismisses; for a motion to dismiss,
when an amended complaint follows it; for a motion for a preliminary
injunction, when one is entered; when a magistrate judge's report is adopted,
on whatever motion; and when a later entry that is not a party's filing may
rule on it. Such an entry rules on the motion's number directly, alone, in a
list ("[45] and [49] are DENIED") or joined to a ruling on a neighbouring
entry ("granting 58 and 45"); or carries a ruling word standing by the
motion's number, by its kind or the relief it asks for, or, on an entry that
cites no other entry, by "the motion" where it is not named as another kind,
with nothing procedural (an extension, a hearing, sealing, discovery,
counsel) and no condition between the two, so an order that denies the motion
and sets a conference is a sign; or is the court's bare order on the motion;
or is an opinion, a decision or findings of fact on an entry that cites no
other entry. A ruling is not read as the motion's where a condition leads
into it (an order to show cause, a notice that failure to respond may result
in the motion being granted), where the motion's name hangs from something
procedural ("argument on the motion to dismiss is denied"), where its
sentence ended before the motion was named, or where it is the recommendation
an order of referral asks for. A number counts as another entry only where it
is cited as one, not as a date, a courtroom or a case number. A ruling the
entry places on another numbered entry is set aside first, and the court's
standing or scheduling order is never a sign. The judgment event's cell is
refused when any entry may show the action over, unless the notation is
negated, conditional, or made of one party alone; an entry from before a
transfer in or a reopening counts, so an action that was closed once and
reopened holds its judgment event, as does one closed administratively. That
net refuses some motions still pending: an order on another party's motion of
the same kind, a ruling on the restraining order a motion for a preliminary
injunction also asked for, and, for a motion to dismiss, the dismissal of a
party on other grounds each read as a sign. Such a motion is not forecast:
the entry that tripped the net stays on the docket, so the hold lasts until
the rule is changed. What it cannot see is the residual: an order whose
docket text says nothing of its ruling ("ORDER (see image)", a sealed order,
"Marginal Order: Denied" on an entry that names no motion), a ruling stated
only by its reasoning ("Counts I and II survive", "Defendant's motion
fails"), a ruling carried only in an attached document's description, what an
answer or a reset deadline implies about a motion, and a ruling entered since
the docket was last read, since nothing polls a district docket
between the refresh's reads and the bound is the whole of that control. The Court's poll
is not run, and the context of any lower-court docket states where the cell
was placed and none of the Court's conditioning fields (the term, the band,
the signals, the cert anchor); the contact-scrub note and the statpack build
are written as for any cell. The briefing, the judge and the related dockets
are written as `record/trial.json` for every trial event's forward cell, and
the slice's predict prompt names the file to a cell.

**What the prompts carry.** The predict prompt
(`.github/prompts/predict-trial.md`) is a district cell's whole contract: the
five questions and their outcomes, that nothing is voided so a forecast
prices withdrawal and mootness in, the record above, the two published
references as context and no base rate, and the claim blocks of *Claims*
above with a worked example. It tells a cell that a filing's text is in the
snapshot where the archive holds it and how to read a snapshot that large,
that it may retrieve the rest and related rulings on a forward cell, that a
replay cell is not provisioned for the stage, and
that an entry or a retrieved order deciding the event already is a
mis-provisioned cell to disclose and not to fold in. The evaluate prompt
(`.github/prompts/evaluate-trial.md`) grades blind as the Court's does: the
judge writes `correct` and the Brier score on the headline binary, which the
stamp recomputes, leaves every base-rate field null, grades the rationale
and the forecast document, and assesses leakage, where a forward prediction
made on or after the day its event resolved is read as mis-provisioned. The
docket text of a ruling is often one line, so the judge may read the court's
own order on the event, in its snapshot or else through CourtListener, to
grade what a forecast said of the ground, and nothing else: no brief, report
or commentary. A claim the
order cannot settle, or an order the archive does not hold, leaves the claim
unresolved. Neither prompt names the other, or the Court's.

**The skill record.** A trial evaluation's Brier score is the harness's, like
the Court's merits and interim ones: the stamp recomputes it from the
committed forecast and outcome and clears the base rate, its basis and the
skill, since the stage registers none.

**Its own process.** The slice's cells are made by predictors and graded by
evaluators registered for the slice, each reading a prompt of the slice's own
that carries the stage's rules, under a label of the slice's own. The fan-out
routes a case to the actors of its population, and that half is built: a
predictor's or an evaluator's registry entry names the population whose
dockets it forecasts or grades (`population`, the Court's unless it names a
slice), the predict and evaluate matrices send a slice's docket to the
slice's actors and every other docket to the Court's, and the Court's
rosters (its backlogs, its coverage and missed-forecast reads, its
back-tests) read the Court's actors alone. An entry that names a population
no code declares is refused when the registry is loaded. Six actors name
the `ai-watchlist` slice, three predictors and three judges, and no other
actor does. So no Supreme Court digest
moves when the slice is switched on, and no Court window holds a slice cell.
The label half is built too: the registry's label rows name their population,
a slice's label is `<slice>-vN` with a counting instant of its own, and
`register-process --population` registers it over the slice's actors alone
(*A prediction slice is its own process* in
[process-version.md](process-version.md)). The slice's label is
`ai-watchlist-v1`.
The freeze-record entry that registers the label states the moments switched
on, the references above, the motions already open that day, and the opener
and resolver rule labels in force.

**What reads the slice.** No published figure, board, update or export reads
the slice's population until one is built for it. The public site reads every
record under `data/cases/`, so the change that first writes a district record
is paired with the site change that says how it is shown.

## Out of scope

Discovery motions, temporary restraining orders, stays pending appeal, jury
verdict detail and damages amounts. An appeal from a listed case is the appeal
stage's ([appeal-stage.md](appeal-stage.md)). The salience gate does not apply:
the slice is the selection.
