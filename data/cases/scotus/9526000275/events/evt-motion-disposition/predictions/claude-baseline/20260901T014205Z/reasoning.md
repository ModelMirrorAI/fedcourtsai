# Rationale for the numbers (claude-baseline, 20260901T014205Z)

**P(unqualified grant) = 0.03.**

*Anchor.* The committed statpack's "The interim docket (applications)" section
publishes per-Term resolved substantive counts. Pooling application-Terms
strictly before my own (Term 2026): OT2025 contributes 226 resolved / 17
granted and OT2024 contributes 70 / 14, a pool of 296 resolved substantive
applications — clearing the pre-registered floor of 50 — with a pooled grant
rate of 31/296 ≈ **10.5%**. That is the published baseline I anchored on.
(The prompt's worked example of a pool stuck at 44 predates this pack; I
computed from the section as instructed. The section's caption states the rate
grounds the scored base rate, so I read it as the scored yardstick.)

*Adjustments down, from 10.5% to 3%:*

1. **The ask is an injunction pending appeal, not a stay.** The Court's own
   standard (Ohio Citizens for Responsible Energy; Respect Maine PAC v.
   McKee) demands "significantly higher justification" than a stay and an
   "indisputably clear" right to relief. The pooled baseline is dominated by
   stay applications, which grant more readily.
2. **The target is a state supreme court's resolution of a state-law
   question.** The dispute is whether the Board of State Canvassers properly
   ran its 1,000-signature sample and properly rejected nine rehabilitating
   affidavits — Michigan election administration. The federal claim has to be
   a constitutional gloss on the initiative process, and there is no
   freestanding federal right to a state initiative; the Court very rarely
   displaces a state high court on ballot-certification mechanics.
3. **Timing.** Relief would add a measure to the ballot days before
   Michigan's September 4 settlement deadline — exactly the last-minute
   judicial alteration of election arrangements the Court's Purcell line
   disfavors, and here the applicants ask the Court to *cause* the change.

*Adjustment up, slight:* the applicants' margin story is sympathetic (709,841
signatures against a 446,198 requirement, blocked on a sample falling "a
handful" short after a 2-2 partisan deadlock), counsel (John Bursch) is an
experienced Supreme Court advocate, and several current Justices are on record
favoring stronger citizenship-verification rules. That keeps me off the floor
(~1%) but cannot carry an "indisputably clear" showing on state-law sampling
mechanics. I land at 0.03.

**Ladder claims.** My record's frozen state (context.json): no response
requested, not referred, zero amicus briefs, `band: null` (normal for interim;
I did not derive one and the caption-class-floor fallback does not apply —
it is cert-stage only).

- *response-requested-increment 0.35.* Corpus-wide, 55 of 340 substantive
  applications (~16%, right-censored, not as-at-prediction) ever drew a
  response request. This application is far more salient than the median of
  that cohort and election emergencies commonly get short-fuse response
  requests, but the ~3-day live window and the weakness of the merits showing
  make a summary denial without response a substantial path. Roughly double
  the (censored) population rate.
- *referral-increment 0.55.* 168 of 340 (~49%, same censoring caveat) were
  referred. A statewide-election application skews toward full-Court
  disposition; in-chambers denial remains live. Slightly above the population
  shape.
- *amicus-increment 0.12.* 51 of 340 (~15%) ever showed an amicus brief, over
  full application lifetimes; this docket has ~3 days to disposition, which
  cuts hard against any filing landing, partially offset by how mobilized
  both sides of this issue are.

**Uncertainties / where to discount me.** (1) No filed-document text was
provisioned — `record/documents/` is absent — so my read of the application's
arguments comes from the docket entry title and contemporaneous public
reporting, not the application itself (a fetch of the supremecourt.gov PDF was
refused with HTTP 403). (2) The statpack's escalation-signal counts are
right-censored and not as-at-prediction, so my ladder numbers are shaped
judgment, not conditioned rates — no published baseline exists for the three
increment claims. (3) The pooled 10.5% baseline blends Terms with uneven
parse coverage (OT2024's 70 resolved sit beside 977 unparsed), and the scored
population is selected higher on the escalation ladder than the pooled cohort.
(4) If the Court simply lets September 4 pass without acting, the formal
disposition could be a dismissal or a later routine denial; either resolves
ungranted, which is the side my number is on.

**Mode note.** Forward cell; retrieval was unrestricted. The public reporting
I used (board deadlock, signature counts, the September 3/4 deadlines, the
Michigan Supreme Court's refusal) all predates my snapshot cutoff or describes
the application itself — no disposition of this application exists or was
sought. Flagged as decisive forward signal in `flags.json` for hygiene.
