# State attorneys general and AI litigation

The state-AGs dashboard on fedcourts.ai shows how far each state's attorney
general goes in taking AI developers to court, which cases each office is in,
and which states tend to act together. This document defines what it reads and
how each figure is made. The registry is `config/state-ags.yaml`, read and
checked by `src/fedcourtsai/state_ags.py`.

## Why a registry of its own

The AI watchlist (`config/ai-watchlist.yaml`) is federal-only, and the pull
reads only the courts it tracks. State AGs act against AI developers mostly in
state court, through investigations and settlements that never reach a court,
and in multistate letters and amicus briefs. None of that is in the corpus, so
the registry is hand-curated, like the watchlist. Each action cites the AG
office's own announcement; a filed one names its court and docket number, and
an action in a case the watchlist follows names that case.

## The rule

An action is listed when an AI developer, or an AI system's training, outputs
or deployment, is central to it (adapted from the watchlist's rule), and one or more
state AG offices took part. The 50 states and the District of Columbia are
covered. An action is added by a PR that cites the rule, on a dated `added`
line; nothing is added automatically.

Each action has one **kind**, and each kind feeds one **track**:

| Kind | What it is | Track |
| --- | --- | --- |
| `letter` | A signed letter or public comment aimed at AI companies | enforcement |
| `amicus` | An amicus brief in a case against an AI developer | enforcement |
| `investigation` | An announced investigation or civil investigative demand | enforcement |
| `settlement` | A settlement or assurance of voluntary compliance reached without suit | enforcement |
| `suit` | A suit against an AI developer, in any court | enforcement |
| `defense` | Defending a state AI law against a developer's challenge | defense |
| `advocacy` | Advocacy to a legislature or agency, not aimed at a developer | context |

Only the enforcement track raises a tier. A defense is litigation with an AI
developer, but the AG did not bring it, so the page lists it beside the tier
rather than in it. Advocacy, such as a letter to Congress about federal
preemption of state AI law, is listed as context only.

## The roster and transitions

`offices` lists every state and DC, how the office is filled (`elected`, or
appointed by the `governor`, the `legislature` or the state supreme `court`),
and its holders in the order they serve, each with a source and a distinct
start day. The first holder is one who served, and only the last may be
pending: a `successor`, elected or appointed and not yet in
office, with the day they take it; or an `uncalled` race, which names no winner
until a major outlet calls it.

Each action is attributed to the office, and through the roster to the holder
in office on the action's date. The map shades the office. A state whose last
holder is pending carries a transition badge naming the outgoing and incoming
AG and the day the change happens. The tier is always the office's: holder
attribution labels each action with who announced it and never changes the
tier, so an incoming AG inherits the office's standing in the window, and the
badge says the record is their predecessor's.

## The ambition measure: `ag-ai-ambition-v1`

An office's **tier** on a day is the highest rung any action reached for it in
the trailing 730 days (the action's `announced` date after the window opens and
on or before the day). The rungs:

| Tier | Label | Reached by |
| --- | --- | --- |
| 0 | None recorded | nothing on the enforcement track in the window |
| 1 | Signals | a `letter` |
| 2 | Joins | an `amicus` brief, or a multistate investigation, settlement or suit another state leads |
| 3 | Investigates | the office's own `investigation` or `settlement`, alone or as the coalition's lead |
| 4 | Sues | the office's own `suit`, alone or as the coalition's lead |

"Own" means the office acted alone or is the action's `lead`; a multistate
investigation, settlement or suit always names its lead, and a filed action
(`amicus`, `suit`, `defense`) always names its court and docket number. A tier is an
ordinal ranking: tier 4 is more than tier 3, by no stated amount. Counts by
kind are published beside every tier so a reader can see what it rests on.

**Reading rule.** The tier measures what an office has done in public, as its
own announcements record it. It does not measure merit, outcome or intent, and
an investigation the office has not announced is invisible to it. A tier 0
means none recorded, not none taken.

The 730-day window and the rung ladder together define `ag-ai-ambition-v1`. A
change to either is a new method version with a new name, never an edit to
this one, so a published tier always says which definition produced it.

## The coalition figures

The coalition figures read only **multistate** actions, those two or more
offices took part in announced on or before the board's day, across both
tracks and every kind, because co-signing is the signal whatever is signed.
For each pair of offices *i* and *j*:

- **affinity** is the Jaccard index: the multistate actions both took part in,
  over the multistate actions either took part in. It is 0 when neither took
  part in any.
- **participation rate** of *j* is the share of all multistate actions *j* took
  part in.

For a chosen lead office *i*, the **join ranking** orders every other office by
affinity with *i* times its participation rate. It is a ranking from past
co-signing, not a probability that a state will join, and the page says so.
Wherever the join ranking or an affinity is shown, the number of multistate
actions it rests on is shown beside it, because both figures are noisy over a
handful of actions.

A forecast of who signs the next multistate action, pre-registered and scored
like the project's other forecasts, is a later step once the registry holds
enough multistate actions to score it against.

## Large AI data centers

`data_centers` lists each AI data center project of at least 1,000 MW (1 GW)
of stated capacity in a state or DC: its developers, locality, capacity, status
(`announced`, `under-construction`, `operating` or `cancelled`), first
announcement date and source, the developer's or the state's own announcement
where one exists. A campus total counts; a multi-site program's total does not
unless one site reaches the threshold. A state hosting any project that is not
cancelled is marked on the map. The layer is context for reading a state's
AI policy, never part of the tier, and a cancelled project stays on record
unmarked. The threshold is part of the layer's definition: a change to it is a
change to the rule, made in its own PR.

## What the site reads

`fedcourts state-ags` writes `metrics/state-ags.json`, carrying each office's
data-center projects and tier, counts by kind in the window and transition,
every action with each participating office's holder on its date (none before
the first holder on record) and the rung it reaches for them, and the
coalition figures, all computed here; the site renders it and computes
nothing. A pending holder whose start day has passed is flagged overdue, so a
roster that has fallen behind shows on the board rather than silently
attributing actions to the wrong AG. An action that names a `watchlist_case`
the AI watchlist does not list is refused, so every case link the site renders
resolves. The weekly metrics refresh does not run the command yet, and the
roster and actions are not yet filled.
