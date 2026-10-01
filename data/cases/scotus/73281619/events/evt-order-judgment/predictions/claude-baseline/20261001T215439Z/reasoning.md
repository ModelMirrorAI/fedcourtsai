# Rationale for the numbers

**P(disturbed) = 0.86; judgment = reversed.** Grant-moment merits cell, forward mode. The snapshot I read is `2026-10-01.json` (dated provenance, cut at 2026-10-02), which ends with the October 1, 2026 order granting certiorari limited to Question 1.

## Baseline

The committed `metrics/statpack.md` merits section publishes an excluded count, so its per-Term disturbed rate is quotable. This case's grant Term is October Term 2026 (grant dated 2026-10-01, taken from the event's `opened_at`, not from the 25- docket number). The ten-Term window is grant Terms 2016 through 2025; the table renders only Terms with a parsed judgment and carries no 2016 row, so the pool is Terms 2017 through 2025.

| Pool | disturbed | parsed | rate |
| --- | --: | --: | --- |
| Grant Terms 2017 to 2025 | 377 | 540 | 69.8% |

Coverage caveat: the 2025 row is 24 parsed of 50 granted and is mostly pendency, so it is the quicker dispositions; the pool clears the 30-judgment floor many times over. This is the bar my skill score is measured against, so every point above it is a deliberate claim.

## Adjustments from the baseline

Upward, and substantially:

- **Who the petitioner is and who lost below.** A religious institution lost on a federal religious-liberty statute in a state high court, and the Court granted. Over the last decade the Court has disturbed the judgment in essentially every argued case where a religious claimant was the petitioner on a free-exercise or RLUIPA/RFRA theory (Holt, Trinity Lutheran, Masterpiece, Espinoza, Fulton, Tanzin, Carson, Kennedy, Ramirez, Groff, Catholic Charities, Mahmoud). The one judgment left standing in that run was an equally divided affirmance after a recusal, not a merits affirmance. This is the strongest single signal and it is a prior about the Court, not about this record.
- **The question the Court chose.** It granted Question 1 only, which is the question with the Court's own precedent behind it: Holt rejected the alternative-means inquiry under a materially identical provision, and the Kentucky court's "mere inconvenience" rationale is the alternative-means inquiry under another name. Declining the Equal Terms question, where the Kentucky court's reasoning was weaker but the record thinner, reads as the Court choosing the clean vehicle for a reversal rather than the broad one.
- **Shape of the opinion below.** I read the Kentucky Supreme Court's opinion through the CourtListener MCP server. It decided the threshold on two factors (a smaller shrine on the church tract; foreknowledge of the ordinance), expressly declined to define "substantial burden" beyond adopting Livingston, and never reached strict scrutiny. A threshold ruling resting on a legal proposition the Court has already rejected in a sibling provision is the shape the Court reverses rather than affirms.
- **Stakes and alignment.** Sixteen cert-stage amicus briefs including twenty States, a repeat Supreme Court advocate as counsel of record, and a response called for before the second distribution. None of this bears on the merits directly, but it marks the case as one the Court took to decide, not to tidy.

Downward, and these are why the number is 0.86 and not 0.92:

- **The record-failure ground.** The BIO's best argument is that petitioner bore the burden of persuasion under § 2000cc-2(b) and offered only conclusory statements about alternatives, so the judgment can be affirmed on failure of proof under any standard. The opinion below says exactly that. Some Justices may find it attractive, and it is the most plausible path to an affirmance (I put affirmance at roughly 0.08).
- **Invited error and the state-ground argument.** Petitioner asked the Kentucky court to adopt Livingston; respondents cite City of Springfield v. Kibbe, where the Court dismissed as improvidently granted on just that posture. The adequate-and-independent-state-ground argument is weak on its own terms (whether RLUIPA's jurisdictional hook is met is federal law, and the state court decided the federal question on its merits), but together they make a DIG a real tail. I put a DIG near 0.04 and an equally divided affirmance below 0.01, so about 0.13 of mass sits on undisturbed outcomes in total.
- **Residual.** A 0.86 leaves room for the Court to see the case as fact-bound in a way I do not.

## Reversed versus vacated

Within the disturbed mass I put reversed at roughly 0.50, vacated at roughly 0.33, and the mixed label near zero (there is one question, not two). Reversal is the modal label because the question presented asks whether an outright prohibition is a substantial burden, and a yes answer resolves the threshold element itself, as in Holt and Ramirez. Vacatur is the alternative if the Court articulates a standard and remands for the Kentucky court to apply it, as in Groff. A reader should treat the label call as a coin that is only modestly weighted.

## Votes

The vote block is banked, not scored, today. My lineup is 8 to 1 with Justice Jackson dissenting on the record-failure ground. I weigh a unanimous judgment at about 0.40, one or two dissents at 0.30, three dissents at 0.20, with the remainder on affirmance. The single-Justice dissent is a hedge between the unanimous mode and the 6 to 3 tail; its expected vote accuracy is about the same as predicting 9 to 0, and I prefer it because the burden-of-proof argument is a genuine fault line. Writing roles beyond author, one concurrence each from Justices Gorsuch and Sotomayor, and a Jackson dissent are left unstated.

## Semantic claims

Both propositions are written to be falsifiable. The ground claim will fail if the Court rests on something other than the statutory definition plus Holt (for example, a canon of construction against the state-law hook, or a pure burden-allocation holding). The breadth claim will fail if the Court writes a fact-bound opinion confined to this grotto, or conversely if it announces a universal definition of "substantial burden" reaching partial restrictions.

## What I worked from, and what I did not

- Provisioned inputs read in full: the questions presented, the petition (51 pages), and the brief in opposition (46 pages), all with text extracted (`empty_text: false`); the snapshot's 28 docket entries and 16 amicus filers; `context.json`.
- No merits briefs are on disk, which is correct for a `moment: grant` cell, so this forecast is made from the cert-stage papers and the docket skeleton, not from merits advocacy.
- Retrieved: the Kentucky Supreme Court opinion below (RLUIPA section and conclusion), via the CourtListener MCP server. The Third Circuit's Anash v. Borough of Kingston opinion, which the BIO flags as a post-petition split development and whose petitioner filed an amicus brief here, had no text available on CourtListener; my account of it rests on the BIO's description. A docket search for the related petition Grand v. City of University Heights (No. 25-965) returned nothing, so I know only that respondents cited it as pending.
- The corpus query (`fedcourts query --court scotus --disposition granted --era 2020s`) returned this case itself and recent granted applications; it offered no doctrinal neighbors and did not move the number.
- The salience band in `context.json` (`elevated`, sal-v4) is a cert construct and I did not anchor on it; the two distributions and the response request are spent cert signals.
- I carry general knowledge of the Court's religious-liberty merits record from training; I know nothing about this case's disposition, which does not yet exist.

## Where to discount me

The upward adjustment from 0.70 to 0.86 is the whole claim, and it rests on a pattern (religious-claimant petitioners win) rather than on a committed cut; the statpack carries no merits rate conditioned on subject matter or on a state-court origin. If that pattern is weaker than I believe, the honest number is closer to 0.78. The reversed-versus-vacated split is the least confident call in the cell.
