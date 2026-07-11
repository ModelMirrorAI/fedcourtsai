# ca1/30929 — evt-petition-disposition (claude-baseline, 20260711T043934Z)

## What this event actually is

The event is pinned to docket entry 124191269 (2020-03-24) in *Ortiz-Romero v.
Gov't Development Bank of PR*, No. 19-2084 (1st Cir.). That entry is not a
party's petition: it is the court's **sua sponte order to show cause** whether
the PROMESA Title III automatic stay applies to the appeal, in light of the
Commonwealth of Puerto Rico's May 3, 2017 Title III petition. The word
"petition" in the entry refers to the *Commonwealth's bankruptcy petition*, so
the keyword extractor classified the entry as a petition event. There is no
grantable request by a party sitting behind this event; I flag that in
`flags.json` and predict what the event will actually be scored against — how
this entry (or, failing an entry-referencing disposing order, the case as a
whole) is eventually resolved and normalized into the
granted/denied/dismissed/other vocabulary.

## The record

From the provisioned snapshot (`data/cases/ca1/30929/record/snapshots/2026-07-11.json`):

- Civil-rights appeal (nature of suit 3440), filing fee paid, appellant Pedro
  Ortiz-Romero. Appellees: Government Development Bank of Puerto Rico (GDB),
  Christian Sobrino Vega, and Guillermo Camba-Casas.
- Originating case: D.P.R. No. 3:18-cv-01993 (Judge García-Gregory), filed
  2018-12-20, judgment entered 2019-09-11; the plaintiff is the appellant, so
  he lost below.
- The appeal was docketed 2019-11-01; only appearances were filed before the
  2020-03-24 show-cause order. Responses were due within fourteen days.

The snapshot ends 2020-03-25. The cell is `forward` mode, but the record is six
years old and CourtListener's copy of the docket has not been updated since
2021 — see the staleness flag. Per the never-retrieve-this-case's-outcome rule
I did **not** look up the docket's post-event entries to see how the show-cause
proceeding or the appeal ended.

## The legal question the show-cause order poses

Whether the automatic stay — 11 U.S.C. §§ 362 and 922, incorporated into
PROMESA Title III by 48 U.S.C. § 2161(a) — reaches this appeal. The structural
facts cut strongly against a stay:

1. **GDB is not a Title III debtor.** The Title III petitioners were the
   Commonwealth and certain instrumentalities (COFINA, ERS, HTA, PREPA, later
   PBA). GDB restructured its debts through PROMESA **Title VI** (its
   qualifying modification closed in November 2018), and Title VI carries no
   § 362 automatic stay. The automatic stay protects debtors; it does not
   extend to non-debtor affiliates absent unusual circumstances.
2. **The suit post-dates the petition.** Section 362(a)(1) stays continuation
   of actions against the debtor that were or could have been commenced before
   the petition; this action was filed in December 2018, a year and a half
   after the Commonwealth's May 2017 petition, so even as to the Commonwealth
   it would fit § 362(a)(1) only if the claims arose pre-petition.
3. **§ 922(a) targets claims against the debtor.** It adds actions against "an
   officer or inhabitant of the debtor" only insofar as they seek to enforce a
   claim *against the Commonwealth*. A civil-rights suit against GDB and two of
   its officers is not on its face such a claim.

The most likely disposition of the show-cause proceeding is therefore an order
concluding the automatic stay does **not** apply (in whole or in principal
part) and letting the appeal proceed — or, in the alternative, a discretionary
pause. Either way, the resulting order reads "show cause discharged" / "appeal
shall proceed" / "appeal stayed," none of which normalizes to `granted`.

## How that maps to the scored target

The pipeline resolves an entry-pinned event either from a later disposing order
that cites this entry, or — via the case-level path — from the docket's
normalized disposition when the appeal terminates with one open event. The
normalizer maps grant-language to `granted`, "dismiss…" to `dismissed`,
"den…" to `denied`, and everything else — including affirmed/reversed merits
judgments and stay orders — to `other`.

- CA1 resolved base rates in the corpus statpack: **other 86.3%, dismissed
  8.0%, denied 5.0%, granted 0.7%**.
- A counseled civil appeal most often ends in a merits judgment (affirmance is
  modal) → `other`. A PROMESA-related pause raises the chance of an eventual
  dismissal (voluntary, settlement, or want of prosecution after a long stay)
  somewhat above the 8% base, but not enough to displace `other`.
- Nothing in this event's plausible resolutions produces grant language, so
  P(granted) sits near the ca1 grant base rate.

## Prediction

- `granted = 0`, `probability = 0.02` — essentially the base-rate chance that
  the eventual disposition text carries grant language.
- `predicted_disposition = other` — the modal outcome under both resolution
  paths (a stay-inapplicable/discharge order, or a merits affirmance).
- `confidence = 0.6` — the direction (not granted) is high-confidence; the
  exact label is less certain because the event's semantics are an extraction
  artifact (see `flags.json`) and the eventual disposition could plausibly be
  recorded as `dismissed` (~25–30% in my estimation) instead of `other`.

## Degradations this run

- The CourtListener MCP server failed on every call with a server-side
  configuration error ("REDIS_URL is not set"), so I could not pull the
  district-court record (the nature of the claims and of the 2019 judgment) or
  pre-2020 PROMESA-stay precedent. The prediction rests on the provisioned
  snapshot, the committed statpack, and general legal knowledge of PROMESA's
  structure.
- `fedcourts query` priors for ca1 returned rows whose attached opinion text is
  mismatched (unrelated nineteenth-century state-court material), so they
  contributed only their disposition labels (`other`), consistent with the
  statpack base rate.
