# Prediction reasoning — scotus/1001131 / evt-petition-disposition

## The legal question

Will the Supreme Court of the United States grant the petition in *Yokamon
Laneal Hearn v. Texas* (docket No. 01-7534)? The event's `decision_target` is the
**disposition** of a petition (`kind: petition`) before the Court. For a SCOTUS
filing of this posture — a petition for a writ of certiorari seeking review of a
state-court criminal judgment — "granted" means the Court agrees to hear the
case; the overwhelmingly common alternative is denial of review.

## Governing standard

Certiorari is discretionary. Under Supreme Court Rule 10, review "is not a matter
of right, but of judicial discretion," and is granted "only for compelling
reasons" — typically a genuine split among courts of appeals or state courts of
last resort, or an important unsettled question of federal law. Four Justices must
vote to grant (the "rule of four"). The empirical base rate is the dominant prior
here: the Court grants only a low-single-digit percentage of paid petitions and
well under 1% of in forma pauperis (IFP) petitions. A petition by an individual
criminal defendant proceeding against a State, arriving from a state court of
criminal appeals, is almost always an IFP petition and faces the lower of those
rates.

## Facts from the snapshot that drive the outcome

From `record/snapshots/2026-06-28.json`:

- **Court:** `scotus` — Supreme Court of the United States.
- **Caption:** *Yokamon Laneal Hearn v. Texas*; `docket_number` `01-7534`.
- **Posture:** `appeal_from_str` = "Court of Criminal Appeals of Texas"
  (`texcrimapp`), with originating trial-court information present — a state
  criminal matter on petition to the Supreme Court.
- **Filed:** `date_filed` 2002-01-07.
- **Disposition fields are unresolved in the snapshot:** `date_cert_granted`,
  `date_cert_denied`, and `date_terminated` are all `null`; `docket_entries` is
  empty. The event is `resolved: false`. There is therefore no snapshot fact
  signaling that review was granted (e.g., a cert-granted date, argument date, or
  merits-stage activity).

The snapshot contains no signal that would lift this petition above the ordinary
prior — no indication of a circuit/state split, no CVSG, no relist, no merits
briefing. A capital case from a single state court does not, by itself, supply the
"compelling reasons" Rule 10 requires; the Court denies the great majority of
capital certiorari petitions.

## Probability and disposition

Anchoring on the IFP/criminal-petitioner base rate and finding nothing in the
snapshot to move off it, I predict the petition is **denied**.

- `predicted_disposition`: **denied**
- `granted`: **0**
- `probability` (P(granted)): **0.02** — slightly above the bare IFP base rate to
  account for residual uncertainty, but firmly on the "denied" side.
- `confidence`: **0.9** — high, because the discretionary-denial prior is strong
  and the snapshot offers no countervailing grant signal.

## Votes

SCOTUS orders disposing of certiorari petitions ordinarily issue without recorded
per-Justice votes (a grant requires four, but denials and grants are reported as
Court actions, not individual tallies). I therefore record no per-judge votes;
`votes` is empty rather than speculative.

## Limitations

Predicted strictly from the provisioned snapshot, per the contract. I did not
fetch new docket facts. The snapshot's disposition fields are null, so this is a
forward prediction from posture and base rates, not a read of a recorded outcome.
