---
name: peel3-phase3
version: 2.57
description: >
  Given a Phase 1 JSON inter-phase contract (produced by new-peel-phase1 v2.0)
  and the Voyant built-in stopword file (stop.en.smart.txt), generates the
  Spyral Notebook JavaScript configuration and all tool cells. Phase 1 supplies
  incList, excList, and clusterDefs authoritatively — no re-selection or
  re-stemming is performed. Produces five deliverables:
  (1) two configuration JS cells — Cell 0 (stoplist ID placeholder, manually
  completed by user after uploading the merged stopword file to Voyant) and
  Cell 1 (incList + clusterDefs + Spyral instantiation); (2) an HTML colour
  legend; (3) a single tools JS file with the 8 remaining Distant Reading
  tool cells in notebook order (Summary and Documents relocated to
  Deliverable 8, Cells 15-18);
  (4) a merged stopword TXT file combining stop.en.smart.txt with the Phase 1
  excList, deduplicated and sorted alphabetically; (5) a permanent, human-
  readable Phase3-results.md documenting token derivation, colour assignment,
  cross-cluster stems, and the merged stopword list.
  Triggers: "Run Phase 3", "Generate Spyral config", "Inject categories",
  or similar imperatives after Phase 1 has been completed.
  compatibility: "claude.ai, Claude Desktop — requires bash_tool and present_files"

  Full version history (all prior version changes, kept verbatim for
  provenance): see "Version History (appendix)" at the
  end of this file.
---

# new-peel-phase3 — Spyral Notebook Configuration and Tool Cell Generation

## Contents

*(Added 2026-07-28. A plain index, not hyperlinks — this file's rendering
environment isn't guaranteed to support markdown anchors, so section
titles are listed as they appear, to be located by text search.)*

- Step 0 — Session log setup · Step 0.9 — Environment precondition check
- Overview
- 0. Inputs (0.0 Ingest Phase 1 JSON · 0.0b Compute corpus_name default · 0.1 Ingest stop.en.smart.txt)
- 1. Derive C[nn] Tokens (1.1 First-word rules · 1.2 Collision detection ·
  **1.3/1.4 — the combined elicitation round, asked together**: 1.3 reports
  it and awaits confirmation, 1.4 is Deliverable 8's collocation-pair choice)
- 2. Assign Tableau20 Colours
- 3. Identify Cross-Cluster Stems
- 4. Deliverable 1 — Configuration Cells (Cell 0 + Cell 1)
- 5. Deliverable 2 — HTML Colour Legend (Cell 13)
- 6. Deliverable 3 — Tool Cells File, JS2–JS11 (6.1 order/specs · 6.2 parameter reference · 6.3 @Category rule)
- 6b. Deliverable 8 — Source vs. Summary Comparison, Cells 14–20
  (6b.1 Cell 14 · 6b.2 Cells 15-18 · 6b.3 Cell 19, the five-tool pattern · 6b.4 Cell 20)
- 7. Deliverable 4 — Merged Stopword List (7.0b optional comprehensive excList ·
  **7.0c mandatory automatic numeral scan** ·
  7.1 merge algorithm · 7.2 write/verify · **7.2b Deliverable 7** — comparison
  corpus ZIP · 7.3 intermediate delivery · 7.4 validate Voyant IDs)
- **7.5 Deliverable 5** — Phase3-results.md
- **7.6 Deliverable 6** — Populated Spyral Notebook (cell ownership, all
  per-cell builder functions, master population function, verification, writing the file)
- 8. Output Files and Delivery · 8.5 Post-delivery live-Voyant checkpoint
- 9. Pre-Generation Checklist
- 10. Lessons Encoded
- Version History (appendix) — full versioned changelog, moved out of the
  frontmatter 2026-07-28; see `status/skills-usability-review.md`

### Numbering lookup — Step # / Deliverable # / Cell # / JS # in one place

*(Added 2026-07-28, closing a usability finding: this file uses four
independent numbering schemes — the "Step"/section number above, the
"Deliverable" number (1–8), the notebook's own fixed Cell number, and
the tool file's JS2–JS11 numbering — with no single place they were all
listed together. This table doesn't change any of them; it's a lookup,
built from the section headings above.)*

| Deliverable | What it is | Built in section(s) | Cell(s) / file |
|---|---|---|---|
| 1 | Configuration cells | 4 (4.1–4.3) | Cell 0, Cell 1 |
| 2 | HTML colour legend | 5 | Cell 13 |
| 3 | Tool cells file | 6 (6.1–6.3) | JS2–JS11 → the 8 remaining Distant Reading tool cells (`TOOL_CELL_IDS`) |
| 4 | Merged stopword list | 7 (7.0b–7.1–7.2) | merged stopword `.txt` |
| 5 | Phase3-results.md | 7.5 | `.md` report |
| 6 | Populated Spyral Notebook | 7.6 | the whole notebook `.html` — every cell |
| 7 | Comparison corpus ZIP | 7.2b | `.zip` |
| 8 | Source vs. Summary comparison | 6b (6b.1–6b.4) | Cells 14–20 (`DELIVERABLE8_CELL_IDS`) |

Sections 1–3 and 8–10 don't correspond to a single Deliverable number —
they're shared setup/output/reference steps that feed or wrap all eight
deliverables, not a deliverable in their own right.

---

## Step 0 — Start the session log (mandatory, before any other step)

Before doing anything else — before reading inputs, before greeting the
user — start the session log:

**Before running `session_log.py init` (added v2.55 — closes a real,
confirmed gap: an earlier PEEL3 cycle's Phase 1 session ran with a
different working directory than that same cycle's Phase 2/3 sessions,
so `session_log.py`'s own `peel-logs/` output — written relative to
whatever directory happens to be current — silently scattered one
cycle's logs across two locations, discovered only by manually
searching the disk afterward, not by anything this skill did at the
time).** Resolve and state the absolute working directory first, and
confirm it against any prior session for the same track:

```bash
pwd
```

State the resolved path to the researcher in the same message that
reports the log was initialized — e.g. "Working directory:
`/path/to/TrackFolder`, session log at `peel-logs/[session]/log.md`
under it" — never silently. If this is a continuation of a track
another phase already started (check for that track's own existing
`peel-logs/`/`session-logs/` entries first), the working directory
must match what that earlier phase used; if it does not, or the
correct location is ambiguous, stop and ask the researcher rather than
guessing or defaulting to wherever the shell happens to already be.
`session_log.py` itself now also prints the absolute resolved path on
every `init`/`append` call (its own 2026-08-06 fix) — read that
output, don't just trust the call succeeded.

**Duplicate-copy warning (found during the same 2026-08-06 pass):**
this file's own path below (`peel-protocol/scripts/session_log.py`) is
stale relative to how this project's own sessions have actually run —
every real session this project has logged used `PEEL3-Scripts/
session_log.py` instead (the location `README.txt` documents as
canonical), leaving a second, easy-to-miss copy at `peel-protocol/
scripts/` that silently drifts out of sync unless remembered by hand
(confirmed: it *had* drifted, missing this same day's absolute-path
fix, until resynced as part of this pass). Prefer `PEEL3-Scripts/
session_log.py` if both exist in the current checkout; if only the
`peel-protocol/scripts/` copy exists, use it but flag to the researcher
that it may be behind the canonical version.

```bash
python3 PEEL3-Scripts/session_log.py init "[corpus-or-topic]-[phase]-[YYYY-MM-DD]"
```

Then, for the remainder of the session, after EVERY conversational
turn — both the user's message and this assistant's response — append
it immediately:

```bash
python3 PEEL3-Scripts/session_log.py append "[session]" --role user   --text "[verbatim user message]"
python3 PEEL3-Scripts/session_log.py append "[session]" --role claude --text "[verbatim assistant response, or a faithful summary if very long]"
```

**This is not optional, not deferrable, and not something to batch at
the end.** A turn that is not logged when it happens is not
recoverable later — there is no memory across sessions by the
researcher's explicit choice, and a log reconstructed from memory at
session's end is not a trustworthy trace, which defeats the entire
purpose. If logging is skipped for any turns, stop, say so to the
user, and backfill before continuing — do not silently treat the gap
as acceptable or invisible.

**At the end of the session**, present `peel-logs/[session]/log.md` via
`present_files` and explicitly remind the researcher to save it into
her own external, iteratively-updated log archive — this script can
only write inside the current sandboxed session and cannot reach the
researcher's machine directly.

------------------------------------------------------------------------

---

## Step 0.9 — Environment precondition check (mandatory, before any other step)

**This skill's entire accountability design assumes its mechanical
checks are actually executed, not narrated** — Step 3.2v / 6.2v, the
coverage calculations, the span-classification bookkeeping, all of it.
A missing or broken code-execution environment does not remove one
input to those checks; it removes the ground all of them stand on.

Before proceeding past this point, confirm a real, working Python 3
execution environment is available in this session:

```
Using whatever code-execution capability is available in this
environment, attempt to run:

    python3 -c "print(2+2)"

(or `python -c "print(2+2)"` if `python3` is not found)
```

- **If this returns `4`**: Python is available. Proceed to Step 1
  normally.
- **If it errors, times out, returns anything else, or no code-
  execution capability exists in this environment at all**: STOP. Do
  not proceed to Step 1 or any later step. Follow the Environment
  Precondition Failure protocol below.

### Environment Precondition Failure protocol

**Never silently substitute a different language, tool, or hand-
computed approximation for this skill's specified Python logic.** This
includes reimplementing checks in another scripting language available
in the session, computing coverage or counts "by reading carefully"
instead of executing code, or any other on-the-spot improvisation —
regardless of how confident the substitute looks or how carefully it is
described. A narrated approximation and a mechanically verified result
are not the same thing, and presenting one as if it were the other is
exactly the failure this skill's own verification gates exist to
prevent — now occurring inside the tool meant to guard against it.

Report the gap to the researcher plainly, and offer these options —
**do not pick one on the researcher's behalf**:

1. **Switch environments.** Recommended default: pause here and re-run
   this skill in an environment confirmed to support Python execution
   (e.g. claude.ai or Claude Desktop with code execution enabled).
2. **Proceed fully unverified, explicitly labeled as such.** Every
   claim this skill would normally back with an executed check —
   counts, percentages, statuses, pass/fail verdicts — must instead be
   generated as the assistant's own unaided judgment, and every single
   one must carry a visible, standalone label: **"UNVERIFIED — no code
   was executed to confirm this."** This label is not a footnote or a
   methodology note; it must be as prominent as the claim it modifies,
   in the chat, in every delivered file, and in every report section
   that would otherwise present a mechanically-checked number.
3. **The researcher explicitly requests an alternate-language
   reimplementation.** Only if asked for directly — never offered as a
   silent default, never chosen unprompted. If this option is taken,
   the actual generated code (not merely its output or a description of
   it) must be delivered to the researcher as a real file, labeled
   clearly: "unaudited, generated on the spot for this session, not
   part of the tested skill, requires independent review before being
   trusted." This is the same standard already applied to every other
   disclosed fallback in this skill (see `## Environment fallbacks
   used`) — the difference is one of degree, not of kind: this fallback
   has never been tested by anyone, not even once, and that fact must
   travel with its output.

Whichever option the researcher chooses, record the choice and the
reason in the session log (already running, per Step 0) and in the
permanent human-readable report for this run.

**NOTE (v2.14):** unlike Phase 1, this file has no pre-existing,
independently-defined `## Environment fallbacks used` section with its
own established meaning (Phase 1's version carries specific NLTK/WordNet
degraded-mode disclosures this skill has no equivalent of) — so there is
no risk of blending two distinct meanings here, and no reason to invent a
second heading. Record the Step 0.9 outcome directly under
`## Environment fallbacks used` in `Phase3-results.md` (Step 7.5),
mandatory every run: state plainly that Python was confirmed available
via `python3 -c "print(2+2)"` returning `4` in the ordinary case, or,
on failure, which of the three options above was chosen and why. Set
`environment_precondition_status` here, once, immediately after this
check resolves (pass or fail) — Step 7.5's report builder reads it
directly, not a re-derivation:

```python
if python_check_returned_4:  # i.e. Step 0.9 above passed
    environment_precondition_status = (
        "Python 3 execution environment confirmed available "
        "(`python3 -c \"print(2+2)\"` returned 4). No environment "
        "fallback was needed this run."
    )
else:
    environment_precondition_status = (
        f"Python 3 execution environment check FAILED: "
        f"<specific error/timeout observed>. Researcher chose option "
        f"<1, 2, or 3 as listed above>: <the option's own wording>. "
        f"Reason given: <researcher's stated reason, or 'none given' if "
        f"none was offered>."
    )
```

---

## Overview

Phase 3 is the bridge between the NewPEEL analytical pipeline and the Voyant
Spyral Notebook. It takes the semantic outputs of Phase 1 (incList, excList,
clusterDefs) as authoritative inputs, transforms cluster names into valid
Voyant `@Category` query tokens, assigns Tableau20 colours, and generates
five ready-to-paste or ready-to-upload deliverables in the correct notebook
injection order.

No re-selection, re-stemming, or re-clustering is performed in Phase 3.
The Phase 1 outputs are consumed exactly as produced.

**Execution order is NOT the same as the numbered order below.** The
numbering of Steps 1–7.7 reflects each deliverable's identity for
reference and delivery purposes, not the order they must actually be
generated in. Follow this order instead:

**v2.32 restructuring, researcher's explicit instruction:** all
elicitations — every point where this skill needs an answer only the
researcher can give — are now bundled into one combined round immediately
after ingest, so the researcher answers everything at once and then waits
for the finished notebook, rather than being interrupted repeatedly
through the run. This supersedes v2.19's rationale below only in *how*
the researcher learns a Voyant round-trip is coming (told directly, in
the combined elicitation message, rather than by literally generating
7.1/7.2/7.7 first) — the underlying goal (full context, no surprise
mid-run) is preserved, just served a different way. The Voyant ID
round-trip itself (Step 7.3/7.4) is **not** an elicitation in this sense
and cannot be folded into the combined round: `voyant_stoplist_id` and
`voyant_comparison_corpus_id` are assigned by Voyant only at the moment
the researcher actually uploads the files, so they are not yet knowable
when the combined round runs. Neither is `catsId` (see v2.35): it is
assigned by Voyant only at the moment `Spyral.Categories().save()`
actually runs there, so it is knowable in advance only if this run is
*regenerating* a notebook that has already been run at least once. **On
a brand-new corpus's first-ever Phase 3 run, this is two Voyant
round-trips, not one** — the stoplist/comparison-corpus pair (Step
7.3/7.4) plus a separate `catsId` scratch-cell round-trip (Step 3.5,
below) — everything on either side of both is fully automatic.

1. Steps 0 through 0.1 (JSON ingest, `stop.en.smart.txt`).
2. **The combined elicitation round — Steps 0.0b, 1, 1.3, and 1.4, all
   presented to the researcher together in a single message.** Confirm
   `corpus_name` (0.0b); derive C[nn] tokens and present the table for
   confirmation (1, 1.3); ask for the one researcher-chosen term from
   C01/C02/C03 that Deliverable 8's Cell 19 needs (1.4 — see 6b.3c for
   what it's used for). Tell the researcher plainly, in this same
   message, that once they answer these three items the merged stopword
   list and comparison corpus ZIP will be generated automatically and
   handed to them for a single Voyant upload round-trip, and that
   everything after that (the complete, instantiated notebook) will be
   produced without further questions. Do not proceed past this round
   until `corpus_name`, the confirmed/corrected token table, and the
   Deliverable 8 term are all in hand.
3. Steps 2 and 3 (colour assignment, cross-cluster stems) — fully
   automatic now that Step 1 is confirmed; no researcher input.
3.5. **Added v2.35 — the `catsId` scratch-cell round-trip, only needed on
   a genuinely first-ever run against this corpus** (skip this step
   entirely if regenerating a notebook that has already been run in
   Voyant at least once — in that case `catsId` is already known and
   confirmed the same way `voyant_stoplist_id` is). Generate
   `[corpus_name]-catsId-scratch-cell.js` from the now-confirmed
   `clusterDefs` (Section 4.2) and hand it to the researcher to paste into
   any empty code cell in her live notebook and run once. Do not proceed
   to Step 6/Deliverable 1 until she reports back the real `catsId`.
4. Step 7.1–7.2 and Step 7.7's own build step — build the merged
   stopword list and the comparison corpus ZIP. Both are computable from
   inputs already in hand (Phase 1's JSON, `stop.en.smart.txt`, the
   source text, Phase 2's `-Summary-{rate}pct.txt` files) — no researcher
   input needed here either.
5. **Step 7.3–7.4 — stop here. This is the one remaining pause in the
   session.** Deliver both files together in a single batch, wait for the
   researcher to upload both to Voyant and report both real assigned IDs,
   and validate them. Nothing past this point may be generated before
   this completes.
6. Once `voyant_stoplist_id`, `voyant_comparison_corpus_id`, and (on a
   first-ever run) `catsId` are all confirmed, run straight through to
   completion with no further stops: Steps 4, 5, 6, and 7.5 (Deliverables
   1, 2, 3, and 5) — Deliverable 1 (Cells 0 and, as of v2.35, 1) and
   Deliverable 5 have a genuine data dependency on the values, the others
   are held with them purely so the researcher receives one clean, usable
   batch.
7. Step 7.6 (Deliverable 6) — if the template was uploaded, assemble the
   actual populated notebook: everything from step 6, plus Phase 1/2's
   own `-results.md` files, Phase 2's `_spyral.html`, and — using the term
   already confirmed back in step 2 and the `catsId` confirmed at step
   3.5 — Deliverable 8's Cells 14–20 (Section 6b). This is the complete,
   instantiated PEEL Spyral Notebook, the end product of PEEL 3; nothing
   about it requires a further researcher answer, since every input it
   needs was gathered in steps 2, 3.5, and 6.
8. Step 8, Round 2 (final delivery of the remaining files).

**If you are reading this skill top-to-bottom and about to act on Step 4,
5, 6, 7.6, or 7.5 before reaching Step 7.3/7.4: stop.** Those steps come
before Step 7 in this document only because deliverables are numbered for
reference, not because they run first. And if you are about to ask the
researcher anything not covered by the combined round in step 2 above
(corpus_name, the token table, the Deliverable 8 term) at any later point
in the run: stop — that question belongs in the combined round, not a
fresh interruption; if it is a genuinely new elicitation need discovered
during redesign work, it should be added to step 2's bundle for the next
version, not asked ad hoc mid-run.

---

## 0. Inputs

**NOTE (expanded for Deliverable 6):** populating the actual notebook
requires more than Phase 1's JSON — it needs the human-readable and
condensation artifacts from Phase 1 and Phase 2 too, plus the notebook
template itself. None of this changes the JSON's authoritative status for
term/cluster data (see below) — these are additional inputs, not
substitutes for it.

| File | Role | Format |
|---|---|---|
| `*-phase1-state.json` | Phase 1 inter-phase contract (incList/excList/clusterDefs/corpusId) | JSON (from Phase 1 v2.0 Step 6) |
| `stop.en.smart.txt` | Voyant built-in English smart stopword list | Plain text, one term per line |
| `*-Phase1-results.md` | Phase 1's human-readable record — supplies Cell 7's Phase 1 narrative and per-term appendix | Markdown |
| `*-Phase2-results.md` | Phase 2's human-readable record — supplies Cell 7's Phase 2 narrative and per-span appendix | Markdown |
| `*_spyral.html` (from the approved Phase 2 round) | The full toggle-equipped condensation — supplies Cell 6 directly and Cell 5 by derivation | HTML |
| `*-CLEANED.txt` (Phase 1's cleaned source text) | **Added 2026-07-18.** The source document itself, required for Deliverable 7's comparison corpus ZIP — without it, source-vs-summary triangulation (Cell 14) has nothing to compare the summaries against | Plain text |
| `*-Summary-{rate}pct.txt` (one per approved Phase 2 rate) | **Added 2026-07-18.** Phase 2's own native plain-text summary deliverable (v3.21), one file per approved condensation rate — the other documents that go into Deliverable 7's comparison corpus ZIP | Plain text |
| `*-TemplateSN.html` | The blank Spyral Notebook template — required for Deliverable 6 only; if absent, Deliverables 1–5 still proceed and Deliverable 6 is skipped with an explicit note, not silently omitted | HTML |
| `*-excList-comprehensive.json` | **Added v2.33, optional.** A researcher-assembled comprehensive stopword-exclusion list (numerals, short tokens, citation artifacts, confirmed author names, the corpus-independent philosophy-prose supplement) — see Step 7.1's own note for why this exists and why it is not something Phase 3 can construct on its own. If present, Deliverable 4 is built from it instead of Phase 1's narrow `excList`, with provenance disclosed. If absent, Phase 3 proceeds with the narrow `excList` (Phase 1's own T-3.32 contract value) and prints an explicit warning rather than silently shipping a list already known, for at least one real corpus, to under-perform the plain default | JSON |

If `*-CLEANED.txt` or any approved rate's `*-Summary-{rate}pct.txt` is
missing, report which file is absent and do not fabricate or reconstruct
it — Deliverable 7 cannot be built without the real files, the same
discipline already applied to the JSON and `stop.en.smart.txt` above.

**Search scope for `*-TemplateSN.html` in local/filesystem environments
(added v2.55, closes a real, confirmed miss).** This table's "required
for Deliverable 6 only; if absent, skipped" language was written for the
claude.ai/Claude Desktop sandbox (`compatibility`, frontmatter), where
every input is a flat "upload" with no folder hierarchy to search. In a
local Claude Code CLI run or similar filesystem-based environment, do
**not** search only the track's own working directory before concluding
the template is absent — the template commonly lives one level up from
the track folder, at the project root, and skipping that check risks
wrongly reporting Deliverable 6 as skipped when the template is
actually present. The blank
template is a one-time, shared asset — like `stop.en.smart.txt` and the
Voyant Data Collection notebook, it is typically distributed once
alongside the skill files and scripts, not duplicated into every track
folder. Before reporting Deliverable 6 skipped, search at minimum: the
track's own working directory, its parent directory, and wherever
`stop.en.smart.txt` was actually found (Step 0.1) — these are likely the
same "package root" location. Report every location checked, not just
"not found," so a false negative here is falsifiable rather than taken
on faith.

**CRITICAL — The JSON is the authoritative source for term/cluster data.
Do not accept the MD as a substitute for it.**

If the user uploads `*-Phase1-results.md` instead of the JSON, report:
> "Phase 3 requires the JSON inter-phase contract (`*-phase1-state.json`),
> not the MD file. Please upload the JSON produced at the end of Phase 1.
> If you do not have it, Phase 1 must be re-run to produce it."

Do not attempt to parse the MD as a fallback **for term/cluster data** —
the MD files are still required, separately, for their own narrative
content (see table above).

If `stop.en.smart.txt` is not uploaded, report:
> "Phase 3 also requires `stop.en.smart.txt` — the Voyant built-in English
> smart stopword list — to produce the merged stopword file (Deliverable 4).
> Please upload it before proceeding."

Do not proceed until both files are present.

---

## 0.0 — Ingest Phase 1 JSON (mandatory first step)

```python
import json, glob, os

json_files = glob.glob('/mnt/user-data/uploads/*phase1-state.json')
if not json_files:
    raise FileNotFoundError(
        "No *-phase1-state.json found in uploads. "
        "Upload the JSON produced by Phase 1 v2.0 Step 6."
    )
json_path = json_files[0]

with open(json_path, 'r', encoding='utf-8') as f:
    phase1 = json.load(f)

inclist     = phase1['incList']
exclist     = phase1['excList']
clusterdefs = phase1['clusterDefs']

assert isinstance(inclist,     list) and len(inclist)     > 0, "incList is empty"
assert isinstance(exclist,     list) and len(exclist)     > 0, "excList is empty"
assert isinstance(clusterdefs, list) and len(clusterdefs) > 0, "clusterDefs is empty"
for c in clusterdefs:
    assert 'name'  in c and isinstance(c['name'],  str),  "Cluster missing 'name'"
    assert 'stems' in c and isinstance(c['stems'], list), f"Cluster '{c['name']}' missing 'stems'"
```

## 0.0b — Compute corpus_name default (mandatory; the actual question is asked later, in the combined round)

**NOTE (fixed):** `corpus_name` was used throughout Deliverable 4 (file
path, header comment, delivery report) but never defined anywhere in this
file — a `NameError` on first real run. Fixed by computing it explicitly,
right here, as early as the JSON filename is available to suggest a
default from — not deferred to whichever step happens to need it first.

```python
default_corpus_name = os.path.basename(json_path).replace('-phase1-state.json', '')
```

**Restructured v2.32 (researcher's explicit instruction to bundle all
elicitations together):** do not send this to the researcher as its own
message here. Compute `default_corpus_name` and hold it — the actual
confirmation question is asked once, together with Step 1.3's token table
and Step 1.4's Deliverable 8 term, in a single combined message. Proceed
through Step 0.1 and Step 1 first; nothing in either depends on
`corpus_name` being confirmed yet. Every later step and deliverable
filename in this skill uses whatever value is confirmed in that combined
message — never the default silently, and never sent as a premature
standalone question here.

## 0.1 — Ingest stop.en.smart.txt

**NOTE (fixed):** a real test run found `stop.en.smart.txt`'s first line
is a comment/attribution header (e.g. `# see http://...`), which this
load code did not filter -- while the merged-output writer (Step 7.1)
*does* filter `#`-prefixed lines. That asymmetry silently counted the
header as a real stopword term on input, then dropped it asymmetrically
on output, producing a write/reload length mismatch. This was found and
worked around live in that session; it was never actually fixed here
until now:

```python
smart_files = glob.glob('/mnt/user-data/uploads/stop.en.smart.txt')
if not smart_files:
    raise FileNotFoundError("stop.en.smart.txt not found in uploads.")

with open(smart_files[0], 'r', encoding='utf-8') as f:
    smart_terms = [line.strip().lower() for line in f
                   if line.strip() and not line.strip().startswith('#')]

print(f"stop.en.smart.txt loaded: {len(smart_terms)} terms")
```

Report to the user:

```
Phase 1 JSON loaded:
  File           : [filename]-phase1-state.json
  incList stems  : <N> stems  (e.g. abilit*, accurate*, ...)
  excList terms  : <N> terms
  Clusters       : <N> clusters
    . <cluster 1 name> (<N> stems)
    . ...

stop.en.smart.txt loaded: <N> terms
```

Do not proceed until both files are successfully loaded and validated.

---

## 1. Derive C[nn] Tokens

For each cluster, derive a Voyant-safe `@Category` query token using the
pattern `C[nn][FirstWord]`, where:

- `nn` is a zero-padded two-digit sequential numeral (01, 02, …)
  assigned in Phase 1 cluster order.
- `FirstWord` is the first content word of the Phase 1 cluster name,
  in Title-case.

### 1.1 — First-word extraction rules

**NOTE (fixed, v2.16):** real bug found running this against a real Phase
1 cluster name ("Philosophical/Methodological Apparatus," from a test
corpus). The delimiter
regex split on whitespace, hyphen, em-dash, comma, and ampersand, but not
`/` — so "Philosophical/Methodological" was treated as a single word,
producing the invalid token `C11Philosophical/methodological` (a literal
slash embedded in what must be a clean JS identifier / Voyant `@Category`
token). Fixed by adding `/` to the delimiter class; re-verified against
the real 12-cluster set this bug was found in: correctly splits into
`Philosophical`, `Methodological`, `Apparatus`, producing `C11Philosophical`.

```python
import re

SKIP_WORDS = {
    'a', 'an', 'the',
    'of', 'in', 'on', 'at',
    'and', 'or', 'but',
}

def derive_token(nn, cluster_name):
    words = re.split(r'[\s\-—,/&]+', cluster_name.strip())
    words = [w for w in words if w]
    first = words[0] if words else ""
    flag_reason = None

    if first.lower() in SKIP_WORDS:
        content_words = [w for w in words if w.lower() not in SKIP_WORDS]
        if content_words:
            first = content_words[0]
            flag_reason = (
                f'First word "{words[0]}" is a non-content word. '
                f'Auto-corrected to "{first}". '
                f'Accept or supply a manual label.'
            )
        else:
            first = "Cluster"
            flag_reason = (
                f'No content word found in "{cluster_name}". '
                f'Manual label required.'
            )

    token_word = first if (first.isupper() and len(first) > 1) else first.capitalize()
    token = f"C{nn:02d}{token_word}"
    return token, flag_reason
```

**NOTE (fixed):** `derive_token()` was defined here but never actually called
anywhere in this file. Step 1.2 assumed a `tokens` list already existed;
Step 3 assumed every cluster dict already had a `'token'` key. Neither was
ever true — this is a function that was written and never wired up to
anything downstream of it. Fixed by actually running the derivation, once,
here, and attaching the result directly onto each cluster's own dict so
every later step (1.2, 1.3, 3, and anywhere else) reads the same confirmed
value rather than each re-deriving or assuming it independently:

```python
tokens = []
flagged = []
for nn, cluster in enumerate(clusterdefs, start=1):
    token, flag_reason = derive_token(nn, cluster['name'])
    cluster['token'] = token   # attached directly -- Step 3 and beyond
                               # read this, not a re-derivation
    tokens.append(token)
    if flag_reason:
        flagged.append((cluster['name'], token, flag_reason))
```

This mirrors the pattern already proven correct in the researcher's own
`peel2-compare` skill (a defensive `c.get('token') or <fallback derive>`),
adapted here to keep this skill's own Step 1.3 confirmation checkpoint —
the compare skill's simpler, faster version has no such checkpoint, which
is reasonable for a personal tool but not for this one.

### 1.2 — Collision detection

After deriving all tokens, check for duplicate first-word substrings
(ignoring the `nn` prefix):

```python
from collections import Counter

first_words = [token[4:] for token in tokens]
counts = Counter(first_words)
collisions = {w for w, c in counts.items() if c > 1}
```

If collisions exist, flag each affected cluster to the user and ask for a
manual label. Do not generate any output until all collisions are resolved.

### 1.3 — Report the combined elicitation round to the user and await confirmation

**Restructured v2.32 (researcher's explicit instruction: bundle every
elicitation into one round, then let the researcher wait for the finished
notebook).** This is the single message where `corpus_name` (0.0b), the
token table (this step), the Deliverable 8 companion-term choice
(1.4, immediately below), and (as of v2.52) the Voyant host are all
presented together — not four separate interruptions at four different
points in the run. Send one message shaped like:

```
Before generating anything, I need four things confirmed:

1. corpus_name (used in every deliverable's filename):
   Suggested (from the uploaded JSON filename): "<default_corpus_name>"
   Confirm this, or provide a different name.

2. Token derivation — confirm this table or supply corrections:
     nn   Token             Phase 1 name
     --   -----             ------------
     01   C01Epistemic      Epistemic concepts
     02   C02Expertise      Expertise and authority
     ...

3. [Step 1.4's own prompt text — see below]

4. Which Voyant instance are you running against? This determines the
   host every Deliverable 8 tool-iframe URL (Cell 19) points at.
   Suggested default: https://voyant.inf.puc-rio.br (the usual production
   instance this project has most often been run against).
   If you're running a local or different instance instead, give its
   base URL (e.g. http://127.0.0.1:PORT) — confirm the default explicitly
   rather than letting it pass by silently, since a wrong host produces
   no error until the researcher actually opens Cell 19 and Voyant reports
   the comparison corpus "does not exist" (a real, confirmed incident,
   2026-08-01 — see the v2.52 changelog entry).

Once these four are confirmed, I'll generate the merged stopword list
and comparison-corpus ZIP automatically and hand them to you for a single
Voyant upload round-trip. After you report back the two real Voyant IDs,
everything else — including the complete, instantiated notebook — will
be produced without any further questions.
```

Do not generate any output until the user has confirmed or corrected all
four items in this one round. **If the user supplies a manual correction
to any token, update that cluster's `cluster['token']` (and its entry in
`tokens`) immediately to match** — every later step reads
`cluster['token']` directly, so a correction that isn't written back
there would silently fail to take effect. Hold the confirmed `voyant_host`
value alongside `corpus_name` — it is not yet knowable at Step 0.0b
(unlike `corpus_name`, it has no derivable default from the uploaded
JSON), so it is proposed here with a stated default and must still be
explicitly confirmed or corrected, not silently assumed even though a
default is offered.

**Closure condition (added 2026-07-28, usability review — same shape as
Phase 2's Step 4.2 rule; extended v2.52 to the fourth item; reframed
v2.54 — see changelog).** The one-round *delivery* stays exactly as the
researcher directed in v2.32 — this does not add a turn or split the
round. A general "looks good" / "confirmed" / "proceed" does not by
itself close this round, for a factual reason, not a scrutiny one: each
of the four items — corpus_name, the token table, the Deliverable 8
pick, and the Voyant host — is a distinct piece of information this
skill genuinely cannot proceed without, so a reply silent on one of them
leaves a real gap, not an implicitly-approved default. If the reply is
silent on one, ask specifically for that missing item, the same way
you'd ask a colleague for a fact they hadn't gotten to yet — not as a
check on whether she read the message carefully. This applies with
particular force to the Voyant host: silently treating the suggested
default as accepted because the researcher didn't object is exactly the
failure mode that produced the 2026-08-01 incident this item exists to
prevent — the default needs an actual answer, not just the absence of an
objection, because the two are genuinely different pieces of
information, not because one is a more diligent response than the other.

**What this requirement is, and what it is not.** This is a completeness
requirement on four necessary inputs, not a test of how carefully the
researcher read the combined message or how closely she is monitoring
this run. Ask for whatever is missing plainly and neutrally — "I still
need [X]: confirm the suggested value, or give me a different one" —
never in a way that implies doubt about her attention or suggests she is
being checked up on. If her reply already addresses an item, even
briefly or by accepting a default in passing, that satisfies this
requirement for that item; only genuine silence on an item needs a
follow-up, and that follow-up asks for the missing fact, not for
reassurance that she looked.

### 1.4 — Elicit Deliverable 8's collocation-pair choice (asked in the same message as 1.3)

**Redesigned, v2.49**, replacing the v2.32 "pick one term, Claude derives
a companion cluster deterministically" flow. That flow is superseded
for the reasons given in Section 6b.3c's own superseded note: no
guarantee the derived pairs ever actually collocate in the source, and a
structural bias that could never select C03 as companion. This step now
drives the empirically-grounded mechanism `_build_cell19.py` already
implements, verified against real data — it presents
*real, source-confirmed* candidates and lets the researcher choose from
them, rather than asking her to pick blind and deriving the rest by
formula.

**Prerequisite, run before building this step's prompt**: load the real
cleaned source text (already a declared Phase 3 input, Section 0 — the
uploaded `*-CLEANED.txt`) and run the empirical scan:

```python
import glob

cleaned_files = glob.glob('/mnt/user-data/uploads/*-CLEANED.txt')
if not cleaned_files:
    raise FileNotFoundError(
        "No *-CLEANED.txt found in uploads -- Deliverable 8's collocation "
        "scan needs the real source text, not just the Phase 1 JSON."
    )
with open(cleaned_files[0], encoding='utf-8') as f:
    source_text = f.read()

candidates = find_source_collocations(source_text, clusterdefs, proximity_n=5)
flag_confounded(candidates)
candidate_table = format_collocation_candidates(candidates, top_n=10)
```

Fold the result into the combined message built at Step 1.3:

```
3. Deliverable 8 (the "Source vs Summary" comparison block, Cell 19)
   needs one or more real collocations from your source text, ranked by
   actual co-occurrence, not a blind pick:

<candidate_table>

   Pick one or more pairs by rank number. Rows flagged "possibly
   confounded" involve a disproportionately frequent term (e.g. a term
   appearing in nearly every sentence) -- co-occurrence with it may just
   be base rate, not a specific relationship. You can still pick a
   flagged row if you judge the specific pairing meaningful (as
   happened this same session: a flagged pair was chosen anyway after
   reviewing the real numbers) -- the flag is a data point for your
   judgment, not a rule that excludes it.

   Only the top 10 (by hit count) are shown. If none of these look
   right, just ask to see more -- I'll expand the list and re-show it
   in this same round, no need to start over.
```

**Validation**: the researcher's answer must resolve to one or more real
rows from `candidates` — by rank number (preferred, matching the table
shown) or by naming the actual terms. Do not accept a pair that isn't in
`candidates` (there is no "derive it anyway" fallback here, unlike the
old flow — if the researcher wants a pair with zero real co-occurrences,
say so plainly and ask her to either accept that the comparison will be
testing a relationship absent from the source, or pick a real one).

**"Show more" handling (v2.51):** if the researcher asks to see more
candidates instead of picking from the initial ten, re-run
`format_collocation_candidates(candidates, top_n=<N>)` with a larger
`top_n` (her stated number, or the full `len(candidates)` if she just
says "show me all of them" / doesn't give a number) and re-present the
expanded table in the same round-trip -- do not silently raise the
default for future runs, and do not drop or reorder rows already shown.
This is not a fallback derivation: every row in the expanded table is
still a real, source-confirmed candidate from the same `candidates`
list, just more of it. Repeat if she asks again.

Hold the researcher's confirmed `selected_pairs` (a list of the actual
chosen dicts from `candidates`, not just term names) and `source_text`
itself for Step 7.6's Deliverable 8 assembly — `build_cell19_content()`
needs both directly, since `source_text` is re-tokenized there to
resolve any wildcard-shaped term in the selected pairs to its real
literal forms (see `resolve_literal_forms()`; a wildcard cannot appear
inside a proximity phrase at all, a hard platform constraint, not a
style choice).

---

## 2. Assign Tableau20 Colours

Assign colours sequentially from the Tableau20 palette in Phase 1 cluster
order. Colours are hardcoded as hex — Voyant does not accept palette names.

```python
TABLEAU20 = [
    "#4E79A7",  # T20-01 steel-blue
    "#F28E2B",  # T20-02 orange
    "#E15759",  # T20-03 red
    "#76B7B2",  # T20-04 teal
    "#59A14F",  # T20-05 green
    "#EDC948",  # T20-06 gold
    "#B07AA1",  # T20-07 mauve
    "#FF9DA7",  # T20-08 pink
    "#9C755F",  # T20-09 brown
    "#BAB0AC",  # T20-10 warm-gray
    "#499894",  # T20-11 dark-teal
    "#A0CBE8",  # T20-12 light-blue
    "#FFBE7D",  # T20-13 light-orange
    "#FF9D9A",  # T20-14 light-red
    "#86BCB6",  # T20-15 light-teal
    "#8CD17D",  # T20-16 light-green
    "#F1CE63",  # T20-17 light-gold
    "#D4A6C8",  # T20-18 light-mauve
    "#FABFD2",  # T20-19 light-pink
    "#D7B5A6",  # T20-20 light-brown
]
```

**NOTE (fixed):** this section defined the palette but never actually
assigned a colour to any cluster — the exact same bug pattern as Step 1's
`derive_token()`, in the very next step, missed on the first pass and only
caught on a deliberate fresh re-read of the whole file. Deliverable 1's JS
(`color: cluster.color`), Deliverable 2's HTML legend (`hex_to_rgb`), and
Deliverable 5's report all read `cluster['color']` — none of it existed
anywhere. Fixed the same way as Step 1, attached directly onto each
cluster's own dict:

```python
for i, cluster in enumerate(clusterdefs):
    cluster['color'] = TABLEAU20[i % len(TABLEAU20)]
```

If the number of clusters exceeds 20, flag to the user and ask how to
proceed before generating any output.

---

## 3. Identify Cross-Cluster Stems

Scan all clusterDefs for stems appearing in more than one cluster. These are
intentional analytical choices from Phase 1 and must be preserved exactly.
Document them in the Cell 1 file header.

```python
from collections import defaultdict

stem_to_clusters = defaultdict(list)
for cluster in clusterdefs:
    for stem in cluster['stems']:
        stem_to_clusters[stem].append(cluster['token'])

cross_cluster = {
    stem: clusters
    for stem, clusters in stem_to_clusters.items()
    if len(clusters) > 1
}
```

---

## 4. Deliverable 1 — Configuration Cells (Cell 0 + Cell 1)

**Do not generate this deliverable until Step 7.3–7.4 is complete and
`voyant_stoplist_id` is confirmed** — Cell 0 requires the real value.
See "Execution order" above.

**Filename:** `[name]-cell-config.js`

The configuration is split across two sequential Spyral cells. Both are
written to the same file, clearly delimited. Cell 0 must be run before Cell 1.
Because Spyral cells share a single JS scope within a notebook, `excListFull`
declared in Cell 0 is visible in Cell 1 and all subsequent tool cells.

### 4.1 — Cell 0: Global Voyant-confirmed values (both stoplist ID and comparison-corpus ID, kept in their own cell)

**NOTE (fixed):** Cell 0 previously shipped with a placeholder
(`"PASTE-STOPLIST-ID-HERE"`) for the researcher to complete alone, later,
with nothing verifying it happened correctly. Fixed per Step 7.3/7.4: the
real ID is now confirmed with the researcher, validated, and baked in
directly, before this cell is generated at all. Cell 0 stays a separate
cell from Cell 1 regardless — isolating these values still protects
against a researcher re-running things out of order later, even though
the reason they were originally unknowable no longer applies once this
checkpoint exists.

**Fix (v2.19):** `voyant_comparison_corpus_id` was added to Step
7.3/7.4's checkpoint, validation, and pre-generation checklist, and to
the notebook's own Cell 11 for this deliverable, to hold both values
together. But this section's own code template was not updated to
match: it still only emitted `excListFull`, never `myComparisonCorpus`
— an instance of the "checkpoint/prose updated, code template silently
not" bug class this file otherwise guards against. Fixed by adding the
second variable to the same cell (`cell11-injection.js`).

```javascript
// ════════════════════════════════════════════════════════════════════════════
// CELL 0 — Global Voyant-confirmed values (confirmed with the researcher during generation)
// ════════════════════════════════════════════════════════════════════════════
//
// Both values below were assigned by Voyant when the corresponding file was
// uploaded, and confirmed with the researcher before this notebook was
// generated -- neither is a placeholder. If you ever re-upload a different
// stopword file or rebuild the comparison corpus, Voyant will assign new
// IDs -- update the two lines below to match before running this cell again.
//
// Global -- both variables are available in all subsequent cells once this runs.

var excListFull = "{voyant_stoplist_id}";
var myComparisonCorpus = "{voyant_comparison_corpus_id}";

show("excListFull: " + excListFull);
show("myComparisonCorpus: " + myComparisonCorpus);
```

### 4.2 — Cell 1: incList + clusterDefs + Spyral instantiation

Cell 1 contains the remaining three components. It reads `excListFull` as
an already-declared global from Cell 0.

**v2.35 — `catsId` is now a third Voyant-confirmed value, obtained the
same way as `voyant_stoplist_id`/`voyant_comparison_corpus_id`, before
this cell can be generated.** Cell 19's iframes (Deliverable 8) need a
real, already-existing `catsId` baked into their src URLs at generation
time — not knowable if Cell 1 has never actually run in Voyant. Generate
`[corpus_name]-catsId-scratch-cell.js` (the `Spyral.Categories()`
creation logic below, using the real `clusterDefs` already derived,
wrapped in throwaway variable names) and ask the researcher to paste it
into any empty code cell in her live notebook and run it once — the same
"data collection notebook" pattern Phase 1 already uses for values Claude
cannot obtain any other way. Once she reports the real `catsId` back,
generate Cell 1 with that value baked in directly, exactly like Cell 0's
`excListFull`/`myComparisonCorpus` — never with a fresh `cats.save()`
call, which would create a second, different Categories object and
orphan Cell 19's already-generated iframes. See the v2.35 changelog entry
for the full incident this closes.

**v2.39 note:** the token-legend comment and every `clusterDefs` entry's
inline `// <Phase 1 name>` comment below are literal JS comment text
inside a code cell, not HTML -- build them from the raw `c['name']`
value directly, never through `esc()`. See Section 6.3's
`build_category_comment_block()` and its accompanying changelog entry
for the real bug this closes (found live in the that later pilot test notebook:
cluster names containing `&` were HTML-escaped to `&amp;` inside this
cell's own comments).

```javascript
// ════════════════════════════════════════════════════════════════════════════
// CELL 1 — incList, clusterDefs, Spyral Categories
// ════════════════════════════════════════════════════════════════════════════

// ── 2.2  INCLUSION LIST ──────────────────────────────────────────────────────
// Significant stems in wildcard form.
// Global — available immediately in all cells.

var incList = [
"stem1*", "stem2*", ...   // 8 stems per line, alphabetical order
];

show("incList loaded: " + incList.length + " significant stems");

// ── CATEGORY INJECTION — generated by new-peel-phase3 ────────────────────────
//
// Token legend (C[nn]FirstWord → full Phase 1 name):
//   C01Token   → Full Phase 1 cluster name
//   ...
//
// Colour assignment: Tableau20 hex, sequential by Phase 1 cluster order.
// Cross-cluster stems (intentional):
//   <stem>  → C[nn1]Token, C[nn2]Token
//   ...
//   (none)  ← if no cross-cluster stems exist
// ─────────────────────────────────────────────────────────────────────────────

// Tableau20 palette reference (hardcoded — Voyant does not accept palette names)
// T20-01 #......  T20-02 #......  ...

var clusterDefs = [
  { name: "C01Token",  color: "#......", // T20-01 description  // Full Phase 1 name
    terms: ["stem1*", "stem2*", ...] },
  ...
];

// ── Spyral instantiation ──────────────────────────────────────────────────────
// v2.35: catsId is a Voyant-confirmed value, not created dynamically here.
// The categories above were already created and saved once, in a scratch
// test cell run directly in Voyant, before this notebook was generated --
// re-running cats.save() here would create a SECOND, different Categories
// object with a new ID, orphaning Cell 19's iframes (which need this exact,
// already-baked-in ID). Matches Cell 0's excListFull/myComparisonCorpus
// pattern: confirmed once, referenced directly, never re-derived.
var catsId = "{confirmed-catsId}";
show("catsId: " + catsId);
show(">>> Categories already created in Voyant; catsId is set. <<<");
```

**Scratch-cell template** (generate and hand to the researcher before this
cell, per the v2.35 note above — not part of the delivered notebook
itself):

```javascript
// ── SCRATCH TEST CELL -- category creation only, to obtain a real catsId
// ahead of the final notebook build. Paste into any empty code cell in
// your live Voyant notebook (myCorpus already loaded) and run once.

var testClusterDefs = [ /* same clusterDefs as above */ ];

var testCatsId = "";
var testCats = new Spyral.Categories();
testClusterDefs.forEach(function(cluster) {
  testCats.addCategory(cluster.name);
  testCats.addFeature(cluster.name, "color", cluster.color);
  cluster.terms.forEach(function(term) { testCats.addTerm(cluster.name, term); });
});

testCats.save().then(function(id) {
  testCatsId = id;
  show("catsId: " + testCatsId);
  show(">>> Copy this catsId and report it back. <<<");
});
```

### 4.3 — Formatting rules

**NOTE (fixed):** a real test run found that Phase 1's `incList` can
contain multi-word phrase entries already wrapped in literal embedded
quote characters (Voyant's own phrase-query syntax, e.g. `"machine
learning"` as a single incList entry, quotes included). Naively
wrapping every entry in another pair of quotes (`f'"{term}"'`) produces
invalid JS -- `""machine learning""`, an empty string followed by
garbage, not a valid string literal. This was found and worked around
live in that session; it was never actually fixed here until now.

Use `json.dumps()` for every `incList` entry — JSON string escaping is a
strict, correct subset of JS string-literal escaping, so it handles
embedded quotes (and any other special characters) correctly regardless
of whether a given entry happens to contain them:

```python
import json

def inclist_js_lines(inclist, per_line=8):
    """Formats incList as JS string literals, 8 per line, correctly
    escaping any embedded quote characters -- never naive re-quoting."""
    quoted = [json.dumps(term) for term in sorted(inclist)]
    lines = []
    for i in range(0, len(quoted), per_line):
        lines.append('  ' + ', '.join(quoted[i:i+per_line]) + (',' if i+per_line < len(quoted) else ''))
    return '\n'.join(lines)
```

- Cell 0 and Cell 1 are delimited by a `// ═══...` banner comment and a
  blank line. Both are written to the same `[name]-cell-config.js` file.
- `incList` array: use `inclist_js_lines()` above — 8 stems per line,
  alphabetical order, correctly quoted (never naive `f'"{term}"'`).
- `clusterDefs` entries: one object per cluster; `terms` array on a single
  line immediately following the opening brace.
- Inline comment per entry: `// T20-NN description  // Full Phase 1 name`
- Token legend: aligned so the `→` column lines up across all entries.
- Cross-cluster section: one line per stem; write `(none)` if none exist.
- `cats.save()` callback MUST use `function(id)` — never `function(saved)
  { saved.id }`.
- `catsId` MUST be declared as `""` before the async call.

---

## 5. Deliverable 2 — HTML: Colour Legend

**Held until after Step 7.3–7.4, as part of the single Round 2 batch —
not because this deliverable has a data dependency on
`voyant_stoplist_id` (it doesn't; it only needs tokens and colours from
Steps 1–2). It's batched with the rest because the researcher can't
productively use any notebook cell until Cell 0 is set up regardless, so
delivering everything together avoids an unnecessary third round.**

**Filename:** `[name]-colour-legend.html`

**v2.12 fix — this deliverable previously had no actual generation
code, only the HTML shape shown below as a template.** That meant every
real run had to improvise the row-building live, with no escaping
guidance — confirmed as the source of unescaped `&` in cluster names
(e.g. "Virtue & Character", "AI & Technology") that broke Voyant's
upload parser. `build_colour_legend_html()` below is the real,
escaping-safe implementation; the HTML block after it is the literal
shape it produces (reference only, not something to hand-fill):

**Fix (v2.23):** the
first `<td>` of every row — clearly intended as a colour swatch, given
its position directly before the colour-tinted category label — was
never actually given a `background-color`. It rendered as an empty
padded cell holding only `&nbsp;`, so the delivered legend showed
colour *only* via the text label's font colour, never an actual
swatch. Also present, identically,
in `build_cluster_color_table_html()`'s row loop below (Cell 7's
cluster table) — same code pattern, same missing style, fixed there
too, not just here. Fixed by adding `background-color: rgb({r}, {g},
{b})` plus a small fixed `width` and `border-radius` to that `<td>`,
turning it into an actual visible colour chip next to each label.

**Fix (v2.24):** this
function was also missing the AI-provenance flag — the small orange
(`#FFA040`) swatch table already established as this project's
standing marker for cells carrying AI-selected/AI-assembled content
(Cell 5's `build_cell5_content()`, Cell 8's `_build_cell8.py`). Cell
13's cluster names and colour assignments are Phase 1/Phase 3
AI-selected content, not purely mechanical typesetting, so the same
flag applies here too. Fixed by prepending the same
flag-table markup, followed by a `<h1>&nbsp;</h1>` spacer (matching
Cell 8's convention, since Cell 13's own first heading is also an
`<h1>`) to clear the floated table before the real heading — this
particular spacer choice is a judgement call, not something dictated
by an existing rule; Cell 5 uses an `<h2>&nbsp;</h2>` spacer instead,
because its own next heading is different. Flagged as such rather than
decided silently.

```python
def hex_to_rgb(h):
    h = h.lstrip('#')
    return tuple(int(h[i:i+2], 16) for i in (0, 2, 4))

def build_colour_legend_html(clusters_ordered, tableau20_palette, title, author):
    """clusters_ordered: list of cluster dicts in Phase 1 order, each
    with 'token', 'name', 'color' (hex) already set (Steps 1-2).
    tableau20_palette: the same TABLEAU20 list from Step 2 -- the
    description text is just that colour's position in the palette
    (e.g. 'Tableau20-03'); Step 2's own inline comments (e.g. 'red') are
    source-code annotations, not retrievable at runtime, so aren't
    fabricated here.
    title, author: from Phase 2's own parse_summary_txt() output (v2.18),
    already computed earlier in populate_notebook()'s assembly sequence
    for Cell 5 -- reused here rather than re-derived. (v2.34 fix: this
    function previously rendered literal '[Author (Year)]'/'[Title]'
    placeholders on the stale claim that no structured author/title input
    existed anywhere in this skill; that stopped being true once
    parse_summary_txt() was added. Cell 2's full bibliographic citation
    remains genuinely out of scope -- this is only the plain title/author
    pair, not a formatted citation.) Falls back to the old placeholder
    text if either string is empty, rather than rendering a blank line."""
    title = title or '[Title]'
    author = author or '[Author (Year)]'
    rows = []
    for c in clusters_ordered:
        r, g, b = hex_to_rgb(c['color'])
        tableau_label = f"Tableau20-{tableau20_palette.index(c['color']) + 1:02d}"
        rows.append(
            '<tr>'
            f'<td style="padding: 5px 12px 5px 0px; background-color: rgb({r}, {g}, {b}); '
            'width: 14px; border-radius: 3px;">&nbsp;</td>'
            f'<td style="padding: 5px 12px 5px 0px; color: rgb({r}, {g}, {b}); font-weight: bold;">'
            f'{esc(c["token"])} &mdash; {esc(c["name"])}</td>'
            '<td style="padding: 5px 0px; color: rgb(136, 136, 136); font-size: 12px;">'
            f'<code>{esc(c["color"])}</code>&nbsp;&mdash; {esc(tableau_label)}</td>'
            '</tr>'
        )
    return (
        '<table align="left" border="2" cellpadding="3" cellspacing="1" style="width: 50px;">\n'
        '\t<tbody>\n\t\t<tr>\n\t\t\t<td style="background: #FFA040; width: 50px;">&nbsp;</td>\n'
        '\t\t</tr>\n\t</tbody>\n</table>\n\n'
        '<h1 style="line-height:1.2em;">&nbsp;</h1>\n\n'
        '<div style="font-family:Georgia,serif;max-width:820px;margin:0 auto;'
        'padding:0 0 4rem;line-height:1.85;color:#1c1a18;">\n'
        '<h1 style="font-family:system-ui,sans-serif;font-size:1.3rem;font-weight:700;'
        'line-height:1.2em;margin:0 0 0.3rem;color:#1c1a18;">Color Coding for Categories</h1>\n'
        '<h3 style="font-family: &quot;Times New Roman&quot;;">Semantic Category Colour Legend</h3>\n'
        f'<p style="font-family: &quot;Times New Roman&quot;;">{esc(author)} &mdash;&nbsp;<em>{esc(title)}</em><br />\n'
        f'{len(clusters_ordered)} clusters &middot; Tableau20 palette &middot; colours assigned via&nbsp;<code>cats.addFeature()</code></p>\n'
        '<table style="border-collapse: collapse; font-family: serif; font-size: 14px;">\n'
        '  <tbody>\n' + '\n'.join(f'    {row}' for row in rows) + '\n  </tbody>\n</table>\n'
        '</div>'
    )
```

Reference shape (one row shown; the function above produces one such row
per cluster, in Phase 1 order, all text pre-escaped):

```html
<tr>
  <td style="padding: 5px 12px 5px 0px;">&nbsp;</td>
  <td style="padding: 5px 12px 5px 0px; color: rgb(<R>, <G>, <B>); font-weight: bold;">C[nn]Token &mdash; Full Phase 1 name</td>
  <td style="padding: 5px 0px; color: rgb(136, 136, 136); font-size: 12px;"><code>#XXXXXX</code>&nbsp;&mdash; Tableau20-NN description</td>
</tr>
```

---

## 6. Deliverable 3 — JS2–JS11: Tool Cells File

**Held until after Step 7.3–7.4, as part of the single Round 2 batch —
same reasoning as Deliverable 2: no direct data dependency on
`voyant_stoplist_id` (`stopList: excListFull` is a variable reference,
not the literal value), batched purely so the researcher isn't handed
files they can't use until Cell 0 exists.**

**Filename:** `[name]-cells-tools.js`

**All 8 remaining Distant Reading tool cells** are written to a single file
in notebook order, separated by a blank line between cells. The user pastes
the whole file and splits at the `// ──` headers. (**Corrected v2.32**: this
file's own frontmatter and Cell-ownership table, line ~2748, already
documented that Summary and Documents were relocated out of this single-
document block into Deliverable 8's Cells 15–18 — but this section's own
JS3/JS11 blocks were never actually removed to match, a real "prose
updated, template silently not" gap of exactly the kind this project's
changelog repeatedly warns about. Removed here; see the note after JS2
below.)

### 6.1 — Notebook order and tool specifications

**JS2 — Reader**

**Fix (v2.27):** every tool
cell from JS2 onward (Reader through CorpusTerms, i.e. every notebook
tool cell from position 20 onward in this notebook's macro-restructured
order) was missing `palette: "Tableau20",` — Cell 13's colour legend
promises a specific Tableau20 palette, but nothing told the tools
themselves to actually render with it, so no tool used the configured
colour coding at all. Fixed by adding
`palette: "Tableau20"` to every tool's `config` object, right before the
closing `}`, mechanically, without per-cell specification. **Note left
for the researcher, not silently resolved**: JS2, JS4, JS9, and JS10
(Reader, Cirrus, Phrases, CorpusTerms) set `categories: "none"` —
deliberately, per each one's own existing comment, "to cancel Voyant's
default category colouring." With no categories active, `palette` has
nothing to colour and is effectively a no-op in those four tools (though
harmless to include, matching the literal instruction to add it to every
cell from 20 onward). Only JS5–JS8 (Trends, Bubblelines, CollocatesGraph,
Contexts) have `categories: catsId` active and are where this fix has a
visible effect.

```javascript
// ── READER ────────────────────────────────────────────────────────────────────

let config = {
  lang:       "en",
  categories: "none",  // Explicitly cancel Voyant's default category colouring
  query:      incList,
  height:     450,
  palette:    "Tableau10",
};
loadCorpus(myCorpus).tool("Reader", config);
```

**JS3 — Summary: REMOVED (v2.32), relocated, not duplicated.** The
single-document Summary tool cell that used to live here was moved to
Cell 17/18 (Deliverable 8, Section 6b.2, `build_cell17_content()` /
`build_cell18_content()` in `_build_cell19.py`) and rewired to
`myComparisonCorpus` — it is not generated a second time in this file.
Do not re-add a `myCorpus`-based Summary block here; that would give the
notebook two Summary cells doing overlapping work, one of them stale.

**JS4 — Cirrus**

**Fix (v2.21):** `whiteList: incList`
was removed. Voyant's Cirrus `whiteList` parameter only matches single-word
terms — every multi-word entry in `incList` (the confirmed Phase 1 phrases,
e.g. `"black box"`, `"ai systems"`) was being silently dropped, with no
error and no visible sign anything was wrong, confirmed by live testing in
Voyant. Keeping `whiteList` in would give
a misleading impression of filtering that wasn't actually happening for
most of `incList`'s content, so it's removed rather than worked around —
Cirrus now shows its natural term frequencies, filtered only by `stopList`.

```javascript
// ── CIRRUS ────────────────────────────────────────────────────────────────────

let config = {
  lang:       "en",
  categories: "none",  // Explicitly cancel Voyant's default category colouring
  visible:    100,
  stopList:   excListFull,
  palette:    "Tableau10",
};
loadCorpus(myCorpus).tool("Cirrus", config);
```

**JS5 — Trends**
```javascript
// ── TRENDS ───────────────────────────────────────────────────────────────────
// Available @Category queries for this corpus:
//   "@C01Token"    Full Phase 1 name
//   ...            (all clusters listed)

let config = {
  lang:              "en",
  categories:        catsId,
  query:             ["@C01Token", "@C02Token", "@C03Token"],
  withDistributions: "relative",
  chartType:         "barline",
  bins:              5,
  palette:           "Tableau10",
};
loadCorpus(myCorpus).tool("Trends", config);
```

**JS6 — Bubblelines**
```javascript
// ── BUBBLELINES ───────────────────────────────────────────────────────────────
// Available @Category queries for this corpus:
//   "@C01Token"    Full Phase 1 name
//   ...            (all clusters listed)

let config = {
  lang:       "en",
  categories: catsId,
  query:      ["@C01Token", "@C02Token", "@C03Token"],
  bins:       5,
  palette:    "Tableau10",
};
loadCorpus(myCorpus).tool("Bubblelines", config);
```

**JS7 — CollocatesGraph**

**FIXED (v2.28, researcher's instruction, 2026-07-19):** `limit` and `context`
are now set explicitly rather than left to Voyant's implicit defaults — per
`Tools.CollocatesGraph.html`, `limit` defaults to 5 (not the `7` this
template previously hardcoded, changed to match the documented default
rather than silently kept) and `context` defaults to 5 (previously omitted
entirely). Both are restated explicitly, at their documented default values,
so a reader of this cell's config never has to check Voyant's own docs to
know what window/count is actually in effect.

```javascript
// ── COLLOCATES GRAPH ──────────────────────────────────────────────────────────
// Available @Category queries for this corpus:
//   "@C01Token"    Full Phase 1 name
//   ...            (all clusters listed)

let config = {
  lang:       "en",
  categories: catsId,
  query:      ["@C01Token", "@C02Token", "@C03Token"],
  limit:      5,  // explicit restatement of Voyant's own documented default
  context:    5,  // explicit restatement of Voyant's own documented default
  palette:    "Tableau10",
};
loadCorpus(myCorpus).tool("CollocatesGraph", config);
```

**JS8 — Contexts**

**Fix (v2.22):** the `query`
array's second and third slots were shipped as literal, un-substituted
template placeholders (`"term*"`, `"term1|term2|term3"`) in the delivered
an earlier test corpus artifact — meaningless generic text, not real corpus content.
**When actually generating a specific corpus's deliverable, these two
slots must be filled with real stems, terms, and/or N-grams arbitrarily
picked from that corpus's own `incList`** — the same discipline already
applied to `@C01Token` (real cluster tokens, never left generic). Pick a
real wildcard-form stem for the second slot, and mix at least one single
term with at least one N-gram/phrase for the third slot, so the example
actually demonstrates Contexts' query syntax variety (stem wildcard,
single term, multi-word phrase) using content the researcher will
recognize from her own corpus.

**Real quoting rule, added v2.48 — this had no real code either, only
prose telling a live improviser what content to pick, not how to
correctly embed it.** Live improvisation filled the third slot with
`"ai|consultants|jagged frontier"` — a plain, double-quoted JS string
with the N-gram `jagged frontier` embedded bare, unquoted. This is wrong
two ways at once: Voyant treats an unquoted multi-word run inside an
OR-pattern as separate word searches, not a phrase, so the N-gram
wouldn't actually search as a phrase even if the JS parsed; and it
doesn't parse anyway, since the outer JS string already uses double
quotes, leaving no way to also wrap the N-gram in its own literal double
quotes without ending the string early. The applicable rule, confirmed
for Contexts (other tools not yet
checked): **when an OR-pattern query expression contains an embedded
quoted N-gram, the containing JS string must use single quotes as its
outer delimiter — the reverse (double quotes outside, single inside, or
no inner quoting at all) does not work.**

```python
def build_contexts_default_query_slot(terms):
    """Builds JS8's third query-array element: an OR-pattern combining a
    mix of plain terms/stems and N-grams from incList. Each N-gram term
    is passed in already carrying its own literal double quotes (Phase
    1's storage convention, e.g. '"jagged frontier"') -- embedded as-is,
    never stripped, since the quotes are what makes Voyant treat it as a
    phrase rather than separate word searches. If any term in the mix is
    an N-gram, the whole JS string must be single-quoted (the researcher's
    confirmed rule); with no N-gram present, a plain double-quoted JS
    string is fine and more conventional."""
    combined = '|'.join(terms)
    has_ngram = any(t.startswith('"') for t in terms)
    return f"'{combined}'" if has_ngram else f'"{combined}"'
```

```javascript
// ── CONTEXTS ──────────────────────────────────────────────────────────────────
// Available @Category queries for this corpus:
//   "@C01Token"    Full Phase 1 name
//   ...            (all clusters listed)

let config = {
  lang:       "en",
  categories: catsId,
  query:      ["@C01Token", "<REAL_WILDCARD_STEM_FROM_INCLIST>", <BUILD_CONTEXTS_DEFAULT_QUERY_SLOT_OUTPUT>],
  // columns: ["left","term","right","position"],
  columns:    ["left","term","right"],
  context:    8,
  expand:     100,
  sort:       "right",
  dir:        "asc",
  termColors: "terms",
  palette:    "Tableau10",
};
loadCorpus(myCorpus).tool("Contexts", config);
```

**JS9 — Phrases**
```javascript
// ── PHRASES ───────────────────────────────────────────────────────────────────

let config = {
  lang:          "en",
  categories:    "none",
  columns:       ["term", "rawFreq", "length"],
  minLength:     2,
  maxLength:     5,
  overlapFilter: "rawFreq",
  sort:          "rawFreq",
  dir:           "desc",
  // query:         incList,  // You can uncomment this line, but in some cases this may raise "OutOfMemoryError" exception.
  palette:       "Tableau10",
};
loadCorpus(myCorpus).tool("Phrases", config);
```

**JS10 — CorpusTerms**

**Comment header corrected v2.32, real mismatch found by end-to-end
execution:** the researcher's own live notebook (session of 2026-07-19)
has this cell's comment header renamed to "Document Terms" — the paired
text cell (Cell 34) was renamed to match, since this notebook's macro
restructuring made the block single-document-only, and "Corpus Terms"
vs. "Document Terms" are Voyant's own two separate-but-equivalent labels
for this case. That live rename was applied directly to
`an earlier test corpus-cells-tools.js` at the time but never ported back into
this template — this skill kept generating `// ── CORPUS TERMS ──`, which
would silently mismatch `TOOL_CELL_IDS`'s corresponding `'DOCUMENT TERMS'`
key (see below) the next time this section was actually followed to
generate a fresh file, exactly the "live edit made, template not updated
to match" gap this project's changelog repeatedly names. The underlying
Voyant API call remains `.tool("CorpusTerms", ...)` — that is Voyant's
real, non-renameable tool identifier, not a display string, and is
unaffected by this fix.

```javascript
// ── DOCUMENT TERMS ────────────────────────────────────────────────────────────
// Available @Category queries for this corpus:
//   "@C01Token"    Full Phase 1 name
//   ...            (all clusters listed)

let config = {
  lang:       "en",
  categories: "none",
  columns:    ["term", "rawFreq", "relativeFreq", "relativePeakedness", "relativeSkewness", "distributions"],
  query:      incList,
  palette:    "Tableau10",
};
loadCorpus(myCorpus).tool("CorpusTerms", config);
```

**JS11 — Documents: REMOVED (v2.32), relocated, not duplicated.** The
single-document Documents tool cell that used to live here was moved to
Cell 15/16 (Deliverable 8, Section 6b.2, `build_cell15_content()` /
`build_cell16_content()` in `_build_cell19.py`) and rewired to
`myComparisonCorpus` — it is not generated a second time in this file.
Do not re-add a `myCorpus`-based Documents block here; that would give
the notebook two Documents cells doing overlapping work, one of them
stale.

### 6.2 — Tool parameter reference table

**`whiteList` column removed (v2.21)** — it was Cirrus-only, and that usage
is now removed too (Voyant's Cirrus `whiteList` silently drops multi-word
terms; see JS4 above). No tool in this table uses `whiteList` any longer.
**Summary and Documents rows removed (v2.32)** — both tools were relocated
to Deliverable 8 (Cells 15–18), which has its own fixed, non-varying
config (see 6b.2), so they no longer belong in this table of Deliverable
3's per-corpus-varying parameters.

| Tool | `query` | `categories` | `stopList` |
|---|---|---|---|
| Reader | `incList` | `"none"` | omit |
| Cirrus | none | `"none"` | `excListFull` |
| Trends | `@Category` array | `catsId` | omit |
| Bubblelines | `@Category` array | `catsId` | omit |
| CollocatesGraph | `@Category` array | `catsId` | omit |
| Contexts | mixed | `catsId` | omit |
| Phrases | `incList` | `"none"` | omit |
| CorpusTerms | `incList` | `"none"` | omit |

### 6.3 — @Category comment block rule

Tools that accept `@Category` queries carry a comment block listing ALL
`@C[nn]Token` values with their full Phase 1 names. The active `query` array
is a user-adjustable subset. Default active query for Trends, Bubblelines,
and CollocatesGraph: first three clusters in Phase 1 order.

**Added v2.39 (a later pilot test, 2026-07-23) — this was
prose-only, no real code, the same "disguised as done" gap this file's
own changelog already names for Cell 13 (pre-v2.12) and Phase 2's
cluster-coverage table (v3.24).** Because nothing here defined how to
actually build this comment block, a live run had to improvise it, and
did so by routing cluster `name` values through this file's `esc()`
HTML-escaping helper -- correct for every other use of `esc()` in this
file (all of which build HTML text), but wrong here: this comment block
lives inside a `<pre class='notebook-code-editor-raw...'>` code cell,
which holds literal JS source, not HTML markup. A real Spyral round-trip
confirmed this empirically -- Spyral's own import/export stores this
content literally (`&` not `&amp;`), never HTML-entity-escaped, in every
code cell checked. The wrong escaping produced `&amp;`-laden JS comments
in the delivered that later pilot test notebook (Cells 1, and Trends/Bubblelines/
CollocatesGraph/Contexts/CorpusTerms), found and corrected in place
during Step 8.5's post-delivery checkpoint -- flagged as a real,
confirmed bug, not yet confirmed as the specific cause of the "error
parsing the input of the document" warning the researcher hit (see the
v2.38 changelog entry for the other candidate, `<tbody>`, ruled out by
itself as sufficient).

```python
def build_category_comment_block(clusters_ordered):
    """Shared comment-only reference listing every @Category token,
    identical across Deliverable 3's category-aware tool cells (Trends,
    Bubblelines, CollocatesGraph, Contexts) and CorpusTerms/Document
    Terms (informational only there -- it uses query: incList, not
    categories). This is literal JS comment text inside a code cell's
    raw <pre class='notebook-code-editor-raw...'> content -- cluster
    names must NOT be routed through esc() or any other HTML-escaping
    here, unlike every HTML-text builder elsewhere in this file."""
    lines = ['// Available @Category queries for this corpus:']
    for c in clusters_ordered:
        lines.append(f'//   "@{c["token"]}"    {c["name"]}')
    return '\n'.join(lines)
```

The same rule applies to Cell 1's token-legend comment (Section 4.2) and
`clusterDefs`' own inline `// <Phase 1 name>` comments -- both are
literal JS comment text, not HTML, and must use the raw `c['name']`
value directly, never `esc(c['name'])`.

---

## 6b. Deliverable 8 — Source vs. Summary Comparison Cells (14–20)

**Added v2.29, 2026-07-21, after a full session of live design and real-Voyant
verification against the an earlier test corpus test case.** This deliverable produces
the "Source vs Summary" block that sits immediately after the configuration
cells (11–13) and before the Distant Reading tool cells: Cell 14 (fixed
intro), Cells 15–18 (Documents and Summary, rewired to the comparison
corpus), Cell 19 (the five-tool comparison pattern — the substantive part of
this deliverable), and Cell 20 (an empty code cell paired with Cell 19).

**Dependency**: this deliverable cannot be generated until Deliverable 7's
`voyant_comparison_corpus_id` is confirmed (Step 7.4) — every cell here loads
`myComparisonCorpus`, not `myCorpus`. Generate this block in the same Round 2
batch as Deliverable 3 (Section 6), after both.

### 6b.1 — Cell 14: comparison intro (fixed, corpus-independent)

No generation needed — this text is generic across every corpus.

```html
<div style="background:#0081AD; color: #FBFBFB; padding: 5px; height: 50px;"><h1><strong>Comparing Source and Summaries</strong></h1></div>

<p>Comparing source and summaries shows how summaries differ from the source. By definition, source and summaries are - and must be - different. The question is: what can we infer from these differences with respect to how the summaries represent the source. What is omitted, what is highlighted, what is simplified, what is repeated verbatim, and so on.</p>
```

### 6b.2 — Cells 15–18: Documents and Summary, rewired to the comparison corpus

**Rationale (2026-07-18 design decision, carried forward)**: Documents and
Summary are the two standard Voyant tools that are genuinely useful for a
*multi*-document view — Documents lists every document side by side, and
Summary gives a per-document quantitative profile. Both are moved here (out
of the single-document Distant Reading block) and rewired to
`myComparisonCorpus` so they operate on Source + every approved Phase 2 rate
at once, rather than the single source document. `stopList` is left
unchanged (`excListFull`, where used) — the merged stopword list filters
common words independent of which corpus is loaded, so the rewire does not
touch it.

```javascript
// ── DOCUMENTS ───────────────────────────────────────────────────────────────
// Runs on myComparisonCorpus (source + every approved summary), not myCorpus
// -- this cell is part of the "Source vs Summary" block.

let config = {
  lang:       "en",
  categories: "none",
  height:     250,
};
loadCorpus(myComparisonCorpus).tool("Documents", config);
```

```javascript
// ── SUMMARY ─────────────────────────────────────────────────────────────────
// Runs on myComparisonCorpus (source + every approved summary), not myCorpus
// -- this cell is part of the "Source vs Summary" block.
// stopList stays excListFull -- the merged stopword list filters common
// words regardless of which corpus is loaded, so this value is unaffected
// by the rewire.

let config = {
  lang:       "en",
  categories: "none",  // Explicitly cancel Voyant's default category colouring
  limit:      100,
  stopList:   excListFull,
};
loadCorpus(myComparisonCorpus).tool("Summary", config);
```

**Text cells 15 and 17** (the tool-description prose paired with each code
cell above) are otherwise the standard fixed template text for Documents and
Summary — with one required check: if the standard template text for
Documents claims the tool "does not add useful information" for a
single-document corpus (true of the *un-rewired* version, since Documents on
a single document is trivial), that claim is now false here and must be
replaced. Use: *"This cell runs on the comparison corpus (the source text
and every approved condensation summary), not the single-document source
corpus used below — so here the Documents tool is genuinely useful: it lists
every document side by side, letting you confirm which is which before
running the comparison tools that follow."*

### 6b.3 — Cell 19: the five-tool comparison pattern

This is the core of the deliverable — a fixed five-tool sequence comparing
the Source against every approved Summary: **TRENDS, BUBBLELINES, CIRRUS,
CONTEXTS, COLLOCATES**. The five tools are always all present — this is not
a researcher-selectable subset.

**Two structural families**, driven by how each tool handles multi-document
legibility (verified against real Distant Reading code and real Voyant
behaviour, 2026-07-21):

- **TRENDS and BUBBLELINES** have Voyant's own built-in interactive
  drill-down (per-document vs. per-corpus), reachable directly inside the
  rendered iframe — so one iframe per tool is enough. No `docIndex` needed.
- **CIRRUS, CONTEXTS, and COLLOCATES** have a similar per-document
  mechanism, but it is hard to reach and use correctly inside Voyant's own
  UI. Instead of relying on it, each of these three is pre-split into
  **three separate iframes**, one per `docIndex` (0 = Source, 1 = first
  approved summary, 2 = second approved summary, ...), so each result is
  immediately legible without the researcher fighting Voyant's interface.
  The accompanying reference `<code>` block is deliberately handed over with
  the alternative `docIndex` values spelled out, so the researcher can copy
  it into Cell 20 and run variations herself.

**Fixed top-level HTML skeleton** (identical shape for every corpus — do not
regenerate this part, only the five tool blocks inside it):

```html
<table align="left" border="2" cellpadding="3" cellspacing="1" style="width: 50px;">
	<tbody>
		<tr>
			<td style="background: #8AC29C; width: 50px;">&nbsp;</td>
		</tr>
	</tbody>
</table>

<p>&nbsp;</p>

<p>&nbsp;</p>

<h1><strong>[TOOL NAME]</strong></h1>

<blockquote>
[tool-specific content -- see 6b.3a/6b.3b below]

<p>&nbsp;</p>
</blockquote>

<p>&nbsp;</p>
```

The green `#8AC29C` swatch at the top is the same AI-provenance flag used
elsewhere in this notebook ("created with AI assistance," per Cell 3's
legend) — this cell's tool selection, query terms, and framing are a
disclosed editorial judgement, not raw AI output, which is why it carries
this flag rather than the stronger orange `#FFA040` ("fully generated by
AI") used on Cells 5/6/8/13. The `<h1>`/`<blockquote>`/trailing-spacer
pattern repeats once per tool, five times, each preceded by the same
`<p>&nbsp;</p>` spacer.

#### 6b.3a — TRENDS and BUBBLELINES: single-iframe family

```html
<p>TRENDS shows how the frequency distributions of the selected categories in the source compare to those in the summaries &mdash; that is, how similar or dissimilar their trends are across segments.</p>

<p><iframe src="https://voyant.inf.puc-rio.br/tool/Trends/?palette=Tableau10&amp;categories=<CATEGORIES_ID>&amp;lang=en&amp;query=<CATEGORY_TOKENS_URLENCODED>&amp;bins=5&amp;corpus=<COMPARISON_CORPUS_ID>" style="width: 100%; height: 432px;"></iframe></p>

<p>Use this code in the empty code cell next to this one to reproduce the visualization we show for the comparison.</p>

<p><code>// ── TRENDS ───────────────────────────────────────────────────────────────────<br />
// Available @Category queries for this corpus:<br />
[full @Category legend -- all clusters, per 6.3's rule]</code></p>

<p><code>let config = {<br />
&nbsp; lang:&nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; "en",<br />
&nbsp; categories:&nbsp; &nbsp; &nbsp; &nbsp; catsId,<br />
&nbsp; query:&nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp;[<CATEGORY_TOKENS>],<br />
&nbsp; withDistributions: "relative",<br />
&nbsp; chartType:&nbsp; &nbsp; &nbsp; &nbsp; &nbsp;"barline",<br />
&nbsp; bins:&nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; 5,<br />
&nbsp; palette: "Tableau10",<br />
};</code></p>

<p><code>loadCorpus(myComparisonCorpus).tool("Trends", config);</code></p>
```

BUBBLELINES follows the identical shape (own description text, own iframe,
own legend, own `config`), with `bins: 5` and no `withDistributions`/
`chartType` keys, `palette` last, and **no extra trailing key after
`palette`** — a real bug found and fixed 2026-07-21: an earlier draft had a
stray `height: 700` key sitting after `palette` that Distant Reading's own
Bubblelines config never had; removed for consistency.

**`<CATEGORY_TOKENS>`**: per 6.3's rule, default to the first three clusters
in Phase 1 order (`@C01Token, @C02Token, @C03Token`) — **not** every
cluster. A real regression was caught and fixed 2026-07-21: a live demo
session temporarily expanded this to eight categories, which leaked into a
delivered artifact; verified against Distant Reading's own code (which
correctly stayed at three) before concluding the demo change was isolated
to this cell and reverting it. Always cross-check against the real Distant
Reading Trends/Bubblelines cells before treating a category count as
correct — do not assume the two must match without checking, but do not
assume they're independent either.

#### 6b.3b — CIRRUS, CONTEXTS, and COLLOCATES: three-iframe family

Shared skeleton per tool (description prose, then three `<h3>`/`<iframe>`
pairs, one per `docIndex`, no spacer between them, then the instruction
line, then the reference code):

```html
<p>[tool description -- see per-tool notes below]</p>

<h3>[Source label]</h3>

<p><iframe src="[tool URL]&amp;docIndex=0&amp;...&amp;corpus=<COMPARISON_CORPUS_ID>" style="width: 100%; height: [N]px;"></iframe></p>

<h3>[label for approved rate 1]</h3>

<p><iframe ...&amp;docIndex=1&amp;...></iframe></p>

<h3>[label for approved rate 2]</h3>

<p><iframe ...&amp;docIndex=2&amp;...></iframe></p>

<p>Use this code in the empty code cell next to this one to reproduce the visualizations we show for the comparison.</p>

<p><code>[comment header, single space before the dash-fill, e.g. "// ── CIRRUS ──────..."]</code></p>

<p><code>[let config = {...}; -- 2-space indent, palette last]</code></p>

<p><code>loadCorpus(myComparisonCorpus).tool("[ToolName]", config);</code></p>
```

**Rate labels are generic, never hardcoded.** Both the visible `<h3>` labels
("Summary at 10% condensation rate") and the code's own `docIndex` comment
(`// 0: Source; 1: Summary at [rate1]%; 2: Summary at [rate2]%;`) must use
whatever rates Phase 2 actually approved for this corpus — never assume
exactly "10%/25%." The code comment specifically should stay in bracket form
(`[rate1]%`/`[rate2]%`) even in a delivered artifact, since it documents the
*pattern*, not a specific run; the visible `<h3>` text uses the real,
resolved rate values for that corpus.

**CIRRUS**

```javascript
// ── CIRRUS ──────────────────────────────────────────────────────────────────

let config = {
    lang:       "en",
    categories: "none",  // category coloring did not render as expected for Cirrus
    visible:    100,
    stopList:   excListFull,
    docIndex: 0, // 0: Source; 1: Summary at [rate1]%; 2: Summary at [rate2]%;
    palette: "Tableau10",
  };
loadCorpus(myComparisonCorpus).tool("Cirrus", config);
```

**Empirical finding, 2026-07-21 (an earlier test corpus, real Voyant test)**:
`categories: catsId` did not produce working category-based colouring for
Cirrus in this notebook — the same behaviour the researcher had already
observed and worked around in the Distant Reading Cirrus cell (`"none"`
there too, Section 6.1, JS4). Kept as `"none"` here for consistency with
that same finding, not as an assumption. If a future run finds
category-based colouring works correctly for Cirrus, this should be
revisited — the comment documents the *observed* behaviour, not a permanent
constraint.

**UX caveat, required in the description prose** (not optional boilerplate —
this addresses a real, verified UX limitation, not a hypothetical one):
Cirrus assigns word colour and word position independently for each
separate rendering, and neither carries comparative meaning across the
three clouds — the same term can appear in a different colour and a
different position in each one. Only relative size (word frequency) is
comparable. State this plainly in the cell rather than letting the
researcher discover it by comparing clouds that don't actually line up, and
point to the SUMMARY tool's cell (immediately above, in this same
"Source vs Summary" block) for genuinely comparable word-frequency data —
do not build a separate frequency table for this purpose; Summary already
provides it. Exact wording used and verified 2026-07-21:

> *"Word color and position in the three clouds below are assigned
> independently for each visualization and carry no comparative meaning —
> the same term can appear in a different color and a different spot in
> each cloud. Only relative size (word frequency) is comparable across the
> three; see the SUMMARY tool's results in the cell above, for easily
> comparable word-frequency information across all documents in this
> comparison."*

Note the deliberately count-agnostic ending ("across all documents in this
comparison," not "across the source and both summaries") — this sentence
must not hardcode how many summaries exist. Regenerate it fresh against
whatever the real corpus's document count is; never branch it into "the
summary" / "both summaries" / "all summaries" conditionals — that pushes
complexity into prose instead of fixing it at the level where document
count is actually a structural constant of this cell (see the note on
`docIndex` below).

**CONTEXTS**

```javascript
// ── CONTEXTS ──────────────────────────────────────────────────────────────────
// Available @Category queries for this corpus:
[full @Category legend -- all clusters]

let config = {
  lang:         "en",
  categories: catsId,
  columns: ['left', 'term', 'right'],
  context: 8,
  expand: 100,
  dir: 'asc',
  docIndex: 0, // 0: Source; 1: Summary at [rate1]%; 2: Summary at [rate2]%;
  query: '"<TERM_A> <STEM>"~5|"<TERM_A> <WORD>"~5|"<TERM_A> <NGRAM>"~5',
  sort: "right",
  termColors: "terms",
  palette: "Tableau10",
};
loadCorpus(myComparisonCorpus).tool("Contexts", config);
```

Matched to Distant Reading's own Contexts cell (`categories`, `expand`,
`termColors` all present; `context: 8`, `sort: "right"`) with one
deliberate difference: `docIndex` is required here (Distant Reading runs on
a single document and doesn't need it) and `stopList` is deliberately
**absent** (Distant Reading's Contexts never sets it either — do not add
it here even though other tools in this cell do).

**Query shape refined 2026-07-22 (researcher's instruction) from a
two-term to a three-term disjunction.** `<TERM_A>` (the researcher's own
elicited choice) is paired via proximity with all three of `<STEM>`,
`<WORD>`, and `<NGRAM>` — Claude's three companion terms, one of each
lexical shape (see 6b.3c) — not just one companion term. Each disjunct
pairs `<TERM_A>` with exactly one companion term; the disjuncts are OR'd
together (`|`), matching the OR-of-2-word-phrases shape already validated
(see below), just extended from two disjuncts to three.

**Description prose must be generated from the real query, never written
once and left static.** A real bug was caught and fixed 2026-07-21: an
earlier description said the cell showed occurrences of "trust" and
"artificial intelligence" — but the actual query only matched the single
word "artificial," not that two-word phrase, and by the time it was
caught the query terms had already changed once during design without the
prose being re-synced. The description prose and the code comment
explaining the query (which must cover *every* branch of the query, not
just the first) are both derived outputs of the actual `query` value —
compose them fresh each time this cell is generated, from whatever
`<TERM_A>`/`<STEM>`/`<WORD>`/`<NGRAM>` actually end up in the code, rather
than treating the prose as independent content that happens to describe
the query. A second real bug of the same family, found by testing the
implementation rather than by reading it (2026-07-22): a first attempt at
generating the "either X or Y or Z" description joined the three terms
with a separator that opened a quote before each term but only closed one
at the very end (`&quot;machine* or &quot;ai or &quot;ai systems&quot;`) —
wrap every individual term in its own complete pair of quotes, never rely
on a shared separator to do both jobs.

**Elicitation for `<TERM_A>` / `<STEM>` / `<WORD>` / `<NGRAM>`** (see 6b.3c
below) — do not default these to any specific term; they must come from
the researcher's choice plus Claude's own companion-term selection, every
time.

**Verified working, 2026-07-21 (an earlier test corpus, real Voyant test, two
independent data points)**: Voyant's `"term1 term2"~N` proximity operator
is genuinely functional — do not assume otherwise if a first attempt
produces an unexpected count. Its distance semantics are **not** what a
naive token-index-gap check would predict: `~N` means *N words between the
two terms*, which corresponds to a token-index gap of `N+1`, not `N` — and
every qualifying token *pair* counts as its own result, not one result per
occurrence of the first term. Confirmed by predicting real Voyant Contexts
result counts twice, correctly, on `~2` (11 hits) and `~5` (22 hits) for
the same real corpus, after correcting for both of these — a plausible-
sounding "did not work" impression from an earlier test turned out to be
exactly this, not a real Voyant defect.

**Verified working, 2026-07-22 (an earlier test corpus, real Voyant test)**: the
`<NGRAM>` disjunct's 3+-word quoted phrase under `~N` (`<TERM_A>` plus a
multi-word companion, e.g. `"opacity ai systems"~5`) was tested for real
and confirmed to behave as intended — this shape had only been assumed by
analogy to the validated 2-word case until this test.

**COLLOCATES**

```javascript
// ── COLLOCATES ──────────────────────────────────────────────────────────────────

let config = {
    lang:         "en",
    columns: ['term', 'rawFreq', 'contextTerm', 'contextTermRawFreq'],
    context: 5,
    docIndex: 0, // 0: Source; 1: Summary at [rate1]%; 2: Summary at [rate2]%;
    query: "<TERM>",
    stopList: excListFull,
    categories: catsId,
    palette: "Tableau10",
  };
loadCorpus(myComparisonCorpus).tool("CorpusCollocates", config);
```

**Real Voyant tool substitution, required and non-negotiable**: the
Distant Reading equivalent of this cell uses `.tool("CollocatesGraph", ...)`
(a network-graph visualization), but `CollocatesGraph` **cannot render a
multi-document corpus**. This cell must call `.tool("CorpusCollocates", ...)`
instead — a different tool, table-based, that does support `docIndex`. The
comment header and description prose should say "COLLOCATES" (matching
Voyant's own documentation convention, which refers to both variants as
"Collocates") — never "CORPUS COLLOCATES" in the human-facing label, even
though `.tool("CorpusCollocates", ...)` is the correct, non-renameable API
call. Do not "fix" this apparent CIRRUS/CONTEXTS/COLLOCATES-vs-Distant-
Reading tool-name mismatch by trying to force `CollocatesGraph` in here —
it is a necessary adaptation, not an inconsistency.

**`<TERM>`**: the same single term elicited for CONTEXTS' `<TERM_A>` (see
6b.3c) — reused directly, unchanged. This is deliberate cell-to-cell
coherence, not a coincidence: COLLOCATES surfaces what co-occurs with the
researcher's chosen term broadly; CONTEXTS then lets the researcher examine
one specific relationship (with Claude's companion term) in situ. The two
cells are meant to "speak to each other."

**Every parameter besides `query` in this cell is fixed** — do not
elicit or vary `columns`, `context`, `stopList`, or `categories`; only the
single search term changes per corpus.

#### 6b.3c — Elicitation

Generating a correct Cell 19 for a new corpus requires exactly one piece of
information from the researcher, once, beyond what Deliverables 1, 3, and 7
already establish — everything else in the companion-term selection is
resolved by Claude, deterministically, not asked:

| # | What's asked | Used for | How it's resolved |
|---|---|---|---|
| 1 | Pick one clustered term (or stem/expression) from clusters C01, C02, or C03 | `<TERM>` in COLLOCATES; `<TERM_A>` in CONTEXTS | Researcher's direct choice |
| 2 | *(not asked — Claude selects)* which of the **other two** C01/C02/C03 clusters (not the researcher's) supplies the companion terms | Determines the companion cluster for `<STEM>`/`<WORD>`/`<NGRAM>` below | **Refined**: the *earliest remaining* cluster in C01→C03 order — e.g. researcher picks from C02, companion cluster is C01; researcher picks from C01, companion cluster is C02. A simple, deterministic tie-break where two clusters remain, not derived from any deeper principle. |
| 3 | *(not asked — Claude selects)* `<STEM>`, `<WORD>`, and `<NGRAM>` — three companion terms from that one companion cluster, one of each lexical shape | `<STEM>`/`<WORD>`/`<NGRAM>` in CONTEXTS' three-way disjunction (6b.3b) | **Refined**: to pit one of each lexical shape against the elicited term as plausibly-frequent companions, classify each term in the companion cluster's `terms` array by shape — contains `*` → stem; contains a space → N-gram; otherwise → plain word — and walk the array front-to-back (array position is still the salience proxy from the original design), taking the first term of each shape encountered. If the companion cluster doesn't contain all three shapes, stop and report this rather than silently omitting a disjunct — a real possibility for smaller or differently-composed clusters, not something to paper over. |

**First real implementation, tested against real test corpus data**:
`phase3-redesign/_build_cell19.py` implements this table plus
the fixed skeleton and per-tool templates from 6b.3a/6b.3b end to end —
`select_researcher_cluster()`, `select_companion_terms()`, `classify_term()`,
and `build_cell19_content()`. Running it against real `clusterDefs` and a
real elicited term (`"opacity"`, C03Opacity) produced a generated cell whose
tag-count profile (p/h1/h3/blockquote/code/iframe counts) matched the
hand-built, hand-verified `cell19-injection.html` exactly — the strongest
structural check available short of a live Voyant render. Three real bugs
were found by running the generator against real data, not by reading the
code: category tokens missing their `@` prefix in the query; commas in the
Trends query left un-percent-encoded (`,` instead of `%2C`); and the
malformed-quoting description bug noted above under CONTEXTS. All three
fixed and re-verified. A fourth real bug was found the same way one layer
deeper, while preparing this generated output for a live paste rather than
just structural checking: the `@Category` legend's full names and
COLLOCATES' description term were interpolated without going through
`esc()`, producing literal unescaped `&` in text content (e.g. "AI Systems
& Technology" instead of "AI Systems &amp; Technology") — exactly the bug
class this file's own Pre-Generation Checklist already warns about for
every other deliverable. Fixed at the source (`build_category_legend_comment()`
and `build_collocates_block()`), re-verified with a comprehensive scan for
any bare `&` not part of a valid entity, not just the instances found by
eye.

**Confirmed rendering correctly in live Voyant (all five tools)** — this is a stronger claim than the
structural/tag-count verification above, and is now the actual evidentiary
basis for treating this script as correct, not just plausible. Treat this
script as the reference implementation for any future automation of this
elicitation, not merely an illustration of it.

Everything else this deliverable needs — comparison-corpus ID, stoplist ID,
`catsId`, the approved rate list, `incList`/`clusterDefs` — is already
confirmed by the time Cell 19 is generated (Deliverables 1 and 7). This is
deliberately a two-input elicitation, not more: **do not** additionally ask
which of the five tools to include (all five, always), how many summaries
to show (structural — see below), or which categories to chart in
Trends/Bubblelines (fixed default, 6.3's rule, first three clusters).

**Document count is a structural constant of this cell, not a
parametrized variable.** CIRRUS, CONTEXTS, and COLLOCATES are each built
with exactly three iframes (`docIndex` 0/1/2 — Source plus exactly two
summaries). If a future corpus has one approved rate, or three, this cell's
*iframe count and docIndex range* need to change, not just its prose. Do
not attempt to solve a variable document count by writing conditional
phrasing ("the summary" / "both summaries" / "all summaries") in individual
sentences — that creates the appearance of flexibility in one spot while
the actual structural constraint (fixed iframe count) sits unaddressed
elsewhere. If a corpus with a different rate count is ever processed, this
whole subsection needs re-deriving for that count, not patched sentence by
sentence. Sentences that must reference "how many documents" without
naming a count (e.g. the Cirrus caveat above) should use a blanket
expression like "all documents in this comparison" instead.

**Superseded, v2.49.** Everything above this note describes
6b.3c's *original* elicitation: researcher picks one term from
C01/C02/C03, Claude deterministically derives a "companion cluster"
(earliest remaining in C01-C03 order) and three companion terms from it
by array position. Kept here as the historical record of that design and
the real bugs found in it (v2.42's missing-shape disclosure, etc.), per
this file's established convention of correcting rather than erasing
prior sections — but it is no longer what `_build_cell19.py` implements.

Two real, confirmed problems with the original design, found by testing
it against real data, not by re-reading the spec:

1. **Structural bias, already disclosed in v2.42 but never fixed**: C03
   can never be selected as companion cluster, for *any* researcher
   choice (C01 or C02 is always "earliest remaining").
2. **No evidence the resulting pairs ever actually collocate in the
   source.** "Maximize formal/cluster variety" and "these two terms
   actually appear near each other in the text" are different
   properties — confirmed empirically: most of the deterministically-
   derived disjuncts returned zero live-Voyant results, because the
   terms were never observed to co-occur in the first place. A
   collocation-loss comparison is meaningless without a real collocation
   to test.

**The real design principle, developed against real
test data**: empirically scan the source text for actual
cross-cluster collocations among C01/C02/C03's significant terms, rank
by real hit count, flag candidates confounded by a disproportionately
frequent term (e.g. "ai" in an AI paper co-occurs with nearly everything
by base rate, not because of a specific relationship — confirmed: it
topped a pure-frequency ranking without being analytically interesting),
and present the ranked, flagged candidates to the researcher for final
selection. This last step is deliberate, not incidental — quoting the
researcher's own framing, confirmed as the design principle: *"A fully
automated version could rank and filter mechanically, but I'd keep a
'here are the top-ranked, non-confounded candidates — pick which one(s)
matter' step in front of the researcher rather than auto-selecting the
top score, precisely because the ai-confound case shows raw frequency
alone can mislead."* Tested and confirmed: the mechanical confound
filter itself isn't perfect either (it also flagged `frontier`/`task*`,
since `task*` is independently high-frequency — a paper about task
assignment says "task" a lot) — the researcher reviewed the actual
numbers and chose that pair anyway, which is exactly the point: the
filter surfaces real data, it doesn't make the final call.

Two hard platform constraints were found and encoded into the query
builders while developing this, both confirmed against live Voyant, both
worth knowing before touching this code again:

- **A wildcard-shaped term cannot appear inside a quoted phrase/
  proximity expression at all** — `"term generati*"~N` silently returns
  zero results even when real matches exist for the un-quoted parts.
  Must be resolved to its dominant real literal forms first
  (`resolve_literal_forms()`).
- **Multiple complete proximity clauses must be combined with pipe
  (`|`), never comma.** Comma silently drops real matches when joining
  multiple full phrase-proximity clauses — confirmed: an identical
  six-clause query returned 21 real matches with comma, 44 with pipe,
  against live Voyant, on this exact corpus. Comma appears reserved for
  combining genuinely different syntax types (a standalone wildcard term
  alongside a phrase, per Voyant's own documented example), not for
  combining multiple same-type proximity clauses with each other.

**New public functions in `_build_cell19.py`** (full docstrings and
verified test block in the file itself): `find_source_collocations()`
(the empirical scan), `flag_confounded()` (the frequency-based filter,
disclosed as a heuristic, not a hard science), `format_collocation_candidates()`
(the researcher-facing ranked table), `resolve_literal_forms()` and
`build_proximity_clauses()` (wildcard resolution), `build_collocation_comparison_query()`
(pipe-combination). `select_researcher_cluster()` and
`select_companion_terms()` are removed, not left dead — nothing calls
them once the empirical mechanism replaces the deterministic one.
`build_contexts_block()` and `build_cell19_content()`'s signatures
changed accordingly (`selected_pairs` + `source_text`, not
`researcher_term`) — see the file's own docstrings, not reproduced here
in full to avoid the exact "two copies drift apart" failure this file's
changelog names repeatedly.

**Elicitation impact — closed in v2.50 (2026-07-24), same day.** The
original two-input elicitation (corpus_name, token table, one
C01/C02/C03 term) needed a third round trip that didn't exist before —
presenting `format_collocation_candidates()`'s output and collecting the
researcher's pair selection — since this can only run after Phase 1's
real source text and cluster terms are both available, which they
already are by Step 1.3/1.4's point in execution order. **See Step 1.4
above**, which was rewritten in v2.50 to actually drive this mechanism as
part of the same combined elicitation round; `_build_cell19.py`'s
functions are real, verified, and (as of v2.50) actually reachable from
the researcher-facing flow, not only from a standalone script.
**NOTE (fixed, usability/correctness review, 2026-07-28):** this
paragraph previously still said the integration was "not yet fully
re-wired... the next open item" — stale as of v2.50, left unedited when
that version closed the gap it describes. Corrected to point forward
rather than leave a resolved gap looking open.

Verified against real data: ran the full pipeline (`find_source_collocations()`
→ `flag_confounded()` → `build_collocation_comparison_query()` →
`build_cell19_content()` → `verify()`) against the real that later pilot test
corpus and clusterDefs. Confirmed: `ai`/`task*` ranks #1 by raw hits (41)
and is correctly flagged confounded; `frontier`/`task*` (38 hits) is also
flagged, honestly, for the reason given above; the query built from the
researcher's actual selected pairs (`frontier`/`task*`,
`generati*`/`task*`) produces exactly the six clauses confirmed live in
Voyant this session (44 real matches, pipe-combined); full
`build_cell19_content()` output passes every structural check
(`verify()`: 0/0 mismatches across all tag types, palette/lang present
in all 8 iframes, five `<h1>` blocks). Patched into the already-delivered
`later-pilot-test-corpus-populated-notebook.html`'s Cell 19 to match —
see the top-level changelog entry.

### 6b.4 — Cell 20: empty code cell (fixed, corpus-independent)

Paired with Cell 19 as the researcher's own playground for the reference
code each tool block hands over — running variations, different `docIndex`
values, different terms, etc.

```html
<p>&nbsp;</p>
```
```javascript
////////////////////////////////////////////////////////////////////////////////
// This is an empty code cell, placed here for users to write and test their own code //
////////////////////////////////////////////////////////////////////////////////
```

---

## 7. Deliverable 4 — Merged Stopword List

**Filename:** `[name]-stoplist-merged.txt`

**Rationale:** The Voyant built-in `stop.en.smart.txt` is accessible to
Voyant's internal tools by filename reference (`excListFull`), but it cannot
be extended programmatically from within Spyral — the file is server-side
and opaque to the API. The Phase 1 `excList` contains corpus-specific
non-significant terms (author names, citation artifacts, encoding fragments,
domain-specific discourse words) that go beyond the built-in list. To make
these exclusions effective in Voyant, the user must upload a merged stopword
file to their Voyant corpus. This deliverable produces that file.

### 7.0b — Check for an optional comprehensive excList

**Added v2.33, closing a real, previously-diagnosed gap.** Phase 1's own
`excList` (the JSON contract's T-3.32 value) is deliberately **narrow** —
Step 5.4 cluster-routing terms only, typically single digits of entries.
A real an earlier test corpus test run (2026-07-16) found that a merged stopword
list built from this narrow `excList` alone looks visibly worse than
Voyant's plain default smart list: it excludes no numerals, and the
researcher does not recognize any of its added terms. Root cause,
confirmed directly against that corpus's real Phase 1 intermediate
artifacts: a genuinely useful merged stopword list needs a **comprehensive**
set of corpus-specific exclusions — numerals (including letter-suffixed
citation-year variants like `2024a`), short citation-artifact tokens,
citation abbreviations (`et`, `al`, `i.e.`, `ibid`, `e.g.`), confirmed
author surnames, and a corpus-independent philosophy-prose supplement —
which is **not** the same thing as Phase 1's own narrow `excList`, is
**not derivable from the Phase 1 JSON alone**, and — critically — its
author-name component requires genuine human judgment (a past session's
real example: 124 of 127 heuristically-flagged candidate names were
correctly author surnames; 3 were confirmed false positives, `ai`,
`finally`, `drawing`, and that confirmation cannot be safely automated
here). Phase 3 does not have — and this fix does not attempt to build —
an automated pipeline for that judgment call.

What this step *can* do honestly: check whether the researcher has
already assembled this comprehensive set (as a one-off, by hand or with
Claude's help, working from Phase 1's own intermediate artifacts,
exactly as happened for an earlier test corpus) and, if so, use it — rather than
silently regenerating the known-inferior narrow version every time, as
this file did before this fix, even when a better list already existed
on disk.

```python
comp_files = glob.glob(f'/mnt/user-data/uploads/{corpus_name}-excList-comprehensive.json')
comprehensive_exclist = None
comprehensive_note = None

if comp_files:
    with open(comp_files[0], 'r', encoding='utf-8') as f:
        comp_data = json.load(f)
    if 'comprehensive_exclist' not in comp_data or not isinstance(comp_data['comprehensive_exclist'], list) or not comp_data['comprehensive_exclist']:
        raise ValueError(
            f"{comp_files[0]} does not have the expected shape "
            f"(a non-empty 'comprehensive_exclist' list) -- refusing to "
            f"guess at its structure. Fix the file or remove it and proceed "
            f"with the narrow excList instead."
        )
    comprehensive_exclist = comp_data['comprehensive_exclist']
    comprehensive_note = comp_data.get('note', '(no note field in the uploaded file)')
    exclist_source_status = (
        f"Comprehensive excList used ({len(comprehensive_exclist)} terms), "
        f"from {os.path.basename(comp_files[0])}. Provenance: {comprehensive_note}"
    )
else:
    exclist_source_status = (
        f"No {corpus_name}-excList-comprehensive.json found -- proceeding "
        f"with Phase 1's narrow excList ({len(exclist)} terms, T-3.32 "
        f"contract value) only. WARNING: for at least one real corpus "
        f"(an earlier test corpus, 2026-07-16), a merged stopword list built from "
        f"the narrow excList alone was reported by the researcher as "
        f"visibly worse than Voyant's plain default smart list -- it "
        f"excludes no numerals and adds no recognizable terms. If this "
        f"corpus's merged list looks similarly weak after upload, build a "
        f"comprehensive excList (numerals, short tokens, citation "
        f"artifacts, confirmed author names, philosophy-prose supplement) "
        f"and re-run this step with it present, rather than assuming "
        f"nothing can be done."
    )

print(exclist_source_status)
```

**Report this status plainly to the researcher in chat, not only in the
log** — this is not a quiet fallback. If no comprehensive file was found,
say so explicitly and offer to help construct one before proceeding, the
same way Step 0.9's Environment Precondition Failure protocol offers
explicit options rather than silently degrading.

### 7.0c — Mandatory automatic numeral-exclusion scan (added v2.55)

**Closes a real, confirmed recurrence of the exact incident Step 7.0b
already names as its own motivation.** Step 7.0b's WARNING is advisory
only — it tells the researcher the narrow excList probably lacks
numerals, then proceeds anyway unless she supplies a comprehensive file
herself. On the the original test paper corpus (2026-08-06), that is exactly what
happened again: no comprehensive file existed, the warning fired, the
narrow excList shipped with zero numeral exclusions, and the researcher
caught 118 numeral-token occurrences (32 distinct) surviving into a
live Cirrus word cloud — the identical symptom `peel3-phase1-v1.1.md`'s
own Rule A 2026-07-20 fix was built to prevent, recurring here because
that fix only repaired *detection* upstream (Phase 1's own significant-
term selection), not *propagation* into this deliverable: Phase 1's
`excList` is contractually scoped to Step 5.4 routing only (see that
file's v1.12 changelog, T-3.32), so numerals Rule A correctly detects
and excludes from term candidacy never reach it.

Unlike the comprehensive excList's other components (author names,
citation abbreviations, a philosophy-prose supplement), numeral
exclusion needs no human judgment call — a bare numeral is
presumptively non-significant Voyant vocabulary regardless of corpus.
This step is therefore **mandatory and automatic, run every time**,
independent of whether a comprehensive file was found or Step 7.0b's
WARNING fired:

```python
# Same pattern already validated in peel3-phase1-v1.1.md's Rule A
# raw-corpus scan (v1.20/v1.27) -- reused here, not re-derived, so both
# phases agree on what counts as a numeral-shaped token. Matches pure
# digits and year+letter suffixes (2021a) and dotted subsection numbers
# (2.1, 3.1.2); bounded by a negative lookaround on both sides so it
# matches only a standalone token, not digits embedded in a longer
# alnum string (a DOI fragment, a footnote-call artifact Phase 1 Step 0
# should already have stripped).
NUMERAL_TOKEN_PATTERN = re.compile(r'(?<![\w.])(\d+(?:\.\d+)*[a-zA-Z]?)(?![\w.])')

# Reuses the same *-CLEANED.txt already required as a Phase 3 input
# (Section 0) and already loaded for Step 1.4's collocation scan if this
# step runs after it -- do not re-prompt the researcher for a file
# already in hand.
cleaned_files = glob.glob('/mnt/user-data/uploads/*-CLEANED.txt')
if not cleaned_files:
    raise FileNotFoundError(
        "No *-CLEANED.txt found -- the mandatory numeral scan needs the "
        "real source text, not just the Phase 1 JSON."
    )
with open(cleaned_files[0], encoding='utf-8') as f:
    _numeral_scan_text = f.read()

auto_numeral_exclist = sorted({
    m.group(1).lower()
    for m in NUMERAL_TOKEN_PATTERN.finditer(_numeral_scan_text)
})

print(f"Automatic numeral scan (Step 7.0c): {len(auto_numeral_exclist)} "
      f"distinct numeral-shaped tokens found in the source text -- "
      f"added to the merged stopword list unconditionally.")
```

**Report this to the researcher in chat, every run, including when the
count is 0** — a clean corpus with no numerals is a real, reportable
outcome, not a silent no-op:

```
Numeral exclusion (automatic, Step 7.0c): <N> distinct numeral-shaped
tokens found in the source text, added to the merged stopword list.
```

Step 7.1's merge (below) folds `auto_numeral_exclist` into `exc_terms`
unconditionally, alongside whichever excList source Step 7.0b resolved.
**This does not replace Step 7.0b's own comprehensive-file mechanism** —
author names, citation abbreviations, and the philosophy-prose
supplement still need a researcher-supplied file and still only produce
the advisory WARNING if absent. It only removes numerals from that gap,
since numerals are the one component of "comprehensive" that never
needed human judgment in the first place, and are now guaranteed
regardless of what the researcher does or doesn't supply.

### 7.1 — Merge algorithm

**NOTE (fixed, v2.15):** this step previously re-opened and re-read
`stop.en.smart.txt` independently of Step 0.1, with its own fresh
`{line.strip().lower() for line in f if line.strip()}` set comprehension
that had no `#`-prefix filter — even though Step 0.1's own v2.10 fix
note claimed "the merged-output writer (Step 7.1) *does* filter
`#`-prefixed lines." That claim was false of the actual code: verified
directly by running this step's literal code against a real
`stop.en.smart.txt` (which genuinely starts with a `# see http://...`
attribution comment), the comment line survived into `smart_terms` as a
garbage 100+-character "stopword" entry. Two independent loads of the
same file are exactly the shape that let this drift happen in the first
place — Step 0.1 got fixed, Step 7.1 silently didn't, and nothing forced
them to stay in sync. Fixed by removing the second load entirely: Step
7.1 now reuses Step 0.1's already-correct `smart_terms` (converting the
list to a set here, since Step 0.1 defines it as a list) rather than
re-reading and re-filtering the file a second time.

**NOTE (v2.33):** `exc_terms` now comes from Step 7.0b's resolution
(`comprehensive_exclist` if a comprehensive file was found, else Phase
1's own narrow `exclist`) rather than unconditionally reading `exclist`
directly — Step 7.0b already decided which source to use and set
`exclist_source_status` accordingly; this step must not re-decide that
question or silently prefer one source over the other on its own.

**NOTE (v2.55):** `exc_terms` now also unions in `auto_numeral_exclist`
(Step 7.0c, mandatory and unconditional) — numerals are folded in
regardless of which excList source Step 7.0b resolved, since Step 7.0c
runs independently of that choice.

```python
# Reuses Step 0.1's already-loaded, already-filtered smart_terms list --
# does NOT re-read stop.en.smart.txt here. See NOTE above.
smart_terms = set(smart_terms)

# Uses whichever source Step 7.0b resolved -- comprehensive if found, else
# Phase 1's own narrow excList -- unioned unconditionally with Step 7.0c's
# mandatory automatic numeral scan. Never re-decided here.
exc_terms = (
    {term.lower() for term in (comprehensive_exclist if comprehensive_exclist is not None else exclist)}
    | set(auto_numeral_exclist)
)

# Merge, deduplicate, sort
merged = sorted(smart_terms | exc_terms)

print(f"stop.en.smart.txt : {len(smart_terms)} terms")
print(f"excList source    : {'comprehensive' if comprehensive_exclist is not None else 'narrow (Phase 1 T-3.32)'} ({len(exc_terms)} terms, incl. {len(auto_numeral_exclist)} auto-detected numerals)")
print(f"Overlap           : {len(smart_terms & exc_terms)} terms already in smart list")
print(f"New terms added   : {len(exc_terms - smart_terms)} terms")
print(f"Merged total      : {len(merged)} terms")
```

### 7.2 — Write and verify

**v2.12 fix (real bug):** this wrote directly to `/mnt/user-data/outputs/`
while Step 8's Round 1 delivery does `cp /home/claude/[name]-stoplist-
merged.txt /mnt/user-data/outputs/` — a `cp` that would fail (or silently
no-op against a stale file) since this deliverable was never staged at
`/home/claude/` in the first place, unlike every other deliverable in this
file. Fixed to match the write-then-`cp` convention Deliverables 3 and 5
already follow:

**CRITICAL — `newline=''` on this write (added v2.56).** Confirmed live
(the test book chapter Phase 3 run, 2026-08-06, on Windows): a plain
`open(output_path, 'w', encoding='utf-8')`, no `newline=''`, silently
converted every `\n` to `\r\n`. Every one of the 2,362 merged stopword
terms therefore carried an invisible trailing `\r` — which does not
match Voyant's tokenized text during exact-string filtering, so the
uploaded stoplist silently filtered *nothing at all*. The researcher's
own live Voyant Cirrus screenshot showed a word cloud dominated by
"the", "that", "is", "and", "a", "an" — exactly the terms the stoplist
should have removed. This is the identical failure mode already
diagnosed and fixed for Deliverable 6's notebook write (v2.47, see
that changelog entry) — but that fix was never propagated to this
sibling write step, so it recurred here independently, undetected
until a live upload made it visible. The reload-and-verify check
immediately below this write used to compare `verify_terms` (built
with `.strip()`) against `merged` — `.strip()` removes `\r` right along
with `\n`, so that check gave false confidence and could never have
caught this defect. Fixed with `newline=''` plus a raw-byte check that
actually looks for `\r\n`:

```python
output_path = f'/home/claude/{corpus_name}-stoplist-merged.txt'

with open(output_path, 'w', encoding='utf-8', newline='') as f:
    # Header comment documenting provenance
    f.write(f'# Merged stopword list for: {corpus_name}\n')
    exc_source_label = 'comprehensive excList' if comprehensive_exclist is not None else "Phase 1's narrow excList (T-3.32)"
    f.write(f'# Sources: stop.en.smart.txt ({len(smart_terms)} terms) '
            f'+ {exc_source_label} + {len(auto_numeral_exclist)} auto-detected '
            f'numerals (Step 7.0c, mandatory) = {len(exc_terms)} terms\n')
    f.write(f'# New corpus-specific terms added: {len(exc_terms - smart_terms)}\n')
    f.write(f'# Total unique terms: {len(merged)}\n')
    f.write(f'#\n')
    # v2.33: disclose which excList source this run actually used, so a
    # future reader of this file (not just this session's chat) can see
    # whether the comprehensive or narrow list was in effect.
    f.write(f'# excList source: {exclist_source_status}\n')
    f.write(f'#\n')
    f.write(f'# NOTE: This file contains corpus-specific exclusions (author names,\n')
    f.write(f'# citation artifacts, encoding fragments) alongside general English\n')
    f.write(f'# stopwords. Do not reuse for a different corpus without review.\n')
    f.write(f'#\n')
    for term in merged:
        f.write(term + '\n')

# Verify: reload and count non-comment lines
with open(output_path, 'r', encoding='utf-8') as f:
    verify_terms = [l.strip() for l in f if l.strip() and not l.startswith('#')]

assert len(verify_terms) == len(merged), "Merged list length mismatch after write"

# Verify (v2.56): check the RAW BYTES for CRLF, not just the .strip()'d
# content above. A content-length check alone is structurally blind to
# line-ending corruption -- .strip() removes '\r' along with '\n', so
# verify_terms would match `merged` term-for-term even on a 100% CRLF
# file. This is the exact gap that let the stoplist ship broken before.
with open(output_path, 'rb') as f:
    raw = f.read()
crlf_count = raw.count(b'\r\n')
if crlf_count:
    raise AssertionError(
        f"{output_path}: write produced {crlf_count} CRLF line endings "
        "-- every term now carries an invisible trailing '\\r' that will "
        "not match Voyant's tokenized text, silently defeating the "
        "entire stoplist on upload. Do not present this file. Confirm "
        "newline='' was actually passed to open()."
    )
print(f"Merged stopword list written and verified: {output_path}")
print(f"  {len(merged)} terms ({len(verify_terms)} non-comment lines), 0 CRLF confirmed")
```

### 7.2b — Deliverable 7: Build the comparison corpus ZIP

**Added 2026-07-18, researcher's own design point.** Every input this
needs — the source text and Phase 2's `-Summary-{rate}pct.txt` files —
already exists by the time Phase 3 starts, exactly like the merged
stopword list above. Bundled into the same early checkpoint (Step 7.3)
rather than delivered separately later, so the researcher makes one trip
to Voyant covering both uploads, not two trips at different points in the
session.

**Filename:** `[corpus_name]-comparison-corpus.zip`

**Rationale:** Cell 14 (source-vs-summary comparison tools — Cirrus,
Links, Summary's distinctive-words) needs the source text and every
approved condensation rate's summary loaded as documents inside a single
Voyant corpus, not compared across separate corpora — TF-IDF-based tools
need multiple documents in the same corpus to be statistically
meaningful, and this project's own 2026-07-11 triangulation session
recommended exactly this shape. A ZIP is the correct upload mechanism:
Voyant ingests a ZIP directly as a multi-document corpus, so the
researcher uploads one file instead of selecting three (or however many
rates were approved) by hand.

**Defensive pre-zip CRLF check (added v2.56).** `zipfile.ZipFile.write()`
reads each source file in binary mode and copies its bytes verbatim —
it is not itself subject to the text-mode `\n`→`\r\n` translation bug
found elsewhere this session (Step 7.2, and independently in
`peel3-phase2-v1.1.md` v1.8), so this function's own code was never the
cause of that defect. But it is only as clean as its inputs: a real run
(the test book chapter, 2026-08-06) found `*-Summary-{rate}pct.txt` — a
Phase 2 output this step consumes as an external input — was itself
CRLF-corrupted by the same bug in `peel3-phase2-v1.1.md`'s write code
(fixed there at v1.8, but this file has no way to know a given upload
was produced by a fixed or unfixed Phase 2 version). Checking here
too, independent of whether Phase 2 was patched, is a defense-in-depth
measure, not a claim that this function itself was previously broken:

```python
import zipfile
import os

def _assert_bare_lf(path):
    with open(path, 'rb') as f:
        raw = f.read()
    crlf_count = raw.count(b'\r\n')
    if crlf_count:
        raise AssertionError(
            f"{path}: contains {crlf_count} CRLF line endings before "
            "zipping. This file was not produced by this Phase 3 run, "
            "but its own generator (Phase 1/Phase 2) may have shipped "
            "it with the same write-time CRLF corruption already "
            "diagnosed elsewhere this project (peel3-phase2-v1.1.md "
            "v1.8, this file's own Step 7.2/7.5, v2.56). Do not zip a "
            "corrupted source file forward -- re-obtain a bare-LF "
            "version of it before proceeding."
        )

def build_comparison_corpus_zip(cleaned_txt_path, summary_txt_paths, output_path):
    """summary_txt_paths: list of paths to *-Summary-{rate}pct.txt files,
    one per approved Phase 2 rate, in the order they were run."""
    _assert_bare_lf(cleaned_txt_path)
    for p in summary_txt_paths:
        _assert_bare_lf(p)

    with zipfile.ZipFile(output_path, 'w', zipfile.ZIP_DEFLATED) as z:
        z.write(cleaned_txt_path, arcname=os.path.basename(cleaned_txt_path))
        for p in summary_txt_paths:
            z.write(p, arcname=os.path.basename(p))

    # Verify: reopen, check every entry is uncorrupted and the document
    # count matches exactly (1 source + one per approved rate) -- the
    # same reload-and-verify discipline Step 7.2 already applies to the
    # merged stopword list.
    with zipfile.ZipFile(output_path) as z:
        assert z.testzip() is None, "Corrupt entry found in comparison corpus ZIP"
        expected = 1 + len(summary_txt_paths)
        assert len(z.namelist()) == expected, (
            f"Expected {expected} documents in ZIP, found {len(z.namelist())}")
        names = z.namelist()

    print(f"Comparison corpus ZIP written and verified: {output_path}")
    print(f"  {len(names)} documents: {', '.join(names)}")
```

### 7.3 — Intermediate delivery and mandatory checkpoint

**NOTE (fixed):** Voyant does not accept user-generated or Claude-generated
identifiers for any Spyral API object — the stoplist ID and the
comparison-corpus ID can only be created by Voyant itself, at the moment
each file is actually uploaded. The previous design treated this as
something to leave entirely to the researcher, unsupervised: deliver a
placeholder, print instructions, and trust it gets filled in correctly
later, with nothing verifying it ever did. That is inconsistent with
every other checkpoint in PEEL, which pause and confirm rather than hand
off and hope. Fixed by making this an actual, mandatory pause — this
session does not proceed to Deliverables 1, 2, 3, or 5 until both real
IDs are confirmed.

**Extended 2026-07-18** to cover both Deliverable 4 and Deliverable 7
together, in one round, rather than pausing twice at two different
points in the session — matching the same "bundle the round-trips"
principle applied to the notebook's own Cell 11.

Present both `[corpus_name]-stoplist-merged.txt` and
`[corpus_name]-comparison-corpus.zip` together via `present_files` — this
is the FIRST thing Phase 3 delivers, before any other deliverable:

```
Two files, two Voyant uploads needed before I can continue:

1. Merged stopword list — stop.en.smart.txt : <N> terms
                           Phase 1 excList   : <N> terms
                           Already in smart  : <N> terms (no duplication)
                           New terms added   : <N> corpus-specific terms
                           Merged total      : <N> unique terms
   File: [corpus_name]-stoplist-merged.txt

2. Comparison corpus — source text + <N> approved condensation rate(s)
   File: [corpus_name]-comparison-corpus.zip

Do both of these in the same sitting, then come back with both IDs:

STEP A
  1. Open your (existing) corpus in Voyant Tools.
  2. Options -> Stopwords -> Edit list -> Upload [corpus_name]-stoplist-merged.txt.
  3. Voyant will assign an ID of the form "keywords-<32hexchars>".

STEP B
  1. Upload [corpus_name]-comparison-corpus.zip to Voyant as a NEW corpus
     (it unzips into a 3-document -- or however many rates were approved,
     plus one -- multi-document corpus automatically).
  2. Voyant will assign that new corpus a plain 32-character ID.

I cannot generate Cell 0, Cell 11's comparison-corpus config, or proceed
to the remaining deliverables, until you provide both IDs Voyant actually
assigned — neither exists until its upload happens, and nothing here can
guess or generate either on your behalf.
```

**Do not proceed to Step 7.4 or any later step until the researcher
responds with both IDs.**

### 7.4 — Validate and record both Voyant-assigned IDs

```python
import re

STOPLIST_ID_PATTERN = re.compile(r'^keywords-[0-9a-f]{32}$')
CORPUS_ID_PATTERN = re.compile(r'^[0-9a-f]{32}$')  # same shape as Phase 1's own corpusId

def validate_stoplist_id(candidate):
    return bool(STOPLIST_ID_PATTERN.match(candidate.strip().lower()))

def validate_comparison_corpus_id(candidate):
    return bool(CORPUS_ID_PATTERN.match(candidate.strip().lower()))
```

Validate each independently — a researcher may report them in either
order, or one before the other. If either response does not match its
pattern (wrong length, wrong/missing prefix, or clearly still the
placeholder text), report which one plainly and ask again for that one
specifically — do not silently accept a malformed value, guess at what
they meant, or block the valid one on the invalid one:

```
The stoplist ID doesn't match the format Voyant assigns ("keywords-"
followed by 32 hex characters). Please double-check the ID you copied
from Voyant and paste it again.
```

```
The comparison corpus ID doesn't match the format Voyant assigns (32 hex
characters, no prefix -- the same shape as a regular corpus ID). Please
double-check the ID you copied from Voyant and paste it again.
```

Once both are validated, store them as `voyant_stoplist_id` and
`voyant_comparison_corpus_id`. Proceed to Steps 1, 2, 3, then Deliverables
1, 2, 3, and 5 (see "Execution order" near the top of this file).

---

## 7.5 — Deliverable 5 — Phase3-results.md

**Held until after Step 7.3–7.4 — this one is a genuine data dependency,
not just delivery batching: the report explicitly documents the
confirmed `voyant_stoplist_id`, so it cannot be assembled correctly
before that value exists.**

**Filename:** `[corpus_name]-Phase3-results.md`

**NOTE (added):** Phase 1 and Phase 2 each produce a permanent, human-
readable results record (`Phase1-results.md`, `Phase2-results.md`). Phase 3
never had one — no durable trace of the token derivation, auto-corrections,
collisions, colour assignments, or cross-cluster stems existed anywhere
except the chat transcript. Fixed by adding the same kind of deliverable
here, mechanically assembled and verified before delivery, not narrated.

```python
def build_phase3_report(corpus_name, json_path, smart_path, inclist, exclist,
                         clusterdefs, tokens, flagged, collisions,
                         cross_cluster, smart_terms, exc_terms, merged,
                         deliverable_filenames, voyant_stoplist_id,
                         environment_precondition_status,
                         exclist_source_status):
    lines = [f"# Phase 3 Results — {corpus_name}\n"]

    lines.append("## Corpus and inputs\n")
    lines.append(f"- corpus_name confirmed: {corpus_name}")
    lines.append(f"- Phase 1 JSON: {json_path}")
    lines.append(f"  - incList: {len(inclist)} stems")
    lines.append(f"  - excList: {len(exclist)} terms")
    lines.append(f"  - clusterDefs: {len(clusterdefs)} clusters")
    lines.append(f"- stop.en.smart.txt: {smart_path}")
    lines.append(f"- Voyant-assigned stoplist ID (confirmed with researcher, "
                  f"Step 7.4): {voyant_stoplist_id}\n")

    lines.append("## Token derivation\n")
    lines.append("| nn | Token | Phase 1 cluster name | Auto-corrected? |")
    lines.append("|---|---|---|---|")
    flagged_by_name = {name: reason for name, tok, reason in flagged}
    for nn, cluster in enumerate(clusterdefs, start=1):
        note = flagged_by_name.get(cluster['name'], "no")
        lines.append(f"| {nn:02d} | {cluster['token']} | {cluster['name']} | {note} |")
    lines.append("")
    if collisions:
        lines.append(f"Collisions detected and resolved: {', '.join(collisions)}\n")
    else:
        lines.append("Collisions detected: none.\n")

    lines.append("## Colour assignment\n")
    lines.append("| Token | Colour (Tableau20) | Phase 1 name |")
    lines.append("|---|---|---|")
    for cluster in clusterdefs:
        lines.append(f"| {cluster['token']} | {cluster['color']} | {cluster['name']} |")
    lines.append("")

    lines.append("## Cross-cluster stems\n")
    if cross_cluster:
        for stem, toks in cross_cluster.items():
            lines.append(f"- `{stem}` -> {', '.join(toks)}")
    else:
        lines.append("None. Every stem belongs to exactly one cluster.")
    lines.append("")

    lines.append("## Merged stopword list\n")
    lines.append(f"- stop.en.smart.txt: {len(smart_terms)} terms")
    lines.append(f"- excList used: {len(exc_terms)} terms")
    lines.append(f"- Overlap: {len(smart_terms & exc_terms)} terms")
    lines.append(f"- New terms added: {len(exc_terms - smart_terms)} terms")
    lines.append(f"- Merged total: {len(merged)} unique terms\n")

    # v2.33: mandatory every run, same "present even when there is nothing
    # unusual to disclose" discipline as "## Environment fallbacks used"
    # below -- a future reader must be able to tell, from this file alone,
    # whether the narrow or comprehensive excList was actually used,
    # without needing this session's own chat log.
    lines.append("## excList source\n")
    lines.append(exclist_source_status + "\n")

    lines.append("## Environment fallbacks used\n")
    lines.append(environment_precondition_status + "\n")

    lines.append("## Deliverables produced\n")
    for i, fname in enumerate(deliverable_filenames, start=1):
        lines.append(f"{i}. {fname}")

    return '\n'.join(lines)
```

**NOTE (fixed):** `deliverable_filenames` must be defined before
`build_phase3_report()` is called — the prose already said so, but the
two code blocks were in the wrong order in this document (the call
appeared before the definition), which only surfaced by actually
executing the concatenated script rather than re-reading the prose,
which read correctly either way:

```python
deliverable_filenames = [
    f'{corpus_name}-cell-config.js',
    f'{corpus_name}-colour-legend.html',
    f'{corpus_name}-cells-tools.js',
    f'{corpus_name}-stoplist-merged.txt',
    f'{corpus_name}-Phase3-results.md',
]

md_report_text = build_phase3_report(
    corpus_name, json_path, smart_files[0], inclist, exclist, clusterdefs,
    tokens, flagged, collisions, cross_cluster, smart_terms, exc_terms,
    merged, deliverable_filenames, voyant_stoplist_id,
    environment_precondition_status,  # set once at Step 0.9, v2.14
    exclist_source_status,  # set once at Step 7.0b, v2.33
)
```

**Verification (mandatory, run before writing any file)** — same pattern
as Step 3.2v/6.2v in Phase 2 and Phase 1:

```python
required_headings = [
    "## Corpus and inputs", "## Token derivation", "## Colour assignment",
    "## Cross-cluster stems", "## Merged stopword list",
    "## excList source",  # v2.33
    "## Environment fallbacks used",  # v2.14
    "## Deliverables produced",
]
missing = [h for h in required_headings if h not in md_report_text]
if missing:
    raise AssertionError(
        "Phase3-results.md is missing required heading(s): "
        + ", ".join(missing) + ". Do not write or present this file until fixed."
    )
```

**NOTE (fixed):** `md_report_text` was built and verified but never
actually written to a file anywhere — Section 8's delivery step assumes
`[corpus_name]-Phase3-results.md` already exists, but nothing created it.
Caught by actually executing the full concatenated script end-to-end,
not by re-reading the prose, which read as complete either way:

**CRITICAL — `newline=''` on this write (added v2.56, same incident as
Step 7.2's fix — see that section's changelog note).** Applying the
same fix here even though this file's own upload/parsing was not the
one observed broken this run: this write had the identical
`open(path, 'w', encoding='utf-8')` gap, and `verify_text ==
md_report_text` below compares two in-memory Python strings that both
already went through universal-newline normalization on read/creation
— that equality check is just as blind to on-disk CRLF corruption as
Step 7.2's old `.strip()`-based check was, for the same underlying
reason (the corruption is a write-time artifact neither string ever
represents in memory).

```python
output_path = f'/home/claude/{corpus_name}-Phase3-results.md'
with open(output_path, 'w', encoding='utf-8', newline='') as f:
    f.write(md_report_text)

# Verify: reload and confirm required headings survived the write
with open(output_path, 'r', encoding='utf-8') as f:
    verify_text = f.read()
assert verify_text == md_report_text, "Phase3-results.md mismatch after write"

# Verify (v2.56): raw-byte CRLF check, independent of the content-equality
# check above -- see this section's own changelog note for why the
# content check alone cannot catch this.
with open(output_path, 'rb') as f:
    raw = f.read()
crlf_count = raw.count(b'\r\n')
if crlf_count:
    raise AssertionError(
        f"{output_path}: write produced {crlf_count} CRLF line endings. "
        "Do not present this file. Confirm newline='' was actually "
        "passed to open()."
    )
print(f"Phase3-results.md written and verified: {output_path} (0 CRLF confirmed)")
```

---

## 7.6 — Deliverable 6 — Populated Spyral Notebook

**NOTE (added, then corrected):** this is the fix for a real, serious gap
found by an actual test run. Every prior version of this skill produced
five ingredient files and stopped — never the notebook itself. This step
actually populates the template and delivers a real, usable notebook.

**A second, more serious correction was needed after the first version
shipped:** the first implementation of this step assumed a single
approved condensation rate. A manually-built reference mockup —
the thing this deliverable was supposed to be automating — showed
**every approved rate** stacked into Cells 5, 6, and 7, each in its own
clearly labeled section, not one rate chosen over the others. Missing this was
not a small bug — every approved condensation rate is meant to remain
part of the permanent, auditable record, and dropping any of them
would have shipped exactly the kind of selective, incomplete accountability
record PEEL exists to prevent. Fixed below: Cells 5, 6, and 7's Phase 2
portion all iterate over every approved rate, in order, none dropped.

**If `*-TemplateSN.html` was not found**, skip this deliverable
explicitly and say so — do not treat its absence as an error, but do not
silently omit it either. In a local/filesystem environment, first
confirm the broadened search from Section 0 actually ran (track
directory, parent directory, and wherever `stop.en.smart.txt` was
found) — do not report this message on the strength of a single
directory's glob coming up empty (v2.55; see that section's own note
for the real incident this closes):
```
Deliverable 6 skipped: no notebook template (*-TemplateSN.html) was
found. Checked: <list every location actually searched>. Deliverables
1-5 are complete. If you have the template, point me to it (or upload
it) and I can produce it in this session.
```

### Cell ownership (confirmed with the researcher, cell by cell)

**Reconciled 2026-07-21.** The numbers below previously described the
notebook's original, pre-restructuring layout (e.g. 10 tool cells at
positions 16–43). Two real changes since then left it stale: the
researcher's own 2026-07-18 macro-restructuring split the notebook into a
"Source vs Summary" block (Cells 14–20) followed by "Distant Reading of the
Source" (21–37) — moving Summary and Documents out of the tool-cell block
and into 14–20, leaving only 8 tool cells in Distant Reading, not 10 — and
the addition of Deliverable 8 (Section 6b) gave Cells 14–20 real, specified
content for the first time. The **Cell 7 row below is also a correction,
not just a renumbering**: an earlier version of this table (and a matching
skill-level bug, `build_documented_steps_html()`) assumed the Phase
1/2/3 results content lived in Cell 7. Direct researcher confirmation
against her real, live notebook established that Cell 7 is a static
heading-only divider with no AI content at all, and the results content
this row describes actually lives in **Cell 8**, built by a different
mechanism (`_build_cell8_v2.py`). `build_documented_steps_html()` was
marked `SUPERSEDED` in this file rather than removed, in case a future
fresh/unrestructured template run needs it — but do not assume it applies
to any specific notebook's Cell 7 without checking that notebook directly
first, which is the exact check that was skipped the first time.

| Cell | Content | Source |
|---|---|---|
| 2 | Citation/abstract | **Out of scope** — the researcher's own bibliographic data, never touched |
| 5 | Plain-text summary, **one section per approved rate** | Derived from each rate's Phase 2 `_spyral.html` by stripping every `<details>` block and all highlighting — no source traces survive |
| 6 | Full toggle-equipped condensation, **one section per approved rate** | Each rate's Phase 2 `_spyral.html`, pasted unmodified |
| 7 | "Documented steps in the pipeline" — **heading only, no AI content** | Fixed template divider — do not populate; see the reconciliation note above |
| 8 | Phase 1 + Phase 2 + Phase 3 results, combined | **Corrected v2.36** — built by `build_cell8_content()` (this file, verified against a real researcher-supplied reference, `cell8-injection.html`), not the external `_build_cell8_v2.py` this row previously named (never part of this project's packaged materials). Quick-jump index + one scrollable box: Phase 1's **full, untoggled** results (single — Phase 1 runs once; no coloured cluster table, confirmed absent from the real reference), Phase 2's **full, untoggled** results **repeated once per approved rate** (each its own sub-anchor), and this run's own `Phase3-results.md`, full and untoggled — all three phases, not Phase 3 alone |
| 9 | "Global Configuration Parameters" — **heading only, no AI content** | **Corrected v2.40, reversing v2.36.** Live-Voyant-verified: v2.36's claim that this cell should carry `Phase3-results.md` was wrong — that was a real duplication of Cell 8's own content, found live in a test notebook, not the intentional design v2.36 left unestablished. Cell 9 is a fixed template divider, like Cell 7 — **out of scope, never populated by Phase 3**, not a stale table row this time; `populate_notebook()`'s write here was the actual bug, and this row's v2.36 correction was itself the mistake. See the v2.40 changelog entry for the real fixed content and its researcher-supplied verbatim text |
| 10 | `myCorpus` | Phase 1 JSON's `corpusId` — **never** `corpus_name`, a completely different value |
| 11, 12 | Cell 0, Cell 1 | Deliverable 1 |
| 13 | Cluster list + colour legend | Phase 1's raw cluster/stem list + Deliverable 2's HTML legend |
| 14–20 | "Source vs Summary" comparison block | Deliverable 8 (Section 6b) — Cell 14 fixed intro, 15–18 Documents/Summary rewired to `myComparisonCorpus`, 19 the five-tool comparison pattern, 20 the paired empty code cell |
| 21 | "Distant Reading of the Source" heading | Fixed template |
| 22/23, 24/25, 26/27, 28/29, 30/31, 32/33, 34/35, 36/37 | 8 tool-description/code pairs: Reader, Cirrus, Trends, Bubblelines, CollocatesGraph, Contexts, Phrases, Document Terms | Deliverable 3, split at `// ── TOOLNAME ──` — these run against `myCorpus` as a whole, not per rate. **Only 8 of the original 10 JS2–JS11 tools remain here** — Summary and Documents were relocated into 15–18 by the same restructuring that created the 14–20 block |
| 38 | Researcher's Notes | **Out of scope** — always the researcher's own, never pre-filled |

### Building Cell 13 — merged cluster/colour legend

**v2.12 fix — `cluster_list_and_legend_html` (used below in
`populate_notebook()`) previously had no function defining it anywhere in
this file**, despite being a required parameter. Any real run had to
improvise this cell's HTML live, which is where most of a real test
run's unescaped `&` characters came from (cluster names like "Ethical
Frameworks & Rules" spliced directly into `<td>` cells). Defined then as
two separate tables back to back (a plain "Phase 1 Clusters and Stems"
table, plus Deliverable 2's own colour-legend table) — reusing
`build_colour_legend_html()` rather than duplicating its row logic.

**Merged into one table, v2.46 (a later pilot test,
researcher-requested).** The two-table shape was genuinely redundant:
both tables list every cluster's token/name, once with stems and no
colour, once with colour and no stems. Cell 13 now uses a single table —
swatch, token/name, and the full stem/term/N-gram list per cluster — in
one row, dropping the separate "Phase 1 Clusters and Stems" table and
the hex-code/Tableau-index column entirely (redundant with the swatch
itself for this in-notebook view). **`build_colour_legend_html()` itself
is deliberately left untouched** — it still feeds Deliverable 2's own
standalone `[name]-colour-legend.html` file, a different artifact with a
different purpose (a literal hex/Tableau reference a researcher might
need to paste by hand), not something this merge should also change.
`build_cluster_stem_table_html()` is removed rather than left orphaned —
nothing calls it once Cell 13's own table absorbs its content, and
leaving an uncalled function in place is exactly the kind of silent dead
code this project's own changelog has flagged elsewhere (Section 8.5's
`build_cluster_color_table_html()` finding, v2.44's call map).

```python
def build_cluster_list_and_legend_html(clusters_ordered, tableau20_palette, title, author):
    """Cell 13 only. One row per cluster: colour swatch, token &mdash;
    name, and its full stem/term/N-gram list (Phase 1's real 'stems'
    field) -- replacing the old two-table layout's separate hex-code/
    Tableau-index column, which this merged view doesn't carry (see
    build_colour_legend_html() for that reference, still produced
    separately for Deliverable 2's own standalone file)."""
    title = title or '[Title]'
    author = author or '[Author (Year)]'
    rows = []
    for c in clusters_ordered:
        r, g, b = hex_to_rgb(c['color'])
        rows.append(
            '<tr>'
            f'<td style="padding: 5px 12px 5px 0px; background-color: rgb({r}, {g}, {b}); '
            'width: 14px; border-radius: 3px; vertical-align: top;">&nbsp;</td>'
            f'<td style="padding: 5px 12px 5px 0px; color: rgb({r}, {g}, {b}); font-weight: bold; '
            'vertical-align: top; white-space: nowrap;">'
            f'{esc(c["token"])} &mdash; {esc(c["name"])}</td>'
            '<td style="padding: 5px 0px; color: #1c1a18; font-size: 13px; vertical-align: top;">'
            f'{esc(", ".join(c["stems"]))}</td>'
            '</tr>'
        )
    return (
        '<table align="left" border="2" cellpadding="3" cellspacing="1" style="width: 50px;">\n'
        '\t<tbody>\n\t\t<tr>\n\t\t\t<td style="background: #FFA040; width: 50px;">&nbsp;</td>\n'
        '\t\t</tr>\n\t</tbody>\n</table>\n\n'
        '<h1 style="line-height:1.2em;">&nbsp;</h1>\n\n'
        '<div style="font-family:Georgia,serif;max-width:820px;margin:0 auto;'
        'padding:0 0 4rem;line-height:1.85;color:#1c1a18;">\n'
        '<h1 style="font-family:system-ui,sans-serif;font-size:1.3rem;font-weight:700;'
        'line-height:1.2em;margin:0 0 0.3rem;color:#1c1a18;">Color Coding for Categories</h1>\n'
        '<h3 style="font-family: &quot;Times New Roman&quot;;">Semantic Category Colour Legend</h3>\n'
        f'<p style="font-family: &quot;Times New Roman&quot;;">{esc(author)} &mdash;&nbsp;<em>{esc(title)}</em><br />\n'
        f'{len(clusters_ordered)} clusters &middot; Tableau20 palette &middot; colours assigned via&nbsp;<code>cats.addFeature()</code></p>\n'
        '<table style="border-collapse: collapse; font-family: serif; font-size: 14px;">\n'
        '  <tbody>\n' + '\n'.join(f'    {row}' for row in rows) + '\n  </tbody>\n</table>\n'
        '</div>'
    )
```

### Building Cell 7's coloured cluster table (v2.13)

**Distinct from Cell 13's table above.** Cell 13 (`build_cluster_list_and_legend_html`)
serves Deliverable 2's own separate purpose and is untouched. This function
reproduces Phase 1's own Step 5.5 `*-Phase1-clusters.html` artifact directly
inside Cell 7 — the single dynamic Phase-1 element the researcher's own
hand-built reference mockup relies on there, placed before the collapsed
full narrative, not colourless and not in Cell 13. Reuses `hex_to_rgb()`
already defined above (Deliverable 2); every fragment is `esc()`-escaped,
which Phase 1's own Step 5.5 code is not (see v2.13 changelog).

```python
def build_cluster_color_table_html(clusters_ordered, inclist, corpus_name):
    """Reproduces Phase 1's Step 5.5 coloured cluster table (same visual
    shape as *-Phase1-clusters.html) from this file's own clusterdefs
    (token/colour already assigned in Steps 1-2) and confirmed
    corpus_name (Step 0.0b) -- Phase 3 does not need *-Phase1-clusters.html
    as a separate upload to reproduce it. Every cluster name and stem is
    esc()-escaped before insertion, unlike Phase 1's own snippet
    generator, which has no escaping path at all."""
    rows = []
    for c in clusters_ordered:
        r, g, b = hex_to_rgb(c['color'])
        stems_str = ', '.join(f'<code>{esc(s)}</code>' for s in c['stems'])
        rows.append(
            '<tr>'
            f'<td style="padding:5px 12px 5px 0; background-color:rgb({r},{g},{b}); '
            'width:14px; border-radius:3px;">&nbsp;</td>'
            f'<td style="padding:5px 12px 5px 0; color:rgb({r},{g},{b}); font-weight:bold;">{esc(c["name"])}</td>'
            f'<td style="padding:5px 0; font-size:0.88em; color:#555;">{stems_str}</td>'
            '</tr>'
        )

    clustered_stems = {s for c in clusters_ordered for s in c['stems']}
    uncolored = sorted(s for s in inclist if s not in clustered_stems)
    if uncolored:
        uncolored_str = ', '.join(f'<code>{esc(s)}</code>' for s in uncolored)
        rows.append(
            '<tr>'
            '<td style="padding:5px 12px 5px 0;">&nbsp;</td>'
            '<td style="padding:5px 12px 5px 0; color:#888; font-style:italic;">(uncolored -- kept in incList, no cluster)</td>'
            f'<td style="padding:5px 0; font-size:0.88em; color:#555;">{uncolored_str}</td>'
            '</tr>'
        )

    total_stems = sum(len(c['stems']) for c in clusters_ordered) + len(uncolored)
    rows_html = '\n'.join(f'    {row}' for row in rows)

    return (
        '<h3>Semantic Clusters &mdash; Phase 1 results</h3>\n'
        '<p style="font-style:italic; color:#666; font-size:0.9em;">\n'
        f'  {esc(corpus_name)} &mdash; {len(clusters_ordered)} clusters &middot;\n'
        f'  {total_stems} stems/phrases &middot; Tableau20 palette\n'
        '</p>\n'
        '<table style="border-collapse:collapse; font-family:serif; font-size:14px;">\n'
        '  <thead>\n'
        '    <tr>\n'
        '      <th style="padding:5px 12px 5px 0;">&nbsp;</th>\n'
        '      <th style="padding:5px 12px 5px 0; text-align:left;">Cluster</th>\n'
        '      <th style="padding:5px 0; text-align:left;">Stems</th>\n'
        '    </tr>\n'
        '  </thead>\n'
        '  <tbody>\n'
        f'{rows_html}\n'
        '  </tbody>\n'
        '</table>'
    )
```

### Plain-text derivation for Cell 5

```python
import re

def parse_summary_txt(summary_txt_content):
    """v2.18: replaces strip_to_plain_text(). Parses a Phase 2 v3.21
    `{corpus}-Summary-{rate}pct.txt` file's content into (title, author,
    body_lines). Phase 2's own block parser guarantees every 'p'/'h2'/'h3'
    block occupies exactly one line in this file (paragraphs are
    space-joined before being written), and blank lines only ever
    separate blocks -- never occur inside one -- so each non-blank line
    after the 'Summary:' marker is exactly one block, in order. This
    reads Phase 2's native pre-annotation text directly; it does not
    derive plain text by stripping HTML (see v2.18 changelog for why the
    previous approach, strip_to_plain_text(), was wrong)."""
    lines = summary_txt_content.split('\n')
    title = lines[0][len('Title: '):].strip()
    author = lines[1][len('Author: '):].strip()
    # lines[2] is 'Summary:', lines[3] is blank
    body_lines = [l.strip() for l in lines[4:] if l.strip()]
    return title, author, body_lines
```

### Escaping raw text before it becomes HTML

**NOTE (v2.12, real bug):** every function below that splices Phase 1/2/3
report text — or Phase 1 cluster names — into HTML output must run that
text through `esc()` first. This was missing entirely before v2.12: a
real test run's notebook shipped 40 literal, unescaped `&` characters
(cluster names like "Virtue & Character") straight into `<td>`/`<h#>`
content, which is exactly what broke Voyant Spyral's upload parser. One
primitive, used everywhere raw text meets an HTML tag:

```python
import html as _html

def esc(text):
    """Escape &, <, > for safe insertion into HTML body text. Quotes are
    left literal, matching the template's own convention (confirmed by
    inspecting the pristine template's raw <pre> code-cell escaping:
    it escapes & but leaves quotes alone)."""
    return _html.escape(str(text), quote=False)
```

### Converting the -results.md reports to HTML

**NOTE:** deliberately not dependent on the third-party `markdown`
package — the live environment this skill runs in may not have it
installed, the same class of risk already found and fixed for NLTK
earlier in this project. This is a small, dependency-free conversion
scoped to exactly the structure Phase 1/2/3's own reports use (headings,
tables, bullet/numbered lists, bold, inline code) — not a general-purpose
parser. **Every text fragment is passed through `esc()` before being
wrapped in a tag** — this must happen before the fragment is embedded,
not as an afterthought pass over the assembled HTML, since by then real
tags (`<table>`, `<li>`, ...) are already mixed into the same string and
escaping indiscriminately would corrupt them.

```python
def md_to_html(md_text):
    lines = md_text.strip().split('\n')
    html_lines = []
    in_table = False
    in_ul = False
    in_ol = False
    for line in lines:
        stripped = line.strip()
        if stripped.startswith('|'):
            cells = [c.strip() for c in stripped.strip('|').split('|')]
            if all(re.match(r'^-+$', c) for c in cells):
                continue  # separator row
            if not in_table:
                # v2.38 fix: <tbody> was missing -- valid HTML (browsers
                # imply one), but Spyral's own import parser is stricter
                # and throws "an error occurred while parsing the input
                # of the document" on every table-bearing cell, then
                # self-heals by inserting the missing tag itself. No data
                # loss (confirmed by diffing a real Spyral round-trip
                # byte-for-byte), but the spurious warning is worth
                # closing at the source rather than living with it.
                html_lines.append('<table border="1" cellpadding="4" cellspacing="0" style="border-collapse:collapse;">')
                html_lines.append('<tbody>')
                in_table = True
                tag = 'th'
            else:
                tag = 'td'
            row = ''.join(f'<{tag}>{esc(c)}</{tag}>' for c in cells)
            html_lines.append(f'<tr>{row}</tr>')
            continue
        elif in_table:
            html_lines.append('</tbody></table>')
            in_table = False
        if stripped.startswith('- '):
            if not in_ul:
                html_lines.append('<ul>')
                in_ul = True
            html_lines.append(f'<li>{esc(stripped[2:])}</li>')
            continue
        elif in_ul:
            html_lines.append('</ul>')
            in_ul = False
        m_ol = re.match(r'^\d+\.\s+(.*)', stripped)
        if m_ol:
            # v2.12 fix: numbered lists (e.g. Deliverable 5's "Deliverables
            # produced" list) previously fell through to <p> tags, one per
            # item, losing the ordered-list structure -- found live during
            # a real test run and ported back here.
            if not in_ol:
                html_lines.append('<ol>')
                in_ol = True
            html_lines.append(f'<li>{esc(m_ol.group(1))}</li>')
            continue
        elif in_ol:
            html_lines.append('</ol>')
            in_ol = False
        m = re.match(r'^(#{1,3})\s+(.*)', stripped)
        if m:
            level = len(m.group(1))
            if level == 1:
                # v2.37 fix: matches Phase 2's own S['h1'] wrapped-title-
                # overlap fix (v3.22) and the researcher's own
                # _build_cell8_v2.py copy of this function -- line-height
                # 1.35 was too tight for a wrapped two-line title at this
                # font size; 1.2em (explicit unit) is the confirmed fix.
                # This shared function feeds Cell 8/9's Phase 1/2/3 <h1>
                # headings, which previously rendered with no line-height
                # at all (the browser default), not just the wrong value.
                html_lines.append(f'<h1 style="line-height:1.2em;">{esc(m.group(2))}</h1>')
            else:
                html_lines.append(f'<h{level}>{esc(m.group(2))}</h{level}>')
            continue
        if not stripped:
            continue
        html_lines.append(f'<p>{esc(stripped)}</p>')
    if in_table:
        html_lines.append('</tbody></table>')
    if in_ul:
        html_lines.append('</ul>')
    if in_ol:
        html_lines.append('</ol>')
    html = '\n'.join(html_lines)
    # Safe to apply after escaping: ** and ` are not HTML metacharacters,
    # so esc() above never touches them, and this only ever adds new real
    # tags around already-escaped text -- it can't re-open anything.
    html = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', html)
    html = re.sub(r'`([^`]+)`', r'<code>\1</code>', html)
    return html


def split_narrative_and_appendix(md_text, appendix_heading_patterns):
    """
    Splits a -results.md file into (narrative_md, appendix_md) at the
    first matching appendix heading. If none of the given patterns are
    found, the entire document is treated as narrative and appendix_md
    is None -- disclosed explicitly (no toggle built), never a silently
    forced or empty toggle. This matters in practice: a real Phase 1
    report from before that file's own heading-verification fix (Step
    6.2v) lacks a clean per-term-appendix marker entirely, and this
    function must degrade honestly rather than break or fabricate one.
    """
    for pattern in appendix_heading_patterns:
        idx = md_text.find(pattern)
        if idx != -1:
            return md_text[:idx], md_text[idx:]
    return md_text, None
```

### Cell substitution functions

```python
from bs4 import BeautifulSoup

def populate_code_cell(html, cell_id, new_code):
    """Replaces ONLY the authoritative raw source of a code cell --
    never the decorative CodeMirror preview markup, which is a frozen
    cosmetic snapshot Spyral does not read to reconstruct the live
    notebook. See the disclosed caveat below.

    v2.12 fix: new_code is esc()-escaped before insertion. A real test
    run found unescaped '&' in cluster-name JS comments (e.g. 'Virtue &
    Character') and literal '<'/'>' sequences (e.g. a show(">>> ... <<<")
    call) inside generated JS, both of which broke Voyant's upload
    parser since this <pre> block's content is real HTML body text, not
    a CDATA/script block. Confirmed round-trip safe: html.unescape() on
    the stored raw content reproduces the original JS byte-for-byte, and
    Voyant/browsers decode entities back to the literal characters before
    the JS ever runs -- this only affects how the source sits in the
    HTML document, not what code executes."""
    pattern = re.compile(
        rf"(<section id='{cell_id}'.*?<pre class='notebook-code-editor-raw[^']*'>)"
        rf".*?(</pre>.*?</section>)", re.DOTALL)
    m = pattern.search(html)
    if not m:
        raise ValueError(f"Code cell {cell_id} not found or has no raw source block")
    return html[:m.start()] + m.group(1) + esc(new_code) + m.group(2) + html[m.end():]

def populate_text_cell(html, cell_id, new_inner_html):
    """Replaces the notebook-text-editor div's inner content for a text cell."""
    section_pattern = re.compile(rf"<section id='{cell_id}'.*?</section>", re.DOTALL)
    m = section_pattern.search(html)
    if not m:
        raise ValueError(f"Text cell {cell_id} not found")
    section_html = m.group(0)
    div_pattern = re.compile(
        r"(<div class='notebook-text-editor'>).*(</div>\s*</section>)$", re.DOTALL)
    m2 = div_pattern.search(section_html)
    if not m2:
        raise ValueError(f"Text editor div not found in cell {cell_id}")
    new_section = section_html[:m2.start()] + m2.group(1) + new_inner_html + m2.group(2)
    return html[:m.start()] + new_section + html[m.end():]

def toggle(label, inner_html):
    """inner_html is assumed already-escaped/well-formed HTML (built by
    md_to_html() or similar) -- only label is raw text here, so only
    label goes through esc()."""
    return (
        '<details style="margin:0 0 1.2rem 0;border:1px solid #ddd;border-radius:4px;overflow:hidden;">'
        f'<summary style="cursor:pointer;padding:0.6rem 1rem;background:#f3f1ec;font-family:system-ui,sans-serif;'
        f'font-weight:700;font-size:0.85rem;color:#1a5c7a;">{esc(label)} (click to expand)</summary>'
        f'<div style="padding:0.6rem 1.1rem 0.9rem;font-family:system-ui,sans-serif;font-size:0.85rem;'
        f'line-height:1.6;color:#1c1a18;">{inner_html}</div></details>'
    )

def split_tool_cells_js(tools_js_text):
    """Splits Deliverable 3's single tools-JS file at its own
    // ── TOOLNAME ── headers -- reuses the same file already written
    for Deliverable 3, does not regenerate anything. Tool cells run
    against the corpus as a whole and are NOT per-rate."""
    blocks = re.split(r'(?=// ── )', tools_js_text.strip())
    result = {}
    for b in blocks:
        b = b.strip()
        if not b:
            continue
        m = re.match(r'// ── ([A-Z ]+?) ──', b)
        if m:
            result[m.group(1).strip()] = b
    return result

TOOL_CELL_IDS = {
    'READER': 'n6fnrd01', 'CIRRUS': 'trn0i4a3',
    'TRENDS': 'jnr8d99e', 'BUBBLELINES': 'ad3kqxh6',
    'COLLOCATES GRAPH': 'xlegqnc2', 'CONTEXTS': 'vh17zumr',
    'PHRASES': 'gv79h3d7', 'DOCUMENT TERMS': 'txqc4gy4',
}
# Corrected v2.32: was 'CORPUS TERMS', which no longer matches the comment
# header JS10 actually generates ("DOCUMENT TERMS", see the note there) --
# would have raised the injection loop's own "No generated block found"
# error the first time this ran against a freshly-generated Deliverable 3
# file, since split_tool_cells_js() keys tool_blocks off the literal
# comment-header text.
# Corrected v2.32: 'SUMMARY': 'oggheb4j' and 'DOCUMENTS': 'j33xw4rk' removed.
# Those two ids are Cells 18 and 16 -- Deliverable 8's comparison-corpus
# Summary/Documents cells (Section 6b.2), not Deliverable 3 tool cells. With
# Section 6's own JS3/JS11 blocks now removed (see the note there), nothing
# in `tool_blocks` is keyed 'SUMMARY' or 'DOCUMENTS' any more; leaving these
# two entries in this dict would have raised a KeyError in the injection
# loop below the first time this ran against a real Deliverable 3 file with
# only 8 blocks in it. Cells 16 and 18 are populated directly, from
# `build_cell16_content()`/`build_cell18_content()`, in populate_notebook()
# below -- not through this generic tool-block loop.
```

### Multi-rate section builders for Cells 5, 6, and 7

**This is the actual fix.** Every approved rate gets its own labeled
section in Cells 5 and 6, in order, none dropped; Cell 7's Phase 2
portion repeats the same way, once per rate, each with its own appendix
toggle so multiple rates' appendices are never conflated into one:

```python
def build_cell5_content(title, author, condensations):
    """v2.18 rewrite -- the previous version didn't match the real
    template cell (`PEEL3-SNunderway.html`, id='jb3c08qu') on any of:
    the AI-flag marker table, Title/Author, the '<h2>&nbsp;</h2>' spacer,
    the '<u><tt>{rate}%</tt></u>' heading markup, or the per-paragraph
    inline-style convention (font-size:11.0pt / line-height:107% /
    Calibri) already established across every other fragment this
    project produces. Verified directly against the real cell.

    title, author: shared across all rates (same source text) -- taken
    from the first rate's parsed summary by the caller, asserted
    consistent across rates.
    condensations: list of dicts, one per approved rate, each with
    'rate' and 'summary_body_lines' (from parse_summary_txt()), in the
    order the rates were run."""
    parts = [
        '<table align="left" border="2" cellpadding="3" cellspacing="1" style="width: 50px;">'
        '<tbody><tr><td style="background: #FFA040; width: 50px;">&nbsp;</td></tr></tbody></table>',
        '<h2>&nbsp;</h2>',
        f'<p><span style="font-size:14.0pt"><span style="font-family:&quot;Calibri&quot;,sans-serif">'
        f'<b>{esc(title)}</b></span></span></p>',
        f'<p><span style="font-size:11.0pt"><span style="font-family:&quot;Calibri&quot;,sans-serif">'
        f'<i>{esc(author)}</i></span></span></p>',
    ]
    for i, c in enumerate(condensations):
        if i > 0:
            # Spacer only *between* rate blocks -- verified against the
            # real approved cell content: no spacer between the author
            # line and the first rate's heading, only before subsequent
            # ones. A first draft of this fix added it unconditionally
            # and would have introduced an extra blank heading before the
            # very first "Summary at N%" line -- caught by diffing
            # against the researcher-approved reference before this was
            # merged, not after.
            parts.append('<h2>&nbsp;</h2>')
        parts.append(f'<h2>Summary at <u><tt>{c["rate"]}%</tt></u>&nbsp;condensation rate</h2>')
        parts.append('<blockquote>')
        for line in c['summary_body_lines']:
            parts.append(
                '<p><span style="font-size:11.0pt"><span style="line-height:107%">'
                f'<span style="font-family:&quot;Calibri&quot;,sans-serif">{esc(line)}</span>'
                '</span></span></p>'
            )
        parts.append('</blockquote>')
    return ''.join(parts)

def build_cell6_content(condensations):
    return '<h1>Details</h1>' + ''.join(
        f'<h2>Summary at {c["rate"]}% rate</h2>{c["full_details_html"]}'
        for c in condensations
    )
```

**Superseded (v2.26) — read before using
this function on a live Voyant notebook.** This function targets internal
cell id `yq7hcf8i`, which every one of this project's own internal
comments (v2.13, v2.25 below) calls "Cell 7" — but in the live notebook
that cell is actually a static colour-banner heading divider
(`<div style="background:#0081AD;...">`), with no AI content, so nothing
this function's output belongs in. The composite content this function builds
(Phase 1 cluster table + narrative, per-rate Phase 2 narrative, toggled
appendices) is functionally superseded, for this notebook's real
architecture, by **Cell 8**, built independently via `_build_cell8.py`
(quick-jump index + single `max-height:800px` scrollable box + its own
already-correct AI-provenance flag — a different design, not toggled
appendices, chosen based on real-environment testing; see this
skill's internal version history). Left in place,
not removed, in case a future Phase 3 run against a fresh/unmodified
template still uses this cell-id target — but do not assume `yq7hcf8i`
corresponds to any particular cell number without checking the real
notebook first, the way this v2.25 fix originally failed to.

```python
def build_documented_steps_html(cluster_color_table_html, phase1_narrative_html,
                                 phase1_appendix_html, condensations):
    """
    v2.13: cluster_color_table_html (built by build_cluster_color_table_html())
    is placed immediately after the Phase 1 heading, before the narrative --
    matching the researcher's own reference mockup's ordering (coloured
    table, then the collapsed full report). Previously this function built
    Cell 7's Phase 1 section from the narrative alone, with no cluster
    table anywhere in it.

    v2.25: prepends the AI-provenance flag (same #FFA040 swatch table as
    Cells 5 and 13) once, for the whole cell -- not duplicated inside
    build_cluster_color_table_html() itself, since that function's output
    is only one piece embedded within this larger cell, the same way
    Cell 5's flag wraps its whole cell rather than being repeated per
    rate. Every piece of this cell's content is AI-selected/AI-assembled
    (Phase 1 clusters, Phase 2 condensation narrative), so the flag
    applies to the cell as a unit. Found and fixed as part of the same
    audit that added Cell 13's flag -- this cell had never been
    delivered, so there was no live artifact confirming the omission
    until this pass.
    Spacer after the flag is '<h2>&nbsp;</h2>', matching Cell 5's choice
    rather than Cell 8/13's '<h1>&nbsp;</h1>' one, since this cell's own
    first real heading ('<h2>Phase 1</h2>') is an h2 -- disclosed as a
    judgement call, not a fixed rule; there is no single spacer
    convention shared by every flagged cell in this project.

    condensations: same list, each also carrying 'phase2_narrative_html'
    and 'phase2_appendix_html' for that rate.
    """
    parts = [
        '<table align="left" border="2" cellpadding="3" cellspacing="1" style="width: 50px;">'
        '<tbody><tr><td style="background: #FFA040; width: 50px;">&nbsp;</td></tr></tbody></table>',
        '<h2>&nbsp;</h2>',
        '<h2>Phase 1</h2>', cluster_color_table_html, phase1_narrative_html]
    if phase1_appendix_html is not None:
        parts.append(toggle('Full per-term WordNet disambiguation appendix', phase1_appendix_html))
    parts.append('<h2>Phase 2</h2>')
    for c in condensations:
        parts.append(f'<h3>Phase 2 — {c["rate"]}% condensation</h3>')
        parts.append(c['phase2_narrative_html'])
        parts.append(toggle(f'Full per-span injection appendix — {c["rate"]}%', c['phase2_appendix_html']))
    return ''.join(parts)
```

### Building Cell 8 — the real replacement for `build_documented_steps_html()`

**Added v2.36, from a real researcher-supplied reference (`cell8-injection.html`,
the actual an earlier test corpus Cell 8 content, confirmed by the researcher as
"the same cell8" this section needs before this was written).** Closes
the gap this file's own cell-ownership table already disclosed (Section
7.6: Cell 8 needs "quick-jump index + one scrollable box," built by
`_build_cell8_v2.py`) but never actually fixed — that file was never part
of this project's own packaged materials, and `populate_notebook()`
kept calling the SUPERSEDED `build_documented_steps_html()` instead.

The real structure differs from `build_documented_steps_html()` in two
load-bearing ways, both confirmed directly against the reference file,
not assumed from the table's prose: **no `<details>`/toggle collapsing
anywhere** — Phase 1's full narrative, every approved rate's full Phase 2
narrative *and* its full injection appendix, and this run's own Phase 3
narrative all render flat, inline, inside one
`max-height:800px;overflow-y:auto` scrollable box; and **a quick-jump
`<ul>` index** (one link per approved rate, nested under "Phase 2") sits
above the box, pointing at old-style `<a name="...">` anchors inside it.
Direct inspection of the same reference file also confirmed
`build_cluster_color_table_html()`'s coloured cluster table does **not**
appear anywhere in real Cell 8 content — it is not called from this
function; whether it is used anywhere else in the real notebook is not
established here.

```python
def build_cell8_content(phase1_md, phase2_by_rate, phase3_md):
    """phase1_md: full Phase1-results.md text (unsplit -- no narrative/
    appendix separation, unlike the superseded function).
    phase2_by_rate: list of (rate, phase2_md_text) tuples, approved order,
    each the FULL Phase2-results.md text for that rate (unsplit).
    phase3_md: full Phase3-results.md text (this run's own).
    All three go through md_to_html() whole -- no toggle() calls."""
    quick_jump_rate_items = ''.join(
        f'<li><a href="#phase2-{rate}pct">Condensation at {rate}%</a></li>'
        for rate, _ in phase2_by_rate
    )
    quick_jump = (
        '<ul>\n'
        '\t<li><a href="#phase1">Phase 1</a></li>\n'
        '\t<li>Phase 2\n'
        f'\t\t<ul>\n\t\t\t{quick_jump_rate_items}\n\t\t</ul>\n'
        '\t</li>\n'
        '\t<li><a href="#phase3">Phase 3</a></li>\n'
        '</ul>'
    )
    phase2_sections = ''.join(
        f'<a name="phase2-{rate}pct">&nbsp;</a>\n<h3>Condensation at {rate}%</h3>\n{md_to_html(md_text)}\n'
        for rate, md_text in phase2_by_rate
    )
    box_content = (
        f'<a name="phase1">&nbsp;</a>\n<h2>Phase 1</h2>\n{md_to_html(phase1_md)}\n'
        '<h2>Phase 2</h2>\n'
        f'{phase2_sections}'
        f'<a name="phase3">&nbsp;</a>\n<h2>Phase 3</h2>\n{md_to_html(phase3_md)}'
    )
    return (
        '<table align="left" border="2" cellpadding="3" cellspacing="1" style="width: 50px;">\n'
        '\t<tbody>\n\t\t<tr>\n\t\t\t<td style="background: #FFA040; width: 50px;">&nbsp;</td>\n'
        '\t\t</tr>\n\t</tbody>\n</table>\n\n'
        '<h1 style="line-height:1.2em;">&nbsp;</h1>\n\n'
        f'{quick_jump}\n\n'
        '<div style="max-height:800px;overflow-y:auto;border:1px solid #ccc;padding:0.5rem 0.8rem;background:#f0ede6;">\n'
        f'{box_content}\n'
        '</div>'
    )
```

Verified against real data: built the real that later pilot test Phase 1/2/3
results.md files through this function, confirmed matching open/close
counts for every structural tag (`ul`, `li`, `div`, `table`, `tr`),
confirmed all three quick-jump anchors and their `<a name="...">`
targets are present, and confirmed no raw Markdown syntax (`#` headings,
`**bold**`) survived the `md_to_html()` pass.

### Building Cell 9 — "Global Configuration Parameters" (fixed, corpus-independent)

**Added v2.40, reversing v2.36.** v2.36 corrected a stale table row by
concluding Cell 9 should carry `phase3_results_html` — the opposite of
what the pristine template's own placeholder text
("[Populated by Phase 3 -- do not edit directly. If this text is still
here, Phase 3 has not yet been run for this notebook.]") actually
requires: it must be replaced with something (an unpopulated Cell 9 is
itself a signal Phase 3 hasn't run), but that something is not this
run's own results — it duplicates Cell 8, which already carries Phase
3's results in full. Live-Voyant-verified (Step 8.5): Cell 9 is a fixed, corpus-independent divider, the same
pattern as Cell 7 and Cell 14 (Section 6b.1) — the exact text below is
what the real, live notebook contains here.

```python
CELL9_FIXED_CONTENT = (
    '<div style="background:#0081AD; color: #FBFBFB; padding: 5px; height: 50px;">\n'
    '<h1><strong>Global Configuration Paramaters</strong></h1>\n'
    '</div>\n\n'
    '<blockquote>\n'
    '<p>Run the code cells below, one-by-one, sequentially, if they are not executed automatically when this notebook is loaded.</p>\n\n'
    '<div style="background:#eeeeee;border:1px solid #cccccc;padding:5px 10px;"><strong>LOADING MAY TAKE A WHILE DEPENDING ON SERVER TRAFFIC AND NOTEBOOK CONTENT VOLUME.</strong></div>\n'
    '</blockquote>\n\n'
    '<p>&nbsp;</p>\n\n'
    '<table align="left" border="2" cellpadding="3" cellspacing="1" style="width: 50px;">\n'
    '\t<tbody>\n'
    '\t\t<tr>\n'
    '\t\t\t<td style="background: #8AC29C; width: 50px;">&nbsp;</td>\n'
    '\t\t</tr>\n'
    '\t</tbody>\n'
    '</table>\n\n'
    '<p>&nbsp;</p>'
)
```

No generation needed beyond this constant — like Cell 14, this text is
generic across every corpus, not derived from any Phase 1/2/3 output.
Note the literal misspelling "Paramaters" is reproduced exactly as the
researcher's real notebook has it, not auto-corrected — this is her own
live template text, not this pipeline's prose.

### Master population function

```python
DELIVERABLE8_CELL_IDS = {
    14: 'n64goemm', 15: 'o3wrqaye', 16: 'j33xw4rk',
    17: 'jrs8uj1x', 18: 'oggheb4j', 19: 'or17hwbf', 20: 'tv9gwc6z',
}
# Confirmed directly against the researcher's real, live, saved notebook
# (PEEL3-SN-Ready-V1-2.html) by extracting every <section id='...'> in
# document order and matching against notebookwrappercounter -- not
# guessed, not carried over from a different template export.

def populate_notebook(template_html, corpus_id, cell0_js, cell1_js,
                       cluster_list_and_legend_html,
                       tools_js_text, condensations, phase1_md,
                       md_report_text,
                       summary_title, summary_author,
                       cell19_html):
    """Added v2.32: `cell19_html` is Deliverable 8's Cell 19 content,
    pre-built by `build_cell19_content()` (`_build_cell19.py`) from the
    researcher's Step 1.4 term choice -- passed in already-built, unlike
    Cells 14/15/16/17/18/20, which are fixed and corpus-independent
    (6b.1/6b.2/6b.4) and are built directly inside this function from
    `_build_cell19.py`'s `build_cell14_content()` etc., with no parameters
    of their own needed.

    Changed v2.36: `cluster_color_table_html`/`phase1_narrative_html`/
    `phase1_appendix_html` params removed -- `build_cell8_content()`
    (the real Cell 8 builder, replacing `build_documented_steps_html()`)
    takes the full, unsplit `phase1_md` and each rate's full, unsplit
    Phase 2 markdown directly (each `condensations` entry now also
    carries `'phase2_md'`, the raw text, alongside its already-built HTML
    fields used elsewhere).

    v2.47 fix (a later pilot test): normalizes `template_html`
    to bare LF as the very first operation, regardless of how the
    template file itself was read. Confirmed live: `*-TemplateSN.html`
    is itself CRLF-native on disk (196 CRLF, 0 bare LF, checked directly
    at the byte level) -- if that CRLF survives into `template_html` (as
    it would under a `newline=''` read, or under any read on a platform
    where universal-newlines doesn't apply), the final write step's own
    `newline=''` guard (see "Writing the file" below) cannot fix it,
    since `newline=''` only stops *further* translation, it does not
    retroactively normalize `\r\n` sequences already embedded in the
    string. Normalizing here, unconditionally, at the one point every
    code path already passes through, is more robust than trying to get
    every possible template-ingest path right instead -- matches the
    same `.replace('\r\n','\n').replace('\r','\n')` pattern this
    project already uses for other CRLF-native source files (Step 7.1's
    `an earlier test corpus-cells-tools.js` fix, `REDESIGN-STATUS.md`)."""
    html = template_html.replace('\r\n', '\n').replace('\r', '\n')

    html = populate_code_cell(html, 'yiyomzni',
        "// This line of code initiates the entire Spyral Notebook procedural content by associating\n"
        "// the corpusID you have identified with the variable 'myCorpus'\n\n"
        f"var myCorpus = '{corpus_id}';\n"
        "loadCorpus(myCorpus);\n"
        "show(\"Corpus ID: \" + myCorpus);")

    html = populate_code_cell(html, 'i5iee23p', cell0_js)
    html = populate_code_cell(html, 'cfgcell01x', cell1_js)

    tool_blocks = split_tool_cells_js(tools_js_text)
    for tool_name, cell_id in TOOL_CELL_IDS.items():
        if tool_name not in tool_blocks:
            raise ValueError(f"No generated block found for tool '{tool_name}'")
        html = populate_code_cell(html, cell_id, tool_blocks[tool_name])

    html = populate_text_cell(html, 'jb3c08qu', build_cell5_content(summary_title, summary_author, condensations))
    html = populate_text_cell(html, 'k0stufao', build_cell6_content(condensations))
    html = populate_text_cell(html, 'yq7hcf8i',
        build_cell8_content(phase1_md,
                             [(c['rate'], c['phase2_md']) for c in condensations],
                             md_report_text))  # RAW markdown -- build_cell8_content()
                                               # runs its own md_to_html().
    html = populate_text_cell(html, 'p3resultsx', CELL9_FIXED_CONTENT)  # v2.40 -- see below;
                                               # never phase3_results_html, which duplicates Cell 8.
    html = populate_text_cell(html, 'nbja51aq', cluster_list_and_legend_html)

    # Deliverable 8 (Section 6b), wired in for the first time v2.32.
    # Cells 14, 15, 17, 20 are text cells except 16/18/20 which are code --
    # matched against each real cell's actual kind (confirmed during the
    # same live-notebook extraction that produced DELIVERABLE8_CELL_IDS).
    html = populate_text_cell(html, DELIVERABLE8_CELL_IDS[14], build_cell14_content())
    html = populate_text_cell(html, DELIVERABLE8_CELL_IDS[15], build_cell15_content())
    html = populate_code_cell(html, DELIVERABLE8_CELL_IDS[16], build_cell16_content())
    html = populate_text_cell(html, DELIVERABLE8_CELL_IDS[17], build_cell17_content())
    html = populate_code_cell(html, DELIVERABLE8_CELL_IDS[18], build_cell18_content())
    html = populate_text_cell(html, DELIVERABLE8_CELL_IDS[19], cell19_html)
    html = populate_code_cell(html, DELIVERABLE8_CELL_IDS[20], build_cell20_content())

    return html
```

### Assembling and calling populate_notebook()

**Every approved rate is included — never a choice between them.** If the
researcher ran a 4-rate bundle in Phase 2, all four go in, in the order
they were run:

```python
# Assemble one dict per approved rate, in order. Each rate's Phase 2
# .md file is split into narrative + appendix, then converted to HTML;
# its _spyral.html is used directly for Cell 6. Cell 5's plain summary
# (v2.18) comes from Phase 2's own native `{corpus}-Summary-{rate}pct.txt`
# deliverable, not from stripping tags out of the _spyral.html fragment.
condensations = []
summary_titles_authors = []
for rate, spyral_html_content, phase2_md_content, summary_txt_content in approved_rates:  # e.g. [(15, ..., ..., ...), (25, ..., ..., ...)]
    narrative_md, appendix_md = split_narrative_and_appendix(
        phase2_md_content, ['## Injection appendix'])
    rate_title, rate_author, summary_body_lines = parse_summary_txt(summary_txt_content)
    summary_titles_authors.append((rate_title, rate_author))
    condensations.append({
        'rate': rate,
        'summary_body_lines': summary_body_lines,
        'full_details_html': spyral_html_content,
        'phase2_narrative_html': md_to_html(narrative_md),
        'phase2_appendix_html': md_to_html(appendix_md) if appendix_md else '(no appendix found in source file)',
        'phase2_md': phase2_md_content,  # v2.36: full, unsplit raw markdown -- build_cell8_content()
                                          # renders this whole (no narrative/appendix split, no toggle)
    })

# Title/author come from the same source text regardless of rate --
# refuse to guess if a rate's file somehow disagrees (v2.18, same
# discipline as Phase 1's T-3.39 and Phase 2's Step 0.0 JSON-selection
# fix: stop and ask rather than silently pick one).
if len(set(summary_titles_authors)) != 1:
    raise ValueError(
        f"Title/author disagree across rates' Summary.txt files: {summary_titles_authors!r} "
        "-- stopping rather than silently picking one.")
summary_title, summary_author = summary_titles_authors[0]

# v2.36: build_cell8_content() renders the FULL, unsplit Phase 1 report
# (no narrative/appendix split, no toggle -- see that function's own note).
# phase1_md is simply the raw file content, nothing derived from it here.
phase1_md = phase1_results_md_content

# v2.12 fix: cluster_list_and_legend_html previously had no function
# building it anywhere in this file (a guaranteed NameError, or a live
# improvisation with no escaping) -- now built explicitly, escaping-safe.
# v2.34 fix: now also passes summary_title/summary_author (already
# computed above from Phase 2's parse_summary_txt(), used for Cell 5)
# instead of leaving Deliverable 2 / Cell 13 with literal
# '[Author (Year)]'/'[Title]' placeholders.
cluster_list_and_legend_html = build_cluster_list_and_legend_html(
    clusterdefs, TABLEAU20, summary_title, summary_author)

# v2.13 fix: Cell 7's coloured cluster table -- previously never built or
# injected anywhere in this file. Distinct from cluster_list_and_legend_html
# above (Cell 13, Deliverable 2's own purpose); this one reproduces Phase
# 1's own Step 5.5 artifact, with corpus_name in its summary line.
cluster_color_table_html = build_cluster_color_table_html(
    clusterdefs, inclist, corpus_name)

# v2.40: the md_to_html(md_report_text) conversion this file used to do
# here (for Cell 9) is gone -- Cell 9 is fixed content now (CELL9_FIXED_
# CONTENT, see "Building Cell 9"), and Cell 8's build_cell8_content()
# takes the raw md_report_text directly, converting it itself. Keeping a
# separate, unused HTML conversion around here would be exactly the kind
# of dead value this project's own changelog warns against leaving in
# place "just in case."

# v2.32 addition: Deliverable 8's Cell 19, built from the pairs the researcher
# already chose in the combined elicitation round (Step 1.4) -- categories_id
# is `catsId`, confirmed by the time this runs (Deliverable 1, Cell 1);
# approved_rates is the same list Step 6's condensations loop above used.
# This is the only Deliverable 8 build call needed here -- Cells 14/15/16/17/
# 18/20 are built directly inside populate_notebook() itself, since they take
# no per-corpus arguments (6b.1/6b.2/6b.4).
#
# NOTE (fixed, usability/correctness review, 2026-07-28): this call site
# still passed `researcher_term=researcher_term` -- the pre-v2.49 single-
# term API -- but build_cell19_content() (see _build_cell19.py) has taken
# `selected_pairs, source_text, primary_term=None` since v2.49; there is
# no `researcher_term` parameter any more. Calling this exactly as
# written would raise a TypeError the first time Deliverable 8's current
# (v2.50/2.51) elicitation flow (Step 1.4) actually reached this point --
# confirmed by direct inspection of the real function signature in
# _build_cell19.py, not merely inferred from the changelog. Fixed to pass
# the two values Step 1.4 actually holds for this purpose.
cell19_html, cell19_elicitation = build_cell19_content(
    clusterdefs,
    comparison_corpus_id=voyant_comparison_corpus_id,  # confirmed at Step 7.4, NEVER phase1['corpusId']
    stoplist_id=voyant_stoplist_id,                    # confirmed at Step 7.4
    categories_id=catsId,                              # confirmed by Deliverable 1, Cell 1
    approved_rates=[c['rate'] for c in condensations],
    selected_pairs=selected_pairs,                     # confirmed at Step 1.4, held since
    source_text=source_text,                           # loaded at Step 1.4's prerequisite scan, held since
    voyant_host=voyant_host,                           # v2.52 -- confirmed at Step 1.3's combined round, held
                                                        # since; NEVER hardcoded (see v2.52 changelog: the real
                                                        # 2026-08-01 incident this parameter exists to prevent)
)

populated_html = populate_notebook(
    template_html=template_html_content,       # the uploaded *-TemplateSN.html
    corpus_id=phase1['corpusId'],               # NEVER corpus_name
    cell0_js=cell0_js_content,                  # Deliverable 1, Cell 0
    cell1_js=cell1_js_content,                  # Deliverable 1, Cell 1
    cluster_list_and_legend_html=cluster_list_and_legend_html,  # Cell 13, Phase 1 list + Deliverable 2
    tools_js_text=tools_js_content,             # Deliverable 3, already written to disk
    condensations=condensations,
    phase1_md=phase1_md,                        # v2.36, raw -- build_cell8_content() converts it whole
    md_report_text=md_report_text,              # v2.40, raw -- build_cell8_content() converts it whole; Cell 9 no longer uses this
    summary_title=summary_title,                # v2.18, from Phase 2's Summary.txt files
    summary_author=summary_author,              # v2.18, from Phase 2's Summary.txt files
    cell19_html=cell19_html,                    # v2.32, Deliverable 8
)
```

### Verification (mandatory, run before writing the file)

**Scoped deliberately to only the cells this deliverable owns** — cell 2's
citation and cell 44's Researcher's Notes are the researcher's own
content and must never be flagged as "missing," since Deliverable 6 was
never meant to touch them. **Also confirms every approved rate is
actually present in Cells 5 and 6** — not just that the cells were
touched, but that no rate was silently dropped:

**v2.12 addition — a permanent, class-level check, not another one-off
symptom fix.** Every prior check here confirms cells were *touched*
(placeholders gone, rates present) but never checked *how* — a real test
run's notebook passed every one of these checks with 40 unescaped `&`
characters still in it, which is exactly what broke Voyant's upload.

**Important implementation detail, confirmed empirically before relying
on it:** the new check must scan the **raw markup string directly**,
using the same regex-based section extraction `populate_code_cell()` and
`populate_text_cell()` already use — **not** `BeautifulSoup`. Tested
this directly: parsing a snippet containing a genuinely unescaped
`Virtue & Character` with `BeautifulSoup(html, 'html.parser')` and then
calling `str()` on the parsed tag silently *re-escapes* it back to
`Virtue &amp; Character` on output. That means a check written as
`_find_unescaped(str(soup.find(...)))` would **always pass**, even
against the exact file that had the real bug — it would silently fix the
evidence before checking it. The raw-string, regex-based extraction
below is not a stylistic choice; it's the only approach that actually
sees what the file contains:

```python
DELIVERABLE6_CODE_CELLS = (
    ['yiyomzni', 'i5iee23p', 'cfgcell01x'] + list(TOOL_CELL_IDS.values())
    + [DELIVERABLE8_CELL_IDS[n] for n in (16, 18, 20)]  # v2.32, Deliverable 8's code cells
)
DELIVERABLE6_TEXT_CELLS = (
    ['jb3c08qu', 'k0stufao', 'yq7hcf8i', 'p3resultsx', 'nbja51aq']
    + [DELIVERABLE8_CELL_IDS[n] for n in (14, 15, 17, 19)]  # v2.32, Deliverable 8's text cells
)

# Matches the exact pattern that found 40 real, confirmed instances
# against a genuinely broken notebook with zero false positives.
_UNESCAPED_AMP = re.compile(r'&(?!amp;|lt;|gt;|quot;|#39;|#x[0-9a-fA-F]+;|#\d+;|nbsp;|mdash;|ndash;|middot;|copy;)')
# Corrected v2.32, found by end-to-end execution against real an earlier test corpus
# data, not by reading: this allow-list previously rejected two classes of
# genuinely well-formed entity, both present in real, researcher-approved
# content -- `&ndash;` (present verbatim in the real, live-approved Cell 15
# text ported into build_cell15_content(), Section 6b.2) and hex-form
# numeric character references like `&#x27;` (175 real instances found in
# Phase 2's own approved `_spyral.html` content for Cell 6, `k0stufao`,
# apostrophes encoded by whatever rich-text editor produced that file).
# `#\d+;` only ever matched decimal numeric entities (`&#39;`), never the
# equally valid hex form -- both are legitimate HTML, neither would break
# Voyant's upload parser, and flagging them was a false positive in the
# check, not a real defect in the delivered notebook.
_STRAY_ANGLE = re.compile(r'<(?![a-zA-Z/!])')

def _raw_pre(html, cell_id):
    """Extracts only the authoritative raw <pre> block for a code cell --
    same scope populate_code_cell() itself writes to. Deliberately
    excludes the decorative CodeMirror preview markup (frozen, untouched,
    out of scope -- see the disclosed limitation above), so that markup's
    ordinary tag-like HTML can't produce false positives here."""
    m = re.search(
        rf"<section id='{cell_id}'.*?<pre class='notebook-code-editor-raw[^']*'>(.*?)</pre>",
        html, re.DOTALL)
    if not m:
        raise ValueError(f"Cell {cell_id} not found or has no raw source block")
    return m.group(1)

def _raw_text_div(html, cell_id):
    """Extracts only the notebook-text-editor div's inner content for a
    text cell -- same scope populate_text_cell() itself writes to (in
    fact, the identical two regexes, reused rather than re-derived). No
    parser involved, so nothing gets silently re-escaped or normalized
    before it's checked."""
    section_m = re.search(rf"<section id='{cell_id}'.*?</section>", html, re.DOTALL)
    if not section_m:
        raise ValueError(f"Cell {cell_id} not found")
    section_html = section_m.group(0)
    div_m = re.search(
        r"(<div class='notebook-text-editor'>).*(</div>\s*</section>)$",
        section_html, re.DOTALL)
    if not div_m:
        raise ValueError(f"Text editor div not found in cell {cell_id}")
    return section_html[div_m.end(1):div_m.start(2)]

def _find_unescaped_special_chars(raw_section_html, cell_id):
    problems = []
    amp_hits = _UNESCAPED_AMP.findall(raw_section_html)
    if amp_hits:
        problems.append(f"[{cell_id}] {len(amp_hits)} unescaped '&' found — this is exactly the class of "
                         f"defect that breaks Voyant's upload parser; run every raw text fragment through esc() first")
    if _STRAY_ANGLE.search(raw_section_html):
        problems.append(f"[{cell_id}] stray '<' not part of a real tag found")
    return problems

def verify_populated_notebook(html, condensations, corpus_name, selected_pairs):
    soup = BeautifulSoup(html, 'html.parser')
    problems = []
    for cell_id in DELIVERABLE6_CODE_CELLS:
        section = soup.find('section', id=cell_id)
        text = section.find('pre', class_='notebook-code-editor-raw').get_text()
        if 'PASTE' in text or 'INSERT' in text:
            problems.append(f"[{cell_id}] raw code cell still has placeholder: {text[:60]!r}")
        problems.extend(_find_unescaped_special_chars(_raw_pre(html, cell_id), cell_id))
    for cell_id in DELIVERABLE6_TEXT_CELLS:
        section = soup.find('section', id=cell_id)
        text = section.find('div', class_='notebook-text-editor').get_text()
        if 'INSERT' in text or 'PASTE' in text:
            problems.append(f"[{cell_id}] text cell still has placeholder: {text[:60]!r}")
        problems.extend(_find_unescaped_special_chars(_raw_text_div(html, cell_id), cell_id))
    # Corrected v2.32, found by end-to-end execution against real an earlier test corpus
    # data, not by reading: this check previously used the SAME marker format
    # for both cells, but build_cell5_content() and build_cell6_content()
    # generate genuinely different heading markup -- Cell 5's real,
    # researcher-confirmed heading is `<h2>Summary at <u><tt>{rate}%</tt></u>
    # &nbsp;condensation rate</h2>` (v2.18), which get_text() renders as
    # "Summary at {rate}%\xa0condensation rate" (note the &nbsp; becomes a
    # non-breaking space, U+00A0, not a regular space, and "condensation"
    # sits between the percentage and "rate"); Cell 6's is the simpler
    # `<h2>Summary at {rate}% rate</h2>`. The single shared marker
    # `f"Summary at {rate}% rate"` matched Cell 6 but could never match
    # Cell 5, so a correctly-built Cell 5 would always fail this check --
    # a false failure in the verification, not a real dropped rate.
    _RATE_MARKERS = {
        'jb3c08qu': lambda rate: f"Summary at {rate}%\xa0condensation rate",
        'k0stufao': lambda rate: f"Summary at {rate}% rate",
    }
    for cell_id, marker_fn in _RATE_MARKERS.items():
        section = soup.find('section', id=cell_id)
        text = section.find('div', class_='notebook-text-editor').get_text()
        for c in condensations:
            marker = marker_fn(c['rate'])
            if marker not in text:
                problems.append(f"[{cell_id}] missing rate section: {marker!r} — a rate was dropped, not just unfilled")
    # v2.36: replaces the v2.13 "Semantic Clusters"/corpus_name check, which
    # verified build_documented_steps_html()'s coloured-table output -- no
    # longer what this cell actually contains (see build_cell8_content()'s
    # own note: that table doesn't appear in the real Cell 8 at all).
    # Checks instead for the real structure's own load-bearing markers: the
    # quick-jump anchors and all three phase headings, confirming the cell
    # was built by build_cell8_content(), not left with stale/superseded
    # content or just touched-but-wrong.
    cell8_text = soup.find('section', id='yq7hcf8i').find('div', class_='notebook-text-editor').get_text()
    for marker in ('Phase 1', 'Phase 2', 'Phase 3'):
        if marker not in cell8_text:
            problems.append(f"[yq7hcf8i] missing '{marker}' section heading in Cell 8")
    for rate in [c['rate'] for c in condensations]:
        marker = f"Condensation at {rate}%"
        if marker not in cell8_text:
            problems.append(f"[yq7hcf8i] missing {marker!r} in Cell 8 -- a rate was dropped, not just unfilled")
    cell8_html = _raw_text_div(html, 'yq7hcf8i')
    for anchor in ('name="phase1"', 'name="phase3"'):
        if anchor not in cell8_html:
            problems.append(f"[yq7hcf8i] missing quick-jump anchor {anchor!r} -- build_cell8_content() may not have run")
    # v2.32 addition: same "touched is not the same as correct" principle,
    # applied to Deliverable 8. A build that silently passed a stale or
    # wrong selection into build_cell19_content() (e.g. an argument left
    # over from a prior test run) would still pass every check above,
    # since Cell 19 would still be non-placeholder, tag-balanced content --
    # just built from the wrong elicitation answer.
    #
    # NOTE (fixed, usability/correctness review, 2026-07-28): this check
    # used to test a single `researcher_term` string against Cell 19's
    # text -- the pre-v2.49 single-term API. Since v2.49, the researcher
    # confirms one or more source-confirmed PAIRS (selected_pairs), not a
    # single term, so the check now confirms every confirmed pair's two
    # terms actually appear in Cell 19, matching the same
    # dict-or-tuple pair shape build_contexts_block() already handles
    # in _build_cell19.py (a pair is either a candidate dict with
    # 'term_a'/'term_b' keys, or a plain (a, b) tuple).
    cell19_text = soup.find('section', id=DELIVERABLE8_CELL_IDS[19]).find('div', class_='notebook-text-editor').get_text()
    for pair in selected_pairs:
        term_a, term_b = (pair['term_a'], pair['term_b']) if isinstance(pair, dict) else pair
        if term_a not in cell19_text or term_b not in cell19_text:
            problems.append(f"[{DELIVERABLE8_CELL_IDS[19]}] researcher's confirmed Step 1.4 pair {(term_a, term_b)!r} not found in Cell 19 — check for a stale/wrong pair passed to build_cell19_content()")
    return problems

problems = verify_populated_notebook(populated_html, condensations, corpus_name, selected_pairs)
if problems:
    raise AssertionError(
        "Deliverable 6 verification FAILED — do not write or present this "
        "file:\n" + "\n".join(f"  - {p}" for p in problems)
    )
```

### Writing the file (mandatory, `newline=''` — do not use plain `open(..., 'w')`)

**Added v2.47 — closes a real
gap: no write step for this deliverable was ever documented as code
anywhere in this file, only implied.** On Windows, Python's default
text-mode `open(path, 'w', encoding='utf-8')` silently translates every
`\n` in the string being written to `\r\n` — even when the in-memory
`populated_html` string, and the template it was built from, are bare-LF
throughout. This is the exact "CRLF corruption breaks Spyral's parser"
failure this project has already diagnosed and fixed twice before, in
two different places (Deliverable 6's own delivery step,
and the merged-stopword-list write, Step 7.2) — but the fix (`newline=''`
on both read and write) was never actually threaded into this specific,
undocumented write step, because the step itself was never written down
as real code for anyone to apply the fix to.

Confirmed live: a notebook
generated and delivered without this guard was 100% CRLF (1233 CRLF, 0
bare LF) — while a confirmed-working reference notebook from a
different corpus (uploaded successfully, no parsing
warning) was 100% bare LF (0 CRLF, 514 bare LF). The two files' document
skeleton, per-cell tag balance, and code-cell content were otherwise
checked and found equivalent — line endings were the one remaining,
previously-unchecked difference, and match this project's own prior
diagnosis exactly.

```python
output_path = f'/home/claude/{corpus_name}-PEEL-Notebook.html'
with open(output_path, 'w', encoding='utf-8', newline='') as f:
    f.write(populated_html)

# Verify: reload and confirm bare-LF survived the write, not silently
# CRLF-converted -- the specific failure mode this guard exists for.
with open(output_path, 'rb') as f:
    raw = f.read()
crlf_count = raw.count(b'\r\n')
if crlf_count:
    raise AssertionError(
        f"Deliverable 6 write produced {crlf_count} CRLF line endings -- "
        "the exact corruption that breaks Spyral's import parser. Do not "
        "present this file. Check that newline='' was actually passed to "
        "open(), and that template_html_content (Step 0's own template "
        "ingest) was itself read with newline='' too, not just this write."
    )
print(f"Deliverable 6 written and verified bare-LF: {output_path}")
```

### Disclosed limitation (mandatory, every time this deliverable is produced)

The substitution functions above replace only the **authoritative raw
source** — the `<pre class='notebook-code-editor-raw...'>` content for
code cells and the `notebook-text-editor` div for text cells. They do
**not** touch the decorative CodeMirror syntax-highlighting preview
markup baked into the original template export, since that markup is a
frozen visual snapshot, not something Spyral reads to reconstruct a live
notebook, and regenerating syntax-highlighted HTML by hand is
impractical. This means a handful of cells may show stale placeholder
text in their cosmetic preview even though the actual content underneath
is correct and complete. State this explicitly to the researcher every
time — do not let a clean verification pass be read as "everything looks
correct in every possible sense":

```
Note on Deliverable 6: the underlying content of every cell is complete
and verified, including every approved rate in Cells 5, 6, and 7. A
small number of cells may still show placeholder text in their
decorative preview rendering (a cosmetic snapshot from the original
template export) -- this does not affect what Spyral actually reads. It
will resolve automatically the next time the cell is opened and
re-rendered live in Spyral; it is not a defect in the delivered file.
```

### Filename

`[corpus_name]-PEEL-Notebook.html`

---

## 8. Output Files and Delivery

**NOTE (fixed):** delivery is now in **two rounds**, not one — the merged
stopword list and the comparison corpus ZIP must reach the researcher,
and the researcher must upload both and report both real Voyant-assigned
IDs, before anything depending on either value can be generated (see
Step 7.3/7.4).

**Round 1 — intermediate delivery, at Step 7.3, run FIRST in the session
(see "Execution order"):**

```bash
cp /home/claude/[name]-stoplist-merged.txt      /mnt/user-data/outputs/
cp /home/claude/[name]-comparison-corpus.zip    /mnt/user-data/outputs/
```

Present both together with `present_files` and stop — do not proceed to
Round 2 until both `voyant_stoplist_id` and `voyant_comparison_corpus_id`
are confirmed and validated (Step 7.4).

**Round 2 — final delivery, once both IDs are confirmed:**

```bash
cp /home/claude/[name]-cell-config.js        /mnt/user-data/outputs/
cp /home/claude/[name]-colour-legend.html    /mnt/user-data/outputs/
cp /home/claude/[name]-cells-tools.js        /mnt/user-data/outputs/
cp /home/claude/[name]-Phase3-results.md     /mnt/user-data/outputs/
cp /home/claude/[name]-PEEL-Notebook.html    /mnt/user-data/outputs/   # only if the template was uploaded (Step 7.6)
```

Present with `present_files` in this order:
1. `[name]-cell-config.js`
2. `[name]-colour-legend.html`
3. `[name]-cells-tools.js`
4. `[name]-Phase3-results.md`
5. `[name]-PEEL-Notebook.html` (Deliverable 6, if the template was provided)

Suggested filename pattern: `[author][year]-cell-config.js` etc.

---

## 8.5 — Post-delivery live-Voyant checkpoint

**Added v2.37.** Restructures
Phase 3 away from treating Round 2's delivery (Step 8) as the end of the
process.

**Rationale.** Deliverable 6's own Disclosed Limitation (Step 7.6) already
admits that `verify_populated_notebook()` can only check the authoritative
raw source of each cell — it cannot see how the notebook actually renders
once opened live in Voyant, the same class of gap that made Step 7.3 a
mandatory pause rather than a hand-off-and-hope instruction for Voyant-
assigned IDs. Historically, the only time a Phase 3 deliverable's live
rendering was ever actually confirmed (Cell 19, v2.31) was incidental —
noticed during unrelated debugging, not produced by a dedicated step.
This section closes that gap by making
the ask explicit, the same way 7.3 already does for IDs — while stopping
short of making it unconditional.

**What this checkpoint is, and what it is not (reframed v2.54 — see
changelog).** This is an offer of a genuine safeguard Phase 3 cannot
otherwise provide, not a monitoring requirement Claude is positioned to
size for her. How much verification a given run warrants is the
researcher's own informed judgment call, shaped by her actual purpose
for it — a notebook she needs to hand off or rely on immediately, where
confirming live rendering now is worth the loop; an exploratory build
she'll open and work through herself soon after, where deferring the
check costs little; a routine regeneration of a corpus she's already
confirmed rendering for once before, where re-checking every time adds
process without adding safety. All three are legitimate, and none of
them is this skill's business to weigh or question — offer the check
plainly, accept either answer at face value, and do not frame declining
it as a lesser or riskier choice than accepting it.

**Trigger.** After Round 2 of Step 8 delivers the populated notebook
(and, on the first-ever run against a given corpus, after the researcher
has already completed the `catsId` round-trip from "Execution order" item
3.5), tell her plainly that Phase 3's own structural checks cannot confirm
live rendering, and ask:

```
Deliverable 6 has passed every structural check I can run offline (tag
balance, escaping, placeholder absence, correct IDs in Cells 0/1/11), but
none of that confirms how the notebook actually renders once it's live in
Voyant -- the same limitation Step 7.6 already discloses. Would you like
to open it there and confirm, or skip this check for this run?
```

**Skip path.** If the researcher declines — for this run specifically,
not as a standing preference — record that decision plainly in
`Phase3-results.md` (see "Durable disclosure" below) and close this step
without further action. A decline is not silence: it must be stated by
the researcher, not assumed from her moving on to something else. Do not
skip this step on her behalf, and do not re-ask if she has already
declined it earlier in the same session.

**Closure condition.** This step closes only when one of two things
happens, stated explicitly by the researcher — never inferred from
silence, matching every other checkpoint in PEEL:
1. She confirms the notebook renders correctly in live Voyant (a general
   "looks good" / "confirmed" is sufficient once she has actually opened
   it — do not require a tool-by-tool sign-off unless she gives one), or
2. She explicitly declines the check for this run (the skip path above).

If she goes quiet without either, ask once, plainly:

```
Are you able to confirm the notebook renders correctly in Voyant, or
would you rather skip that check for this run?
```

**Handling a reported problem.** If instead she reports something wrong:
1. Identify which cell(s) are affected from her report.
2. Look up the owning builder in Step 7.6's cell-ownership table (Section
   "Cell ownership, confirmed with the researcher, cell by cell") — this
   table is the dispatch map; do not guess which function owns a cell or
   improvise a fix outside the function that actually produced it.
3. Fix the identified gap in that builder function, following Part 1's
   own fix-and-verify standard (execute against the real data for this
   corpus, inspect the actual output — a description of a fix is not a
   fix).
4. Rebuild only the affected deliverable file(s) — not a full regeneration
   of every deliverable, unless the fix genuinely touches more than one.
5. Re-run `verify_populated_notebook()` (Step 7.6) against the corrected
   notebook before redelivering.
6. Redeliver the corrected file(s) via Step 8's Round 2 pattern.
7. The checkpoint reopens: return to "Closure condition" above. The
   researcher's confirmation now applies to the corrected notebook, not
   the one that had the problem.

**Durable disclosure.** Whatever the outcome — confirmed, declined, or
fixed-and-reconfirmed — record it in `Phase3-results.md`, not only in
chat (chat-only disclosure is not durable, the same discipline Phase 2's
Step 4 report already enforces). Append one of the following directly
under a `## Live Voyant confirmation` heading, using the actual date:

- `**CONFIRMED RENDERING CORRECTLY IN LIVE VOYANT (YYYY-MM-DD):** <what
  the researcher reported, e.g. "all cells, researcher-confirmed">`
- `**SKIPPED FOR THIS RUN, RESEARCHER'S EXPLICIT DECISION (YYYY-MM-DD):**
  live-Voyant rendering was not checked; Deliverable 6's structural
  verification (Step 7.6) is the only evidentiary basis for this run's
  notebook.`
- `**FIXED AND RECONFIRMED (YYYY-MM-DD):** <cell(s)>, <what was wrong>,
  <what was fixed>, <the builder function corrected>. Confirmed rendering
  correctly by the researcher after redelivery.`

If a problem is reported and fixed, also add the matching changelog entry
to this skill file itself (this file's own established format — version
bump, context tag, what triggered it, what was fixed, how it was
verified), the same way every other real bug found against a real corpus
already has been.

---

## 9. Pre-Generation Checklist

- [ ] Phase 1 JSON successfully loaded; all three structures validated
- [ ] `stop.en.smart.txt` successfully loaded
- [ ] Number of clusters ≤ 20 (Tableau20 limit)
- [ ] All C[nn] tokens derived; token table confirmed by user
- [ ] All auto-corrections (non-content first words) flagged and accepted
- [ ] All collisions resolved before any JS generation
- [ ] Cross-cluster stems identified and documented in JS config header
- [ ] Tableau20 colours assigned sequentially in Phase 1 cluster order
- [ ] `clusterDefs` array covers all Phase 1 clusters — no cluster dropped
- [ ] Each cluster's `terms` array matches Phase 1 output exactly — no re-stemming
- [ ] `incList` array: 8 stems per line, alphabetical, double-quoted
- [ ] Merged stopword list AND comparison corpus ZIP delivered together
  (Round 1) **before** any other deliverable is generated — this is the
  first thing the researcher receives in the session, not something
  reached mid-run
- [ ] Comparison corpus ZIP contains exactly one entry per approved rate
  plus the source text (verified by reload, not just asserted at write time)
- [ ] Session paused after Round 1 until the researcher reports BOTH real
  Voyant-assigned IDs — never proceeded on a placeholder or guess for either
- [ ] Stoplist ID validated against `keywords-<32hexchars>`; comparison
  corpus ID validated against a plain 32-hex-character pattern; a
  mismatch on either was reported back specifically and a corrected
  value requested, not silently accepted
- [ ] **Cell 0** contains the real, confirmed `voyant_stoplist_id` —
  never `"PASTE-STOPLIST-ID-HERE"` — while remaining its own separate cell
- [ ] **Cell 11** contains the real, confirmed `voyant_comparison_corpus_id`
  — never `"PASTE-COMPARISON-CORPUS-ID-HERE"`
- [ ] **Cell 1** contains `incList`, `clusterDefs`, `catsId`, and Spyral instantiation
- [ ] `catsId` declared as `""` before `cats.save()`
- [ ] `cats.save()` uses `function(id)` callback — never `function(saved) { saved.id }`
- [ ] Every tool cell declares `categories` explicitly — either `catsId` or `"none"`
- [ ] `catsId` tools: Trends, Bubblelines, CollocatesGraph, Contexts
- [ ] `"none"` tools: Reader, Cirrus, Phrases, CorpusTerms (v2.32 — Summary
  and Documents removed from this list; they are Deliverable 8 cells now,
  not Deliverable 3 tool cells, and are checked separately below)
- [ ] `stopList` present only in Cirrus (`excListFull`) among Deliverable 3's
  8 tool cells (v2.32 — Summary's `stopList` is now checked under
  Deliverable 8, Cell 18, not here)
- [ ] `whiteList` not present on any tool cell (v2.21 — removed from Cirrus, the only tool that ever used it; Voyant's Cirrus silently drops multi-word `whiteList` entries)
- [ ] Contexts' `query` array has real stems/terms/N-grams from this corpus's own `incList` in its second and third slots — never the generic template placeholders (`<REAL_WILDCARD_STEM_FROM_INCLIST>`, `<TERM_A>|<TERM_B>|<TERM_C_OR_NGRAM>`) left un-substituted (v2.22, real bug found in the delivered an earlier test corpus artifact)
- [ ] All 8 remaining tool cells use `loadCorpus(myCorpus)` — never `loadCorpus(corpusId)`
- [ ] JS2, JS4–JS10 (8 tool cells — Summary/JS3 and Documents/JS11 removed
  v2.32, relocated to Deliverable 8) in a single file in notebook order,
  separated by blank lines
- [ ] HTML colour legend: hex converted to `rgb()` programmatically
- [ ] Merged stopword list: deduplicated, sorted, header comment written
- [ ] Merged stopword list: verified by reload and non-comment line count
- [ ] (v2.33) Step 7.0b's optional `*-excList-comprehensive.json` check ran
  before Step 7.1, and `exclist_source_status` was set from its real
  result -- never skipped, never silently defaulted to narrow without the
  check actually running
- [ ] (v2.33) If no comprehensive file was found, the fallback warning was
  actually reported to the researcher in chat, not only logged -- and
  `Phase3-results.md`'s `## excList source` heading states plainly which
  source (comprehensive or narrow) was used, matching what the merged
  stopword list's own header comment says
- [ ] (v2.55) Step 7.0c's mandatory automatic numeral scan ran regardless
  of whether a comprehensive excList file was found, its count (including
  zero) was reported to the researcher in chat, and `auto_numeral_exclist`
  is unioned into `exc_terms` before the merge -- never skipped, never
  made conditional on Step 7.0b's outcome
- [ ] Session log (Step 0) started before any other step, and the resolved
  absolute working directory (v2.55) was stated to the researcher, not
  just assumed
- [ ] Environment precondition (Step 0.9) confirmed before proceeding
- [ ] `corpus_name` confirmed with the user before any deliverable is generated
- [ ] `Phase3-results.md` assembled and its required headings verified
      before any file is written
- [ ] If the template was uploaded: Deliverable 6 generated, verified
  (scoped to its own owned cells only), and the CodeMirror-preview
  caveat disclosed explicitly — never silently omitted or claimed as a
  perfect result
- [ ] If the template was **not** uploaded: Deliverable 6 explicitly
  reported as skipped, not silently absent
- [ ] No unescaped `&`/`<`/`>` in any populated text or code cell —
  verified automatically by `verify_populated_notebook()`'s raw-string
  scan, not by manual inspection (v2.12: this is what a real test run's
  Voyant upload failure traced back to; every raw text fragment — Phase
  1/2/3 report content, cluster names — must go through `esc()` before
  being spliced into HTML)
- [ ] Deliverable 8 (Cells 14-20) not generated before Deliverable 7's
  `voyant_comparison_corpus_id` is confirmed -- every cell in this block
  loads `myComparisonCorpus`
- [ ] (v2.32) The combined elicitation round (Step 1.3/1.4: `corpus_name`,
  the token table, and the Deliverable 8 term) was presented to the
  researcher as one message, not split across separate interruptions --
  and no further researcher question was asked at any later point in the
  run outside the one unavoidable Voyant ID round-trip (Step 7.3/7.4)
- [ ] (v2.32) `populate_notebook()` actually received and injected Cells
  14-20 using the real ids in `DELIVERABLE8_CELL_IDS` -- not silently
  skipped because Deliverable 6 was written before Deliverable 8 existed
- [ ] (v2.32) `TOOL_CELL_IDS` contains exactly 8 entries (no `'SUMMARY'`/
  `'DOCUMENTS'` keys) and Section 6's JS3/JS11 blocks were not
  regenerated -- confirms the Deliverable-3/Deliverable-8 collision this
  version fixed hasn't silently crept back in
- [ ] (v2.32, updated v2.49/2.50 for the selected_pairs API)
  `verify_populated_notebook()`'s selected_pairs check passed -- Cell 19
  actually contains every source-confirmed pair confirmed at Step 1.4,
  not a stale or mismatched one
- [ ] Cell 19's five tools are all present (Trends, Bubblelines, Cirrus,
  Contexts, CorpusCollocates) -- never a researcher-selectable subset
- [ ] Cell 19's Trends/Bubblelines `query` defaults to the first three
  clusters in Phase 1 order, matching 6.3's rule -- verified against the
  real Distant Reading Trends/Bubblelines cells, not assumed
- [ ] Cirrus, Contexts, and CorpusCollocates each have exactly three
  iframes (`docIndex` 0/1/2), never one shared iframe across documents
- [ ] Cell 19 calls `.tool("CorpusCollocates", ...)`, never
  `.tool("CollocatesGraph", ...)` -- CollocatesGraph cannot render a
  multi-document corpus
- [ ] (v2.50) The researcher's selected collocation pair(s) come from
  `find_source_collocations()`'s real candidate list (Step 1.4) -- never
  a pair with zero confirmed source co-occurrences, and never derived by
  the old deterministic "companion cluster" formula -- before Contexts'
  query is finalized. CorpusCollocates' single anchor term is the first
  selected pair's `term_a`, disclosed as a simplification (Section
  6b.3c's SUPERSEDED note), not left as generic placeholder text
- [ ] Every `palette: "Tableau10"` in Cell 19's code blocks has a matching
  `palette=Tableau10` in its corresponding iframe URL -- code and iframe
  checked as a pair, not just one or the other (value changed from
  Tableau20 in v2.57; see Lesson 9 and the v2.57 changelog entry)
- [ ] Cell 19's description prose (query descriptions, document-count
  language) was generated from the real, current query/rate values --
  never left over from an earlier draft
- [ ] No cell in the 14-20 block references a hardcoded document count in
  prose ("both summaries") where a count-agnostic phrase would do
- [ ] All files (five, or six if the template was provided; seven if
  Deliverable 8 was generated) written to
  `/mnt/user-data/outputs/` and presented
- [ ] (v2.37) Step 8.5's post-delivery checkpoint offered explicitly after
  Round 2 delivery — never silently skipped on the agent's own initiative
- [ ] (v2.37) Step 8.5 closed only on the researcher's explicit
  confirmation or explicit decline, never inferred from silence — and, if
  she reported a problem instead, the fix was routed through Step 7.6's
  cell-ownership table to the actual owning builder, re-verified via
  `verify_populated_notebook()`, and redelivered before the checkpoint was
  treated as closed again
- [ ] (v2.37) Step 8.5's outcome (confirmed, skipped, or fixed-and-
  reconfirmed) recorded under `Phase3-results.md`'s `## Live Voyant
  confirmation` heading — not left as chat-only disclosure

---

## 10. Lessons Encoded

1. **Phase 1 is authoritative.** Never re-select, re-stem, or re-cluster in
   Phase 3. The incList, excList, and clusterDefs from Phase 1 are consumed
   exactly as produced.

2. **The configuration is two cells, not one — and generation now pauses
   until the real Voyant ID is confirmed.** `excListFull` lives in **Cell
   0** alone. Originally this was because the ID was "unknowable before
   the user uploads the file"; that upload now happens mid-session, as a
   mandatory checkpoint (Step 7.3/7.4), so the value is confirmed and
   validated *before* Cell 0 is even generated — it is never a
   fill-in-later placeholder. The cells stay separate anyway: isolating
   this one value still protects against a researcher re-running things
   out of order later, and it costs nothing to keep. `incList`,
   `clusterDefs`, and `catsId` live in **Cell 1**. Cell 0 must be run
   first; Cell 1 reads `excListFull` as an already-declared global. This
   separation is safe because Spyral cells share a single JS scope
   within a notebook — globals declared in Cell 0 are visible in all
   subsequent cells.

3. **Non-content first words are auto-corrected, not hard-stopped.** Articles
   (`the`, `a`, `an`) and common prepositions produce meaningless tokens.
   Skip to the first content word and flag the correction to the user.

4. **Collisions require user resolution before output.** The `nn` numeral
   makes every token technically unique, but duplicate first-word substrings
   are confusing in `@Category` queries. Always resolve before generating JS.

5. **Cross-cluster stems are preserved exactly.** A stem appearing in two
   Phase 1 clusters appears in both `clusterDefs` entries. Document in header.

6. **Every tool cell must declare `categories` explicitly.** Voyant inherits
   the global `catsId` implicitly when `categories` is omitted, applying its
   default "good/bad" colouring in an uncontrolled way. The two valid values
   are `catsId` (intentional use) and `"none"` (explicit cancellation).
   An empty string `""` does not reliably cancel the default — always use
   `"none"`.

7. **`cats.save()` resolves directly to the ID string.** Use
   `cats.save().then(function(id) { catsId = id; })`. Never
   `function(saved) { var catsId = saved.id; }` — `saved.id` is `undefined`.

8. **Pass `catsId` to `categories`, never the `cats` object.** Passing `cats`
   directly causes HTTP 414 URI Too Long on Trends and other tools.

9. **Tableau20 colours are hardcoded as hex for the HTML legend's own CSS
   styling -- this is a separate fact from the tool cells' `palette`
   parameter.** The legend (Deliverable 2) sets inline `background-color`
   via CSS, which cannot interpret a palette name, so it converts hex to
   `rgb()` programmatically. This does NOT mean the same is true of every
   tool cell's own `config.palette` key -- **correction,
   real-Voyant-verified**: every tool cell's `palette: "Tableau20"` (both
   in the JS `config` object and in the equivalent iframe URL's
   `palette=Tableau20` query parameter) does work and is confirmed correctly
   rendering Tableau20 colours in live Voyant. An earlier version of this lesson claimed otherwise; that
   claim was never actually verified and was wrong.

   **Further correction (v2.57):** every tool cell's `palette`
   value was changed from `"Tableau20"` to `"Tableau10"`. Reason: Voyant
   does not ship a built-in palette named "Tableau20" at all -- it ships
   `Tableau10` natively (via d3-scale-chromatic); a genuine 20-colour
   Tableau20 rendering was only ever achieved on one specific local
   VoyantServer via a custom `StoredResource` (a server-specific ID, not
   a literal palette name).
   Given that, the earlier "real-Voyant-verified" claim above was most
   likely Voyant silently ignoring an unrecognized palette name and
   falling back to its own default colouring, not genuine Tableau20
   rendering -- consistent with this project's repeated pattern of silent,
   no-error failures (whiteList, CRLF stoplists, etc.), though this was
   not re-tested live to confirm that specific mechanism. This change has
   **not** been re-verified against live Voyant with the new value; treat
   `"Tableau10"` as the correct native palette name, not yet as a fresh
   confirmed fact the way the entries above were. Left
   deliberately unchanged: Step 2's hardcoded 20-colour hex list, the
   cluster-to-colour assignment (`% len(TABLEAU20)`), and the HTML legend
   -- `cats.addFeature()` still assigns each cluster its own explicit hex
   colour regardless of what `palette` is set to, so this is a change to
   the tools' own default/fallback colouring only, not to the actual
   per-category colours in tools using `categories: catsId`.

10. **`stopList` is tool-specific.** Only Summary and Cirrus use `excListFull`.
    All other tools omit `stopList` — passing it to Bubblelines, CollocatesGraph,
    Contexts, Phrases, or Documents corrupts output or has no effect.

11. **`whiteList` is no longer used by any tool (v2.21).** It was Cirrus-only,
    and removed from Cirrus too: Voyant's own Cirrus `whiteList` parameter only
    matches single-word terms, silently dropping every multi-word entry in
    `incList` (the confirmed Phase 1 phrases) with no error — confirmed by
    testing directly in live Voyant. Passing a
    filter parameter that silently fails for most of its intended content is
    worse than not passing it at all, so it was removed rather than kept as a
    partially-working filter.

12. **The @Category comment block is a reference, not a constraint.** It lists
    all available tokens so the user can modify the active `query` array without
    returning to the Phase 1 MD. The default query (first three clusters) is a
    starting point only.

13. **`bins` is corpus-size sensitive.** Default of 5 suits typical academic
    articles. Suggest 3 for short texts, 10 for long monographs.

14. **Always use `loadCorpus(myCorpus)`, never `loadCorpus(corpusId)`.** Every
    tool cell must begin with `loadCorpus(myCorpus).tool(...)`.

15. **The merged stopword list is corpus-specific.** The Phase 1 excList
    contains author names, citation artifacts, and encoding fragments specific
    to the processed text. The merged file must not be reused for a different
    corpus without review. The header comment documents this provenance.

16. **The merged stopword list uses a comment header.** Lines beginning with
    `#` are skipped by Voyant's stopword parser. The header documents the
    provenance (source counts, overlap, new terms) without affecting function.
    Verify by counting non-comment lines after write.

17. **Multi-document legibility is solved per-tool, not uniformly.** Trends
    and Bubblelines have a working built-in per-document drill-down inside
    the rendered Voyant iframe -- one iframe suffices. Cirrus, Contexts, and
    CorpusCollocates do not have a usable equivalent, so each is pre-split
    into three separate iframes (one per `docIndex`) instead. Do not assume
    every multi-document comparison tool needs the same treatment -- check
    whether the tool's own interactive drill-down actually works before
    deciding to pre-split it.

18. **`CollocatesGraph` cannot render a multi-document corpus; use
    `CorpusCollocates` instead for any comparison-corpus cell.** These are
    two different real Voyant tools, not a naming inconsistency -- Voyant
    documentation calls both "Collocates" in human-facing text, but the API
    tool name differs by corpus shape. Never "fix" this by forcing
    `CollocatesGraph` into a multi-document cell.

19. **Voyant's proximity operator (`"term1 term2"~N`) works correctly, but
    its distance semantics are not what a naive token-index-gap check would
    predict.** `~N` means N words *between* the two terms -- a token-index
    gap of N+1, not N -- and every qualifying token pair is its own result,
    not one result per occurrence of the first term. Verify against real
    Voyant output before concluding this operator is broken; a plausible-
    looking mismatch is more likely a counting-methodology error than a
    Voyant defect (confirmed twice, independently, against real data).

20. **Cell prose that describes a query, a term set, or a document count
    must be generated from the actual underlying value every time, never
    hand-written once and left to drift.** A real bug: description text
    named specific query terms that had already changed by the time the
    prose was checked, because the two were never kept in sync. Compose
    such prose as a derived output of the real config, not as independent,
    static content that happens to describe it.

21. **Do not solve a variable document/rate count with conditional prose
    branching ("the summary" / "both summaries" / "all summaries").** If a
    cell's actual structure (e.g. a fixed `docIndex` 0/1/2 range, or a fixed
    number of iframes) assumes a specific document count, that is a
    structural constant of the cell, not a phrasing problem -- solve it at
    that level if it ever needs to vary, and use count-agnostic language
    ("all documents in this comparison") for any prose that must remain
    correct regardless of count.

22. **A tool parameter observed not to work should be documented as an
    observed finding, not asserted as a permanent or categorical fact about
    the platform.** Cirrus's `categories: catsId` did not produce working
    category-based colouring in real testing (an earlier test corpus); documented as
    "did not render as expected," with `"none"` used instead -- not as an
    unqualified claim that the feature is broken, which would be an
    unverified overstatement about Voyant itself.

23. **Offline structural verification and live rendering are different
    evidentiary claims, and only one of them was ever actually asked
    for.** `verify_populated_notebook()` (Step 7.6) confirms tag balance,
    escaping, and placeholder absence; it cannot confirm the notebook
    renders correctly once actually opened in Voyant. That gap was
    disclosed honestly for several versions (the Disclosed Limitation
    note) without ever being converted into a real, repeatable ask —
    Cell 19's one real live-Voyant confirmation (v2.31) happened only
    incidentally, noticed during unrelated debugging,
    not because this skill requested it. Step 8.5 (v2.37) closes that
    gap directly, but deliberately does not make it unconditional: a
    researcher may reasonably review outputs directly rather than through
    an automated checkpoint, depending on the purpose of a given run. A
    disclosed limitation that is never acted on is not meaningfully
    different from an undisclosed one; the fix is a real, explicitly
    offered — but not compulsory — ask, not a stronger disclaimer.

24. **A persistent, unexplained error across multiple unrelated fixes is
    itself evidence — check for a shared cause before treating it as
    inherent to the platform.** Seven real, independently-verified
    content bugs were found and fixed in one project notebook, and the
    same Spyral parsing dialog appeared after every single one,
    unchanged. The instinct to conclude "this is just how Voyant
    behaves" was wrong — a real counter-example (a different, working
    notebook from the same pipeline, no such dialog) was sitting in
    evidence the whole
    time. The actual cause (v2.47: CRLF line endings, from a CRLF-native
    template file, surviving an undocumented write step with no
    `newline=''` guard) was found only by comparing the working and
    broken files directly at the structural and byte level, not by
    continuing to search for one more content bug inside the broken file
    alone. When a symptom outlives several genuinely different fixes,
    the fixes were probably all real — and probably all beside the
    point; the next move is a working reference to diff against, not
    another hypothesis about what else might be wrong internally.


---

## Version History (appendix)

This appendix is a condensed changelog of substantive changes across this file's version history, kept for provenance. **Current behavior is documented in the numbered steps above, not here** — if this appendix and the steps above ever appear to disagree, the steps above are authoritative; this appendix is a historical record only.

- **v2.0** — Switched to reading the Phase 1 JSON inter-phase contract (instead of Phase 1 Markdown); added `stop.en.smart.txt` as a required second input; added Step 7.5 (merged stopword list generation, Deliverable 4) and its delivery/checklist entries.
- **v2.1** — Split the single configuration cell into Cell 0 (stoplist ID placeholder, completed manually after Voyant upload) and Cell 1 (incList + clusterDefs + Spyral instantiation), since the stoplist ID is unknowable before upload.
- **v2.2** — Fixed a missing driver loop: `derive_token()` was defined but never called, so no cluster ever got a `token` key, despite later steps assuming one existed.
- **v2.3** — Fixed an undefined `corpus_name` (guaranteed `NameError`) by adding a confirmation step early in the run. Added session logging and an environment-precondition check. Added Deliverable 5 (`Phase3-results.md`) as a permanent, human-readable record of token derivation, colour assignment, cross-cluster stems, and stopword-list stats.
- **v2.4** — Fixed a second instance of the v2.2 bug class: the TABLEAU20 palette was defined but never assigned to any cluster, so `cluster['color']` was read everywhere but set nowhere. Also fixed a stale "four deliverables" reference left after Deliverable 5 was added.
- **v2.5** — Found by executing the file's own code end-to-end rather than re-reading it: a function was referenced before its defining code block, and the results Markdown was built and verified but never actually written to disk.
- **v2.6** — Voyant only assigns Spyral object IDs (e.g. the stoplist ID) at upload time; the previous design handed a placeholder to the researcher with nothing verifying it was ever filled in correctly. Fixed by splitting delivery into two rounds: Round 1 delivers the stopword list and pauses for the real Voyant-assigned ID; Round 2 (validated ID format) generates the remaining deliverables.
- **v2.7** — Found by checking document order against Step dependencies: Steps 4–6 (Deliverables 1–3) were positioned before Step 7's ID checkpoint they actually depend on. Added an explicit "Execution order" section stating generation order is not deliverable numbering.
- **v2.8** — Fixed the Phrases tool's `sort` parameter (`"length"` → `"rawFreq"`, ordering by occurrence count rather than phrase word-count).
- **v2.9** — Major fix: this skill previously produced only ingredient files for manual pasting into 13 cells, with nothing verifying correct placement. Added Deliverable 6: an actual populated-notebook generation and verification step, built from a full cell-by-cell mapping of the real template. **Known limitation:** verification can only check the authoritative raw source of each cell, not the decorative CodeMirror preview markup, which Spyral does not read anyway.
- **v2.10** — Ported back two fixes that had only ever existed as live workarounds in a prior session (a stopword-file comment-header filter, and correct JSON-based quoting of `incList` phrase entries), closing the standing gap where a live fix not ported back into this file recurs on the next run.
- **v2.11** — Corrected Deliverable 6 to handle multiple approved condensation rates: it previously assumed a single rate and would have silently dropped every rate but one. `populate_notebook()` now takes a list of per-rate condensation data, and verification confirms every approved rate's marker is present, not just that the cell was touched.
- **v2.12** — Root-caused a Voyant/Spyral upload parse error to unescaped `&` characters in text cells (e.g. from cluster names like "Virtue & Character"): this file had no HTML-escaping path for text-cell generation at all. Added a shared `esc()` helper used throughout, plus a permanent verification check that scans raw markup for unescaped entities.
- **v2.13** — Added a coloured, per-cluster stem table to Cell 7 (reproducing Phase 1's own cluster table), since the existing Cell 13 table was a different, lower-fidelity reconstruction that did not satisfy this need.
- **v2.14** — Added a mandatory `## Environment fallbacks used` section to `Phase3-results.md` so environment-precondition fallback decisions are durably recorded rather than only mentioned in chat.
- **v2.15** — Fixed a stopword-list bug: Step 7.1 independently re-read `stop.en.smart.txt` with its own comment-filtering logic that didn't actually filter, letting a garbage comment-header line leak into the merged stopword list. Fixed by having Step 7.1 reuse Step 0.1's already-filtered term set instead of re-reading the file.
- **v2.16** — Fixed `derive_token()`'s word-splitting regex to treat `/` as a delimiter; a cluster name containing a slash produced an invalid token.
- **v2.17** — Fixed the colour-legend HTML builder: it returned an unstyled, unwrapped fragment instead of the project's established styled-`<div>` convention.
- **v2.18** — Rewrote Cell 5's builder to match the real template cell structure (heading markup, AI-provenance flag, Title/Author block, per-paragraph inline styling), replacing a prior implementation that derived "plain text" by stripping tags from the annotated Phase 2 output — a contamination risk since fixed upstream by Phase 2 shipping a genuine plain-text deliverable.
- **v2.19** — Moved merged-stopword-list generation (Deliverable 4) earlier in execution order, since none of its inputs depend on later steps. Added Deliverable 7: a comparison-corpus ZIP (source text + all approved summaries) for the source-vs-summary comparison tools, consuming Phase 2's plain-text summary output. Bundled the stoplist-ID and comparison-corpus-ID confirmations into a single round-trip instead of two separate pauses.
- **v2.29** — Added Deliverable 8 (Cells 14–20, the "Source vs Summary" comparison block): a fixed intro, Documents/Summary cells rewired to the comparison corpus, and a five-tool comparison pattern (Trends, Bubblelines, Cirrus, Contexts, CorpusCollocates). Documented a two-input elicitation for the CONTEXTS companion term. Corrected an unverified claim that Voyant's `palette` parameter rejects `"Tableau20"` — confirmed working in practice at the time (see v2.57 for a later correction).
- **v2.30** — Refined the CONTEXTS elicitation from a two-term to a three-term disjunction (one companion term per lexical shape: stem, word, N-gram). Added the first real implementation of the Deliverable 8 builder script, closing three bugs found only by running it (missing `@` prefix on category tokens, un-encoded commas, malformed quoting in generated prose).
- **v2.31** — Fixed a fourth bug in the same builder: unescaped `&` in interpolated category names and description text.
- **v2.32** — Closed the gap where Deliverable 8 was fully specified and had a tested generator, but `populate_notebook()` was never wired up to call it — cells 14–20 would have shipped blank. Wired in all seven cells, corrected the tool-cell count from "10" to "8" throughout (Summary/Documents were relocated, not duplicated), and fixed several bugs surfaced only by running the corrected pipeline end-to-end (wrong dict-key names, a stale tool-cell rename, an overly strict entity allow-list, a shared verification marker that could never match one of two differently-structured cells).
- **v2.33** — Documented the gap between Phase 1's narrow `excList` (deliberately limited in scope) and the more comprehensive exclusion set (numerals, citation artifacts, confirmed author names, a domain-specific supplement) a usable stopword list may need. **Known limitation:** author-name confirmation requires human judgment and is deliberately not automated. Added an optional comprehensive-excList input; if absent, the narrow list is used with an explicit warning, recorded in `Phase3-results.md` either way.
- **v2.34** — Fixed a stale docstring claim that no structured title/author input existed; Phase 2's plain-text summary format had already made this available, so the colour-legend and Cell 13 builders were updated to use the real values instead of a placeholder.
- **v2.35** — Fixed a first-run-only gap: Cell 19's comparison-corpus iframes need a real, already-assigned `catsId` baked in at generation time, which does not exist yet on a brand-new corpus's first run (only on a regeneration of an already-live notebook). Added a standalone category-creation snippet the researcher runs once in Voyant to obtain a real, permanent ID before Cell 1/Deliverable 1 can be generated, and changed Cell 1's own template to reference the confirmed ID directly rather than creating the category object a second time.
- **v2.36** — Wrote the actual builder for Cell 8 (quick-jump index + one scrollable box for Phase 1/2/3 results), replacing a call to a function that was documented but never part of this project's packaged materials, and correcting the file's own record of Cell 8's structure to match the real template.
- **v2.37** — Fixed a heading line-height regression in `md_to_html()`'s HTML output (an upstream fix had never been ported into this file's own Markdown-to-HTML converter) and applied the same correction to the colour-legend heading. Also introduced the post-delivery live-Voyant checkpoint (Step 8.5): an optional, explicitly offered check of how a delivered notebook actually renders once opened in Voyant, since structural verification alone cannot see that.
- **v2.38** — Root-caused a Spyral import warning ("error occurred while parsing the input") to missing `<tbody>` tags in generated tables — valid by a browser's implied-tbody rule but not tolerated cleanly by Spyral's stricter import parser. Fixed by always emitting explicit `<tbody>` tags.
- **v2.39** — Found that the v2.38 fix alone did not resolve the import warning: two more generation gaps existed with no real code path at all (prose-only templates for Cell 1 and the tool-cell category comment block), and content had been improvised live with the wrong escaping convention (HTML-escaping used inside literal JS/code cells, where it corrupts the source). Added real generator functions for both. **Known limitation:** whether this fully closed the original import-warning trigger was not established with certainty at the time (later closed by v2.47's CRLF fix).
- **v2.40** — Reversed a v2.36 misunderstanding: Cell 9 should carry a fixed, corpus-independent divider (matching Cells 7 and 14), not a duplicate of Cell 8's content. Also fixed a latent bug where a function's parameter name didn't match what its own body referenced.
- **v2.41** — Fixed a malformed-query bug in the CONTEXTS proximity-operator builder: it unconditionally added quotes around a term that could already be a pre-quoted N-gram, producing doubled quotes and an invalid query.
- **v2.42** — Fixed a content-placement bug: a disjunction-shape disclosure note was hardcoded at the top of Cell 19 rather than generated next to the CONTEXTS block it describes. The underlying function was also changed to report a missing lexical shape rather than raising an exception, so a corpus missing one shape degrades gracefully with disclosure instead of failing outright.
- **v2.43** — Closed a previously-flagged risk: a run without a comprehensive excList showed prominent numerals in a word-cloud tool, exactly the failure mode v2.33 had warned about. Built and applied a comprehensive excList for that run following the established rule-based schema.
- **v2.44** — Closed the follow-on from v2.43: after the merged stopword list changed, its Voyant-assigned ID becomes stale and must be re-confirmed everywhere it's referenced (Cell 0's declaration, its preview copy, and every `stopList` parameter across the affected tool cells) — not just in one place.
- **v2.45** — Fixed a content gap in the base notebook template itself (a section-divider cell was missing an explanatory paragraph present in a known-good reference notebook) — a fix that had been made in a separate, unversioned copy of the template but never propagated into this project's own packaged template file.
- **v2.46** — Merged two redundant tables in Cell 13 (a plain cluster/stem table and a separate colour-legend table covering the same clusters) into one combined table with swatch, token/name, and full stem list.
- **v2.47** — Root-caused the recurring Spyral import-parsing warning, after several unrelated content fixes failed to resolve it: the delivered notebook was 100% CRLF line endings, while a known-working reference notebook was 100% bare LF. Windows' default text-mode file writing silently converts line endings unless `newline=''` is passed. Fixed by normalizing line endings on template ingest and adding an explicit, previously-undocumented write step using `newline=''`, plus a post-write verification. **Known limitation / standing risk:** this exact bug (silent CRLF corruption from an unguarded `open()` call) recurred twice more later in this file's history (v2.48, v2.56) — any new file-write code path should default to using `newline=''` with a raw-byte post-write check, not a content-only comparison.
- **v2.48** — Fixed the same quoting bug class as v2.41, found in a different tool cell (Contexts' default query slot): an N-gram embedded unquoted inside an already-double-quoted JS string. Added a helper that picks the correct outer-quote delimiter automatically. Also caught and fixed a near-miss where a patch script reintroduced the v2.47 CRLF bug.
- **v2.49** — Replaced the CONTEXTS companion-term mechanism with an empirically-grounded one: instead of deterministically deriving a companion cluster and picking terms by array position (which had no guarantee the resulting term pairs ever actually co-occur in the source), the generator now scans the source text for real cross-cluster collocations, ranks them by hit count, and flags candidates confounded by a disproportionately frequent term.
- **v2.50** — Wired the researcher-facing elicitation (Step 1.4) to actually drive the v2.49 mechanism: it now loads the source text, runs the collocation scan, and presents ranked, flagged candidates for the researcher to choose from, instead of asking for a single blind term pick.
- **v2.51** — Fixed a usability gap in the same elicitation: a candidate pair actually worth selecting ranked outside the default top-10 table. Added an explicit "ask to see more" affordance so a researcher isn't limited to the default cutoff.
- **v2.52** — Fixed a hardcoded Voyant host: Deliverable 8's tool iframes assumed a fixed production server URL, which fails outright against any other Voyant instance (e.g. a local server) with a "corpus does not exist" error that is accurate but misleading about the real cause. Added an explicit, required `voyant_host` parameter with no silent default.
- **v2.53** — Documented a known third-party limitation: Voyant's Phrases tool (JS9) can crash with a Java heap `OutOfMemoryError` on some documents, traced to a Trombone (Voyant's backend) recursion bug with no effective length cap, independent of JVM heap size, cache state, or the cell's own `query`/`stopList` parameters. **Known limitation:** this is not fixable from the Spyral cell or server settings; the template now ships with the `query` line commented out by default, with an inline warning that this does not guarantee the crash won't occur.
- **v2.54** — Reworded two checkpoints (Step 1.3's closure condition and Step 8.5's live-Voyant check) to ground their requirements in factual necessity rather than language that reads as testing the researcher's attentiveness or diligence.
- **v2.55** — Three fixes from a cross-phase retrospective: (1) added a mandatory, unconditional automatic numeral-exclusion scan (Step 7.0c) to the merged stopword list, since numeral exclusion needs no human judgment and the prior optional comprehensive-excList mechanism could silently skip it; (2) broadened the search scope for the blank notebook template in local/filesystem environments, since it commonly lives one directory above the track folder, not only inside it; (3) added working-directory confirmation and logging at Step 0, after a case where different phases of the same run logged to different locations undetected.
- **v2.56** — Fixed the same CRLF line-ending defect as v2.47, recurring at a different, previously-unguarded write site (the merged stopword list, Step 7.2): every term carried an invisible trailing `\r`, which does not match Voyant's tokenized text, so the uploaded stoplist silently filtered nothing. Added `newline=''` to that write and, defensively, to the results-Markdown write, plus a raw-byte post-write check (a content-only or `.strip()`-based comparison cannot detect this class of defect, since stripping removes the `\r` along with everything else). Also added a defensive check to the comparison-corpus ZIP step for the same defect arriving from an upstream Phase 2 file.
- **v2.57** — Changed every tool cell's `palette` value from `"Tableau20"` to `"Tableau10"`. Voyant does not ship a built-in palette literally named "Tableau20" — only `"Tableau10"` natively; a genuine 20-colour rendering had only ever been achieved via a one-off, server-specific custom resource, not the literal palette name. The earlier "verified working" claims for `"Tableau20"` were most likely Voyant silently falling back to its default colouring rather than genuinely applying 20 colours. **Scope:** only the `palette` parameter changed; the hardcoded 20-colour hex list and per-cluster colour assignment used by the HTML legend and `categories`-driven tools are unaffected, since those assign colours explicitly rather than through this parameter.
