# McClane v. Boon — evt-petition-disposition (scotus/103650)

## The legal question

The event asks for the disposition of a Supreme Court petition: will review be
granted (`granted` = 1) or will the petition resolve some other way (denied,
dismissed, other)?

## What the snapshot actually contains

The 2026-07-04 snapshot is a nearly bare docket stub:

- Case name **McClane v. Boon**, SCOTUS, docket id 103650.
- **No docket entries at all**, no docket number, no filing date, no
  termination date, and — decisive for the framing — `date_cert_granted` and
  `date_cert_denied` are both null.
- One linked **opinion cluster** (cluster 87911).
- `date_created` 2014-10-29 with `source` 16, the profile of a docket
  materialized from CourtListener's bulk opinion scrape rather than from a live
  docket feed.

That profile — an opinion cluster attached to a docket with no cert-stage
fields and no entries — is the signature of a **historical SCOTUS case from the
bulk opinion corpus**, almost certainly from the pre-certiorari (pre-1925
mandatory-jurisdiction) era, where cases arrived by writ of error or appeal and
were decided on the merits or dismissed on jurisdictional grounds. A modern
"cert petition granted/denied" framing does not map cleanly onto such a docket;
I flag that separately in `flags.json`.

## Governing standard and calibration

With no petition-stage facts in the snapshot (no questions presented, no lower
court, no procedural posture), the only defensible approach is base-rate
calibration against the corpus population this docket belongs to:

- `fedcourts stats --court scotus` over the corpus's 296 **resolved** SCOTUS
  events — which are overwhelmingly this same population of bulk-scraped,
  opinion-bearing historical dockets — gives: **other 78.4%, dismissed 15.9%,
  denied 4.4%, granted 1.4%**.
- Per-Term cuts (`--group-by term_year`) have no resolved cases in any bucket,
  so there is no sharper Term-level anchor; the snapshot has no dates to place
  the case in a Term anyway.
- `fedcourts query --court scotus` priors confirm the pattern: comparable bare
  opinion-cluster dockets resolve as "other" (merits dispositions such as
  affirmed/reversed map there) or "dismissed" (jurisdictional dismissals),
  almost never as "granted".

## The facts that drive the outcome

1. **The docket carries a published opinion cluster.** The court disposed of
   the case with an opinion, which in this corpus's disposition mapping lands
   on "other" (merits) or "dismissed" (want of jurisdiction) — not on a
   cert-style "granted".
2. **Both cert-date fields are null** despite the case being decided, further
   evidence this is a mandatory-jurisdiction-era case where "grant of review"
   was never an event that could occur.
3. **The resolved-corpus base rate for "granted" is 1.4%.** Nothing in this
   snapshot distinguishes the case upward from that base rate.

## Prediction

- **predicted_disposition: `other`** — the modal outcome (78.4%) for exactly
  this population, and the natural mapping for an opinion-bearing historical
  merits case.
- **granted: 0**, **probability (P(granted)): 0.02** — essentially the corpus
  base rate (1.4%), rounded up slightly for mapping uncertainty in how the
  reconciler will label this outcome.
- **confidence: 0.55** — moderate. The binary call (not granted) is very safe;
  the specific label is less certain because "dismissed" is a live alternative
  at ~16% and the disposition mapping for pre-cert-era cases is itself the
  data-quality question flagged for this event.
- No per-judge votes: the snapshot identifies no panel and no era, so any vote
  list would be invented.
