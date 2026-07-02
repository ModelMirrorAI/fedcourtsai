# scotus/1013192 — Mutual Assurance Soc. v. Watts' — evt-petition-disposition

## The legal question

The event asks for the disposition of a "petition" in this SCOTUS case:
granted, denied, granted-in-part, dismissed, withdrawn, or other.

## What the snapshot actually contains

The snapshot (`record/snapshots/2026-07-01.json`) is nearly bare. The only
substantive facts it carries are:

- Court: `scotus`; case name: *Mutual Assurance Soc. v. Watts'*.
- One linked opinion cluster (CourtListener cluster 85156) — so the Court
  issued an opinion in this case.
- Everything else is empty or null: no docket number, no docket entries, no
  filed/argued/terminated dates, no cert-granted or cert-denied dates, no
  parties beyond the caption, no panel.

## The governing frame (legal context, not case facts)

The caption and the low CourtListener cluster id place this in the early
Marshall-era reporter volumes — this is *Mutual Assurance Society v. Watts'
Executor*, 14 U.S. (1 Wheat.) 279 (1816). In that era the Supreme Court's
appellate jurisdiction over such cases was **mandatory** (writ of error /
appeal under the Judiciary Act of 1789); the discretionary certiorari petition
did not exist until the Evarts Act (1891) and did not become the dominant
route until the Judiciary Act of 1925. A "petition granted/denied" framing is
therefore anachronistic for this case: there was no discretionary petition to
grant or deny. The case was heard and decided on the merits with a full
opinion — which is exactly what the snapshot's opinion-cluster link shows.

This is the pre-1925 mandatory-jurisdiction category the repo's predict scope
normally excludes; this docket appears to have slipped through because its
corpus row is bare (no dates and no docket number for the exclusion predicate
to classify on). Flagged in `flags.json`.

## Base rates (corpus)

`fedcourts stats --court scotus --resolved-only` over the corpus's 296
resolved SCOTUS cases: **other 78.4%**, dismissed 15.9%, denied 4.4%,
**granted 1.4%**. The resolved slice of this corpus is dominated by
merits-era decisions whose dispositions do not map onto the modern
grant/deny vocabulary — they resolve as "other" (affirmed / reversed /
decided on the merits).

## Prediction and calibration

- **predicted_disposition = `other`.** A mandatory-jurisdiction case that
  produced a merits opinion resolves as a merits disposition (here, the 1816
  Court affirmed the judgment below), which the corpus's labeling vocabulary
  records as "other" — also the overwhelming base-rate mode (78.4%) for
  resolved SCOTUS cases of this vintage.
- **granted = 0, probability = 0.02.** P(granted) is anchored on the 1.4%
  corpus base rate, nudged up slightly for label uncertainty in how a
  reconciler might map a heard-on-the-merits pre-cert-era case. There was no
  discretionary petition to be "granted," so a `granted` label is very
  unlikely.
- **confidence = 0.4** — deliberately low. The snapshot carries almost no
  facts, and the residual risk is labeling, not law: if the ground-truth
  `outcome.json` maps "case heard and decided" to `granted`, this prediction
  is wrong on disposition even though the historical account is right.
- **No per-judge votes.** The snapshot has no panel information, and
  predicting a full 1816 Marshall-Court lineup from nothing would be
  invention.
