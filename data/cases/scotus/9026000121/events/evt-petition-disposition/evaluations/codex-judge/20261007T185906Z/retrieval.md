# Evaluator retrieval record

## Supplied and committed inputs

Read AGENTS.md, the evaluation prompt, and the evaluation/flags/tooling schemas. Read the cert event definition and outcome; each of claude-baseline, gemini-baseline, and codex-baseline's blinded prediction, rationale, pointed-to forecast, retrieval note, and harness retrieval log; the evaluator context and October 5 snapshot; the questions-presented text and selected petition passages concerning the procedural dismissal and disputed employment timing. Read the committed statpack's sal-v4 segment table and scope text, and calculated the OT2017–OT2025 reached-band baseline from its rendered rows. The supplied snapshot is dated October 5, 2026; no claim about the remote corpus's current vintage is made.

No corpus query or open-events command was used, so there is no ranged-corpus-read transfer line. `fedcourts paths --court scotus --docket 9026000121 --event evt-petition-disposition --role evaluator` was used for path confirmation, not factual retrieval. No candidate identity was sought, and no unblinded prediction tree or repository history was read.

## General authority checks

These checks concern preexisting doctrine, not new facts about the scored case. No external Basso docket or outcome was sought.

1. Web search call with queries `site.loc.gov "Lawrence v. Chater" "State Supreme Court"` and `site.supremecourt.gov "Caperton" "most matters" "constitutional"`. The tool returned no visible content.
2. Two page-open attempts for `https://supreme.justia.com/cases/federal/us/516/163/`. Both returned no visible content. No proposition rests on these attempts.
3. CourtListener `search(type="o", citation="516 U.S. 163", num_results=1, fields=["caseName", "citation", "dateFiled", "opinions"])`. The first result was the unrelated Monoson v. United States, 516 F.3d 163; it was discarded rather than treated as the requested authority.
4. CourtListener `search(type="o", court="scotus", case_name="Lawrence v. Chater", num_results=1, fields=["caseName", "citation", "dateFiled", "opinions"])`. First attempt was rate-limited; the later repeat succeeded and returned Lawrence, decided January 8, 1996, including lead opinion 9433233.
5. CourtListener `search_document(opinion_id=9433233, query="State Supreme Court", snippet_size=900)`. The majority's discussion at 516 U.S. 166–67 expressly lists state supreme court decisions among developments supporting past GVRs. Used to check the categorical claim in claude-baseline's rationale, not to forecast or rescore an auxiliary claim.
6. CourtListener `search_document(opinion_id=9435330, query="constitutional level", snippet_size=650)`. Read the Caperton majority's discussion distinguishing ordinary disqualification from extraordinary constitutional cases. Used to check the doctrinal distinction in codex-baseline's rationale. The combined document contains other opinions, but only the identified majority passages support the assessment.

## Output checks

Use isolated schema validation for the alias-keyed output rather than the repository-wide evaluation-target check, which requires the harness's later restoration and un-aliasing. The default Python environment did not provide jsonschema; validation uses an isolated `uv run --with jsonschema` environment without changing project dependencies.
