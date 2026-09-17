# Retrieval record

- Read committed `metrics/statpack.md`: modern discretionary-cert disposition counts, originating-circuit context, paid-segment relist and CVSG cuts, and sal-v4 reached-band table. Read `metrics/statpack.json` for exact elevated reached rates and denominators in Terms 2017–2024. Local arithmetic returned 484 / 2810 = 0.17224199288256228. Ran `git log -1 --format='%cs %h' -- metrics/statpack.md`; the reported last change was `2026-09-14 55121cdb8`. No live corpus-freshness claim follows from that commit date.
- Attempted `web.run` open of the September 2, 2026 reply PDF expressly linked in the provisioned snapshot. The tool returned no usable text or source citation. No search for the case or its disposition was made.
- Attempted the same known filing through `curl -fsSL --max-time 40` piped to `pdftotext - - | head -n 180`. The PDF executable was unavailable, and curl reported a failed output write. No filing text was obtained. The exact retrieval target, recorded as a code literal, was:

  `https://www.supremecourt.gov/DocketPDF/25/25-1142/422829/20260902154306837_25-1142_PetitionerReplySupplementalBrief.pdf`

- Checked locally installed PDF libraries after the failed extraction: pypdf was available, pymupdf and pdfplumber were not. No subsequent extraction or additional retrieval was performed; the forecast proceeds without the reply.
- No CourtListener MCP lookup, `fedcourts query`, or `fedcourts open-events` call was made. Consequently there were no ranged-corpus transfer lines to record.
- Local contract reads and path resolution were not case-law retrieval. The initial `uv run fedcourts paths --court scotus --docket 73281629 --event evt-petition-disposition --role predictor` failed because the default cache was read-only; rerunning with a writable temporary cache succeeded.

No target-case outcome material was encountered.
