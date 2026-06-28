# Prediction: White v. United States

## Event

The event asks for the disposition of the Supreme Court petition in `scotus/1001151`, docket `01-7700`, titled `White v. United States`. I used the provisioned snapshot at `data/cases/scotus/1001151/record/snapshots/2026-06-28.json`.

## Snapshot facts used

The snapshot identifies a Supreme Court docket filed on January 14, 2002, with appeal from the United States Court of Appeals for the Fifth Circuit and originating docket number `01-20053`. The case is captioned `Timothy Dashun White v. United States`. The snapshot contains no docket entries, no certiorari grant date, no certiorari denial date, no argument date, no termination date, no panel, no parties, and no merits issue description.

The corpus event row marks this petition-disposition event as unresolved. Among resolved Supreme Court petition-disposition rows in this corpus, grants are rare: 4 granted, 11 denied, 46 dismissed, and 183 other. Those labels are noisy and incomplete, but they support a very low prior probability for a grant.

## Governing standard

Supreme Court certiorari is discretionary. A petition usually needs a compelling reason, such as a conflict among courts, an important federal question, or a serious departure from accepted judicial practice. The snapshot does not identify any such reason.

## Reasoning

The strongest predictor is the certiorari base rate: most petitions are denied, and the snapshot provides no affirmative signal that this petition is one of the uncommon grants. The docket is a petition against the United States from the Fifth Circuit, apparently tied to a criminal or post-conviction matter, but the snapshot gives no issue, split, government concession, relist history, lower-court reasoning, or other fact that would justify moving materially above the low prior.

I therefore predict denial. I assign `P(granted) = 0.015`: low, but not zero because any Supreme Court petition can present an undisclosed issue not visible in this sparse snapshot. I do not predict individual Justice votes because the snapshot contains no vote information and certiorari votes are generally not docketed in a way that supports judge-specific prediction here.
