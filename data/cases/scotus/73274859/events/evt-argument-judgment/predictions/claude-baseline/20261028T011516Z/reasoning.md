# Reasoning — P(disturbed) = 0.68, judgment `reversed`

## What I read
- `record/snapshots/2026-10-06.json` (the provisioned baseline). Cert was granted
  2026-02-23 after five conference distributions, with an added question on
  statutory and Article III jurisdiction. The SG filed at the cert stage and on the
  merits supporting the petitioners, and argued as amicus. A Clerk's letter of
  2026-09-28 says **Justice Alito will not participate**. Argued 2026-10-05.
- `record/documents/argument-transcript.txt`, read in full. This is the evidence
  this moment adds.
- `record/argument-features.json` (coverage: 233 Justice turns, 232 attributed, 4/4
  segments attributed). I used it only to check where the questioning fell. Every
  Justice except Thomas (a handful of turns either way) spent more turns on the
  petitioner-aligned side, so the counts do not discriminate here. I put no weight
  on them as votes.
- `questions-presented.txt`. The QP is whether federal law precludes state-law
  claims for injuries from the effects of interstate and international
  greenhouse-gas emissions on the global climate.
- **I did not read the merits briefs, the reply, or the US merits amicus brief in
  full.** They are provisioned (`merits-brief-petitioner.txt`,
  `merits-brief-respondent.txt`, `merits-reply-petitioner.txt`,
  `merits-amicus-united-states.txt`). The US brief supports the petitioners, as the
  docket and the SG's argument confirm. The argument rehearsed each side's
  positions fully, so I relied on the transcript for the parties' theories. A
  reader should know the briefs informed this cell only through the argument.

## Anchor
`metrics/statpack.md`, *The merits docket (granted cases)*. That section publishes an
`excluded` column, so it is quotable. The grant date is 2026-02-23, so the grant
Term is OT2025. The pool is grant Terms 2015–2024; the table carries rows only for
2017–2024. Pooled: disturbed 378 of parsed 537 = **70.4%**. Every pooled Term's
`parsed` is close to its `granted` (e.g. 2024: 76/79), so pendency censoring is
minor. 537 is well above the 30-judgment floor. That is the bar I am scored against.

## Adjustments
- **Toward reversal.** The SG supports the petitioners. Kavanaugh was emphatically
  with them on the Milwaukee/*Ouellette*/*AEP* line. Barrett accepted that interstate
  pollution is an enclave of federal law and pressed Russell on why a tort suit
  differs from a Colorado statute capping other States' emissions. The Chief
  Justice asked Russell whether the suit is "an attempt to evade those decisions"
  and raised the prospect of copycat suits in every State. Thomas asked for a
  limiting principle. Kagan floated the Clean Air Act as the "natural and simpler
  route" to the petitioners' result.
- **Away from reversal.**
  - The recusal leaves eight Justices. The petitioners need five, and a 4–4
    affirmance counts as undisturbed.
  - Sotomayor and Jackson look like firm no-votes, on jurisdiction, forfeiture of
    the extraterritoriality argument, and prematurity.
  - Gorsuch's questioning was ambivalent. He got the SG to agree that the issue is
    one of federal common law, but doubted that the Clean Air Act leaves no remedy
    at all.
  - The Chief and Kagan both pushed back on the constitutional theories the
    petitioners led with.
  - The jurisdiction question is real. Thomas opened with it, and Sotomayor and
    Jackson pressed it. *Atlantic Richfield* favors the petitioners, but a dismissal
    for want of jurisdiction would be undisturbed.

Rough per-Justice probabilities of a vote to disturb: Kavanaugh ~0.92, Barrett
~0.8, Roberts ~0.75, Thomas ~0.75, Gorsuch ~0.6, Kagan ~0.4, Sotomayor ~0.1,
Jackson ~0.08. The votes are positively correlated, and the jurisdiction and DIG
exits come on top. Together that puts P(five or more to disturb, with jurisdiction
found) at about two-thirds. I land at **0.68**, essentially the base rate. The
argument signals tilt toward the petitioners, and the eight-member bench and the
jurisdiction question tilt back by about as much.

## Votes and writers
I predict 6–2 with Kagan in the majority, at low confidence (about a coin flip for
Kagan, about 0.6 for Gorsuch). For a reference point I looked at the statpack's
per-Justice table for OT2022–OT2024, which precede the grant Term. The disturb rates
cluster at 59–77% across the bench, so they do not separate Justices usefully; I
used the transcript instead. For authorship I used no committed per-Justice
assignment history beyond general knowledge. Kavanaugh, Roberts and Barrett lead.
The per-curiam share is small and mostly covers an equally divided Court, which
the masking rule would probably exclude anyway.

## Where to discount me
- I did not read the briefs in full.
- I may be over-reading Kagan's Clean Air Act remark.
- I have no outcome knowledge. The case postdates my training, and I did no
  retrieval about it beyond the provisioned record.
