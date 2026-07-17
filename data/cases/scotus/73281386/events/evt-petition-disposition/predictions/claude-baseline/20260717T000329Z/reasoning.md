# U.S. DOGE Service v. U.S. District Court for D.C. (No. 25-1103) — cert disposition

**Prediction: grant (P = 0.70), most likely a plenary grant; a summary
reversal/vacatur is the leading alternative form of grant.**

## The legal question

CREW sued under FOIA claiming the U.S. DOGE Service (USDS) — nominally an
advisory body within the Executive Office of the President — is an "agency"
subject to FOIA because it wields "substantial independent authority" (the
*Soucie*/*Meyer v. Bush* line). The district court ordered discovery into
USDS's structure and authority to resolve that threshold question. The
government sought mandamus; the D.C. Circuit denied it. The Supreme Court
(No. 24A1122, June 6, 2025) then **granted certiorari, vacated, and
remanded**, holding that requests for intra-Executive-Branch USDS
recommendations were "not appropriately tailored," that agency status
"cannot turn on the entity's ability to persuade," and that separation-of-powers
concerns require *Cheney* deference and restraint — and it **stayed discovery
pending any new cert petition**. On remand, CREW withdrew the
recommendations-related requests; the D.C. Circuit granted mandamus as to the
withdrawn requests and otherwise summarily denied it (July 14, 2025; rehearing
denied Dec. 18, 2025). The SG's new petition presents two questions: (1) whether
the D.C. Circuit departed from the Court's instructions and *Cheney*; and
(2) whether broad discovery may ever be ordered against an EOP advisory body to
decide whether FOIA applies at all.

## Signals driving the probability

**For a grant (dominant):**

- **The Court has already intervened once in this exact dispute.** The June 6,
  2025 order was itself a cert grant (GVR form), and the accompanying stay of
  discovery *pending the disposition of a future cert petition* required a
  judgment that there is a "reasonable probability" the Court would grant
  review again — the petition says so, and the stay's existence is the
  strongest single predictor here.
- **The Solicitor General is the petitioner.** SG petitions are granted at
  rates vastly above the ~2–3% baseline for paid petitions (historically well
  over half), and this SG office has had extraordinary success obtaining
  relief from this Court in Executive-Branch litigation in 2025–26.
- **A mandate-compliance narrative.** The petition credibly frames the D.C.
  Circuit's one-paragraph remand disposition as reading the Court's order
  "untenably narrowly" — it never performed a *Cheney* analysis of the
  remaining discovery (internal directives, employee details, classified-data
  "plans," and a deposition of the USDS Administrator). The Court polices
  perceived defiance of its remands, often by summary reversal — which the
  petition expressly invites.
- **Separation-of-powers subject matter.** Discovery against an EOP advisory
  body, including a deposition of its head, sits squarely in *Cheney*
  territory, where the current majority has been consistently protective of
  Executive confidentiality.
- **Related-circuit tension.** Both sides cite *In re Musk* (4th Cir. 2026),
  a parallel DOGE-discovery mandamus fight, so the QP is recurring across
  circuits and administrations.

**Against a grant:**

- **Posture.** This is an unpublished, interlocutory mandamus denial with no
  square circuit split; the BIO leans hard on the abuse-of-discretion standard
  and vehicle problems (the government conceded below that *some* discovery
  can be appropriate, and mandamus requires a clear-and-indisputable right).
- **The order was narrowed.** CREW withdrew every request touching USDS
  "recommendations" — the specific category the Court's 2025 order flagged —
  so the Court could conclude its instructions were substantially satisfied
  and privilege objections can be litigated request-by-request later.
- **Waning practical stakes.** The USDS Temporary Organization expired
  July 4, 2026; Musk has left government; the BIO argues other litigation
  (e.g., *AFL-CIO v. DOL*) has already produced substantial USDS discovery,
  blunting the confidentiality-harm claim.

## Weighing

The base rates alone would say deny: modern paid petitions grant at ~3%, and
even CADC-originating petitions in the corpus run ~12% (denial-reweighted).
But those pools contain almost no cases where the Court has *already* granted
cert once, stayed the challenged order pending a further petition, and is being
asked by the SG to enforce its own prior ruling. The June 2025 stay is close to
a pre-commitment: denying now would dissolve the stay and let the very
discovery the Court twice restrained proceed unexamined. The realistic downside
scenarios — the Court deems the narrowed discovery tolerable, or lets the
dispute wash out as DOGE winds down — are real but secondary. I estimate
P(any grant, including summary reversal or another GVR) at **0.70**.

On disposition form: the Court already tried a summary "narrow it" order and,
in the government's telling, the D.C. Circuit under-read it. That makes a
plenary grant (to settle the *Cheney*-in-FOIA-discovery and EOP "agency"
questions with an opinion) the most likely single outcome, with an outright
summary reversal the main alternative; I label the disposition **granted**.
The schema's `gvr` label (grant in light of an intervening decision or
Munsingwear vacatur) fits less well than a plenary grant or summary reversal
here, so I do not use it, though a second summary vacatur-and-remand would
also fall on the grant side of the binary axis.

Timing: distributed for the September 28, 2026 long conference; a relist or
two before any grant or summary disposition would be typical.

## Big-case score

0.8 — Nationally covered DOGE litigation, a direct separation-of-powers clash
over discovery into the President's advisors, and a QP whose resolution would
shape FOIA's reach into the Executive Office of the President for future
administrations. Not 0.9+ because the vehicle is a discovery-scope mandamus
rather than a final merits ruling on FOIA coverage.

## Inputs used

- Provisioned snapshot `record/snapshots/2026-07-16.json` (docket through the
  July 8, 2026 distribution).
- Provisioned documents: `questions-presented.txt`, `petition.txt` (97 pp.),
  `brief-in-opposition.txt` (44 pp.) — the QP section, the petition's
  introduction/statement/reasons, and the BIO's introduction, statement, and
  reasons-for-denial structure, including its equities arguments.
- Committed `metrics/statpack.md` base rates and two `fedcourts query` corpus
  lookups (see `retrieval.md`).
