# Rationale for the numbers

**P(disturbed) = 0.85, judgment = reversed, 6–3.**

**Anchor.** The committed statpack's "The merits docket (granted cases)"
section publishes an `excluded` count, so its rates are quotable. This grant
dates 2026-06-30 → grant Term 2025, so the pool is grant Terms 2015–2024
strictly before mine; the table renders every Term the pack holds and carries
parsed judgments only for 2017–2024, so those eight rows are the pool:
359 disturbed / 515 parsed = **69.7%**, well over the 30-parsed floor. That is
the baseline my Brier skill is scored against.

**Adjustments up (+15 points).**

- *Grant against a lower-court consensus.* Every circuit to face a post-Bruen
  assault-weapons ban had upheld it (CA1, CA2, CA4, CA7, CA9); there is no
  split to resolve, so the grant is hard to read as anything but corrective.
  Grants taken to ratify a unanimous consensus are rare; grants over one
  usually reverse.
- *Telegraphed votes.* At the June 2025 denial in Snope v. Brown (Maryland's
  ban) — pre-snapshot public record, from training knowledge — Thomas dissented
  from denial, Alito would have granted, and Kavanaugh's statement respecting
  denial said the AR-15 question would recur "in the next Term or two" and
  criticized the Fourth Circuit's reasoning. The Court then granted the next
  clean vehicles. Four-plus justices signalling before the grant, on this
  question specifically, sits well above the ordinary granted case.
- *The question as framed.* The limited grant adopts Viramontes's QP, which
  builds the petitioners' frame into the question ("semiautomatic rifles that
  are in common use for lawful purposes"). The BIO's core argument — that
  common use is not dispositive — is exactly the proposition the reformulated
  grant puts at issue.

**Adjustments down / residual uncertainty (why not higher).**

- Roberts and Barrett pulled the Court back from maximalist Bruen readings in
  Rahimi; a majority opinion could still be written narrowly enough to vacate
  and remand rather than reverse (both disturb, so this moves the label, not
  the number), and there is a real if modest path (~10%) to affirmance if both
  defect and one more vote follows.
- Seventeen distributions over five months before the grant reads as a
  contested internal process — consistent with dissents-from-grant or
  vehicle-shopping, and a reminder the Court was not unanimous about taking
  this. I treat it as noise for the merits.
- DIG or equally divided affirmance: no visible vehicle defect, no recusal in
  prospect — ~5% combined.

**What I worked from.** Forward-mode cell at the grant moment: the provisioned
snapshot (docket through 2026-08-16), the cert-stage documents (QP, petition,
BIO — all with extracted text; the 211-page petition is marked truncated, which
mostly costs appendix material), the committed statpack, and open-web retrieval
confirming the consolidation (lead case Viramontes v. Cook County, No. 25-238,
CA7), the limited QP, and the merits calendar (petitioners' brief due
2026-08-28, respondents' 2026-10-21). **No merits briefing exists yet**, so
this is a forecast from the cert-stage record plus public context — the
grant-moment cell's designed condition, not a gap.

**Discounts a reader should apply.** The vote block leans on justice-level
priors from Bruen/Rahimi/the Snope writings rather than case-specific merits
advocacy, which does not exist yet. My Roberts and Barrett votes are the soft
ones. The 0.85 assumes the Court's grant dynamics reveal intent; if the grant
was instead forced by four votes over a reluctant middle, the true number is
nearer 0.7 (the unconditional base rate). The context's salience band ("high")
is a cert construct already spent by the grant and I did not anchor on it, per
the stage rule.

**Corpus retrieval.** A `fedcourts query` citation lookup for priors citing
Bruen/Heller returned no rows — the citation column covers 161 of 590k SCOTUS
rows and matches a case's own cites only — so corpus priors contributed
nothing beyond the statpack; noted in `retrieval.md` and not retried.
