# Prediction: petition disposition

## Legal question

The event asks for the Supreme Court petition disposition in `Michigan Pub. Util. Comm'n v. Duke`, docket number `283`. The prediction target is whether the petition or equivalent request for Supreme Court review will be granted.

## Snapshot used

I used `data/cases/scotus/1003917/record/snapshots/2026-06-29.json`.

The snapshot identifies a Supreme Court case, `Michigan Pub. Util. Comm'n v. Duke`, with CourtListener docket id `1003917`. It contains no docket entries and no explicit `date_cert_granted` or `date_cert_denied` fields. The important case-specific signal is that the snapshot contains an opinion-cluster reference in `clusters`: `https://www.courtlistener.com/api/rest/v4/clusters/100552/`.

## Governing standard

Supreme Court review is discretionary in the ordinary certiorari posture, and most petitions are denied. A grant normally requires an important federal question, a conflict among lower courts, or another reason making Supreme Court review institutionally warranted. For older Supreme Court matters, the precise procedural vehicle may not be modern certiorari, but the event still asks whether the case was accepted for Supreme Court review rather than left denied at the petition stage.

## Reasoning

The baseline for a Supreme Court petition is denial. Here, however, the snapshot has a strong contrary signal: it links this docket to an opinion cluster. A Supreme Court opinion cluster usually indicates that the case reached a merits disposition, which ordinarily follows a grant or acceptance of review. A denied petition normally would not produce a merits opinion cluster for the docket.

The record is sparse because it lacks docket entries, lower-court details, and explicit certiorari dates. I therefore do not treat the outcome as certain from the snapshot alone. Still, the merits-cluster signal is much stronger than the general denial prior.

I predict that the petition disposition was granted, with `P(granted) = 0.97` and confidence `0.90`. I do not predict per-Justice votes because this event concerns the petition disposition, and the snapshot contains no vote-specific information.
