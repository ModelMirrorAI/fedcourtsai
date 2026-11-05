# Rationale — P(disturbed) = 0.70, judgment "reversed"

## Inputs used
- Snapshot `record/snapshots/2026-10-22.json` (forward mode, date cut 2026-10-22).
  It shows the petition (docketed Jan 2026), about 20 cert-stage amicus briefs,
  a waiver followed by the Court's call for a response, the BIO (May 14), three
  distributions, the grant (June 29, 2026; grant Term OT2025), argument set for
  Dec 7, 2026, petitioners' merits brief (Sep 8), the United States' amicus
  brief (Sep 15) and motion for divided argument, and respondents' merits brief
  (Oct 21, corrected).
- Documents read: `questions-presented.txt`, `merits-brief-respondent.txt`
  (question presented, summary of argument, Part A on affirm-or-DIG),
  `merits-amicus-united-states.txt` (summary, conclusion), and
  `merits-brief-petitioner.txt` (the mootness footnote 13 and the conclusion).
  I only skimmed the petition, BIO and cert reply. The staged respondent brief
  URL is the Oct 30 corrected copy, while the docket entry is dated Oct 21. I
  treated it as the brief whose filing opened this event.
- **The United States' amicus brief supports petitioners.** It asks the Court
  to vacate and remand on its own theory: a State that changes parents' control
  over their child's medical care inflicts a present injury. My forecast
  largely follows the US on the outcome and partly on the ground. I do not
  expect the Court to adopt the US rule at its full breadth.

## Anchor
Statpack "The merits docket (granted cases)" section, which publishes an
`excluded` count, so it is quotable. Grant Term is OT2025 (the grant order is
dated 2026-06-29). Pooling grant Terms 2015–2024 gives the rendered rows
2017–2024 (2015–16 carry no parsed rows): disturbed 375 of 533 parsed, or
**70.4%**. Coverage is near-complete for those Terms (parsed/granted e.g.
76/79 for 2024, 56/56 for 2023). That is above the 30-judgment floor.

## Adjustments
- Upward: the cert history points to a Court that wanted this case. It called
  for a response after Washington waived, relisted, then granted, after three
  Justices flagged the question in Lee v. Poudre. Mirabelli v. Bonta (2026, per
  curiam), cited by both sides, shows a majority receptive to parents' claims
  in this setting. The SG backs petitioners. The case comes from the Ninth
  Circuit, and en banc rehearing was denied over dissents.
- Downward: this Court is strict on standing (Clapper, Murthy, FDA v. AHM,
  TransUnion), and the fact pattern is a textbook speculative chain. Roberts,
  Kavanaugh and Barrett could find a narrow affirmance attractive. There is
  also real DIG risk from mootness and new theories (about 7%), which counts as
  undisturbed.
- On net the factors roughly cancel against the base rate. I stay at 0.70:
  about 0.70 disturbed, 0.07 DIG, 0.23 affirmed.

## Votes
Per-Justice disturb rates, OT2020–OT2024 (Terms strictly before the OT2025
grant Term), are compressed in the 55–77% range for every Justice. For
example, Kavanaugh's disturb rates were 39/51 (OT2024), 31/46, 32/44, 36/49
and 28/39; Thomas's were 32/51, 28/46, 26/44, 32/49 and 22/38. These rates do
not tell the blocs apart here, so the lineup rests on the ideological valence
of parental-rights and gender-identity cases: 6–3. Roberts and Barrett are the
likeliest defectors to an affirmance, and Kagan the likeliest addition to a
narrow reversal.

## Author and separate-writer numbers
These are judgment calls shaded off a roughly uniform 1/9 share. Alito gets
extra weight for Lee v. Poudre, and Barrett for standing (Murthy). Per curiam
gets a small share because an argued case like this is rarely decided
unsigned. Separate writing is high for Jackson, Thomas and Sotomayor.

## Uncertainties
I did not read the full merits briefs or the Ninth Circuit opinion. I do not
know how Mirabelli resolved standing or the merits beyond what the briefs cite.
No argument has happened yet. The corpus query I ran returned granted-petition
rows that were not informative for a merits judgment.
