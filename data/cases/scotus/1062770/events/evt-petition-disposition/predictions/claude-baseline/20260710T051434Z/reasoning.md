# Stone v. Farmers' Loan & Trust Co. — evt-petition-disposition

## Prior-knowledge disclosure (read first)

I recognize this caption from general legal knowledge: *Stone v. Farmers' Loan &
Trust Co.*, one of the Railroad Commission Cases decided by the Waite Court in
1886, a landmark on state regulation of railroad rates ("the power to regulate
is not a power to destroy"). That means I know how the Supreme Court actually
disposed of this case. Per the predictor rules I am disclosing this here and in
`flags.json` (category `other`) so the evaluation can discount this cell. The
prediction below deliberately does **not** use that outcome knowledge: it rests
only on the snapshot, the era-appropriate procedural posture, and corpus base
rates — and, as it happens, those inputs alone fully determine the call I make,
so the same prediction would issue without the recognition.

## The legal question and posture

The event asks for the disposition of the "petition" in this Supreme Court
case. The critical contextual fact is the era: this is an 1880s case. Before
the Judiciary Act of 1891 and especially the Judges' Bill of 1925, the Supreme
Court's appellate docket was dominated by **mandatory** review (appeals and
writs of error), not discretionary certiorari. A case like this one — an appeal
in an equity suit — did not face a cert-stage grant/deny gate at all; the Court
took the case and disposed of it on the merits (affirm / reverse / dismiss for
want of jurisdiction).

The modern grant/deny/dismiss vocabulary of the disposition label therefore
maps poorly onto this case. The corpus reflects exactly that: resolved SCOTUS
cases label overwhelmingly `other` (78.4%), with `dismissed` 15.9%, `denied`
4.4%, and `granted` only 1.4% (see `metrics/statpack.md`). The predict prompt
itself notes that merits-era labels "read mostly `other`."

## Facts from the snapshot

The provisioned snapshot (`record/snapshots/2026-07-10.json`) is nearly empty:
caption (*Stone v. FARMERS'LOAN & TRUST CO.*), court (`scotus`), a linked
opinion cluster (not consulted — retrieving it would reveal the outcome), and
no docket entries, no dates, no docket number, no parties beyond the caption,
no nature-of-suit. There are no case-specific facts to reason from beyond what
the caption itself implies: Farmers' Loan & Trust Co. was a major New York
trust company that routinely appeared as mortgage trustee for railroad
bondholders, consistent with a railroad-finance/regulation dispute of the
period, and "Stone" appearing as petitioner/appellant suggests the state-side
party sought review. I flag the snapshot sparsity in `flags.json`
(`data-quality`).

## Reasoning to the prediction

1. **Era mapping dominates.** For a merits-era mandatory appeal, the realized
   disposition label in this corpus is almost always `other` (affirmed/reversed
   outcomes have no granted/denied bucket to land in). The SCOTUS resolved base
   rate puts `other` at 78.4%.
2. **The runner-up is `dismissed`** (15.9%) — merits-era dockets were sometimes
   dismissed for want of jurisdiction or prosecution. Nothing in the snapshot
   (e.g. a jurisdictional defect on the record) elevates that here.
3. **`granted` is a 1–2% label** for resolved SCOTUS cases and belongs almost
   entirely to the modern discretionary-cert regime, which does not govern this
   case.
4. Corpus retrieval (`fedcourts query`, see `retrieval.md`) surfaced no
   resolved 1880s SCOTUS priors, and the unfiltered SCOTUS priors returned were
   consistent with the base rate: overwhelmingly `other`, a few `dismissed`.

**Prediction:** `predicted_disposition = other`, `granted = 0`,
`probability = 0.02` (P(granted), at the base rate for the label given the
era), `confidence = 0.55` — moderate, because while the era-driven label
mapping is robust, the snapshot supplies essentially no case-specific facts and
the event's grant/deny framing fits this case poorly (also flagged as
`ambiguous-event`).

No per-judge votes are predicted: the snapshot identifies no panel, and given
the prior-knowledge disclosure above, reconstructing the 1886 bench from
memory would only leak outcome-era knowledge into an optional field.
