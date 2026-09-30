# Data sources, terms & PII

The decided position behind the README's *Data & attribution* credit: where the
case data comes from, the terms we operate under, what reaches public git, and how
personal data in court records is handled. For the ingestion mechanics see
[data-pipeline.md](data-pipeline.md); for the security controls see
[SECURITY.md](../SECURITY.md).

## Source and attribution

Case data comes from two upstream providers, through the pipeline's four
ingestion channels (**pull**, **live**, **historical**, **enrich** —
[data-pipeline.md](data-pipeline.md)):

- **[CourtListener](https://www.courtlistener.com/)**, a project of the
  [Free Law Project](https://free.law/): the **REST API** (targeted enrichment —
  the `pull` channel, and the opinion-cluster enrichment that shares its
  budget). Part of the stored court-of-appeals slice comes from a second
  CourtListener channel, the one the credit in [`NOTICE`](../NOTICE) names
  beside the API: the **quarterly bulk-data exports**, normalized through the
  same shared normalizer as the API rows and still carrying a bulk provenance
  the storage projection keys on
  ([data-pipeline.md](data-pipeline.md)). The CourtListener terms below cover
  both channels.
- **supremecourt.gov's per-docket JSON and filed-document PDFs**, served by the
  Court itself — the live SCOTUS channel that owns SCOTUS freshness and loads
  the historical Term set. These are public records with no third-party license
  attached (the CourtListener terms below cover Free Law Project's curation,
  not these records). Design in [live-sources.md](live-sources.md); the
  ingested facts land in the same access-gated corpus under the same
  no-republication posture. Filed documents are stored today as
  pipeline-extracted text; one possible later direction — a direction, not a
  commitment — is landing the historical documents (motions, opinions) on the
  same access-gated S3 store as raw PDFs rather than extracted text only.

A further channel is planned but not yet adopted: Free Law Project's commercial
**database replication** offering, the intended eventual upstream for the
CourtListener roles once funding allows — see *The planned end-state* in
[data-pipeline.md](data-pipeline.md). Adopting it requires reviewing that
agreement's terms alongside the licenses below.

Two vote sources are **registered**, both the Court's own documents. The
first is **the Court's own opinions** (`supremecourt-opinions`), the source of
per-Justice merits votes and authorship — the channel
[decision-model.md](decision-model.md) needs to populate `Outcome.votes` with
the provenance block no docket text supports.
Every signed opinion's syllabus closes with a lineup paragraph ("ALITO, J.,
delivered the opinion of the Court, in which … joined. SOTOMAYOR, J., filed a
dissenting opinion, in which … joined."), and that paragraph names who wrote
what and who joined it.

- **Source and scope.** Fetched pipeline-side from supremecourt.gov: each
  October Term's opinions listing (`/opinions/slipopinion/<YY>`), then the
  opinion PDF each row links — the slip opinion until the preliminary print
  replaces it, then the print. The chosen scope is merits decisions from
  roughly OT16 onward. A row is read only when it is a signed opinion on a
  Term-form docket with a per-opinion PDF: applications (interim rulings) and
  original actions are out of scope, a per curiam is skipped because its
  syllabus prints no lineup and a dissent without a writing is recorded only in
  the opinion's body, and a Term whose listing links into a whole
  preliminary-print or bound volume is skipped until volume pages are read.
  As read on 2026-09-29 (a `fedcourts opinion-lineups` pass over the
  listings), that leaves OT16–OT19 and 15 of OT20's 68 rows unread.
  Cert- and interim-stage acts are the orders source's, below.
- **Terms.** The opinions are works of the federal government in the public
  domain, with no third-party license, and a lineup is a fact about the
  published decision. A vote list read from one therefore redistributes
  nobody's coded values when it lands in public git, which is what separates
  this source from SCDB below. Its registration is the provenance statement
  itself: every record's `vote_provenance` names the source, the documents
  (the opinion PDF's supremecourt.gov URL) and a stamp of each grammar that
  read it, with that grammar's version.
- **Access.** The same public, token-free, budget-free channel as the live
  docket JSON ([live-sources.md](live-sources.md)), through the same client:
  a browser user agent, about one request a second, one retry after a pause,
  and no request that leaves the Court's host — the listing's links and every
  redirect are held to it.
- **Method and credit.** The lineup grammar is a Python implementation of the
  syllabus-lineup grammar documented in `docs/justices.md` of
  [ceRt](https://github.com/baldrige/ceRt) (baldrige/ceRt). It is written
  from that documentation of the Court's printing conventions, and no ceRt
  code or data is used; ceRt publishes no license, so its conventions, which
  describe how the Court prints a lineup, are all this project takes from it.
  Names resolve through the same roster the authorship recital parser uses
  (`pipeline/justices.py`), so one surname spelling serves every vote surface.
- **The bench.** The grammar credits a Justice by silence where the Court's
  convention does, so it reads against the bench that decided the case: the
  Justices in service on the printed decision date, from the seat roster in
  `pipeline/justices.py` (each Justice's oath and end of service as the
  Court's *Members* page prints them; the oath day itself does not seat). A
  Justice who took the oath on or after the printed argument date — the
  latest, for a reargued case — is never credited by the convention: only the
  paragraph can place them, and the syllabus ordinarily says they took no
  part. Where no argument date is printed, everyone sworn in since the July
  before the decision's Term is treated the same way. A paragraph silent
  about such a Justice leaves the lineup incomplete rather than guessing
  either way.
- **Completeness.** A vote list is `complete` only when every participating
  Justice is accounted for, with a Justice who took no part recorded as not
  participating. A paragraph the grammar cannot read yields an incomplete
  lineup with no votes rather than a best-effort one, and a Justice the
  writings do not place leaves the lineup incomplete. The channel yields a
  vote record only from a complete lineup that also passes two cross-checks —
  the listing's author initials name the lead opinion's author, and the
  printed decision date is the listing's — so it never writes a partial list.
- **Writing roles.** Authorship lives in `votes[].writing`. A Justice's
  writings map onto `WritingRole` one to one where a role says them
  faithfully; a writing concurring or dissenting only in part, or two writings
  of different roles, has no single role and records null ("not stated")
  rather than the nearer of two wrong values. A Justice observed to write
  nothing records `none`. Where the syllabus shows every participating
  Justice's writing, the same roles are also stamped in `Outcome.writing_roles`
  (below), so the field means one thing whichever source wrote it.
- **The Granted & Noted cross-check.** Each Term the Court also publishes a
  *Granted & Noted* list (`/orders/<YY>grantednotedlist.pdf`): per argued
  case, the dockets decided together, the decision date, the author of the
  Court's opinion, and every other Justice who wrote, with a code for what
  (`C`, `D`, `C/J`, `C/P`, `D/P`). It is a second, independently prepared
  record of what the lineup says, so the two are compared
  (`pipeline/granted_noted.py`): the decision date, the lead author, and the
  set of separate writers with the kind each wrote. Joins are not compared:
  the list prints none. The list is a check and never a source — nothing it
  says is written — and `fedcourts granted-noted-check` prints a Term's
  disagreements. As read on 2026-09-30 over OT2020–OT2025, 282 of the 286
  complete lineups agree with it; the four that do not are a writer the list
  qualifies to one docket of a consolidated pair, two list errors (a
  mistyped year, a decision dated two days early), and a reargued case whose
  entry mixes the reargument order's dissent with the decision's writers. It also says which
  dockets one opinion decides, which the opinions listing does not: the
  listing prints only the lead docket of a consolidated case.
- **What exists.** The lineup model, the syllabus grammar and the read-only
  fetcher (`pipeline/lineup.py`, `pipeline/syllabus_lineup.py`,
  `pipeline/opinion_lineups.py`), with `fedcourts opinion-lineups` printing
  what the channel would write for a Term ([cli.md](cli.md)); the
  registration in code (`pipeline/vote_sources.py`) that `validate` holds
  every committed vote list to; the Granted & Noted cross-check; and the
  writer, *The vote writer* below.

The second registered source is **the Court's orders**
(`supremecourt-orders`) — the per-Justice acts it publishes at the cert and
interim stages. Its records are banked, never scored: `scores_votes` admits
only merits moments, and vote scoring reads only a record whose provenance
says `complete`, which this source's never does
([decision-model.md](decision-model.md)).

- **Source and scope.** Fetched pipeline-side from supremecourt.gov, from two
  per-Term listings:
  - the order lists and miscellaneous orders (`/orders/ordersofthecourt/<YY>`);
  - the *Opinions Relating to Orders* (`/opinions/relatingtoorders/<YY>`).

  An order list prints one entry per docket, or per group of dockets sharing
  an order. The writings published with it are appended after the list:
  dissents from denial, statements, and a summary disposition's per curiam.
  An order on an application that carries writings usually appears as an
  Opinion Relating to Orders.
- **Terms and access.** The same as the opinions source: public-domain works
  of the federal government, read through the same client (browser user agent,
  about one request a second, one retry, no request off the Court's host).
- **What is read, and by which grammar.** Two grammars over the shared lineup
  model (`pipeline/order_grammars.py`). Each stamps its name and version on
  what it reads.
  - `scotus-order-notations` reads an order's own sentences:
    - a noted vote, "Justice X would grant|deny the petition|application";
    - an unwritten "X dissents from the denial of …";
    - "X took no part in the consideration or decision of this petition",
      recorded as `did-not-participate`.

    A noted vote counts only when it is on the petition or the application,
    whole.
  - `scotus-writing-headers` reads the first sentence of each separate
    writing, such as "JUSTICE ALITO, with whom JUSTICE THOMAS joins,
    dissenting from the denial of certiorari." or "Statement of JUSTICE
    SOTOMAYOR respecting the denial of certiorari." It records the kind,
    author and joiners. It records a vote only where the header names the
    act: a dissent from a denial is `grant`, a dissent from a grant is `deny`,
    and a concurrence in either is that act's side. A statement, a
    concurrence in the judgment, a bare "dissenting", and a joiner of only
    part of a writing record no vote.
  - "The Chief Justice" resolves to the bench's Chief, and every name resolves
    through the roster against the bench in service on the order's date
    (`bench_on`).
- **Refusals.** Any problem empties the docket's vote list. Either grammar
  reports one for:
  - a name the roster does not carry;
  - a Justice off the bench;
  - a Justice read two ways;
  - a header it cannot read at all.

  The notation grammar also reports one for:
  - a noted act on a motion or a petition for rehearing;
  - a vote limited to part of the matter;
  - non-participation in anything but a petition, an application, a case or
    a matter;
  - a writing announced as forthcoming;
  - any sentence shaped like a Justice's act that no rule reads.

  A header whose act is on a motion, a petition for rehearing, or part of the
  matter, or whose writing is mixed ("concurring in part and dissenting in
  part"), is not a problem: the header grammar records the writing with no
  vote.

  The channel never guesses a Justice. Its split adds cross-checks of its
  own, each a problem when it fails:
  - Every writing prints its author in its running head, and the check runs
    both ways within each section: a running head naming a Justice with no
    header read, and a header whose author no running head names.
  - An appended section must carry its document's date, and a document must
    print the date its listing gives.
  - A Justice who took no part must not sign a writing.
  - A document's text must not be cut at the extraction cap.
- **Completeness.** The vote list is always `complete: false`, because a
  Justice who noted nothing is unobserved, not a vote to deny; `validate`
  refuses a record from this source claiming otherwise. Writings differ, as
  [decision-model.md](decision-model.md) says: once an order is final,
  whether each participating Justice wrote is observed. The channel sets
  `writings_complete` for a docket only when all of these hold:
  - it read every document the Court lists for the order's date, each fetched
    and extracted whole;
  - no document read for that date has a problem;
  - the docket has no problem.

  Then every participating Justice who wrote nothing records `none`.
  Otherwise only the authors carry a role. One document read alone never
  sets it. A writing respecting an order is ordinarily published with it but
  can follow it, so the writer reads an order date only once it is seven
  days old: a same-week reading could record as having written nothing a
  Justice who has not written yet.
- **What a record holds.** `votes` carries only the Justices the order names
  — a noted vote, an unwritten dissent, a writing whose header names the act,
  or non-participation — each with its writing role where one is observed.
  `writing_roles` carries every participating Justice's role, `none`
  included, and is present only where writings are complete; it is a
  separate field because a Justice who noted nothing has no vote to hang a
  role on. `vote_provenance` names the source, every document of the date
  that names the docket, one stamp per grammar with its own version, and
  `participating`: the bench the roster seats on the order's date less every
  Justice the order records not taking part.
- **Rehearing and motions.** A noted vote on a petition for rehearing or a
  motion is refused by the grammar. Non-participation is recorded only when
  it attaches to the cert or application act: the writer reads a docket only
  on the date of the order disposing of its petition or application (the
  outcome's `resolved_at`), and holds back a docket whose order text on that
  date mentions a rehearing. It also holds back a docket that shares its
  order or a writing with a docket of the other stage — a cert petition
  grouped in one order-list entry with an application — since a notation on
  the stay would otherwise be read onto the petition.
- **A day's writings stand or fall together.** One problem on any
  document the Court lists for a date leaves every docket on that date
  without writing roles, and a docket whose reading has a problem gets no
  record at all. So coverage is per date, and the largest order lists — the
  ones with the most separate writings — are the likeliest to lose it; a
  figure read off `writing_roles` reports its per-date coverage beside it.
- **Spot check, as read on 2026-09-30.** Recall only: for eight OT2024 order
  dates, every sentence in the day's documents shaped like a notation or a
  writing header — found with a pattern broader than either grammar's — was
  checked to lie in a piece the channel read, recorded there or refused as
  a problem. Seven dates recalled every one. On the eighth (2025-06-06) the
  listing links a preliminary-print volume of orders under the date; the
  channel refuses it as a document problem, so that day has no writing
  roles, and the 26 sentences it held belong to other dates. Precision —
  whether a recorded act is attributed to the right Justice and docket — was
  checked by hand on four dockets only (23-1072, 23-1254, 23-1280, 23-1137),
  all correct; it is not measured.
- **What exists.** The two grammars and the read-only channel
  (`pipeline/order_lineups.py`), with `fedcourts order-notations` printing
  one reading per docket for a date or a single document ([cli.md](cli.md));
  the registration; and the writer, below. The live ingest of new order
  lists — stamping each as it settles rather than by a dispatched backfill —
  is not built.

**The vote writer** (`vote_writer.py`) is how either source reaches
`outcome.json`. It reads the corpus for one column — each case's docket
number, which is how a ledger case is found in the Court's documents — and
writes nothing but committed `outcome.json` files: `votes`,
`vote_provenance` and `writing_roles`. It runs only as two `run-repair`
passes, dry run first ([data-pipeline.md](data-pipeline.md), *Maintenance
passes*):

- `opinion-votes` (`fedcourts stamp-opinion-votes`) stamps merits-stage
  outcomes resolved in OT2020 or later — the Terms whose listing links a PDF
  per opinion. It maps the outcome's docket through the Term's Granted &
  Noted list to every docket decided with it, reads the one opinion the
  listing prints for them, and stamps only a complete record that the Granted
  & Noted list agrees with, onto an outcome resolved on the date the opinion
  is dated.
- `order-votes` (`fedcourts stamp-order-votes`) stamps cert- and
  interim-stage outcomes resolved in OT2024 or OT2025, the two most recent
  complete Terms: both sat the same bench, both grammars were checked against
  real orders of the later one, and every interim outcome in the ledger (as
  of 2026-09-30) is among them. A docket with no noted vote and writings not complete has
  nothing to stamp.

An outcome already carrying the same record is left alone, so a re-run is a
no-op; one carrying a different record is held back unless the dispatch
names `replace-differing`. An apply refuses above its bound, and refuses
outright when a listing or a Granted & Noted list could not be read.

One more channel is planned and not yet adopted, **for historical depth
only**: the **Supreme Court Database** (SCDB) — the standing academic coding
of every Supreme Court decision since the 1946 Term, which would extend the
vote record back past the Terms the opinions source reads. Its terms are why
it is not adopted, and they are
split across two hosts that do not agree. Everything in this section is **as
read on 2026-08-15**, from the hosts named in it; it is a record of a reading,
not a live check, so an adoption decision re-reads both hosts first:

- **The current home states no license at all.**
  [`scdb.la.psu.edu`](https://scdb.la.psu.edu/) is where the data is now
  published, and none of its homepage, *About*, *Documentation*, *Data*,
  current-release, or *Cite Us* pages carries a license, a terms-of-use
  statement, or anything about redistribution. What they carry is a university
  copyright footer — "Copyright ©2026 The Pennsylvania State University" — and
  a citation request.
- **The legacy host carries a badge and no sentence.** `scdb.wustl.edu` still
  resolves and still serves the old site over plain HTTP (it refuses TLS, so it
  is unreachable to any HTTPS-only client). That page carries a live
  `rel="license"` badge linking
  [CC BY-NC 3.0 US](https://creativecommons.org/licenses/by-nc/3.0/us/) —
  Attribution-NonCommercial, with no ShareAlike and no NoDerivatives term. The
  sentence that would have named the license in prose is **HTML-commented out**
  and renders to nobody, so an image link is the whole of the declaration.
- **Neither states terms for the release we would actually import.** A badge on
  the superseded host is not a licence grant for the Penn State-published 2025
  release, and the publishing host says nothing. **Treat the terms as unknown
  rather than permissive**, and note that the more restrictive reading is the
  safe one precisely because the permissive-looking evidence is the stale half.
- **That is the blocker, and NC is why it matters.** Taking the badge at face
  value, the question is not whether this pilot is commercial — unfunded
  research over public records, publishing no paid product, is the easy case —
  but that NC binds downstream reuse of everything derived under it, and this
  pipeline is built as a durable evaluation harness rather than one paper. An
  adoption decision has to answer that for the project's intended future. Since
  the publishing host answers it neither way, adopting this channel means
  **getting the terms in writing from the maintainers first**, not inferring
  them from a commented-out caption on a host the project has moved off.
- **Attribution is specific and versioned.** The project asks to be cited with
  its full author list and the exact release, because the data is corrected and
  extended in place: "Please be sure to include the specific Version Number;
  e.g., 'Version 2024 Release 01' in your citation, as this will indicate the
  particular version of the database being employed at the time of your
  reference." The named authors are Harold J. Spaeth, Lee Epstein, Michael J.
  Nelson, Andrew D. Martin, Jeffrey A. Segal, Theodore J. Ruger, and Sara C.
  Benesh. The current release is **2025 Release 01** (1 September 2025, Terms
  1946–2024), while the *Cite Us* page still prints the 2024 release — one more
  reason adoption pins the release in the ingesting code and copies that exact
  string into [`NOTICE`](../NOTICE) and the README credit rather than
  paraphrasing it.
- **Host and support.** Penn State: "a project of the Initiative on Legal
  Institutions and Democracy in The McCourtney Institute for Democracy … made
  possible with support from Washington University in St. Louis and the
  National Science Foundation."

**The redistribution question, answered rather than inferred.** SCDB-derived
votes would *not* stay in the access-gated corpus the way CourtListener content
does. They would resolve merits events, so they would land in **public git** as
`data/cases/<court_id>/<docket_id>/events/<event_id>/outcome.json` — vote values
plus a `vote_provenance` block naming the release, keyed to case ids and
public-record docket numbers. That is a redistribution of SCDB's *coded values*,
not merely a derived judgment over them, and it is a stronger claim on the
upstream than anything in *What we redistribute* below, where the qp-topic
artifacts republish no source text and prediction reasoning is original
analysis. So this channel is the one place the public surface would carry
another project's dataset, however thinly — which is precisely why the terms
have to be settled before any value is written, and why an import that cannot
cite a license should not run.

**The join, decided.** **Docket number plus Term** is the primary join: the
docket number is the one the Court itself assigned, the Term disambiguates its
reuse across years, and the pair covers the corpus as it stands — SCDB
publishes a docket-organized cut of both its case-centered and justice-centered
files, so the join is against a shipped organization rather than a
reconstruction. The U.S. Reporter citation (`usCite`) join is the more precise
one and is deliberately **not** primary: it reaches only the corpus rows whose
`citations` column is populated — a small minority, since the column fills only
as the opinion-cluster enrichment backlog (*Pull cadence* below) works through
the cert-granted slice, not from anything SCDB controls. It stays a confirmation
path, not the key. Justice names normalize to the **entry-printed surnames** the
authorship parser returns — the roster in `pipeline/justices.py` — rather than
to SCDB's justice-name or numeric justice-id variables,
so a single spelling serves both the docket-derived authorship recital and any
imported vote list. The spelling map lives beside the roster
(`SCDB_JUSTICE_SURNAMES`, the modern-span `justiceName` values verbatim from
the SCDB online codebook, onto the printed surnames;
`normalize_scdb_justice` returns `None` for a spelling it does not carry, so
an import would refuse rather than guess), and the recital parser resolves its
capture case-blind against the map's surnames plus the one compound spelling
the Court's history holds, so the normalization target holds in fact. The map
is many-to-one where surnames repeat across the span (two Jacksons, seven
decades apart — no two same-surname Justices sit in one Term); the
docket-number-plus-Term join above is what disambiguates, never the name.

**The vote-source hold.** No vote reaches public git before its source is
registered here, and the hold is mechanical as well as stated: `validate`'s
`outcome_votes_await_a_registered_source` check refuses any committed outcome
carrying votes without a `vote_provenance` block, or a block naming a source
that is not registered. A registered source's records are held to the shape
its registration states (`pipeline/vote_sources.py`). For the opinions
source: a Supreme Court case, a merits-stage event, a `scotus-syllabus`
grammar stamp with its version, an opinion PDF on the Court's own host. For
the orders source: a Supreme Court case, a cert- or interim-stage event,
stamps only of its two grammars, only order and opinion PDFs on the Court's
own host, and never `complete`. For both: every Justice — in `votes` and in
`writing_roles` — spelled as the roster spells them and seated on the
outcome's decision date by the seat roster; `participating` equal to that
bench less the Justices recorded not taking part; for a record claiming
`complete`, exactly that bench, since that bit is what vote scoring is gated
on; and `writing_roles`, where present, naming exactly the Justices who took
part. A source that has not registered, SCDB included, stays refused; an
SCDB import additionally settles the terms above before it writes any value.

**The Solicitor General's office roster** is reference data for an analytics
annotation, not case data and not a vote source. The counsel annotation
`sg-office-v1` (`pipeline/counsel.py`, read by `fedcourts party-rates
--counsel-rule`) reads a committed, dated roster of the people who signed the
federal government's Supreme Court filings: every Solicitor General and acting
Solicitor General from OT2015 on, the principal deputies seen signing as
counsel of record, and one career deputy. It was retrieved on 2026-09-30 from
the Department of Justice's Office of the Solicitor General pages — the
historical list of Solicitors General (`justice.gov/osg/historical-bios`) and
the biographies it links, plus the current Solicitor General's staff profile.
Those pages give an exact day for three boundaries (Verrilli sworn in
2011-06-09, Francisco sworn in 2017-09-19, Sauer in office from 2025-04-04) and
a year range for the rest. A span that begins or ends at a change of
administration takes the inauguration day; the remaining days — the 2016, 2017
and 2020 acting handovers and the principal deputies' other bounds — come from
the public record of those handovers, and the career deputy's start is the
roster's OT2015 coverage floor, not an appointment; none of these is on an OSG
page. Each span's `source` field in
the module names which kind of date it holds. The roster is part of the rule:
a corrected or extended span is a new rule label, never an edit to
`sg-office-v1`. The pages are works of the United States government, which
carry no copyright, and the committed roster republishes only names and the
dates of public office.

Two layers of rights apply, and they are different:

- **The underlying records are public.** Federal court opinions and docket data are
  public records of the U.S. federal courts — public domain, and the facts within
  them are not copyrightable.
- **CourtListener's own content is licensed CC BY-ND 4.0** (Attribution-NoDerivatives),
  except where indicated — covering Free Law Project's curation and value-adds, not
  the public-domain records themselves.

Attribution is given in the README *Data & attribution* section and the top-level
[`NOTICE`](../NOTICE), and is required wherever CourtListener content is surfaced.

## What we redistribute

The NoDerivatives term is why the **derived corpus is not publicly republished**.
The raw-fact corpus — every docket, snapshot, judge, and case record drawn from
CourtListener — lives in the **access-gated** private S3 estate, its payload-free
index blob and the per-case content store that holds the snapshots and extracted
document text alike, never in public git (see
[data-pipeline.md](data-pipeline.md) → *Storage*). It is an internal
working set, not a public dataset. There is a **second gated location, on the
same terms**: the staging corpus (see *The staging corpus (provisioning
runbook)* in [security.md](security.md)), a lean slice of that same content
copied into its own private bucket pair for integration testing. The NoDerivatives posture travels with the copy — same
access gate, no wider read principal, and nothing published from it — because
what governs is the content, not where it happens to sit.

What does go to **public git** under `data/` is only our **own work product**: the
model-generated predictions, outcomes, and evaluations, keyed by case id, plus the
reasoning text that explains them — and the two qp-topic artifacts
(`docs/qp-topic.md`), the hand-labeled reference set and the accrued per-case
labels: subject-matter judgments keyed by case id and public-record
docket number, republishing no source text — and the plain-language case
summaries (`docs/case-summaries.md`), model-written restatements of a case's
record. Those are written only from records whose snapshot is the Court's own
supremecourt.gov docket JSON and whose documents are supremecourt.gov filings,
so what they restate is public-record Court content outside the CC BY-ND term,
and the prompt asks for a summary in the model's own words rather than
quotation. There is also a **non-git** public
channel that carries corpus-derived text: `run-analytics`' five one-day
GitHub Actions artifacts, which on a public repository any logged-in user can
download for their retention window. What each one
discloses is inventoried once, in *S3 / the private stores* in
[security.md](security.md), and not re-enumerated here; two of the five
carry stored questions-presented text and are argued in `docs/qp-topic.md`.
That text is derived from petition PDFs fetched from supremecourt.gov — public
records, outside the CC BY-ND term above — and that channel is accepted for the
labeling run and, on the same footing, the case-summary lane's staged records
(supremecourt.gov docket JSON and filings only; the lane refuses a
CourtListener REST snapshot), not as a route for corpus content generally. The other
three republish no document text. Prediction reasoning may quote or summarize
public-record docket facts in the course of explaining a prediction, and may
characterize what a provisioned filing argues — a petition, a brief in
opposition, a questions-presented section, either side's brief on the merits or
reply on the merits — on the same public-record footing as the questions-presented text above: those
PDFs are fetched from supremecourt.gov, outside the CC BY-ND term, and the
staged copies are gitignored and never committed. The prompt contract asks a
cell to summarize rather than reproduce, which is what keeps that a
characterization; a brief pasted at length into `reasoning.md` would be
republication of a document by a route the ledger was never meant to open. An
evaluation's `basis` and `evaluation.md` may quote the passage of a majority
opinion a semantic grade rests on — the opinion body is CourtListener's text
extraction of a public-domain federal opinion, outside the CC BY-ND value-add
layer, the staged copy is gitignored and never committed, and `basis` is capped
at 2,000 characters by schema. Both are original
analysis attributing CourtListener as the source, not a republication of their
dataset.

A **results release** adds one more surface: the release dataset, a flat
export of the ledger built from the tagged commit by `fedcourts export` — a
predictions table and a gradings table (CSV and Parquet), the reasoning
documents, a data dictionary, the schemas, and a manifest naming the commit and
each file's checksum — deposited on Zenodo as a dataset record. The command
exists; no release has published a bundle yet. The data files are under
**CC BY 4.0**, a licence that covers only the project's own predictions,
outcomes and evaluations; the schemas are generated from the code and ship
under its BSD 3-Clause licence. It carries **no code**. Everything in it is the
ledger's own work product re-laid as tables, including the caption each event
already carries in public git, plus exactly **one field from the corpus**: the
case's docket number, the identifier the Court itself assigned. That is a
public-record fact outside the CC BY-ND term, and it is the same field the
qp-topic artifacts above already publish beside case ids. Nothing else crosses
from the corpus: no CourtListener value-add field (nature of suit, judges,
panel, cluster citations, summaries), no snapshot, and no document or opinion
text beyond what the ledger's own reasoning and evaluation prose may quote on
the footing above. The data dictionary repeats the attribution in
[`NOTICE`](../NOTICE): most of the case ids the export is keyed on are
CourtListener docket ids (a petition the live channel reached first keeps a
reserved-range id the project mints), and the ledger was built from the corpus
either way.

The big-case board (`metrics/big-cases.json`) publishes the same docket number
on the same footing without reading the corpus at all: it decodes a
reserved-range id, which packs the docket number, and otherwise copies the one
the qp-topic labels artifact already publishes (*Docket numbers* in the board's
section of [metrics/README.md](../metrics/README.md)).

The public surface is therefore our derived judgments over public-domain
facts — not a redistribution of the bulk corpus.

## Pull cadence and the API budget

The automated consumer stays within CourtListener's published API limits by design:

- **The supremecourt.gov channels spend no API budget** — the Court's
  site has no metered API; the client is simply polite (browser user-agent,
  ~1 request/second, backoff on errors).
- **SCDB would spend none either.** It publishes no API — access is bulk file
  download only, including CSV and Stata, offered as case-centered and
  justice-centered cuts (each organized by citation, by docket, or by
  issue/legal provision). So that channel's cost is a release pin and a
  re-download when the release moves, not a request budget, and it competes
  with nothing below.
- **`pull` owns the CourtListener API budget**, throttled in-process
  (`courtlistener/ratelimit.py`) to the ceilings set in the prod environment
  (`FEDCOURTS_COURTLISTENER_RPM` / `_RPH` / `_RPD`, wired from repo variables
  to the held Free Law Project tier described below), with
  per-run caps in [`config/tracking.yaml`](../config/tracking.yaml) well under
  them.
- **Opinion enrichment shares that budget**, through the same client and the
  same configured ceilings; the `enrich-opinions` scope, its per-case request
  count, and the headroom arithmetic are owned by
  [data-pipeline.md](data-pipeline.md) and stated only there. What belongs to
  the terms question is the boundary: opinion coverage at bulk scale is not a
  REST problem, the **database replication** channel named above remains the
  intended route to opinion bodies across the whole corpus, and nothing here is
  a step toward reading them out of the API instead.

The pilot holds a paid Free Law Project **membership tier** — **Tier 4**, at 25
requests a minute, 300 an hour and 1,400 a day, for $1,000 a year. It is the top
published tier, so more throughput now means the replication agreement (or
shifting work to the budget-free supremecourt.gov channels), never a code
change to the governor.

**One account, one credential.** The project holds a single CourtListener
account and a single API credential, surfaced under one name everywhere it is
consumed. The rate limits above are the account's, so they are a property of
the membership tier and cannot be widened by how the pipeline is arranged:
splitting work across additional accounts, or issuing a second credential to
raise effective throughput, is **not an available option** — it would violate
the terms the access rests on, and it is the kind of workaround a
throughput problem invites. The honest paths are the ones named above: the
replication agreement, or shifting work to the budget-free supremecourt.gov
channels.

## PII stance

Federal dockets can carry personal data about parties, counsel, and third parties.
Our position is **minimal collection, gated storage, and a hard floor on sensitive
material**:

- **We ingest only what is already in the public upstream records** — no separate
  collection, enrichment, or de-anonymization, and no redaction beyond what
  CourtListener already applies to the public records. Narrowing on privacy
  grounds happens one step later instead, on the copy staged for a cell
  (below), so the stored record stays the record as ingested.
- **Raw facts stay access-gated.** The corpus that holds the full docket detail
  lives in the private S3 estate — the snapshot payloads in its per-case content
  store, the scannable index beside them — not public git. The only PII that can
  reach public git is whatever a piece of reasoning quotes from a public docket
  while explaining a prediction.
- **A filing made in person is scrubbed before a cell reads it.** Where the
  provisioned snapshot serves a counsel block on either party side — petitioner
  or respondent — naming nobody but the party to write to — no attorney, the
  party as their own, or a prisoner register number — or where an amicus block
  on the `Other` list reads the same way on the first two arms, the
  filed-document text staged under a cell's `record/documents/` has its
  contact-detail shapes — emails, telephone numbers, post-office boxes, street
  addresses — and the contact values on every block of each such party side replaced
  by a fixed placeholder, and the cell's manifest records that it was, and by
  which passes ([live-sources.md](live-sources.md)). The question is asked of a
  **served** block: a payload carrying no counsel on a side is unknown rather
  than unrepresented on that side, and a respondent who has not appeared has no
  block to read, so a docket awaiting its opposition is not scrubbed on that
  account. The `Other` list — amici and other non-party filers — is read on
  the first two arms (no attorney, or the amicus as its own); the
  register-number arm is not asked there, because `PrisonerId` on that list
  holds free text rather than a register number, and only a qualifying
  amicus's own values key the value pass. Where the `Other` list is the only
  list read so, the staged text gets that value pass alone — no shape pass — since
  what is staged there is counsel's filings; a self-represented non-amicus
  `Other` filer whose own opposition is staged gets the value pass alone too.
  A self-filing amicus whose served
  name carries a title or joinder the attorney field lacks is not read as
  self-represented and stays as served.
  This is the one narrowing applied on privacy grounds, and it applies to the
  **staged copies** alone: the source PDF and the corpus row are untouched. On
  the same docket the snapshot staged beside the documents has each
  self-represented block's `Address`, `City`, `Zip`, `Phone`,
  `Email` and `Title` values replaced by the same placeholder and a party's prisoner register
  number by a fixed marker that keeps the number's presence (a populated
  `PrisonerId` on a qualifying amicus block, which holds no register number,
  takes the contact placeholder instead); the party name,
  the attorney field and `State` stay, and every other block — a represented
  party's counsel, a represented amicus — is as served. The
  filing
  is public, so the concern is re-publication and aggregation rather than
  disclosure — a self-represented filer's home address reaching the public
  ledger beside whatever else their petition says about them. It narrows the
  default path rather than sealing the material: a cell holding retrieval rights
  can reach the same public PDF upstream, and what the scrub removes is the
  detail that would otherwise arrive unasked-for in the cell's own record.
- **Sealed, privileged, or otherwise sensitive material is never fed into the
  pipeline** — asserted in [SECURITY.md](../SECURITY.md) and restated here. The
  scope is public-record federal appellate and Supreme Court dockets only.
- **A vote record raises no PII question.** The only people named in a vote
  list, whether read from an opinion's lineup or from SCDB, are the Justices,
  acting as public officials in a published
  decision; nothing about who they are is collected, and the values are their
  official acts rather than personal data.

This is a research project over public court records, not a people-search service;
the design deliberately keeps the bulk personal data out of the public surface.
