# Prediction: Dollar Savings Bank v. United States

## Event

The event asks for the disposition of the petition in `scotus/1018831`, `evt-petition-disposition`.

## Snapshot Used

I used `data/cases/scotus/1018831/record/snapshots/2026-07-02.json`.

The snapshot identifies the case as `Dollar Savings Bank v. United States` in the Supreme Court. It contains a CourtListener cluster link, but no docket number, docket entries, filing date, last-filing date, termination date, cert grant or denial date, originating court, question presented, party detail, panel, or docket text.

## Governing Standard

For a Supreme Court petition disposition, a grant is rare and generally requires a reason for discretionary review such as an important federal question, a conflict among lower courts, a strong vehicle, or some other institutional reason for the Court to spend merits-calendar capacity. The snapshot does not supply any such signal. It also does not show the posture clearly enough to distinguish an ordinary certiorari petition from an older or irregular Supreme Court record.

## Corpus Context

I used the local corpus only for aggregate and prior context. For resolved Supreme Court rows in the available corpus, the aggregate disposition split was:

- other: 232 of 296, or 78.4%
- dismissed: 47 of 296, or 15.9%
- denied: 13 of 296, or 4.4%
- granted: 4 of 296, or 1.4%

A small `fedcourts query` sample and topical searches for banking/tax context did not return useful comparable resolved cases for this docket. The case-specific record is therefore much weaker than the aggregate base-rate signal.

## Analysis

The absence of a docket number, lower-court origin, filing date, question presented, docket entries, and cert dates prevents a merits-based grant analysis. The title alone shows a dispute involving the United States and a bank, which could involve federal financial or tax law, but the snapshot does not identify an issue, split, procedural posture, or reason the Supreme Court would grant review.

Given that lack of positive grant indicators, I assign a grant probability close to the corpus base rate: 1.5%. I classify the likely disposition as `other`, not `denied`, because the corpus slice for sparse Supreme Court records is dominated by `other` dispositions and this snapshot resembles a bare historical or irregular docket more than a modern, fully docketed cert petition.

Predicted outcome: not granted.
