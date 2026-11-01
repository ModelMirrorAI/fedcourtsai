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
- **supremecourt.gov's per-docket JSON and filed-document PDFs**, and its
  legacy HTML docket pages for the dockets the JSON does not serve, served by the
  Court itself — the live SCOTUS channel that owns SCOTUS freshness and loads
  the historical Term set. These are public records with no third-party license
  attached (the CourtListener terms below cover Free Law Project's curation,
  not these records). Design in [live-sources.md](live-sources.md); the
  ingested facts land in the same access-gated corpus under the same
  no-republication posture. Filed documents are stored today as
  pipeline-extracted text; one possible later direction — a direction, not a
  commitment — is landing the historical documents (motions, opinions) on the
  same access-gated S3 store as raw PDFs rather than extracted text only.
  The same terms cover the Court's **oral argument transcripts**: the per-Term
  transcript list and the transcript PDFs it links, prepared by the Court's
  contract reporter and posted by the Court on its own site, read by the live
  poll's transcript pass and stored as extracted text in the same corpus.

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

The same documents feed **the per-opinion record**, the corpus `opinions`
table ([corpus/README.md](../corpus/README.md)) that `fedcourts
backfill-opinion-record` builds (`pipeline/opinion_record.py`): one row per
opinion in a decided case — its order in the document, kind, author, joiners
and length — for the opinion-authorship and opinion-length figures a Term's
statistics count per opinion rather than per case. It is a historical record,
held corpus-side and read by nothing a predict cell or a registered evaluate
cell sees; a pilot round's evaluate cell is given each decision's writings
(`provision-opinion --writings`). Its
apply runs as run-repair's `opinion-record` pass over OT2020–OT2025, and as a
standing sweep on run-seed's daily window over the current and previous Term,
each fetching in a job that holds no credential
([data-pipeline.md](data-pipeline.md#maintenance-passes)).

- **Source and scope.** Every row of a Term's opinions listing, read through
  the same client: the signed merits opinions, the per curiams (summary
  reversals and argued per curiams alike), and the applications and original
  actions the listing also carries. A row the listing links into a whole
  preliminary-print or bound volume is skipped unfetched, which on the
  Court's listings as read on 2026-10-01 is every row before OT2020 and some
  of OT2020's.
- **Who wrote what.** For a signed decision the syllabus lineup is the record
  of each writing's kind, author, coauthors and joiners: the grammar above,
  unchanged. A partial join is stored with its printed limit as the
  qualifier ("as to Part II-B", "except as to Part III-B"); a join in full
  has none. The record keeps the phrase, not a parsed set of parts. A per
  curiam prints no lineup, so its record comes from the opinion headers
  ("JUSTICE X, with whom JUSTICE Y joins as to Part I, dissenting."), read for
  author, kind and joiners; a per curiam's own joiners are not printed and
  are not recorded.
- **Splitting, and the cross-check.** Each document is split at each
  opinion's header. The slip opinion opens every opinion on a new page under
  the Court's caption and bracketed date; the preliminary print runs them on
  within a page, so there an opinion opens at a body-type line that reads as
  a header. A signed document is recorded only when the split agrees with
  its syllabus: the same number of opinions, in the same order, each header
  naming the same author or authors and a compatible kind, each separate
  writing's header naming the same joiners, and no separate writing's header
  left inside an opinion. A lead's header prints no joiners, so the lead's rest on
  the syllabus alone. Anything else refuses the whole document with the
  reason. Refusals come from a syllabus the grammar cannot read whole (it
  does not read "concurring in part" without "the judgment", or a join
  limited to a footnote, "except as to n. 1") and from a text layer that runs
  words together.
- **Coverage, and what it leaves out.** As read on 2026-10-01, documents
  recorded, refused and skipped per Term: OT2025 70 / 4 / 0 (172 opinions),
  OT2024 63 / 4 / 0 (153), OT2023 54 / 6 / 0 (136), OT2022 50 / 8 / 0 (113),
  OT2021 60 / 6 / 0 (139), OT2020 48 / 5 / 15 (109); OT2017–OT2019 are
  skipped whole (volume-linked). The refusals are not random: their causes
  (a partial concurrence, a join limited to a footnote) concentrate in
  fractured, many-opinion decisions, so a total, an average or a "longest"
  list taken from the table under-represents exactly those. A figure read
  from it states its population and the Term's refusal count beside it.
- **The word count** (rule `scotus-opinion-words`, version 1). An opinion's
  text runs from its header sentence to the next opinion's header or the end
  of the document.
  - **Footnotes are in.** Each opinion's footnotes count toward it, and the
    record also stores their share, about 11% of OT2025's words. Against
    the published OT2025 combined totals below, body text alone runs 10–21%
    short; with footnotes, 1–4% short.
  - **Excluded:** the syllabus and headnote; the caption (court, docket
    number, parties, the writ, the bracketed date); the preliminary print's
    counsel listing, its amicus-brief and "Together with" notes, and its
    closing Reporter's Note; running heads and page numbers; and the print's
    "Page Proof Pending Publication" watermark.
  - **Tokens.** A hyphen ending a line is closed up, so a word broken across
    lines counts once. The text then splits on whitespace and on the em
    dash, and a token counts when it holds at least one letter or digit. So
    a hyphenated compound ("well-settled") and a number range ("404–405") are
    one word each. A citation counts token by token: "19 How. 393" is three
    words, and "§1983" and "§ 1983" are one each, since a bare "§" holds no
    letter or digit. Ellipsis dots and stray punctuation are not words.
  - **Reference marks.** A footnote's own number at the head of the note is
    not a word. A reference mark the text layer separates from its word
    ("… 75. 1 Smith") is dropped where it is the next expected number after
    punctuation; one printed against its word ("realms.2") adds nothing.
  - **Which opinion a footnote belongs to.** In the slip, the opinion on its
    page. In the print, where one page can end one opinion and open the
    next, numbering restarts with each opinion, so a page's notes numbered 1
    go to its opinions by count: to the opened opinions when the previous
    one already has notes; otherwise the ones beyond one per opened opinion
    are the previous opinion's. One case is not told apart: a previous
    opinion whose first note falls on its last page, beside an opened opinion
    with no note on that page. There the note goes to the opened opinion,
    which moves words between the two and leaves the decision's total
    unchanged.
  - **Text layers.** Each format is read in the pypdf mode that extracts it
    cleanly: the slip in layout mode, since its plain mode splits words at
    kerning ("pr esent"), with footnotes below the em-dash rule; the
    preliminary print in plain mode, since its layout mode letter-spaces,
    with footnotes told from body text by their smaller type.
- **The text** (rule `scotus-opinion-text`, version 1). Each read document's
  writings are also stored as text, for grading a merits forecast against
  what the Court wrote: each writing's body from its header sentence on, and
  its footnotes, exactly the lines the word count is taken over, with each
  line's spacing collapsed and its line breaks and line-end hyphens kept; a
  footnote loses its own number, and the text layer's own faults, such as a
  dropped "fi" ligature in the preliminary print, stay in. The text is held to the counts: the word
  rule must count the body (reference marks dropped) and the footnotes to the
  stored words and footnote words, or the document is refused. It is stored
  in the access-gated content store, one object per document, with a pointer
  row in the corpus (`opinion_texts`), and like the rest of the record it is
  read by nothing a predict cell sees.
- **Checked against.** SCOTUSblog's *Final Stat Pack for the 2025-26 Term*
  (updated 2026-07-06; its figures are quoted here, with attribution, for
  comparison only) was compared with a dry run over OT2025, as a check
  only: nothing from it is stored. The dry run recorded 63 of the 66
  decisions the stat pack covers (Pung, Postal Service v. Konan and Barrett
  v. United States were refused; Texas v. New Mexico, which the pack does
  not count, was refused too).
  - Its ten longest combined totals and five longest individual opinions
    all run under the pack's rounded figures, by 1–4% and most within 2%:
    Barbara 59,355 words across 6 opinions against ≈60,400, Thomas's dissent
    there 28,901 against ≈29,400. The direction is the same every time,
    which points to a difference of rule rather than noise.
  - The shortest opinions agree within a few words (Chatrie's 65 against
    ≈60).
  - Per-author averages fall between 4% over and 7% under: Roberts 7,003
    against ≈7,100, Barrett 3,067 against ≈3,300. They are not like for
    like, since the three refusals remove opinions unevenly by author, but
    Barrett wrote nothing in a refused decision, so her gap is not a
    refusal's.
  - Opinion counts by author: Roberts's 6 match; Thomas's 26 and Jackson's
    25 become the pack's 28 and 26 with the refused decisions' opinions
    added back. The pack does not count an opinion concurring in part and
    dissenting in part among dissents: Jackson's 10 dissents are exactly her
    plain dissents here.

  The stat pack does not publish its counting rule, so the residual is
  unexplained.

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
  - Where the extracted text lifts captions' serial numbers out of their
    lines (`25- DOE …`) into a column of bare numbers, the column must fit
    those captions: one serial each, ascending, each between the whole
    captions around it. A column that does not fit, a lifted caption with no
    column, and a column no caption claims are each a problem; the column is
    never read as order text.
  - An entry's order text must contain a letter.
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
`vote_provenance`, `writing_roles` and, on a merits outcome, `merits_author`.
It runs as two `run-repair` passes, dry run first
([data-pipeline.md](data-pipeline.md), *Maintenance passes*), and the orders pass also as a standing sweep on run-seed's daily window, which
stamps each settled order list under a per-window cap and never replaces a
record:

- `opinion-votes` (`fedcourts stamp-opinion-votes`) stamps merits-stage
  outcomes resolved in OT2020 or later — the Terms whose listing links a PDF
  per opinion. It maps the outcome's docket through the Term's Granted &
  Noted list to every docket decided with it, reads the one opinion the
  listing prints for them, and stamps only a complete record that the Granted
  & Noted list agrees with, onto an outcome resolved on the date the opinion
  is dated. Apart from that record it stamps `merits_author`, the author code
  the listing prints on the decision's row (a Justice or `per-curiam`), onto
  every outcome whose row is dated its resolution, signed or per curiam.
- `order-votes` (`fedcourts stamp-order-votes`) stamps cert- and
  interim-stage outcomes resolved from OT2024 through the current October
  Term. OT2024 and OT2025 sat the same bench, both grammars were checked
  against real orders of OT2025, and every interim outcome in the ledger (as
  of 2026-09-30) is among them; the current Term is in reach as soon as it
  opens, so its orders are stamped as they settle. The notation grammar
  refuses rather than guesses: a name off the bench, an object it does not
  read, and any leftover sentence shaped like a Justice's act that no rule
  read are problems, and a docket with a problem is held back, so a new
  phrasing in a new Term shows as a held-back count rather than a wrong
  record. What that guard cannot see is a notation that does not name a
  Justice's act at all, which reads as no notation. A docket with no noted
  vote and writings not complete has nothing to stamp. An outcome's
  documents are those listed for its `resolved_at`, read from that day's
  October Term listing and, for a day in October, the outgoing Term's as
  well, since the Court's listing pages roll over on the first Monday in
  October. Where no document for the date names the docket (and every
  document was read whole), three dispositions are reported apart as having
  no order text by design, a heuristic read off the outcome's disposition: a
  petition dismissed (most are the Clerk's Rule 46 dismissals, entered with
  no order), an application withdrawn, and one its Circuit Justice decided
  alone (not referred to the full Court). The rest of that skip is the
  unexplained part.

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
part. A stamped `merits_author`, which needs no `vote_provenance`, is held to
the same rule: `per-curiam`, or a Justice spelled as the roster spells them and
seated on the outcome's `resolved_at`. A source that has not registered, SCDB
included, stays refused; an SCDB import additionally settles the terms above
before it writes any value.

**The Solicitor General's office roster** is reference data for an analytics
annotation, not case data and not a vote source. The counsel annotation
`sg-office-v1` (`pipeline/counsel.py`, read by `fedcourts party-rates
--counsel-rule` and by `fedcourts executive-success`) reads a committed, dated roster of the people who signed the
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

**The Solicitor General's posted briefs** are a candidate document source,
assessed and not adopted. The question it would answer is narrow: on a docket
the Court has put under Rule 34.6 and Paragraph 9 of its electronic filing
guidelines (`PredictionContext.paper_only_filings`), the Court posts no party
filing, so a cell gets no `documents/`; where the United States is a party,
the Office of the Solicitor General may post its own brief on its site even
though the Court does not.

- **Source and shape.** `justice.gov/osg/supreme-court-briefs` lists the
  Office's filings as a table of Term, docket number, caption, brief type and
  filing date, and each brief has its own page (`justice.gov/osg/brief/<slug>`)
  carrying the docket number and a type such as *Petition Stage Response*
  (the Office's label for a brief in opposition), with the PDF linked from it.
  The docket number is the join to a corpus row, and the types map onto the
  existing kinds in `pipeline/documents.py`: the Office's petition onto
  `petition`, a *Petition Stage Response* onto `brief-in-opposition`. A
  waiver of response posts no brief at all.
- **Terms.** The Department of Justice's legal-policies page states that,
  unless otherwise indicated, information on its sites is in the public domain
  and may be copied and distributed without permission; the stated exceptions
  are third-party photographs and graphics and the Department's seals. A brief
  filed by the United States is a work of the federal government. Fetching,
  storing in the access-gated content store, and staging into a cell are
  therefore permitted on the copyright question, under the same
  no-republication posture as the Court's own filings.
- **One check before the first summary.** The RECAP terms above were read from
  search-engine copies of Free Law Project's RECAP FAQ and the site licence
  notice, because the live CourtListener terms of use and the `free.law` pages
  are not reachable from the project's sessions. Before the first summary is
  published, someone with access reads the live CourtListener terms of use and
  copyright policy for any condition on RECAP documents downloaded through the
  site; a condition found there narrows this rule.

**Model summaries of the AI watchlist's rulings** are an adopted public
surface, not yet built. The AI-cases update will carry, beside an
activity record for an opinion or a ruling, a short plain-language summary of
that ruling, labeled with the model that wrote it, as the case summaries are.
The update renders without it. The question is what such a summary may be
written from, given the two layers of rights below.

- **The ruling is public domain; CourtListener's docket is not.** A district
  court's order or opinion is a work of the federal government. Free Law
  Project's RECAP FAQ states that court-created PACER documents are works of
  the federal government and in the public domain. The copy the pipeline reads
  comes from the RECAP archive through CourtListener, and its text is
  CourtListener's extraction of that public-domain document, the footing the
  opinion bodies below already stand on. The docket around it, as
  CourtListener serves it (the compiled entry list, the normalized caption,
  nature of suit, cause, the judge and party fields, and any CourtListener
  summary), is Free Law Project's curation, under CC BY-ND.
- **What NoDerivatives means for a summary.** CC BY-ND lets the licensed
  material be shared verbatim with attribution and does not let an adaptation
  of it be shared. A model summary written from CourtListener's docket record
  is a restatement of that record, and publishing it would publish an
  adaptation the licence does not grant. Whether a short factual summary is an
  adaptation in copyright terms is arguable, since facts are not protected; the
  project does not rely on that argument, the same posture the case-summary
  lane holds when it refuses a CourtListener REST snapshot
  ([case-summaries.md](case-summaries.md)).
- **The rule.** A summary may be published only
  where it is written from the ruling's own text and from court-record
  identifiers: the court, the docket and entry numbers, the filing date, and
  the watchlist's own case name. Nothing from CourtListener's curated layer is
  staged for the writer: no docket payload, no value-add field, and no entry
  description (the clerk's entry text is a court record, but the activity
  records already carry none of it, and the summary keeps that line). That
  needs a staged record of its own shape, the order document plus identifiers,
  since the case-summary lane's staged record is a docket. A party's filing (a
  complaint, a brief) is written by counsel rather than the government and is
  not public domain by authorship, so a summary of one is out of scope: only
  rulings are summarized. Attribution follows [`NOTICE`](../NOTICE), since the
  copy came through RECAP and CourtListener.
- **PII.** A district ruling can name individuals: a minor in a product
  liability suit, a self-represented party. The *PII stance* below governs the
  staged text, and a summary names no private individual, identifying the case
  by the watchlist's own name.
- **Not yet verified.** As read on 2026-10-31 the RECAP terms were taken from
  search-engine copies of Free Law Project's RECAP FAQ and the site licence
  notice; the live CourtListener terms of use and the `free.law` pages were not
  read. Before any summary is
  generated, someone with access reads the live CourtListener terms of use and
  copyright policy for any condition on RECAP documents downloaded through the
  site, and records the decision here: summaries built on this footing, or
  dropped.

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
reasoning text that explains them — and the four qp-topic artifacts
(`docs/qp-topic.md`), the hand-labeled reference set, its application block
and the two accrued per-case labels files: subject-matter judgments keyed by case id and public-record
docket number, republishing no source text — and the plain-language case
summaries (`docs/case-summaries.md`), model-written restatements of a case's
record. Those are written only from records whose snapshot is the Court's own
supremecourt.gov docket JSON and whose documents are supremecourt.gov filings,
so what they restate is public-record Court content outside the CC BY-ND term,
and the prompt asks for a summary in the model's own words rather than
quotation. Beside them sit the AI watchlist's activity records
(`data/ai-cases/activity/`), on the footing of the `order-scan` report below:
court-record identifiers (court, docket and entry numbers, filing dates), the
kind our rule reads from each entry, the watchlist's own case name, and a link
to the entry on CourtListener, whose path carries CourtListener's slug of the
docket caption. They copy no entry text and no CourtListener value-add field.
There is also a **non-git** public
channel that carries corpus-derived text: `run-analytics`' one-day
GitHub Actions artifacts, which on a public repository any logged-in user can
download for their retention window. What each one
discloses is inventoried once, in *S3 / the private stores* in
[security.md](security.md), and not re-enumerated here; two of the six
carry stored questions-presented text and are argued in `docs/qp-topic.md`.
That text is derived from petition PDFs fetched from supremecourt.gov — public
records, outside the CC BY-ND term above — and that channel is accepted for the
labeling run and, on the same footing, the case-summary lane's staged records
(supremecourt.gov docket JSON and filings only; the lane refuses a
CourtListener REST snapshot), not as a route for corpus content generally. The other
four republish no document text. One of those four is not corpus-derived at all:
the `order-scan` report names district dockets the corpus does not hold, read
from CourtListener's RECAP search, and carries only court identifiers, docket
numbers, filing dates and the matched entries' numbers and dates with the
order kinds read from them. It copies no caption (a district caption can name
an individual party, such as a noncitizen in an immigration suit) and no
CourtListener value-add field such as nature of suit, so what it republishes is
court-record identifiers, the same footing as the Court identifiers the
`run-repair` handoffs carry. `run-repair`'s one-day handoff artifacts ride
the same channel with public Court identifiers and supremecourt.gov content
only, never a corpus row, snapshot or stored document; the application back-fill's plan, whose served
docket JSON carries counsel blocks, and the OCR, re-cut and document back-fill
plans, whose filing text can carry a self-represented filer's contact details,
cross under the
carve-outs recorded in *PII stance* below. Prediction reasoning may quote or summarize
public-record docket facts in the course of explaining a prediction, and may
characterize what a provisioned filing argues — a petition, its separately
linked appendix, a brief in opposition, the petitioner's cert-stage reply, the
Solicitor General's invited brief, a questions-presented section, either side's
brief on the merits or reply on the merits, an application, the response to it
and the applicant's reply — on the same public-record footing as the questions-presented text above: those
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
  them. Every lane below spends the same account under its own fixed share
  (`courtlistener_budget` there), its client stopping at the lane's run cap,
  and the shares are sized to stay under the daily ceiling while the dispatched
  lanes run at most one a day ([data-pipeline.md](data-pipeline.md)).
- **Opinion enrichment shares that budget**, through the same client and the
  same configured ceilings; the `enrich-opinions` scope, its per-case request
  count, and the headroom arithmetic are owned by
  [data-pipeline.md](data-pipeline.md) and stated only there. Its live-window
  step's requests count against the same account limits but not against the
  pull governor's per-process tally, since each process counts only its own.
  What belongs to the terms question is the boundary: opinion coverage at bulk scale is not a
  REST problem, the **database replication** channel named above remains the
  intended route to opinion bodies across the whole corpus, and nothing here is
  a step toward reading them out of the API instead.
- **The decision-below dry run shares it too.** `decision-below` reads the
  lower court's docket rows, clusters, opinions and post-judgment docket
  entries for a named case or a sample of at most 50, through the same client
  and configured ceilings: four requests for a typical circuit case, sixteen at
  worst. Its requests count against the same account limits but not against
  the pull governor's per-process tally, since each process counts only its
  own. It is a maintainer's measurement, not a lane; `run-analytics`'s
  `decision-below` mode runs the fill's dry run instead, over 25 cases with
  its governor capped at order-scan's 150 requests. Both read only what CourtListener already holds — no RECAP
  Fetch request, so no PACER charge ([cli.md](cli.md)).
- **The decision-below fill shares it too.** `enrich-decision-below` makes the
  same requests for at most 50 cases a run, about four each — six cases on each
  of `run-pull`'s four full live windows a day — and stores what
  they return: the lower court's opinion text, and a short docket record the
  fill writes, in the access-gated corpus like every other document. The
  opinion is CourtListener's text extraction of a public-domain federal
  opinion; the record keeps upstream's panel and judges strings, which a
  staged copy carries only into a cell's gitignored record. No RECAP Fetch
  request is made ([cli.md](cli.md)).
- **The adverse-order scan shares it too.** `order-scan` runs the RECAP
  searches `config/order-scan.yaml` configures — district dockets whose
  entries match an order phrase in a window of entry dates, one request a
  page — through the same client, and stops before the request that would
  pass the config's run cap (150); a larger scan spans several dispatches,
  each resuming the last. Its requests count against the same account limits
  but not against the pull governor's per-process tally, since each process
  counts only its own; the workflow runs it with the cap as its governor's
  hourly limit, so a retried request counts too, and at 8 requests a minute,
  since CourtListener throttles its search endpoint below the tier's
  per-minute rate. It is dispatched
  as `run-analytics`'s `order-scan` mode, never scheduled, so its spend is a
  maintainer's choice of hour. It reads only what CourtListener already holds
  (no RECAP Fetch, no PACER charge), its report carries court-record
  identifiers without caption, entry text or nature of suit, and the dockets
  it names are not admitted to the corpus.

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
  (below), so the stored record stays the record as ingested. The one
  collection-side refusal is a consolidated member's borrowing from its lead
  docket (below), which is declined rather than narrowed.
- **Raw facts stay access-gated.** The corpus that holds the full docket detail
  lives in the private S3 estate — the snapshot payloads in its per-case content
  store, the scannable index beside them — not public git; stored content
  leaves it only through the short-lived run artifacts *What we redistribute*
  above inventories (the case-summary lane's contact-scrubbed staged record,
  run-analytics' questions-presented extracts). The only PII that can reach
  public git is whatever a piece of reasoning quotes from a public docket while
  explaining a prediction. Apart from what the contact scrubs miss (named at
  the end of the second carve-out), the only places a self-represented
  filer's contact detail travels unscrubbed are the transient run artifacts
  in the carve-outs below, which hold no stored copy and never reach git.
- **One carve-out: the application back-fill's plan artifact** (maintainer
  decision, 2026-10-01; extended to OT2016's legacy docket pages, 2026-10-27).
  Every byte it admits is the Court's own public docket
  record, served openly at supremecourt.gov, and none of it comes from our
  private stores; it lets that record transit one short-lived workflow
  artifact between two jobs of the same run.
  - *What:* the docket JSON exactly as supremecourt.gov serves it for the
    dockets in one `application-backfill` run's plan — and, for a serial of
    a Term in `LEGACY_HTML_TERMS` (OT2016) that serves no JSON, the Court's
    legacy HTML docket page exactly as served — counsel blocks
    included, which for a self-represented filer carry a home address,
    telephone, email or prisoner register number — plus the structured fields
    parsed from it. Nothing read from the corpus, the content store or any
    snapshot we stored — which rests on the job that writes the plan holding
    no corpus credential at all. Both that job and the applications writer
    refuse a plan not shaped as served docket JSON or a served docket page
    plus the fields parsed from it.
  - *Where:* one workflow artifact, `repair-plan-<run_id>`, kept one day and
    consumed by the applications writer in the same run. It is never committed
    to git and never printed to a log or step summary; the step summary
    carries the ledger's counts and each row's parsed fields (docket number,
    kind, dates, a counsel *count*), never a served block's text.
  - *Unchanged:* the corpus and the content store stay access-gated; the
    contact scrubs below still withhold these details from every cell, model
    provider and summary, within what they reach; nothing under this
    carve-out reaches `data/`.
  - *Not a precedent:* any other pass whose plan would carry a stored or
    private record still crosses a public-only projection. A new use of this
    carve-out is its own decision, recorded in this section.
- **A second carve-out: the OCR sweep's plan artifact** (maintainer
  decision, 2026-10-17, by promoting the sweep's run-seed jobs). Every byte it
  admits is a
  filing the Court serves openly at supremecourt.gov, read off its page
  images, and none of it comes from our private stores.
  - *What:* for each item of one window's worklist that the parse could read,
    the text the extractor and OCR recovered from the filing at the item's
    Court URL, with its page count and the `truncated` and `ocr_derived`
    flags. A self-represented filer's scanned application or petition carries
    a home address, telephone or prisoner register number in that text.
    Nothing read from the corpus, the content store or any stored snapshot:
    the job that writes the plan holds no corpus credential, and the worklist
    it reads carries case ids, kinds, Court URLs and page counts only.
  - *Where:* one workflow artifact, `ocr-plan-<run_id>`, kept one day and
    consumed by run-seed's OCR sweep writer in the same run. It is never
    committed to git and never printed to a log or step summary; the summary
    carries each row's identifiers, page count, character count and flags.
    The writer refuses a plan whole above the window's cap, off its shape, or
    naming anything not on the window's worklist, and writes a row only into
    a stored document still empty at the same URL.
  - *The dispatched pass* (proposed; promoting the split of run-repair's
    `ocr-recovery` pass to `main` decides it). The same text, of the same shape, read
    the same way, crosses run-repair's credential split as
    `repair-plan-<run_id>`, on an applied dispatch only, kept one day and
    consumed by that run's OCR recovery writer. Every term above holds for
    it: nothing from our stores, never committed or printed, and refused
    whole by its writer on the same checks against the projection's own
    worklist — less two the dispatched pass never applied (a reading need
    not be `ocr_derived`, and one of another page count is written with the
    count read), plus one: the plan must account for every worklist item
    exactly once. Its worklist is at most `repair_bound` items and at most
    200, so a plan is at most that many filings, each under the document
    cap.
  - *Who can read it:* the repository is public, so while the artifact
    exists any signed-in GitHub user can download it from the run page —
    for a day, on each of run-seed's four windows a day that recovered
    anything, and on each applied `ocr-recovery` dispatch. The same is true of
    the application back-fill's artifact above.
    Deleting the artifact as soon as the writer has consumed it would shorten
    that to minutes, at the price of `actions: write` on the writer job; that
    trade is the maintainer's to make, and is not made here.
  - *Unchanged:* the corpus and the content store stay access-gated, and
    nothing under this carve-out reaches `data/`. The contact scrubs below
    run over recovered text as over any other stored text, and OCR output does
    not always lay contact details out in the shapes the scrub withholds. Where
    the shape pass ran, a residual detector re-reads the scrubbed document's
    opening and closing; a document it still finds a contact shape in is
    recorded as **not** scrubbed (`contact_residuals` in the cell's manifest)
    and left out of the case-summary lane's staged record, but it is still
    staged to the cell, and so reaches its model provider, as scrubbed. What
    the detector does not read (a document's middle, or any document a
    value-only scrub ran over) is not checked at all
    ([live-sources.md](live-sources.md), the contact-detail scrub;
    [case-summaries.md](case-summaries.md)).
- **A third carve-out: the re-cut's plan artifact** (proposed; promoting the
  split of run-repair's `recut` pass to `main` decides it). Every byte it
  admits is a filing the Court serves openly at supremecourt.gov, read off its
  text layer, and none of it comes from our private stores.
  - *What:* for each item of one dispatch's worklist that the parse re-cut,
    the text the fetching lanes' extractor cut from the filing at the item's
    Court URL, with its page count and `truncated` flag; for every other item,
    one of the pass's own outcome strings (a failed fetch and its reason
    class, unparseable bytes, another page count, an empty re-cut). A
    self-represented filer's petition or application carries a home address,
    telephone or prisoner register number in that text. Nothing read from the
    corpus, the content store or any stored snapshot: the job that writes the
    plan holds no corpus credential, and the worklist it reads carries case
    ids, kinds, Court URLs and stored page counts only.
  - *Where:* one workflow artifact, `repair-plan-<run_id>`, kept one day and
    consumed in the same run — on an apply by the `documents` writer, on a dry
    run by the read-only `documents-dry-run` reader, because the rest of each
    outcome reads the stored text, which never crosses, and a dry run that
    reads as its apply needs it judged. It is the one plan that crosses on a
    dry run too. It is never committed to git and never printed to a log or
    step summary; the summary carries each item's identifiers, page count,
    character count and flags, and its outcome. Both readers refuse a plan
    whole if it is off its shape, names anything not on the projection's own
    worklist (downloaded by artifact id), does not account for every
    worklist item exactly once, or carries a row of another URL or page count
    than its item's or a text above the document cap; the writer then writes
    a row only into a stored document still in the re-cut class at that URL
    and page count. Its worklist is at most `repair_bound` items, or on an
    unbounded dry run the class in scope, of which the parse's slice deadline
    reaches what its step can read; each text is under the document cap.
  - *Who can read it:* as above, any signed-in GitHub user, for a day, on
    each `recut` dispatch.
  - *Unchanged:* the corpus and the content store stay access-gated, nothing
    under this carve-out reaches `data/`, and the contact scrubs below run
    over a re-cut text as over any other stored text.
- **A fourth carve-out: the document back-fill's plan artifact** (proposed;
  promoting the split of run-repair's `document-backfill` pass to `main`
  decides it). Every byte it admits is a filing the Court serves openly at
  supremecourt.gov, read off its text layer, and none of it comes from our
  private stores.
  - *What:* for each item of one applied dispatch's worklist that the parse
    reached, either a docket loss, a floor reading, or the documents the
    fetching lanes' own `fetch_case_documents` produced for it — each one's
    kind, Court URL, entry date, page count and text cut at the document cap,
    the derived questions-presented row among them. A self-represented filer's
    petition or application carries a home address, telephone or prisoner
    register number in that text. Nothing read from the corpus, the content
    store or any stored snapshot: the job that writes the plan holds no corpus
    credential, and the worklist it reads carries case ids, missing kinds, the
    upstream docket address and Term, and the Court URLs of each case's stored
    documents only.
  - *Where:* one workflow artifact, `repair-plan-<run_id>`, on an applied
    dispatch only — the dry run is read whole in the parse and hands nothing
    on — kept one day and consumed by the `documents` writer in the same run.
    It is never committed to git and never printed to a log or step summary;
    the summary carries each item's identifiers, each document's kind and
    character count, and its floor or loss. The writer refuses a plan whole if
    it is off its shape, names anything not on the projection's own worklist
    (downloaded by artifact id), does not account for every worklist item
    exactly once, or carries a document of another case, a second of one kind
    or a text above the document cap, and writes nothing for a candidate whose
    gap has changed since the projection. Its worklist is at most
    `repair_bound` items; the parse's slice deadline and a byte budget below
    the hand-off cap end the slice early where the filings run long.
  - *Who can read it:* as above, any signed-in GitHub user, for a day, on
    each applied `document-backfill` dispatch.
  - *Unchanged:* the corpus and the content store stay access-gated, nothing
    under this carve-out reaches `data/`, and the contact scrubs below run
    over a back-filled text as over any other stored text.
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
  account. One exception: the Court's own docket JSON (it carries
  `ProceedingsandOrder`) that carries the respondent side's counsel key but no
  `Petitioner` key at all is how the Court serves a pseudonymous
  self-represented petitioner, and it is read as self-represented on the
  petitioner side; with no block served, the staged text gets the shape pass
  alone. The `Other` list — amici and other non-party filers — is read on
  the first two arms (no attorney, or the amicus as its own); the
  register-number arm is not asked there, because `PrisonerId` on that list
  holds free text rather than a register number, and only a qualifying
  amicus's own values key the value pass. Where the `Other` list is the only
  list read so, the staged text gets that value pass alone — no shape pass — since
  what is staged there is counsel's filings; a self-represented non-amicus
  `Other` filer whose own opposition is staged gets the value pass alone too.
  A self-filing amicus whose served
  name carries a title or honorific ("Professor", "Hon. … (Ret.)"), names
  several people jointly, or adds a comma-separated description (", APC") is
  read as self-represented where the attorney field is the person, or one of
  the people, it names. On every list, a served name that opens with an
  "In re", "In the Matter of" or "Ex parte" caption is compared without it,
  so a filer captioned "In re <name>" whose attorney field is that name reads
  as self-represented.
  A consolidated member's merits filings read off its lead docket are staged
  and scrubbed on the member's own reading, since only the member's own side's
  filings are borrowed; a lead whose petitioner or respondent side reads as
  self-represented lends nothing at all, because provisioning reads one case's
  snapshot and cannot key the scrub on the lead's blocks.
  This is the staged-copy narrowing applied on privacy grounds, and it applies to the
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
  The reading is of the filers *at the Court*: an appendix that reproduces
  record material a then-unrepresented party filed below (a declaration, a
  complaint) is staged as served where every party is represented here, the
  same as a bound appendix inside a petition.
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
