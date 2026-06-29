# Prediction reasoning — scotus/1003811, evt-petition-disposition

## The legal question

The event asks for the **disposition** of a petition (`kind: petition`,
`decision_target: disposition`) in *George F. Shafer, as Attorney General of the
State of North Dakota v. Farmers' Grain Company of Embden*, a Supreme Court of
the United States matter (docket number 34). The outcome space is the standard
disposition enum (granted / denied / granted-in-part / dismissed / withdrawn /
other); `granted` is the binary target and `probability` is P(granted).

## What the snapshot actually tells me

I predict only from the provisioned snapshot
(`data/cases/scotus/1003811/record/snapshots/2026-06-29.json`). That snapshot is
a **bare metadata stub**:

- `docket_entries: []` — no filings, no motion text, no order text.
- `date_argued`, `date_filed`, `date_cert_granted`, `date_cert_denied`,
  `date_terminated` are all `null`.
- No assigned judge / panel (`assigned_to`, `panel` empty), no `nature_of_suit`,
  no `cause`, no `jurisdiction_type`.
- The only substantive identifiers are the court (`scotus`), the raw docket
  number (`34`), the case name, and a single linked opinion cluster.

So the snapshot carries **no merits facts** about the petition itself — no
question presented, no procedural posture, no party briefing. There is
essentially nothing case-specific to move the prediction off the prior. Per the
contract I did not follow the linked cluster URL or otherwise fetch new docket
facts, and I did not look up the historical outcome, since the disposition is
exactly the quantity under evaluation.

## How I reach a probability

With no case-specific signal, the only defensible anchor is the **base rate** of
SCOTUS petition dispositions. Petitions placed before the Supreme Court for a
discretionary disposition are denied in the overwhelming majority of cases;
grants are the rare exception. Absent any fact suggesting this petition is
unusual, the conservative call is the modal outcome — **denied** — with a low
P(granted).

I set `probability = 0.07` rather than near zero to leave room for the ambiguity
in this stub record. The very low docket number (`34`) and the entirely absent
cert dates make it unclear whether "petition" here maps onto modern discretionary
certiorari or an older as-of-right appellate posture, in which the Court reached
the merits far more often than the modern cert-grant rate would suggest; that
widens my uncertainty. The petitioner here is a State Attorney General — a
government petitioner, a category that historically fares somewhat better than
the overall pool — but that is a weak, category-level prior, not a snapshot fact,
so I let it nudge rather than drive the estimate. `confidence = 0.15` reflects
that this is a base-rate guess on an information-free snapshot, not a fact-driven
call.

- `granted = 0`
- `predicted_disposition = denied`
- `probability (P granted) = 0.07`
- `confidence = 0.15`
- No per-judge `votes` — the snapshot identifies no panel or authoring judge, so
  any vote breakdown would be invented.

## Data-quality note

This is a known limitation rather than a blocker: the snapshot is a stub with no
docket entries, so the prediction is unavoidably a prior-only estimate. I made
the most conservative reasonable call (modal disposition, low confidence) and
recorded it here rather than guessing at facts not present in the snapshot. The
inputs are well-formed (valid event definition, valid snapshot JSON), just
sparse, so the run was not blocked and no issue comment was necessary.
