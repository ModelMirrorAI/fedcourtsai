# Kamani v. Stone, No. 25-1285 — cert petition disposition

**Prediction: denied. P(grant, GVR included) ≈ 0.005.**

## The case

Petitioner Moneesha Kamani's dog died shortly after discharge from an emergency
veterinary clinic (AESC) in Poulsbo, Washington. She sued the treating
veterinarian and the clinic for intentional infliction of emotional distress
(outrage) and fraud, resting on video evidence, audit-trail proof of ~30
post-mortem alterations to the dog's medical records, expert testimony, and a
cease-and-desist letter in which the clinic threatened civil liability and
criminal prosecution under a nonexistent Washington criminal-libel statute if
she posted negative reviews. The trial court granted summary judgment for the
defendants on the intentional torts; the Washington Court of Appeals, Division
II, affirmed in an unpublished opinion (Apr. 22, 2025, corrected Aug. 5, 2025);
the Washington Supreme Court denied discretionary review on January 7, 2026.

The petition (filed May 8, 2026, docketed May 14, 2026, paid docket, OT2025 No.
25-1285) presents two questions: (1) whether threats of criminal prosecution
and civil liability made to suppress speech on social media may be "discounted
as a matter of law" notwithstanding the First Amendment and state anti-SLAPP
laws; and (2) whether a court may grant summary judgment by disregarding record
evidence and imposing "novel, unrecognized legal burdens."

## Why this is a near-certain denial

**Both questions are fact-bound error correction.** QP2 is explicitly a
misapplication-of-settled-standards claim — the petition itself argues the
court below departed from *Tolan v. Cotton* and *Anderson v. Liberty Lobby*
rather than that any court disagrees about what those cases require. Under
Rule 10, "the asserted error consists of erroneous factual findings or the
misapplication of a properly stated rule of law" is the paradigm of a
non-certworthy claim. The petition's "intractable split between state and
federal courts" is asserted, not documented: it cites no conflicting holdings,
only the contention that this unpublished decision is out of step with settled
law everywhere.

**QP1 has no state action and no developed split.** The speech-suppression
theory targets a *private* cease-and-desist letter; the First Amendment
question arrives only obliquely, through whether state tort law must treat such
threats as evidence of outrage. The petition identifies no conflict of
authority on that question, and the court below apparently did not pass on the
federal question at all (the petition complains the opinion "failed to address,
analyze, or even acknowledge" the criminal threats) — raising a serious
preservation/adequate-state-ground vehicle problem on top of the substantive
weakness.

**Poor vehicle in every other respect.** The decision below is an unpublished
intermediate state appellate opinion with no precedential force, applying
Washington's summary-judgment rule (CR 56) and Washington tort law — largely
independent state grounds. The state supreme court denied review. There are no
amici, no CVSG, and counsel is a small Ohio animal-law firm rather than
Supreme Court specialists.

**Docket signals are all baseline-or-worse.** The petition was distributed on
July 1, 2026 for the September 28, 2026 conference — the summer "long
conference," where the overwhelming bulk of denials issue. Zero relists so
far (statpack relist-0 bucket: granted 0.8%). No CVSG. The snapshot shows no
brief in opposition on the docket (response was due June 15, 2026), and
distribution without a response — with no call for response — is itself a
denial-side signal: the Court essentially never grants without first calling
for a response.

**No GVR candidate.** No intervening decision of this Court bears on the
questions presented, and nothing suggests mootness, so the GVR path adds
essentially nothing to P(grant).

## Quantitative anchor

From the committed statpack (metrics/statpack.md and statpack.json):

- Term 2025 modern discretionary-cert base rate: denied 95.4%, granted 2.5%,
  dismissed 2.1%.
- Term 2025 **paid** fee class (this petition is paid): grant ≈ 5.4% — the
  starting anchor.
- Relist bucket 0: granted 0.8%; CVSG "none": granted 3.0%.
- State-court originators in the live slice grant rarely (most state-court
  buckets in the "Petitions by originating court" table are 90–100% denied).

Note: the statpack version in this checkout does not carry the "Segment base
rate by salience band" table the prompt describes, so I could not anchor on a
salience-band rate; I anchored on the paid fee-class rate and adjusted from
the signal cuts instead.

Starting from the ~5.4% paid anchor, this petition sits far below the average
paid petition: fact-bound QPs, no documented split, unpublished state
intermediate decision, state-ground/preservation vehicle problems, no BIO/CFR,
zero relists, long-conference distribution, non-specialist counsel. Each of
those moves the estimate toward the relist-0 floor and below it. I put
P(grant) at **0.005** and predict **denied**. Dismissal or withdrawal is
possible but rare (~2%) and there is no settlement signal, so denial is the
modal disposition by a wide margin.

## Stakes (big_case_score = 0.05)

A denial here would be invisible outside the parties; even a grant would
present a relatively narrow question about pre-litigation speech threats as
tort evidence. The anti-SLAPP gap the petition identifies (protections trigger
only once a suit is filed) is a genuine policy question, but this private
pet-death tort case is not the vehicle through which it becomes a major
national controversy.

## Inputs and degradations

- Snapshot: `record/snapshots/2026-07-17.json` (one day old at prediction
  time; mode `forward` per `record/context.json`).
- Provisioned documents: `questions-presented.txt` and the full 40-page
  `petition.txt` (both read; no BIO was provisioned and none appears on the
  docket).
- Corpus: one `fedcourts query` for recent granted SCOTUS priors (confirms
  grants cluster with multiple distributions/CVSG/specialist counsel);
  base rates from the committed statpack.
- The CourtListener MCP server returned HTTP 429 (daily rate limit exhausted)
  on my single confirmatory docket lookup; I proceeded on the provisioned
  inputs per the degradation rule. The lookup was confirmatory only — the
  snapshot is fresh — so the degradation does not materially affect the
  forecast.
