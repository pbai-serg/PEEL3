---
name: peel3-phase1
version: 1.31
description: >
  Given a TXT corpus file, a Voyant-produced Terms TSV, and a Voyant-produced
  Phrases TSV, generates valuable elements for an AI-assisted distant reading
  of the text, which constitutes a single-file corpus: (1) a list of
  non-significant terms; and (2) a categorized list of the most significant
  lexical stems and multi-word phrases of the corpus. This skill is activated
  by an instruction like: "Run Phase 1", "Run", "Go", or similar triggering
  imperatives. The output is defined at each stage defined below.

  This file forks from peel2-phase1-v2.13.md — the last PEEL 2 version — as
  the start of the PEEL 3 file series. All v2.0 through v2.13 changelog
  entries below describe the inherited PEEL 2 history and are kept verbatim
  for provenance; PEEL 3's own changes start at v1.0 immediately below this
  paragraph and continue at the end of this changelog, after v2.13.

  Full version history (all prior version changes, kept verbatim for
  provenance): see "Version History (appendix)" at the
  end of this file.
---

# new-peel-phase1 — Term Selection, Stemming, and Semantic Categorization

## Contents

*(Added 2026-07-28. A plain index, not hyperlinks — this file's rendering
environment isn't guaranteed to support markdown anchors, so section
titles are listed as they appear, to be located by text search.)*

- Step 0 [Session-Log Protocol] — session logging setup
- Step 0.9 — Environment precondition check
- 0. [Phase 1 Step 0] Corpus Cleanliness Inspection
  - 0.1 Structural artifact scan · 0.1b Front matter/publisher metadata ·
    0.1c Footnote/endnote content · 0.1d Figures and tables ·
    0.2 Broken-hyphenation · 0.3 Faulty-juxtaposition · 0.4 Typographic/encoding noise ·
    0.4b General spelling/typo detection ·
    0.5 Report and confirm · 0.6 Draft exclusion harvesting
- 0.7 Inputs
- 1. Read and Verify (1.1 Terms TSV · 1.2 Phrases TSV)
- **1c.** Term Selection Method (automated only — see v1.28 changelog)
- **1b.** N-gram Extraction and Boundary-Trimming
- 2. Detect Corpus Language and ask user for Base Parameters
- 3. Select Most Semantically Significant Terms
  (3.1 Filter · 3.2 Coverage-N · 3.2b POS/Example filter · 3.3 Zipf elbow ·
  3.3b Multi-tool corroboration · 3.4 Verify)
- Term selection provenance (mandatory, every run)
- 3.4b WordNet precondition check
- 3.4c Disambiguation bypass via confirmed context
- 3.5 WordNet Sense Disambiguation
- 4. Compress to Wildcard Stems (4.1 Group by stem · 4.2 Verify coverage · 4.3 Sort)
- 5. Semantic Categorization (5.1 Assign clusters · 5.1b Grounding tally ·
  5.2 Reporting format · 5.3 Escalation rule · 5.4 Await confirmation ·
  5.5 Generate HTML snippet)
- 6. Serialize to JSON (6.1 Contract fields · 6.2 Write and verify ·
  6.2v Report verification · 6.3 Report and present)
- Editing the JSON before Phase 2
- Version History (appendix) — full versioned changelog, moved out of the
  frontmatter 2026-07-28; see `status/skills-usability-review.md`

---

## Step 0 [Session-Log Protocol] — Start the session log (mandatory, before any other step)

Before doing anything else — before reading inputs, before greeting the
user — start the session log:

**Before running `session_log.py init` (added v1.30 — closes a real,
confirmed gap: an earlier PEEL3 cycle's Phase 1 session ran with a
different working directory than that same cycle's Phase 2/3 sessions,
so `session_log.py`'s own `peel-logs/` output — written relative to
whatever directory happens to be current — silently scattered one
cycle's logs across two locations, discovered only by manually
searching the disk afterward, not by anything this skill did at the
time).** Resolve and state the absolute working directory first:

```bash
pwd
```

State the resolved path to the researcher in the same message that
reports the log was initialized — e.g. "Working directory:
`/path/to/TrackFolder`, session log at `peel-logs/[session]/log.md`
under it" — never silently. Since Phase 1 is normally the *first*
phase run for a new track, there is usually no prior session to match
against — but if the track name was already mentioned or a folder for
it already exists, check there first rather than creating a second,
inconsistent location. `session_log.py` itself now also prints the
absolute resolved path on every `init`/`append` call (its own
2026-08-06 fix) — read that output, don't just trust the call
succeeded.

**Duplicate-copy warning (found during the same 2026-08-06 pass):**
this file's own path below (`peel-protocol/scripts/session_log.py`) is
stale relative to how this project's own sessions have actually run —
every real session this project has logged used `PEEL3-Scripts/
session_log.py` instead (the location `README.txt` documents as
canonical), leaving a second, easy-to-miss copy at `peel-protocol/
scripts/` that silently drifts out of sync unless remembered by hand
(confirmed: it *had* drifted, missing this same day's absolute-path
fix, until resynced as part of this pass). Prefer `PEEL3-Scripts/
session_log.py` if both exist in the current checkout.

```bash
python3 PEEL3-Scripts/session_log.py init "[corpus-or-topic]-phase1-[YYYY-MM-DD]"
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

(Note, updated 2026-07-28: this is "Step 0" of the session-logging
protocol, distinct from the corpus-cleanliness "0." numbering
immediately below, which is Phase 1's own first content step. The two
share the bare numeral by coincidence of separate authorship, not by
design. Rather than renumber either one — which would break the many
existing cross-references to sub-steps like 0.1, 0.1b, and 0.7
throughout this file — each heading now carries its own bracketed tag,
**[Session-Log Protocol]** here and **[Phase 1 Step 0]** immediately
below, so neither is ever referred to as bare "Step 0" in a way that
could mean either one.)

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
permanent human-readable report for this run, under a heading naming
the gap explicitly — not folded into or blended with the existing
`## Environment fallbacks used` section, since that section already
carries a specific, established meaning (a tested, pre-approved
degraded mode) that this situation does not qualify for.

---

## 0. [Phase 1 Step 0] Corpus Cleanliness Inspection

**Runs on the TXT file alone. Do not request the Terms or Phrases TSVs yet —
those depend on Voyant tokenization, and the point of this step is to catch
defects before that tokenization happens.**

**CODE-VERIFIED, MERGED (v1.13).** Was PROSE-ONLY through v1.12 — no
executable code existed for any of 0.1 through 0.4's detection logic (see
`PEEL3-phase1-execution-status.md`). Implemented and verified against a real
raw PDF extraction (Delacroix, 2026, no manual cleanup — genuine running
headers/footers, footnote-call digits, broken hyphenation, and a front-matter
block injected mid-sentence after the Introduction heading), not a synthetic
test case. See the v1.13 changelog entry above for the three real bugs this
verification pass found and fixed in the first draft, and the two disclosed
limitations left open. Full script and corpus: `DelacroixTest/step0_detectors.py`,
`DelacroixTest/mycorpus-RAW.txt`.

```python
import re
from collections import Counter
import nltk
from nltk.corpus import wordnet as wn

WORDNET_VOCAB = set(w.lower() for w in wn.all_lemma_names())

# Added v1.20, for 0.3 and 0.4b: WordNet's lemma list is a content-word
# dictionary and does not cover closed-class function words (the, this,
# and, should, ...). Without this, both the faulty-juxtaposition check
# and the new spelling/typo check misclassify ordinary function words as
# unrecognized. `stop.en.smart.txt` (571 words) already ships alongside
# this skill for exactly this purpose.
with open('stop.en.smart.txt', encoding='utf-8') as _f:
    STOPWORD_VOCAB = {_line.strip().lower() for _line in _f
                       if _line.strip() and not _line.startswith('#')}

# Added v1.22, for 0.4b (defined here, alongside STOPWORD_VOCAB, so it
# exists before any Step 0 sub-step that might call `_is_known_word()`
# runs, not only after 0.4b's own block). Small, hand-curated allowlist
# of Latin/foreign-phrase words common in untranslated English scholarly
# prose -- not exhaustive. Seeded from real-corpus testing
# (the test corpus), which confirmed "sui," "generis," "modus," "ponens,"
# "absurdum," "simpliciter," and "quo" as real false positives, plus a
# small set of other well-known scholarly Latin tags not seen in that
# particular corpus but common in academic English generally. Residual
# risk, disclosed rather than ignored: a genuine typo that happens to
# collide with one of these short forms would be silently suppressed.
LATIN_SCHOLARLY_TERMS = {
    'sui', 'generis', 'modus', 'ponens', 'tollens', 'simpliciter',
    'absurdum', 'reductio', 'prima', 'facie', 'priori', 'posteriori',
    'facto', 'jure', 'ergo', 'ipso', 'ceteris', 'paribus', 'mutatis',
    'mutandis', 'inter', 'alia', 'versa', 'quo', 'passim', 'sic',
    'per', 'se', 'vis',
    # Added v1.26: 'hoc' ('ad hoc', 'post hoc') was confirmed missing by
    # the second real-corpus test (2026-07-29) -- a genuine completeness
    # gap in this non-exhaustive list, not a design flaw. Audited every
    # other phrase already represented here (each multi-word phrase's
    # words checked in full: 'sui generis', 'modus ponens'/'tollens',
    # 'reductio ad absurdum', 'prima facie', 'a priori'/'posteriori', 'de
    # facto'/'jure', 'ipso facto', 'ceteris paribus', 'mutatis mutandis',
    # 'inter alia', 'vice versa', 'status quo', 'per se', 'vis-a-vis') and
    # found no other gap of the same kind: the other short Latin function
    # words these phrases need ('a', 'de', 'ad', 'in') are 1-2 characters
    # and never reach this check at all, since `scan_spelling_typos`'s
    # `word_pat` only tokenizes runs of 3+ characters. 'vice' (in 'vice
    # versa') is a genuine gap in coverage terms but not in outcome: it is
    # already an ordinary WordNet lemma (English "vice," a moral fault),
    # so it already resolves via `WORDNET_VOCAB` without needing to be
    # listed here. 'hoc' was the only 3+-character word both missing from
    # this list and not independently resolvable some other way.
    'hoc',
}
```

### 0.1 Structural artifact scan

Scan for:
- Isolated numeral lines sitting alone between paragraphs (page numbers)
- Short lines recurring at regular intervals across the document (running
  headers/footers, repeated chapter titles)
- Digits fused directly onto a word or onto trailing punctuation with no
  space (`knowledge1 is`, `topic.1`, `transmission?2`) — footnote-call
  artifacts, distinguishable from genuine numerals by their mid-word or
  clause-final position

```python
def scan_isolated_numerals(lines):
    hits = []
    for i, line in enumerate(lines):
        stripped = line.strip()
        if stripped and re.fullmatch(r'\d{1,4}', stripped):
            hits.append((i + 1, stripped))
    return hits


def scan_recurring_short_lines(lines, min_repeats=3, max_len=80):
    """Normalizes embedded page numbers ('Page 2 of 32' -> 'Page N of N')
    so templated headers/footers with a changing page number are still
    recognized as the same recurring line. Verified against real data,
    Delacroix (2026): correctly found the journal's repeating masthead line
    and page-footer glyph across all 32 pages."""
    def normalize(s):
        return re.sub(r'\d+', 'N', s.strip())

    normalized = [normalize(l) for l in lines]
    counts = Counter(n for n in normalized if n and len(n) <= max_len)
    recurring = {n for n, c in counts.items() if c >= min_repeats}

    hits = [(i + 1, line.strip()) for i, (line, norm) in
            enumerate(zip(lines, normalized)) if norm in recurring and line.strip()]
    return hits, recurring


def scan_footnote_call_artifacts(lines):
    """Word-char, closing-punct, or sentence-punct immediately followed by
    a 1-2 digit run not itself preceded/followed by another digit --
    excludes genuine multi-digit numbers/years. Verified against real
    data: 31 genuine hits (e.g. 'Delacroix1', 'networks10'), zero false
    positives on the many 4-digit years already present in the running
    text.

    NOTE (fixed, live evidence, the test book chapter verification,
    2026-08-06): the prefix character class only ever covered
    [a-zA-Z)'’] -- a letter, closing paren, or apostrophe immediately
    before the digit. Real academic footnote calls routinely land after
    other punctuation instead: a period ('time.2'), comma (',19'),
    semicolon (';25'), question mark ('?18'), or closing curly double
    quote ('."35'). On this real corpus, the original class caught only
    18 of 54 distinct (line, matched-text) footnote-call/notation sites
    -- 36 genuine calls (footnotes 2 through 37, in sequence) were
    silently missed, discovered only because Step 0.6's draft-exclusion
    carry-forward required an exact line-by-line footnote inventory and
    the gap surfaced there. Fixed by widening the prefix class to
    `.,;:?"'` in addition to the original set. Re-run against the same
    corpus after the fix: 62 raw hits (some formal-notation tokens like
    `VA4`/`E1`/`t1` occur more than once on the same line, so the raw
    count exceeds the 54 distinct sites), zero new false positives --
    every one of the 36 newly-caught sites is a real footnote number in
    sequence, hand-verified against the source text. Confirmed by
    executing the actual function against the corpus and inspecting its
    real return value, not by re-deriving the count from a separately
    written comparison script -- an earlier verification pass here used
    exactly that shortcut and it silently collapsed six genuine
    same-line duplicate occurrences into one, undercounting the true
    result until the function itself was actually run."""
    pattern = re.compile(r'(?<![\d])([a-zA-Z)\'’.,;:?”])(\d{1,2})(?![\d])')
    hits = []
    for i, line in enumerate(lines):
        for m in pattern.finditer(line):
            ctx = line[max(0, m.start() - 15):min(len(line), m.end() + 15)]
            hits.append((i + 1, ctx.strip(), m.group(0)))
    return hits
```

### 0.1b Front matter and publisher metadata

**Always kept: the title and the author names.** Everything else in the
front-matter span — from the start of the file up to the first body
heading (typically `Introduction`) — is a redaction candidate:

- Author affiliation, institutional address, and email — one repeating
  block per author (name / institution line(s) / city, country / email),
  not necessarily a single shared line
- The abstract (heading and body)
- `ARTICLE HISTORY` (received/accepted dates)
- `KEYWORDS` (see the researcher-keyword step below — this heading's
  content is redacted, not carried through as-is)
- `CCS Concepts`
- `ACM Reference Format` (a self-citation block repeating the title,
  author list, venue, and DOI)
- The journal masthead (journal name, volume/issue, page range, DOI),
  typically at the very top of the file
- Any copyright/license/venue/ISBN/DOI notice

**These blocks are not reliably positioned — locate by content pattern,
not by position.** A copyright/contact/venue block can appear once near
the top, or it can be injected mid-sentence, anywhere in the document
(confirmed live, twice now on two different sources: the original
GarciaOkonkwo2025 extraction placed this block mid-sentence in the
body and mid-abstract on a rougher second extraction; the Delacroix 2026
verification pass below independently reconfirmed it on unrelated real
data). When a redacted block interrupts a sentence, rejoin the sentence
across the excision — do not leave a dangling half-sentence on either side.

**Researcher-supplied keywords, optional.** Since author-supplied
keywords can be misleading when read out of context, ask the researcher
whether she wants to supply her own instead of (not in addition to) the
redacted `KEYWORDS` content. If she does, record them as
`researcher_keywords`, tagged `researcher-keyword` — kept
provenance-distinct from any (redacted) author keywords; see the "Term
selection provenance" section and Step 3.2's `top_n_terms` assembly, both
of which union this list in.

```python
FRONT_MATTER_PATTERNS = [
    ('journal_masthead', re.compile(r'^(ORIGINAL RESEARCH|[A-Z][a-z]+\s+\(\d{4}\)|https://doi\.org/)', re.I)),
    ('article_history', re.compile(r'^Received:.*Accepted:', re.I)),
    ('copyright_notice', re.compile(r'^©|under exclusive licence|Springer Nature', re.I)),
    ('acm_reference_format', re.compile(r'^ACM Reference Format', re.I)),
    ('ccs_concepts', re.compile(r'^CCS Concepts', re.I)),
    ('keywords_heading', re.compile(r'^Keywords\b', re.I)),
    ('abstract_heading', re.compile(r'^Abstract\b', re.I)),
    ('email', re.compile(r'[\w.+-]+@[\w-]+\.[\w.-]+')),
    ('affiliation', re.compile(r'Universit|CNRS|Department of', re.I)),
]


def scan_front_matter(lines, body_heading_pattern=r'^\d+\s+Introduction\b'):
    """NOTE (fixed, live evidence, Delacroix 2026 verification, 2026-07-15):
    the first draft of this scanner searched only the span before the
    first body heading, on the assumption front matter is confined there.
    Run for real, this corpus's own extraction injected its ARTICLE
    HISTORY/copyright/author block *after* the Introduction heading and
    mid-sentence -- confirming, on live data this file had not previously
    tested against, the "not reliably positioned" warning above. Scans the
    whole document by content match now, not a bounded span."""
    body_start = None
    for i, line in enumerate(lines):
        if re.match(body_heading_pattern, line.strip()):
            body_start = i
            break

    hits = []
    for i, line in enumerate(lines):
        for tag, pat in FRONT_MATTER_PATTERNS:
            if pat.search(line):
                hits.append((i + 1, tag, line.strip()))
    return hits, body_start
```

### 0.1c Footnote/endnote content

**DISCLOSED LIMITATION (v1.29) — this file does not detect a
References/Bibliography section at all.** The line below has always
assumed one is already gone by the time this step runs; nothing in Step
0 checks that assumption or acts on it if it's false. If a researcher
submits a text with its bibliography intact — and a substantial one can
easily contribute hundreds of extra tokens (author names, journal and
book titles, one per entry) — those tokens flow straight into the
Voyant Terms/Phrases exports and distort every one of Step 3's
statistical decisions (coverage-N, the Zipf elbow, WordNet grounding),
not merely add a few excludable citation markers. Step 3.1 Rule C
excludes scattered in-text citation markers ("et al", "ibid") as
individual terms, but only after Voyant has already computed frequencies
over the contaminated whole — it cannot undo the effect hundreds of
extra tokens have on the coverage-N/Zipf-elbow math itself. See the
v1.29 changelog entry for the full scenario (a researcher's own
question, not a live execution) and why Phase 2's own bibliography
pre-flight check (its Step 0.1) cannot retroactively fix this. Not
designed or implemented here — left as an open item.

Detect a `Notes` / `Endnotes` / `Footnotes` heading, using the same
heading-recognition approach as `ABSTRACT`/`KEYWORDS` above — it
typically appears after the last body heading (e.g. `Conclusion`), in
the position a References/Bibliography section would occupy if the
researcher had not already removed it before sending the text. Match
each numbered entry under that heading to its corresponding in-text call
(by number — a call marked `.1` matches entry `1.`, etc.), then remove
both the entire section and the in-text call markers (per 0.1's
footnote-call pattern). Do not assume every document has this section:
most test cases so far have had bare calls with no matching content
block at all — treat that as the normal case, not a failure to find one.

**HONESTY NOTE (added, Delacroix 2026 verification, 2026-07-15; CLOSED,
the test book chapter live verification, 2026-08-06 — see below).** This
rule covers one specific structural pattern — a single `Notes`/`Endnotes`
heading late in the document. It does not cover a different pattern:
per-page academic footnotes, which a page-by-page PDF extraction
interleaves throughout the body text rather than collecting under one
heading. This was previously a disclosed, left-for-a-future-pass gap,
because handling it well is a genuinely different problem (matching
inline footnote text to its call *and* removing it from the middle of
running body text without breaking sentence flow) than `scan_endnote_section`'s
scope. That future pass is below.

```python
def scan_endnote_section(lines):
    heading_pat = re.compile(r'^(Notes|Endnotes|Footnotes)\s*$', re.I)
    for i, line in enumerate(lines):
        if heading_pat.match(line.strip()):
            return {'found': True, 'line': i + 1, 'heading': line.strip()}
    return {'found': False}
```

#### 0.1c-ii — Per-page interleaved footnotes (closes the gap above)

**Detection.** A per-page footnote block, unlike a References section,
has no heading to anchor on — the only reliable signal is that each
entry starts its own line with a number, and across the whole document
those numbers run sequentially from 1. A single numbered line
in isolation could be a numbered list item; a long run of them,
strictly increasing by 1 each time, is not.

```python
def scan_interleaved_footnotes(lines):
    """Detects per-page footnote entries by the only structural signal
    they reliably have: each starts its own line with a number, and the
    numbers run sequentially across the whole document starting at 1.
    Verified against real data (the test book chapter, 2026-08-06): found
    all 37 real footnote entries, confirmed genuine (not a numbered
    list or enumerated argument) by checking the sequence is exactly
    1..37 with no gaps -- a coincidental one-off numbered line would not
    extend an existing run, and a numbered list restarting at 1 elsewhere
    in the document would not chain onto this run either, since the
    check requires strict n, n+1, n+2... continuation."""
    entry_pat = re.compile(r'^\s{0,3}(\d{1,2})\s+[A-Z]')
    candidates = []
    for i, line in enumerate(lines):
        m = entry_pat.match(line)
        if m:
            candidates.append((i + 1, int(m.group(1))))
    if not candidates:
        return {'found': False, 'entries': []}
    nums = [n for _, n in candidates]
    is_sequential = nums == list(range(1, len(nums) + 1))
    return {
        'found': is_sequential,
        'entries': candidates if is_sequential else [],
        'note': ('sequential 1..%d, high-confidence footnote run' % len(nums)
                  if is_sequential else
                  'numbered lines found but not a clean 1..N sequence -- '
                  'likely a numbered list or argument enumeration, not '
                  'footnotes; do not remove without checking by hand'),
    }
```

**Removal and rejoin.** Deleting each footnote entry's line (plus any
isolated structural-numeral lines from 0.1's own scan) routinely leaves
the surrounding body text split mid-sentence, since the debris often
sits at a PDF page boundary the extraction fell across mid-paragraph.
Nothing upstream of this point checks for that. Determine, per
contiguous run of lines being deleted, whether the text immediately
before it ends mid-sentence:

```python
def detect_debris_removal_rejoins(lines, delete_line_numbers):
    """For each contiguous run of lines slated for deletion (footnote
    entries, isolated structural numerals, front-matter block -- any
    0.1/0.1b/0.1c-ii finding the researcher confirms removing), finds the
    nearest non-blank kept line before and after the run and classifies
    whether removing the run would split a sentence:
      NATURAL -- the line before ends in . ! ? (or the run is at the very
                 start/end of the file) -- safe to just delete, no rejoin
      REJOIN  -- the line before ends mid-word/mid-clause -- the kept
                 lines before and after must be concatenated with a
                 single space once the run is removed, or a sentence
                 breaks in two
      UNCLEAR -- the line before ends in a colon, which often introduces
                 a following definition/quote block (in which case NATURAL
                 is correct) but is not itself proof of that -- always
                 surfaced for the researcher, never silently resolved
                 either way
    Verified against real data (the test book chapter, 2026-08-06): 25 runs
    found across the confirmed footnote/structural-numeral/front-matter
    deletions, classified 3 NATURAL, 1 UNCLEAR, 21 REJOIN -- every one of
    the 21 REJOIN verdicts checked by hand against the actual source
    sentence and confirmed to read correctly once concatenated (e.g.
    "...it is interesting" + "that many pieces of evidence..." ->
    "...it is interesting that many pieces of evidence..."); the single
    UNCLEAR case was a colon introducing a formal definition block, where
    NATURAL was in fact correct -- confirming the UNCLEAR category is
    doing real work, not just padding out the other two with a hedge."""
    n = len(lines)
    sorted_del = sorted(delete_line_numbers)
    if not sorted_del:
        return []
    runs = []
    start = prev = sorted_del[0]
    for x in sorted_del[1:]:
        if x == prev + 1:
            prev = x
        else:
            runs.append((start, prev))
            start = prev = x
    runs.append((start, prev))

    results = []
    for (s, e) in runs:
        b = s - 1
        while b >= 1 and lines[b - 1].strip() == '':
            b -= 1
        a = e + 1
        while a <= n and lines[a - 1].strip() == '':
            a += 1
        before_text = lines[b - 1].rstrip() if b >= 1 else ''
        after_text = lines[a - 1].strip() if a <= n else ''
        last_char = before_text.rstrip()[-1] if before_text.strip() else ''
        if last_char in '.!?' or last_char == '':
            verdict = 'NATURAL'
        elif last_char == ':':
            verdict = 'UNCLEAR -- colon may introduce a following block; confirm'
        else:
            verdict = 'REJOIN'
        results.append({
            'run': (s, e), 'before_line': b, 'after_line': a,
            'before_tail': before_text[-40:], 'after_head': after_text[:40],
            'verdict': verdict,
        })
    return results
```

**Integration with Step 0.5.** Present `scan_interleaved_footnotes`'s
result alongside 0.1's other findings at the same confirm-before-correct
checkpoint — do not remove anything on this step's say-so alone. Once
the researcher confirms which lines to delete (footnotes, structural
numerals, front matter), run `detect_debris_removal_rejoins` against
that confirmed deletion set and show its verdicts in the same table:
REJOIN and UNCLEAR rows both need the researcher's eyes before the
cleaned TXT is written, exactly as any other 0.5 finding does. Only
after that confirmation does Claude write the cleaned TXT, performing
the deletions and, for every REJOIN (and researcher-confirmed UNCLEAR)
run, concatenating the kept before/after lines with a single space.

### 0.1d Figures and tables

**Figure captions and in-text figure calls are always kept**, wherever
they land in the extraction — floating figure placement does not respect
logical reading order (a caption can appear before the abstract).

**Table captions and in-text table calls are always kept, regardless of
content.** Table *content* is kept only when the table is structured or
non-numeric (categorical descriptions, participant/demographic rosters,
classification schemes) and dropped when the table is a numeric data or
statistics table (means, standard deviations, p-values, effect sizes,
raw measurements). A table with numeric-looking but categorical entries
(e.g. binned age ranges, years-of-experience brackets in a demographics
table) counts as structured, not numeric — the test is whether the table
reports measurements, not whether its cells contain digits.

**HONESTY NOTE.** Implemented per the spec above but never exercised
against real data — the Delacroix 2026 verification corpus contains no
figures or tables. `scan_figures_tables` below correctly returns empty on
that corpus (an honest negative, not a false claim of validation), but the
numeric-vs-structured table judgment itself remains CODE-UNVERIFIED until
tested on a corpus that actually contains a table.

```python
def scan_figures_tables(lines):
    caption_pat = re.compile(r'^(Fig(ure)?\.?\s*\d+|Table\s*\d+)[.:]', re.I)
    return [(i + 1, line.strip()) for i, line in enumerate(lines)
            if caption_pat.match(line.strip())]
```

### 0.2 Broken-hyphenation detection

Flag every line-final hyphen (including the soft-hyphen character some PDF
extractions emit) and every internal hyphen splitting what looks like a
single morpheme. Distinguish broken words from genuine compounds:
- If the dehyphenated form appears elsewhere in the corpus as a clean,
  unhyphenated token → likely a wrap-break artifact, flag for correction.
- If the hyphenated form itself recurs consistently → likely a genuine
  compound, leave as is.
- If neither condition holds (the break occurs only once, with no second
  occurrence either way) → report as unclear rather than guessing; this is
  exactly what Step 0.5's mandatory confirm-before-correct checkpoint is
  for. Verified against real data: of 130 real breaks found, most resolved
  cleanly to "wrap-break artifact," a genuine minority stayed "unclear" —
  the detector defers to the researcher there rather than picking a side.

```python
# NOTE (fixed, live evidence, the test book chapter verification,
# 2026-08-06): this function previously only ever scanned for a hyphen
# at the literal end of a TXT line, joining to the start of the next
# line -- the shape a PDF-extraction line-wrap break has *if* the
# extraction preserved the original page's physical line breaks. Run for
# real against a corpus where line-wrap hyphens survived reflow into
# running paragraphs instead (a broken word sitting mid-sentence, e.g.
# "epis-temology" inline in running text, not at a line boundary), this
# function found ZERO broken hyphens -- while the corpus actually
# contained 473 hyphen-joined word-pair occurrences (259 distinct
# pairs). The gap was found only because Step 0.5's confirm-before-
# correct checkpoint forced a full corpus-wide hyphen audit by hand when
# the researcher asked for the underlying data, not because anything in
# this function's own execution surfaced it.
#
# Fixed by normalizing line-final hyphen+newline breaks into the same
# inline form a mid-line break already has (`word1-\nword2` ->
# `word1-word2`), then running ONE corpus-wide pair scan over the
# result -- rather than maintaining two separate detection mechanisms
# for what is structurally the same artifact. This is a broadening, not
# a behavior change, for every case the original line-final scan already
# covered: any hyphen the old regex would have found is still found
# here, since the normalization step reduces to an identical inline
# hyphen before the pair-scan ever runs.
#
# Verified against real data (the test book chapter): 259 distinct pairs
# found (473 total occurrences) -- 162 classified wrap-break artifact,
# 8 genuine compound, 89 unclear, reproducing the same wrap-break count
# a manual corpus-wide audit found independently, plus one case
# (`Lasonen-Aarnio`, a hyphenated proper name recurring 19 times) the
# manual audit's own scope had excluded by only ever considering
# lowercase pairs -- correctly caught here since this function does not
# have that restriction.
def scan_broken_hyphenation(lines):
    full_text = '\n'.join(lines)
    # Added v1.24 (same bug as 0.4b v1.23): real published text uses the
    # curly/smart apostrophe (U+2019), not the straight ASCII one, so a
    # contraction or possessive elsewhere in the corpus would otherwise
    # fragment at the apostrophe when building `token_freq` below.
    full_text_norm = full_text.replace('’', "'")

    # Normalize a line-final hyphen (or soft hyphen) followed by a
    # newline and optional leading whitespace into the same inline form
    # a mid-line break already has, so the single pair-scan below covers
    # both shapes of the same artifact.
    flattened = re.sub(r'([a-zA-Z]+)[­-]\s*\n\s*([a-zA-Z]+)', r'\1-\2', full_text_norm)

    # token_freq: how often each token appears as its OWN standalone
    # word, with hyphens treated as word boundaries rather than
    # stripped. Deliberately NOT built by stripping every hyphen from
    # the whole text first (an earlier version of this fix used that
    # approach and found it self-counting: stripping the very hyphen
    # under test inflates the joined form's own frequency by counting
    # occurrences of the artifact itself, artificially favoring the
    # wrap-break verdict). Tokenizing with hyphens as boundaries avoids
    # this entirely.
    token_freq = Counter(re.findall(r"[a-zA-Z']+", flattened))

    # NOTE (fixed, same verification pass, live evidence): grouping by
    # raw case (not lowercased) split one real compound into two weaker
    # entries whenever it also occurred sentence-initially -- on this
    # corpus, "higher-order" (73 lowercase occurrences) and
    # "Higher-order" (6 sentence-initial occurrences) counted as two
    # distinct pairs instead of one, caught only by re-running this
    # exact code against the corpus and finding 9 genuine-compound
    # entries instead of the expected 8. Grouping by lowercase form
    # fixes this; the reported `hyphenated_form` below still shows the
    # first-encountered casing, not a forced-lowercase display.
    pairs = re.findall(r'\b([a-zA-Z]{2,})-([a-zA-Z]{2,})\b', flattened)
    pair_counts = Counter((a.lower(), b.lower()) for a, b in pairs)
    display_form = {}
    for a, b in pairs:
        display_form.setdefault((a.lower(), b.lower()), f"{a}-{b}")

    hits = []
    for (first_part, second_part), n in pair_counts.items():
        joined = first_part + second_part
        hyphenated_form = display_form[(first_part, second_part)]

        # A pair recurring 3+ times whose joined form never appears as
        # its own clean word is strong evidence of a genuine hyphenated
        # compound (or proper name); a pair whose joined form IS
        # independently attested is strong evidence of a wrap-break,
        # regardless of recurrence -- matching the same two-signal logic
        # this function has always used, now applied corpus-wide instead
        # of only at line ends.
        if token_freq.get(joined, 0) >= 1:
            verdict = 'wrap-break artifact'
        elif n >= 3:
            verdict = 'likely genuine compound'
        else:
            verdict = 'unclear'
        hits.append((hyphenated_form, n, joined, verdict))
    return hits
```

### 0.3 Faulty-juxtaposition detection

Flag long lowercase tokens with no dictionary match that split cleanly into
two or more dictionary words with no leftover characters
(`domainindependent` → `domain independent`). This is the same failure class
as 0.2, in the opposite direction (words wrongly joined rather than wrongly
split).

**HONESTY NOTE (fixed, Delacroix 2026 verification, 2026-07-15).** The first
draft used raw WordNet lemma-name membership as its only dictionary check
and produced 13 false positives on this real corpus — ordinary derived or
inflected English (`paradigmatically`, `everything`, `discussing`) that
WordNet does not list as its own lemma, none of them genuine fusion
artifacts. Fixed with morphological reduction (`wn.morphy`), a small
derivational-suffix-stripping pass (`-ally`, `-ically`, `-able`, `-ible`,
`-al`, `-ly`), a small closed-class-pronoun allowlist (`everything`,
`someone`, etc.), and a minimum split-part length of 4 characters (a 2-3
character remainder like `pro-` + `-positional` is a prefix fragment, not a
second fused content word). Re-run against the same corpus after the fix:
zero false positives.

```python
_CLOSED_CLASS_COMPOUNDS = {
    'everything', 'something', 'anything', 'nothing',
    'everyone', 'someone', 'anyone', 'everybody', 'somebody', 'anybody', 'nobody',
}
_DERIVATIONAL_SUFFIXES = (
    ('ically', 6, ('ic', 'ical')),
    ('ally', 4, ('al', '')),
    ('ible', 4, ('', 'e')),
    ('able', 4, ('', 'e')),
    ('al', 2, ('', 'e')),
    ('ly', 2, ('', 'e')),
    # Added v1.20 (0.4b real-corpus test, 2026-07-29): -ism/-ist family was
    # entirely uncovered, false-flagging genuine academic/philosophical
    # vocabulary (reliabilism, responsibilism, internalism, externalism,
    # veritist, reliabilist...) as typos.
    ('isms', 4, ('ity', 'y', 'e', '')),
    ('ists', 4, ('ity', 'y', 'e', '')),
    ('ism', 3, ('ity', 'y', 'e', '')),
    ('ist', 3, ('ity', 'y', 'e', '')),
    # Added v1.25 (0.4b real-corpus test, further morphology gaps): each
    # verified against a real WordNet stem before being added, not guessed
    # -- "abductive" -> "abduct" (real verb), "coauthored" -> "coauthor"
    # (real WordNet lemma morphy's own verb-inflection rule didn't reach,
    # since "coauthor" isn't tagged as a verb in WordNet), "judgers" ->
    # "judge" (+'e'), "sexers" -> "sex", "seemings" -> "seeming" (a
    # two-step reduction, "seemings"->"seeming"->"seem", that morphy does
    # not chain automatically).
    ('ive', 3, ('ion', 'e', '')),
    ('ed', 2, ('e', '')),
    ('ers', 3, ('e', '')),
    ('er', 2, ('e', '')),
    ('s', 1, ('e', '')),
)


def _is_known_word(tok):
    tok = tok.lower()
    # Added v1.23: possessive 's stripped before any lookup -- neither
    # WordNet nor morphy resolve it on their own ("book's" has no entry),
    # and this only matters for tokens 0.4b passes in (0.3's own regex is
    # lowercase-letters-only and never produces an apostrophe-bearing
    # token), so this cannot change 0.3's behavior, only 0.4b's.
    if tok.endswith("'s") and len(tok) > 2:
        return _is_known_word(tok[:-2])
    # STOPWORD_VOCAB added v1.20, LATIN_SCHOLARLY_TERMS added v1.22 (both
    # for 0.4b) -- both strictly widen what counts as "known," so neither
    # can introduce a new false positive in 0.3's own faulty-juxtaposition
    # check, only remove possible false negatives.
    if (tok in WORDNET_VOCAB or tok in _CLOSED_CLASS_COMPOUNDS
            or tok in STOPWORD_VOCAB or tok in LATIN_SCHOLARLY_TERMS):
        return True
    if wn.morphy(tok) or any(wn.morphy(tok, p) for p in ('n', 'v', 'a', 'r')):
        return True
    for suf, cut, extra_forms in _DERIVATIONAL_SUFFIXES:
        if tok.endswith(suf) and len(tok) - cut > 2:
            stem = tok[:-len(suf)]
            candidates = {stem, stem[:-cut] if cut and len(stem) > cut else stem}
            candidates.update(stem + extra for extra in extra_forms)
            if any(c and (wn.morphy(c) or wn.synsets(c)) for c in candidates):
                return True
    return False


def scan_faulty_juxtaposition(lines, min_len=10, min_part_len=4):
    full_text = '\n'.join(lines)
    tokens = set(re.findall(r'\b[a-z]{%d,}\b' % min_len, full_text))
    hits = []
    for tok in tokens:
        if _is_known_word(tok):
            continue
        for split_at in range(min_part_len, len(tok) - min_part_len + 1):
            left, right = tok[:split_at], tok[split_at:]
            if _is_known_word(left) and _is_known_word(right):
                hits.append((tok, left, right))
                break
    return hits
```

### 0.4 Typographic/encoding noise

Lower priority, same pass: smart-quote/dash **mis-encoding** (not the mere
presence of smart quotes/dashes, which are normal correct typography),
broken ligatures (`fi`/`fl`), OCR confusables (`rn`/`m`, `1`/`l`/`I`), and a
lone capital letter isolated on its own line (usually near the top of the
document) — typically a mis-extracted icon or badge graphic (e.g. an
open-access lock symbol), not a real character or a footnote call.

**HONESTY NOTE (fixed, Delacroix 2026 verification, 2026-07-15).** The first
draft flagged every line containing a curly quote or en/em dash (~340 of
~1,300 lines on the test corpus) as "noise" — conflating ordinary correct
typography with actual mis-encoding. Fixed to check for genuine mojibake
byte sequences (classic UTF-8-read-as-Latin1/cp1252 patterns) and the
Unicode replacement character (U+FFFD) instead, which are the real signal
of a broken decode. Re-run against the same corpus: correctly finds zero —
this particular extraction's encoding is clean — rather than forcing a hit.
The OCR-confusables sub-check (`rn`/`m`, `1`/`l`/`I`) remains CODE-UNVERIFIED:
this is a native-text PDF, not a scanned/OCR source, so this corpus cannot
exercise that specific sub-check either way.

```python
def scan_typographic_noise(lines):
    hits = {'mis_encoding': [], 'lone_capital': []}
    mojibake_pat = re.compile(r'�|Ã[\x80-\xbf]|â€[\x80-\x9d]')
    lone_cap_pat = re.compile(r'^[A-Z]$')
    for i, line in enumerate(lines):
        if mojibake_pat.search(line):
            hits['mis_encoding'].append((i + 1, line.strip()[:60]))
        if lone_cap_pat.match(line.strip()):
            hits['lone_capital'].append((i + 1, line.strip()))
    return hits
```

### 0.4b General spelling/typo detection

**Added v1.20, closing a confirmed gap.** None of 0.1 through 0.4 do general
spell-checking: 0.2 only catches line-final wrap-breaks, 0.3 only catches two
real dictionary words wrongly fused into one token, and 0.4 only catches
mojibake and a lone capital letter. A plain transposition typo
("epinstemic" for "epistemic") passed through all of Step 0 completely
undetected. This sub-step closes that gap for **non-word errors** — a typo
that produces a token not recognized as any English word. It does **not**
catch **real-word errors** (a typo that happens to land on a different valid
word, e.g. "form" typed for "from") — that failure class needs contextual
judgment, not dictionary lookup, and remains open; see the disclosed
limitation below.

**Method.** For every token not recognized by `_is_known_word()` (0.3's
WordNet/morphy/derivational-suffix check, now also covering closed-class
function words via `STOPWORD_VOCAB` and common untranslated Latin/foreign
scholarly phrases via `LATIN_SCHOLARLY_TERMS`, added v1.22):
- **Added v1.22.** If it appears capitalized, not sentence-initial,
  anywhere in the corpus (via `find_capitalized_candidates()`, below), it is
  reported as an **unrecognized recurring term** with no suggested fix,
  regardless of how many times it occurs — a hapax proper noun is just as
  legitimate as a recurring one, and the frequency-only heuristic below
  had no way to rescue one cited only once.
- If it recurs more than `low_freq_threshold` times in the corpus, it is
  reported as an **unrecognized recurring term** with no suggested fix.
  Recurrence is treated as evidence it is more likely intentional
  vocabulary (a proper name, domain term, or coinage) than a one-off
  keystroke error — the same reasoning already used, in the opposite
  direction, by 0.2's "recurs consistently → genuine compound" rule.
- If it occurs `low_freq_threshold` times or fewer, it is checked against
  known-word candidates within Damerau-Levenshtein distance
  `max_edit_distance` (adjacent-letter transpositions count as one edit,
  not two, since transposition is one of the commonest real typo types).
  Candidates already attested elsewhere in this corpus are preferred over
  WordNet-wide matches, ranked by in-corpus frequency, since a word the
  author already uses elsewhere is stronger evidence of intent than an
  obscure WordNet lemma the corpus never otherwise uses. If a close match
  exists, it is reported as a **likely typo** with the suggested fix(es).
  If no close match exists at all, the token is not flagged — too weak a
  signal to surface (could be a rare proper name, a foreign-language
  quotation, or a genuine neologism).

**HONESTY NOTE (CODE-VERIFIED against synthetic test cases only — NOT yet
run against the real Delacroix 2026 corpus or any other real corpus).**
Built and iterated against a hand-constructed test corpus covering the
specific failure modes this design needed to survive, each caught by
actually running the code, not by reasoning about it in the abstract:
(1) the original "epinstemic"/"epistemic" case that surfaced the gap —
correctly flagged with the correct single suggestion; (2) plain WordNet-only
recognition falsely flagged ordinary function words ("this", "that",
"should", "and", "the") as typos, since WordNet's lemma list is a
content-word dictionary — fixed by adding `STOPWORD_VOCAB` to
`_is_known_word()`; (3) plain (non-Damerau) Levenshtein distance ranked a
transposition typo ("teh") as equidistant from several unrelated words
("tea", "tec") as from the correct fix ("the"), and alphabetical
tie-breaking then dropped "the" off the top-3 entirely — fixed by using
Damerau-Levenshtein and by preferring corpus-attested candidates over
WordNet-wide ones; (4) a repeated invented technical term and a repeated
proper name (both simulated stand-ins for real domain vocabulary) were
correctly routed to "unrecognized recurring," not falsely offered a typo
fix; (5) a genuine one-off rare real word and a genuine one-off proper name
were correctly left unflagged. **Not yet established:** real-corpus false
positive/negative rates, and runtime at real corpus scale with many
distinct low-frequency unrecognized tokens (only a synthetic worst-case
sketch was run, not a full timed pass against real data) — both should be
confirmed the first time this step runs against an actual corpus, the same
way 0.1 through 0.4 were.

**Disclosed limitation, not yet designed.** Real-word errors (typo lands on
a different valid word) are structurally outside what dictionary/edit-distance
matching can ever catch, since the wrong word still passes `_is_known_word()`.
An optional, opt-in contextual second pass (asked of the researcher, not run
by default, given its cost relative to this free deterministic layer) was
discussed as the way to close that gap, restricted to the sentences around
already-borderline tokens rather than a full-corpus pass — but this has not
been designed or implemented. Treat it as a separate open item, not part of
this sub-step's current scope.

**Disclosed limitations of the v1.22 capitalization and Latin-phrase
signals, confirmed by the real-corpus test that motivated them (see the
v1.22 changelog entry for full before/after numbers):**
- The capitalization signal only rescues a proper noun that appears
  non-sentence-initially **somewhere** in the corpus. A name that happens
  to occur only at the start of sentences throughout the whole document is
  still missed and falls through to typo-checking — a real, not
  hypothetical, residual gap, not a claim of complete coverage.
- `find_capitalized_candidates()` tokenizes by whitespace-splitting
  sentences, while `scan_spelling_typos()` itself tokenizes with the
  `word_pat` regex. The two do not always agree at the edges (e.g. a
  hyphenated or apostrophe-bearing proper name) — a known, disclosed
  imprecision from reusing the two tokenizations together, not a new bug
  specific to this combination.
- `LATIN_SCHOLARLY_TERMS` is a hand-curated allowlist, not a Latin
  dictionary or a formatting-aware detector. The stronger signal available
  in the original source (these phrases are conventionally italicized) is
  structurally unavailable here, since Step 0 runs on the plain TXT file
  alone, after formatting has already been stripped. A genuine typo that
  happens to collide with a listed term would be silently suppressed --
  an accepted, disclosed trade-off given the list's small size. **Added
  v1.26:** `hoc` ('ad hoc'/'post hoc') was confirmed missing by the
  second real-corpus test and added; the rest of the list was audited at
  the same time and found otherwise complete for the phrases it already
  represents (see the v1.26 changelog entry).

**Disclosed limitations of the v1.26 "un-" prefix fix (`_strips_known_prefix`),
confirmed by the same second real-corpus test that found the gap:**
- Deliberately narrow by design, not by oversight: only a leading `un-`
  is stripped. Other English negation prefixes (`in-`/`im-`/`il-`/`ir-`,
  `non-`, `dis-`) are not handled at all -- a real word like
  "irrecoverable" or "nonrecurring" still gets no prefix-stripping rescue
  and falls through to ordinary typo-checking exactly as before this fix.
  This is a distinct, undesigned item, not silently folded into "prefix
  handling is done."
- Like `_splits_into_known_words`, this is local to 0.4b only, not folded
  into the shared `_is_known_word()` -- so it cannot change Step 0.2's,
  0.3's, or 0.4's own already-validated behavior.

```python
def _edit_distance(a, b, max_dist):
    # Damerau-Levenshtein (optimal string alignment): counts an adjacent
    # transposition ("teh"/"the") as one edit, not two.
    if abs(len(a) - len(b)) > max_dist:
        return max_dist + 1
    la, lb = len(a), len(b)
    d = [[0] * (lb + 1) for _ in range(la + 1)]
    for i in range(la + 1):
        d[i][0] = i
    for j in range(lb + 1):
        d[0][j] = j
    for i in range(1, la + 1):
        for j in range(1, lb + 1):
            cost = 0 if a[i - 1] == b[j - 1] else 1
            d[i][j] = min(
                d[i - 1][j] + 1,
                d[i][j - 1] + 1,
                d[i - 1][j - 1] + cost,
            )
            if i > 1 and j > 1 and a[i - 1] == b[j - 2] and a[i - 2] == b[j - 1]:
                d[i][j] = min(d[i][j], d[i - 2][j - 2] + 1)
    return d[la][lb]


def _wordnet_by_length():
    idx = {}
    for w in WORDNET_VOCAB:
        idx.setdefault(len(w), []).append(w)
    return idx


_WN_BY_LEN = _wordnet_by_length()


def _closest_known_words(tok, corpus_known_pool, corpus_freq, max_dist):
    # Tier 1: words already attested elsewhere in this corpus -- the
    # strongest available signal for what the author actually meant,
    # ranked by how often the corpus itself uses them.
    corpus_hits = []
    for w in corpus_known_pool:
        if w == tok or abs(len(w) - len(tok)) > max_dist:
            continue
        d = _edit_distance(tok, w, max_dist)
        if d <= max_dist:
            corpus_hits.append((d, w))
    if corpus_hits:
        corpus_hits.sort(key=lambda item: (item[0], -corpus_freq.get(item[1], 0), item[1]))
        best_d = corpus_hits[0][0]
        return [w for d, w in corpus_hits if d == best_d][:3]

    # Tier 2: only if the corpus itself offers no candidate, fall back to
    # WordNet at large (unranked by real-world frequency -- weaker signal).
    pool = set()
    for L in range(len(tok) - max_dist, len(tok) + max_dist + 1):
        pool.update(_WN_BY_LEN.get(L, ()))
    wn_hits = []
    for w in pool:
        if w == tok:
            continue
        d = _edit_distance(tok, w, max_dist)
        if d <= max_dist:
            wn_hits.append((d, w))
    if not wn_hits:
        return []
    wn_hits.sort()
    best_d = wn_hits[0][0]
    return [w for d, w in wn_hits if d == best_d][:3]


def find_capitalized_candidates(corpus_text):
    # Added v1.22. Capitalized, non-sentence-initial tokens -- tested
    # against a real corpus (see the v1.22 changelog entry).
    sentences = re.split(r'(?<=[.!?])\s+', corpus_text)
    candidates = {}
    for sent in sentences:
        words = sent.split()
        for i, w in enumerate(words):
            clean = w.strip('.,;:()"\'')
            if i == 0 or not clean or not clean[0].isupper():
                continue
            if not clean.isalpha():
                continue
            candidates[clean] = candidates.get(clean, 0) + 1
    return candidates


def _splits_into_known_words(tok, min_part_len=3):
    # Added v1.25, local to 0.4b only -- deliberately NOT folded into the
    # shared `_is_known_word()`, since Step 0.3's own faulty-juxtaposition
    # check calls `_is_known_word()` on the whole fused candidate before
    # ever reporting it; if this lived there, 0.3 would silently stop
    # reporting genuine fused-compound artifacts (e.g. "simpleminded")
    # instead of surfacing them for the researcher to confirm, defeating
    # 0.3's own purpose. Kept separate so 0.4b can recognize a legitimate
    # compound ("toolkit") as not-a-typo while 0.3 independently keeps
    # doing its own, different job of flagging fused compounds for
    # confirmation -- the two checks are not redundant, they serve
    # different purposes on the same underlying pattern.
    for split_at in range(min_part_len, len(tok) - min_part_len + 1):
        left, right = tok[:split_at], tok[split_at:]
        if _is_known_word(left) and _is_known_word(right):
            return True
    return False


def _strips_known_prefix(tok, min_stem_len=3):
    # Added v1.26, local to 0.4b only, for the same reason
    # `_splits_into_known_words` (v1.25) is local rather than folded into
    # the shared `_is_known_word()`: nothing else in Step 0 needs it, and
    # keeping it local guarantees it cannot change 0.2's, 0.3's, or 0.4's
    # own already-validated behavior. Closes a gap the second real-corpus
    # test (2026-07-29, see v1.26 changelog) confirmed: neither
    # `_is_known_word()` nor `_DERIVATIONAL_SUFFIXES` strip a leading
    # negation prefix, only trailing suffixes, so a real word with "un-"
    # prepended ("unexamined" -> "un" + "examined", "unmet" -> "un" +
    # "met") was flagged as a typo despite being ordinary English.
    # SCOPE (deliberately narrow, matching exactly what was confirmed
    # missing, not a general prefix-stripping framework): only the "un-"
    # prefix is handled. Other negation prefixes (in-/im-/il-/ir-, non-,
    # dis-) are a distinct, undesigned item -- see the disclosed
    # limitation below, not silently assumed covered by this fix.
    if tok.startswith('un') and len(tok) - 2 >= min_stem_len:
        return _is_known_word(tok[2:])
    return False


def scan_spelling_typos(lines, low_freq_threshold=1, max_edit_distance=2):
    full_text = '\n'.join(lines)
    # Added v1.23 (real-corpus test, 2026-07-29): real published text uses
    # the curly/smart apostrophe (U+2019), not the straight ASCII one, but
    # `word_pat` below only recognizes the latter -- so "doesn't" tokenized
    # as "doesn" + a dropped "'t", producing a false typo ("doesn" ->
    # "does"). Normalizing once, upfront, fixes both the tokenization loss
    # and the STOPWORD_VOCAB lookup below (which stores contractions with
    # straight apostrophes) with a single change, rather than touching the
    # regex character class and the vocabulary separately.
    full_text = full_text.replace('’', "'")
    word_pat = re.compile(r"\b[a-zA-Z']{3,}\b")
    freq = Counter(tok.lower() for tok in word_pat.findall(full_text))
    corpus_known = {tok for tok in freq if _is_known_word(tok)}

    # Added v1.22: a token that appears capitalized, not sentence-initial,
    # anywhere in the corpus is very likely a proper name -- rescued from
    # typo-checking regardless of frequency (a hapax proper noun is just
    # as legitimate as a recurring one; the old frequency-only heuristic
    # missed every name cited exactly once).
    capitalized_lower = {c.lower() for c in find_capitalized_candidates(full_text)}

    hits = []
    for tok, count in freq.items():
        if _is_known_word(tok):
            continue
        # Added v1.25: a token not otherwise recognized but that splits
        # cleanly into two real dictionary words ("toolkit" -> "tool" +
        # "kit") is legitimate vocabulary, not a typo -- silently treated
        # as known, same as a direct WordNet hit. Does not duplicate or
        # suppress Step 0.3's own, separate fused-compound report (0.3
        # only ever considers tokens >=10 characters as whole-token fusion
        # candidates and writes its findings to its own report category;
        # this only affects what 0.4b itself flags as a typo).
        if _splits_into_known_words(tok):
            continue
        # Added v1.26: a token formed by prepending "un-" to a real word
        # ("unexamined", "unmet") is legitimate vocabulary, not a typo --
        # see `_strips_known_prefix` above for scope and reasoning.
        if _strips_known_prefix(tok):
            continue
        # Added v1.23: a possessive of a proper noun ("Watson's") is not
        # itself in `capitalized_lower`, since `find_capitalized_candidates`
        # requires `clean.isalpha()` and the apostrophe fails that check --
        # but the bare name ("Watson") usually is, since it typically also
        # appears unpossessed elsewhere. Check the possessive-stripped form
        # as a fallback rather than leaving every possessive proper noun
        # unrescued.
        base = tok[:-2] if tok.endswith("'s") and len(tok) > 2 else tok
        if tok in capitalized_lower or base in capitalized_lower:
            hits.append({'token': tok, 'count': count, 'category': 'unrecognized_recurring',
                         'suggestion': None, 'signal': 'capitalized, non-sentence-initial'})
            continue
        if count > low_freq_threshold:
            hits.append({'token': tok, 'count': count, 'category': 'unrecognized_recurring',
                         'suggestion': None, 'signal': 'recurs in corpus'})
            continue
        candidates = _closest_known_words(tok, corpus_known, freq, max_edit_distance)
        if candidates:
            hits.append({'token': tok, 'count': count,
                         'category': 'likely_typo', 'suggestion': candidates, 'signal': None})
    return hits
```

### 0.5 Report and confirm — mandatory checkpoint

Never auto-correct silently. Present findings as a table:

```
Category                | Line     | Found                         | Suggested fix
-------------------------------------------------------------------------------------
Broken hyphenation       | 412      | "epi-\nstemic"                | "epistemic"
Faulty juxtaposition     | 88       | "domainindependent"           | "domain independent"
Dangling page number     | 230      | "47"  (alone)                 | delete
Footnote call artifact   | 156      | "knowledge1 is"               | "knowledge is"
Front matter/publisher   | 1-14     | affiliation, journal masthead | redact (title/authors kept)
Footnote/endnote content | 229-237  | "Notes" section, 2 entries    | redact (matches calls at 50, 56)
Numeric table content    | 334-360  | statistics table (M/SD/p/r)   | drop content, keep caption
Icon/badge glyph         | 7        | lone "Q"                      | delete (mis-extracted icon)
Likely typo              | 501      | "epinstemic" (x1)             | "epistemic"
Unrecognized recurring   | 88, 340  | "gadzorpal" (x3)              | (no suggested fix — see below)
```

Ask the user to confirm, reject, or correct each category. **Do not proceed
to Step 0.6 until the user has explicitly confirmed.** Only after
confirmation does Claude write the cleaned TXT.

**Added v1.20 — resolution paths for the two 0.4b row types differ from the
rest of the table:**
- **Likely typo** rows carry a suggested fix, same as every other category:
  the researcher confirms it, rejects it (leave the token as-is), or
  supplies her own replacement instead of the suggested one.
- **Unrecognized recurring** rows carry no suggested fix — there is nothing
  to confirm or reject. The question put to the researcher is different in
  kind: *is this a real term (proper name, domain vocabulary, coinage) to
  leave untouched, or is it actually an error?* If she confirms it is
  intentional, it is carried forward into Step 0.6's draft exclusion list
  (see below) rather than silently dropped once confirmed. If she says it is
  in fact wrong, she supplies the correction herself, the same as the
  "correct it herself" path for a likely-typo row. **Added v1.22:** this
  category now has two distinct bases, disclosed via the internal `signal`
  field so the researcher isn't shown a bare "recurring" label without
  knowing why — "capitalized, non-sentence-initial" (a likely proper name)
  versus "recurs in corpus" (the original frequency-only reasoning). Show
  which basis applies in the report table rather than collapsing both to
  one unexplained row type.

### 0.6 Draft exclusion harvesting

While scanning, collect candidate proper names (capitalized tokens not at
sentence-initial position), standalone numerals, and citation artifacts
(`et al`, `ibid`, `e.g.`) into a draft exclusion list. Carry this list
forward into Step 3.1 Rule C instead of rebuilding it from scratch.

**Added v1.20.** Also fold in any 0.4b "unrecognized recurring" term the
researcher confirmed as intentional at the 0.5 checkpoint — it is exactly
the kind of item this list already exists to hold (real vocabulary the
automated checks don't otherwise recognize), so it should not sit in a
separate bucket nothing downstream ever looks at again.

Report to the user: the cleaned TXT is ready for Voyant upload. The draft
exclusion list (N candidate terms) will be presented again for confirmation
at Step 3.1.

**HONESTY NOTE (added, live evidence, 2026-07-15).** Every version of this
step through v1.12 said only "the cleaned TXT is ready for Voyant upload"
and left it there — a silent assumption that the researcher already knows
the actual mechanism, or that the TSVs in Step 0.7 below simply materialize.
Confirmed live: Claude does not have a way to drive Voyant's
own file-upload dialog (a native OS picker, outside any web page's DOM,
which browser automation cannot see or dismiss) — attempting to do so left
a browser tab stuck. **The actual mechanism requires the researcher's own
hands, every time, and must be asked for explicitly, not assumed:** ask the
researcher to open a Spyral page and upload/paste in this project's Data
Collection Notebook (`PEEL-DataCollectionNotebook.html` or equivalent),
paste the corpus's Voyant ID (obtained by the researcher creating the
corpus directly on the Voyant instance) into its `loadCorpus(...)` cell, run
the Terms and Phrases cells, export each as TSV, and upload those TSV files
here. Do not proceed past this point assuming the researcher already knows
this sequence — ask for it directly, the same discipline Step 0.7 below
already applies to the files themselves, now extended to the mechanism that
produces them.

---

## 0.7 Inputs

**Three uploaded files are required, in this order.** The TXT must already
have passed Step 0.5 confirmation. Do not proceed if any is missing — ask the
user to supply it before continuing.

| File | Role | Format |
|---|---|---|
| `*.txt` | Corpus text (cleaned per Step 0) | Plain UTF-8 |
| `*-terms.tsv` | Voyant term-frequency list | tab-separated: **DocIndex, Term, RawFrequency, RelativeFrequency, ZScore, ZScoreRatio, TF-IDF, Distributions** — see note below |
| `*-phrases.tsv` | Voyant phrases / N-gram list | tab-separated: Phrase; RawFrequency; RelativeFrequency; … (exact columns vary by Voyant version); any overlap setting (`none`, `prioritize longest`, `prioritize most frequent`) accepted — see revised Step 1b |

**NOTE (fixed, live-run finding, corpus GarciaOkonkwo2025):** the column
list above was previously stated as `Term; inDocumentsCount; RawFrequency;
RelativeFrequency; RelativePeakedness; RelativeSkewness; Distributions` —
never verified against an actual export, and wrong. The Data Collection
Notebook's actual Terms cell uses this Spyral config:

```javascript
let config = {
    "lang": 'en',
    "columns": ['term', 'rawFreq', 'relativeFreq', 'tfidf', 'zscore', 'distributions'],
    "dir": 'asc',
    "sort": 'term',
    "termColors": 'null',
  };
 myCorpus.tool("documentterms", config);
```

**`DocIndex` always appears in the export regardless of the `columns`
config** — this is the same "export all available data," not just the
visualization, discipline PEEL has used from the beginning, and is not
something to configure away. `columns` controls what the live Voyant tool
*displays*; the "export all available data" option pulls every field the
tool computes internally, `DocIndex` included. Only `Term` and
`RawFrequency` are actually referenced by this file's code downstream, so
this discrepancy has no effect on any step below — but the column list
above should describe what a real export actually contains, not an
unverified guess.

**How to export the Phrases TSV from Voyant:**
Open the Phrases tool (add it via the tool menu if not visible). Export using
the grid icon at the bottom of the panel. Save with a `.tsv` extension.

**CRITICAL — Read both TSVs with the same settings:**
```python
import pandas as pd

terms_df  = pd.read_csv('terms.tsv',   sep='\t', encoding='cp1252', on_bad_lines='skip')
phrases_df = pd.read_csv('phrases.tsv', sep='\t', encoding='cp1252', on_bad_lines='skip')
```
- Separator is **tab**, not comma.
- Encoding is **corpus/export-specific — verify every time, do not assume
  cp1252 (or any fixed choice) carries over from a prior run.** For the
  GarciaOkonkwo2025 export, `cp1252` was correct and `latin1` produced
  mojibake (`aristotle's` read as `aristotle�\x80\x99s`) because that
  export's smart-quote/accented characters were single-byte cp1252 code
  points, which `latin1` cannot represent. For the Delacroix 2026 export
  (verified live, 2026-07-15), the opposite held: every non-ASCII character
  turned out to be valid **multi-byte UTF-8** (e.g. the byte sequence for a
  curly apostrophe, `\xe2\x80\x99`, is exactly U+2019 under UTF-8 but splits
  into three garbled characters under cp1252). Neither encoding is the
  "real" default — each export's actual bytes decide it.
  **NOTE (fixed, live evidence, Delacroix 2026 verification, 2026-07-15):
  verify by inspecting actual codepoints/bytes (e.g. `hex(ord(ch))` on the
  decoded string, or a raw hex dump of the file), never by how a decoded
  string renders when printed to a terminal.** A first attempt at this
  export's decode check trusted printed output and concluded cp1252 was
  correct, because the terminal couldn't render the correctly-decoded
  UTF-8 character and displayed a replacement glyph that looked like a
  failure — a wrong verdict that direct codepoint inspection caught and
  reversed. Terminal rendering is not a substitute for checking the actual
  decoded value.
- `on_bad_lines='skip'` handles rows with European number format (e.g. `9,62E+02`).
- Always verify shape and head of **both** DataFrames before proceeding.
- **NOTE (fixed, live-run finding, corpus GarciaOkonkwo2025):** this file
  previously claimed the Terms TSV arrives "already sorted by RawFrequency
  descending" and instructed against re-sorting. Run for real, the export
  was sorted alphabetically by term — the Data Collection Notebook's Terms
  cell config (`"dir": 'asc', "sort": 'term'`, shown above) controls this,
  and its default sorts by term, not frequency. Rather than depend on the
  researcher remembering to set `"dir": 'desc', "sort": 'rawFreq'` in that
  Spyral cell every time — a silent, easy-to-forget precondition, the same
  fragility class this file has already removed elsewhere (e.g. Step 1b no
  longer requires a specific Voyant Phrases-overlap setting) — Step 3.2
  below now sorts `filtered_df` by `RawFrequency` descending explicitly,
  in code, regardless of the order the TSV actually arrives in. This makes
  the coverage-N calculation correct independent of Notebook configuration.

Report to the user:
- Number of errors during reading of each file.
- List of errors (if applicable).

---

## 1. Read and Verify

**Navigation note (added 2026-07-28): the next three sections do not
appear in numeral order.** After this section, the file reads **1 → 1c →
1b → 2** — Step 1c (a branch decision) is placed *before* Step 1b
deliberately, because 1c determines whether 1b's automated phrase
generation runs at all, so it has to be read and decided first. Nothing
was renumbered to fix this (doing so would break the many existing
cross-references to "Step 1b" and "Step 1c" throughout this file) — this
note exists so the reading order doesn't need to be rediscovered by
trial.

### 1.1 — Terms TSV

```python
import pandas as pd

terms_df = pd.read_csv('terms.tsv', sep='\t', encoding='cp1252', on_bad_lines='skip')
print(f"Total terms: {len(terms_df)}")
print(f"Columns: {terms_df.columns.tolist()}")
print(terms_df[['Term','RawFrequency']].head(10))
```

Report to the user:
- Total number of terms
- Frequency range (min, max)
- First 10 terms (sanity check)

### 1.2 — Phrases TSV

```python
phrases_df = pd.read_csv('phrases.tsv', sep='\t', encoding='cp1252', on_bad_lines='skip')

# Normalise column name — Voyant versions differ
if 'Phrase' not in phrases_df.columns:
    phrases_df = phrases_df.rename(columns={phrases_df.columns[0]: 'Phrase',
                                             phrases_df.columns[1]: 'RawFrequency'})

print(f"Total phrases: {len(phrases_df)}")
print(f"Columns: {phrases_df.columns.tolist()}")
print(phrases_df[['Phrase','RawFrequency']].head(10))
```

Report to the user:
- Total number of phrases
- Frequency range (min, max)
- First 10 phrases (sanity check)

---

## 1c. Term Selection Method

**REMOVED, 2026-07-31 (researcher-requested skill edit, live full-cycle
test): the researcher-seeded selection path (formerly option (a) here,
and the full Step 3s section it routed to) has been removed entirely.**
This is no longer a branch point — term selection is always automated
(the process formerly called "path (b)"): filter the TSVs, compute
coverage-N, flag POS/example-vocabulary outliers, and the researcher
confirms in batches (Steps 3.1–3.4). See the v1.28 changelog entry for
the removal and its rationale. `selection_method` is still recorded, now
always `'automated'`, since downstream steps (filenames, the "Term
selection provenance" report section) still reference it by name.

```python
selection_method = 'automated'
```

Proceed to Step 1b, then Step 2, then Step 3.1.

---

## 1b. N-gram Extraction and Boundary-Trimming

**Purpose:** identify multi-word expressions that are conceptually unified,
frequent enough to be meaningful, and trimmed of boundary stopwords so they
function as reliable exact-phrase search terms in Voyant. These will be
carried forward as `"quoted phrase"` entries alongside wildcard stems in the
incList and cluster definitions.

**No specific Voyant export configuration is required.** This step works
with whatever overlap setting (`none`, `prioritize longest`, `prioritize
most frequent`) the user's Voyant export happens to use. A phrase padded
with a boundary stopword (`"the common good"`) is strictly worse as an
exact-phrase search term than its trimmed core (`"common good"`), since it
would miss `"a common good"` or `"common good"` appearing alone — trimming
is therefore always applied, regardless of how the export was produced.

### Algorithm

```python
import re

# Step 1: keep only phrases of 2+ words — no frequency filter yet.
# Filtering on raw frequency this early would be overlap-mode-sensitive:
# under "prioritize longest", the surviving row for a span is the longest
# padded variant, whose own frequency is deflated relative to its core
# phrase's true frequency, and could be wrongly excluded before trimming
# ever runs.
phrases_df['word_count'] = phrases_df['Phrase'].apply(lambda p: len(str(p).split()))
multi = phrases_df[phrases_df['word_count'] >= 2].copy()

# Step 2: boundary-stopword trimming
#
# Boundary-stopword trimming is a generic linguistic operation, not a
# corpus-specific significance judgment -- deliberately decoupled from
# Step 3.1's exclusion set (which encodes corpus-specific calls the
# researcher confirms at a later checkpoint this step has no business
# waiting on). Loads a standard, generic stopword list on its own.
# See Implementation Notes #1 (appendix) for why this was decoupled.
#
# Language: a lightweight, UNCONFIRMED detection picks which NLTK
# list to load, by checking which candidate language's stopword set
# has the highest token overlap with the corpus. This is local to
# this step only, used solely to pick a generic trimming list, and is
# NOT a substitute for Step 2's user-facing language confirmation,
# which remains authoritative for everything else in the pipeline.
# EMBEDDED FALLBACK (primary path -- see note below on why this is
# primary, not a fallback-of-last-resort). English and Portuguese only;
# this mirrors the same English/BP-uncertainty scope already documented
# for the Voyant built-in stoplists elsewhere in this project. Sized for
# boundary-trimming (articles, prepositions, conjunctions, basic
# pronouns/verb-forms) -- it does not need to be an exhaustive list.
_EMBEDDED_STOPWORDS = {
    'english': {
        'a','an','the','and','or','but','if','then','than','so',
        'of','at','by','for','with','without','about','against',
        'between','into','through','during','before','after','above',
        'below','to','from','up','down','in','out','on','off','over',
        'under','again','further','once','here','there','when','where',
        'why','how','all','any','both','each','few','more','most',
        'other','some','such','no','nor','not','only','own','same',
        'too','very','is','are','was','were','be','been','being',
        'have','has','had','having','do','does','did','doing','this',
        'that','these','those','i','you','he','she','it','we','they',
        'them','his','her','its','our','their','as','it\'s',
    },
    'portuguese': {
        'a','o','as','os','um','uma','uns','umas','e','ou','mas','se',
        'de','do','da','dos','das','em','no','na','nos','nas','por',
        'para','com','sem','sobre','entre','contra','ate','desde',
        'apos','antes','depois','quando','onde','como','que','quem',
        'qual','quais','todo','toda','todos','todas','algum','alguma',
        'nenhum','nenhuma','mesmo','mesma','muito','pouco','mais',
        'menos','ser','estar','sao','eram','foi','foram','tem','tinha',
        'este','esta','estes','estas','esse','essa','esses','essas',
        'eu','tu','ele','ela','nos','voces','eles','elas','seu','sua',
        'seus','suas','nosso','nossa',
    },
}

# This environment has no network access by default, so the embedded
# list above is the PRIMARY path, not a last-resort fallback. NLTK is
# used opportunistically, only if its 'stopwords' corpus is *already*
# present locally -- no download is attempted. See Implementation
# Notes #2 (appendix) for why.
_detected_lang = None
# Added v1.24 (same bug as 0.4b v1.23, found there first): real published
# text uses the curly/smart apostrophe (U+2019), not the straight ASCII
# one -- `_EMBEDDED_STOPWORDS['english']` includes "it's" with a straight
# apostrophe, so a corpus using curly apostrophes throughout would have
# every contraction fragment at the apostrophe and never match, silently
# depressing the English overlap score. Normalized inline, at the point of
# use, since `txt` is assumed already loaded from an earlier step, not
# assigned in this snippet.
_doc_tokens = set(re.findall(r"[a-zA-Z']+", txt.lower().replace('’', "'")))

# Overlap is normalized by each candidate list's own size (fraction of
# the list that appears in the document), not raw count -- raw count
# biases toward larger candidate lists regardless of actual fit. See
# Implementation Notes #3 (appendix) for the concrete failure this
# prevents.

try:
    import nltk
    nltk.data.find('corpora/stopwords')
    from nltk.corpus import stopwords as nltk_stopwords
    _candidate_langs = nltk_stopwords.fileids()
    def _overlap_score(lang):
        lang_words = set(nltk_stopwords.words(lang))
        if not lang_words:
            return 0.0
        return len(_doc_tokens & lang_words) / len(lang_words)
    _detected_lang = max(_candidate_langs, key=_overlap_score)
    stopwords = set(nltk_stopwords.words(_detected_lang))
    _source = f"NLTK '{_detected_lang}' corpus ({len(stopwords)} words)"
except (ImportError, LookupError):
    def _overlap_score(lang):
        lang_words = _EMBEDDED_STOPWORDS[lang]
        if not lang_words:
            return 0.0
        return len(_doc_tokens & lang_words) / len(lang_words)
    _detected_lang = max(_EMBEDDED_STOPWORDS, key=_overlap_score)
    stopwords = _EMBEDDED_STOPWORDS[_detected_lang]
    _source = f"embedded '{_detected_lang}' list ({len(stopwords)} words, no NLTK available)"

if _overlap_score(_detected_lang) < 0.15:
    print("WARNING: very low stopword-overlap with this corpus -- the "
          "detected language for boundary-trimming may be wrong, or "
          "this corpus is in a language not covered by the embedded "
          "lists. Boundary trimming may under-perform; check the "
          "'estimated' phrases below more carefully.")

print(f"Boundary-trim stopword list: {_source} -- provisional "
      f"detection local to this step, independent of Step 2's "
      f"confirmed corpus language")
```

**Carry this forward** into the Phase1-results.md report (a permanent
`## Environment fallbacks used` section, not just a chat-turn or printed
message): record `_source` (which list was actually used and why) and,
if it fired, the low-overlap warning. This is the same discipline as
Step 3.5's WordNet grounding tally — mandatory every run, not only when
the result looks questionable, so a researcher reopening this corpus's
deliverables later can see which mode actually ran without having to
trust that they happened to read the right line of a long session.

```python
def trim_boundaries(phrase):
    words = phrase.split()
    while words and words[0].lower() in stopwords:
        words = words[1:]
    while words and words[-1].lower() in stopwords:
        words = words[:-1]
    return ' '.join(words)

multi['trimmed'] = multi['Phrase'].apply(trim_boundaries)
multi = multi[multi['trimmed'].str.split().str.len() >= 2]

# Step 3: resolve trimmed form against existing rows
phrase_freq = dict(zip(phrases_df['Phrase'], phrases_df['RawFrequency']))

def resolve(row):
    if row['trimmed'] in phrase_freq:
        return phrase_freq[row['trimmed']], 'measured'
    return row['RawFrequency'], 'estimated (padded-variant fallback)'

multi[['final_freq', 'confidence']] = multi.apply(
    lambda r: pd.Series(resolve(r)), axis=1
)

# Step 4: deduplicate by trimmed form, keep highest-confidence/highest-freq row
multi = (multi.sort_values(['confidence', 'final_freq'], ascending=[True, False])
               .drop_duplicates(subset='trimmed', keep='first'))

# Step 5: apply MIN_FREQ to the resolved frequency — not the raw row.
# This is the only point in the pipeline where the threshold is applied,
# and it now operates on a value that means the same thing regardless of
# which overlap mode produced the original export.
MIN_FREQ = 3  # lower to 2 only for corpora under ~5,000 tokens
candidates = multi[multi['final_freq'] >= MIN_FREQ].copy()
candidates = candidates.sort_values('final_freq', ascending=False).reset_index(drop=True)
```

### Reporting

Present the full candidate list to the user in a table, including the
confidence column:

```
Rank | Phrase                  | Freq | Confidence
-----|-------------------------|------|---------------------------
  1  | common good             |  11  | measured
  2  | human dignity           |   9  | measured
  3  | artificial intelligence |   8  | estimated (padded-variant fallback)
  4  | social doctrine         |   7  | measured
  ...
```

Then ask:

> "These are the significant multi-word expressions found in the Phrases
> TSV, trimmed of boundary stopwords. Entries marked 'estimated' mean the
> trimmed form wasn't found as its own row — its frequency is a lower bound
> derived from a padded variant. Please confirm which ones to include as
> search phrases, or request removals. Confirmed phrases will appear as
> `\"quoted\"` entries in the incList and in their relevant cluster."

**Do not proceed to Step 2 until the user has confirmed the phrase list.**

Corrections:
- If the user removes phrases, drop them from `candidates`.
- If the user adds a phrase not in the list, verify it appears in the TXT before
  accepting.

### Integration into downstream steps

- Confirmed phrases are stored in a `selected_phrases` list (list of strings).
- In **Step 4**, they are appended to the stem list as `'"phrase text"'`
  (double-quoted strings), sorted alphabetically alongside wildcard stems.
- In **Step 5**, they are assigned to clusters exactly like stems and appear in
  the clusterDefs `stems` array as `"phrase text"` entries.
- In **Step 6**, they appear in `incList` as `"phrase text"` strings (Voyant
  accepts quoted strings as exact-phrase searches).

---

## 2. Detect Corpus Language and ask user for Base Parameters

Determine the language of the corpus by reading the TXT file.

Ask user for:
 (a): the corpusID established by Voyant when the text was first uploaded;
      the corpusID is a 32-character alphanumeric string; verify user's input.
 (b): the stop-word list the user wants to take as a basis;
      if no stop-word list is informed, the quality of the analysis will be
      considerably degraded.

Report to the user:
- The language of the Text
- The informed and verified corpusID
- The informed stop-word list; warn user about degraded results when no
  stop-word list is informed.

**Carry the verified corpusID forward** as `corpus_id` — it is written into
the Step 6.1 JSON contract so that Phase 3 can read it directly instead of
asking the user a second time.

---

## 3. Select Most Semantically Significant Terms (incList source)

### 3.1 Filter non-significant terms
Apply the following exclusion rules **by querying the TSV**, never by guessing:

**Rule A — Numerals:** exclude any term matching `^\d+[a-z]?$` (pure digits, year+letter
suffixes like `2021a`) found in the Terms.tsv candidate list, **and, separately, every
numeral-shaped token found by scanning the raw cleaned corpus TXT directly** — see the
NOTE and `apply_rule_a_corpus_scan` below for why both sources are required, not just one.

**NOTE (see this skill's internal version history for the full record).** Prior versions of
this rule only ever queried the Terms.tsv candidate list, never the raw corpus text. This
silently missed two distinct classes of numeral, surfaced only once live Cirrus output was
checked and still showed numerals a delivered stopword list was supposed to suppress:
1. **Below Voyant's own frequency cutoff.** Terms.tsv only lists candidates above a
   frequency threshold; Cirrus and the other live Voyant tools tokenize the *raw* corpus
   directly, with no such floor. A numeral used once or twice (a single-digit citation, an
   uncommon year) never appears in Terms.tsv at all and so could never be caught by a rule
   that only ever queries it.
2. **Structurally unmatchable by the original pattern.** Dotted subsection numbers (`2.1`,
   `3.1`, `4.2`) contain an internal period the original `^\d+[a-z]?$` regex has no
   provision for — these are excluded at *any* frequency, not just low ones.
   On a real corpus this was checked against, direct regex scanning found 103 distinct
   numeral-shaped tokens in the raw text; the TSV-only rule caught 41 of them exactly, with
   zero drift, and missed the other 62 (53 below-frequency-cutoff, 9 dotted/structurally
   unmatchable) — confirming both failure modes are real, not hypothetical. This fix has
   been verified against real corpus data; it has not yet been independently re-verified in
   every deployment of this skill.

**Rule B — Single/double character tokens:** exclude `len(term) <= 2`. **No context-check
exception path exists for this rule** — a meaningful short token (e.g. an acronym) has no
way to survive this cutoff, however significant it is to the corpus. This already caused a
real omission in this project's history (see `PEEL-Phase1-EpistemicThreats-Catalog.md`,
T-3.1) and remains open — deciding what should count as a legitimate exception is a
judgment call for the researcher, not something to resolve silently here.

**Rule C — Known non-significant categories:** build an exclusion set covering:
- Generic function words, filler verbs, discourse connectors, degree adverbs and adjectives
- Author names (identified from the TXT by reading it — see Rule D)
- Citation artifacts: `et`, `al`, `e.g`, `i.e`, `ibid`, and variants
- Unit abbreviations: `ml`, `m`, `km`, `l`, `ft`, `mi`, `mg`, `kg`, etc.

```python
import re

# Rule A -- TSV-candidate pass (original mechanism, unchanged, kept for
# the case where the TSV candidate is the only thing being classified,
# e.g. downstream code that already has a `terms` list and no corpus text
# handy). NOT sufficient on its own -- see apply_rule_a_corpus_scan below,
# which is now MANDATORY, not optional, per the fix note above.
def apply_rule_a(terms):
    return [t for t in terms if re.match(r'^\d+[a-z]?$', t)]

# Rule A -- raw-corpus scan (MANDATORY, run in addition
# to apply_rule_a above, never as a substitute for it). Tokenizes the raw
# cleaned corpus text directly -- the same text Cirrus and the other live
# Voyant tools actually operate on -- rather than relying on Terms.tsv's
# own frequency-filtered candidate list. Pattern extended from Rule A's
# `^\d+[a-z]?$` to `\d+(?:\.\d+)*[a-zA-Z]?` so it also matches dotted
# subsection numbers ("2.1", "3.1.2") that the original pattern could
# never match at any frequency. Bounded on both sides by a negative
# lookaround excluding word chars and periods, so it matches only a
# standalone numeral-shaped token, not digits embedded inside a longer
# alnum string (a DOI fragment, a footnote-call artifact) -- Phase 1
# Step 0 should already have stripped those from the cleaned TXT, but the
# boundary is defensive regardless. Verified against real data
# (mycorpus-CLEANED.txt): found 103
# distinct numeral-shaped tokens, of which the TSV-only apply_rule_a
# above independently matched exactly 41 with zero drift -- confirming
# this is a strict superset, not a divergent second definition.
NUMERAL_TOKEN_PATTERN = re.compile(r'(?<![\w.])(\d+(?:\.\d+)*[a-zA-Z]?)(?![\w.])')

def apply_rule_a_corpus_scan(corpus_text):
    """Returns the set of distinct numeral-shaped tokens (lowercased) found
    anywhere in the raw corpus text, regardless of Terms.tsv frequency
    membership. Union this with apply_rule_a's TSV-based result before
    building the final exclusion set -- do not use one in place of the
    other, since each catches cases the other structurally cannot."""
    return {m.lower() for m in NUMERAL_TOKEN_PATTERN.findall(corpus_text)}

# Rule B
def apply_rule_b(terms):
    return [t for t in terms if len(t) <= 2]

# Rule C -- mechanical sub-parts (stopwords, citation artifacts, unit
# abbreviations). Verified against real data, GarciaOkonkwo2025,
# 2026-07-14. Generic stopwords: reuse Step 1b's own stopword-loading
# logic (NLTK if available, embedded English/Portuguese fallback
# otherwise) rather than reimplementing it, so the two steps can never
# drift out of sync with each other.
CITATION_ARTIFACTS = {'et', 'al', 'e.g', 'i.e', 'ibid'}
UNIT_ABBREVIATIONS = {'ml', 'm', 'km', 'l', 'ft', 'mi', 'mg', 'kg'}

# NOTE (fixed, live evidence, another test corpus full-cycle test, 2026-07-31):
# a real run found 8 curly-apostrophe contractions (don't, doesn't, it's,
# i'm, let's, that's, you're, can't) silently surviving Rule C's stopword
# filter into top_n_terms. Root cause: stop.en.smart.txt stores contractions
# with the straight ASCII apostrophe, but real Voyant Terms.tsv exports use
# the curly/smart apostrophe (U+2019), matching the source text -- so
# `t.lower() in generic_stopwords` silently failed to match. This is the
# third live instance of this exact bug class in this file; Step 0.2 (v1.24)
# and Step 0.4b (v1.23) were each fixed once already, but Rule C's own
# mechanical check was never covered by either fix. Same normalization
# applied here now.
def apply_rule_c_mechanical(terms, generic_stopwords):
    def _norm(t):
        return t.lower().replace('’', "'")
    stopword_hits = [t for t in terms if _norm(t) in generic_stopwords]
    citation_hits = [t for t in terms if _norm(t) in CITATION_ARTIFACTS]
    unit_hits = [t for t in terms if _norm(t) in UNIT_ABBREVIATIONS]
    return {
        "stopwords": stopword_hits,
        "citation_artifacts": citation_hits,
        "unit_abbreviations": unit_hits,
    }

# Rule B/C -- possessive-form extension. NOTE (fixed, live evidence,
# the test book chapter verification, 2026-08-06): a possessive apostrophe-s
# form of an already-excludable token was checked against neither Rule B
# nor Rule C above, because Rule B tests raw length (a 1-character
# notation variable becomes 3 characters once possessive, `s` -> `s's`,
# clearing the <=2 cutoff) and Rule C's stopword set stores base forms
# only (`one`, not `one's`). On this real corpus, `one's` (25
# occurrences) and `s's` (12 occurrences -- the possessive of the
# formal-notation variable `S`, already excluded in its bare form by
# Rule B) both survived every Step 3.1 rule and reached the final
# selected-term set, discovered only when Step 3.5's WordNet
# disambiguation returned no synsets for either and the researcher asked
# why. Re-run against the same Terms.tsv after the fix: 9 possessive
# forms correctly excluded (`another's`, `everyone's`, `e's`, `h's`,
# `latter's`, `one's`, `p's`, `someone's`, `s's`) -- every one strips to
# a base already covered by Rule B or Rule C, confirmed by checking each
# stripped base against `generic_stopwords`/length directly, not
# asserted from the possessive form's own appearance.
def apply_rule_bc_possessive(terms, generic_stopwords):
    def _strip_possessive(term):
        t = term.replace('’', "'")
        if t.endswith("'s") and len(t) > 2:
            return t[:-2]
        return None

    hits = []
    for t in terms:
        base = _strip_possessive(t)
        if base is None:
            continue
        if (len(base) <= 2 or base in generic_stopwords
                or base in CITATION_ARTIFACTS or base in UNIT_ABBREVIATIONS):
            hits.append(t)
    return hits

# Rule C -- author-name sub-part, governed by Rule D below. NOTE (fixed,
# 2026-07-14, live evidence): every prior execution of this sub-part
# asserted a hardcoded set of names with no code checking any of them
# against the source text -- the exact "guessing" Rule D prohibits. This
# had a real cost: the cited author "watson" was missed by a hardcoded
# guess in the GarciaOkonkwo2025 run, passed this step unflagged,
# and was misresolved at Step 3.5 to the wrong WordNet sense (a DNA
# geneticist, not the cited philosopher) -- caught only later, by an
# unrelated gloss-check pass. This version performs the check Rule D
# actually specifies, cheaply: it extracts only the sentences containing
# each candidate term -- cost bounded by that term's own frequency, not
# corpus length -- instead of requiring a full re-read of the source text
# for every candidate. Same "scoped extraction, not full re-read"
# principle as Step 3.4c's CONTEXTS-consistency lever. Candidates for
# this check are proper-noun-shaped tokens in the term list (capitalized
# in the source TXT, lowercase in the TSV) -- adapt candidate detection
# to the corpus's own capitalization conventions if they differ.

def extract_term_contexts(term, corpus_text, max_excerpts=5):
    sentences = re.split(r'(?<=[.!?])\s+', corpus_text)
    pattern = re.compile(r'\b' + re.escape(term) + r'\b', re.IGNORECASE)
    hits = [s.strip() for s in sentences if pattern.search(s)]
    return hits[:max_excerpts], len(hits)

def check_author_name_candidates(candidate_terms, corpus_text):
    """Never asserts membership without evidence attached. Present the
    excerpts to the researcher before excluding a term as a citation
    artifact -- this function surfaces evidence, it does not replace
    judgment."""
    results = {}
    for term in candidate_terms:
        excerpts, total = extract_term_contexts(term, corpus_text)
        results[term] = {
            "occurrences": total,
            "excerpts": excerpts,
            "verdict": ("NOT FOUND IN TEXT" if total == 0
                        else "CANDIDATE -- inspect excerpts to confirm citation use"),
        }
    return results
```

**Rule D — Do NOT guess membership in any category.** If uncertain whether a term belongs
in a category, check the TXT file for context. For Rule C's author-name sub-part, this
means using `check_author_name_candidates` above and presenting its excerpts, not asserting
a list from memory or recall.

**Rule E — Philosophical Prose Supplement.** Apply this domain-specific stopword layer
*on top of* the base list (Rule C) before N-selection. It targets genre-infrastructure
vocabulary that escapes the SMART list but carries no argument-specific content in
philosophical or academic-humanities corpora. The list below is the current default;
append new terms discovered across runs.

```python
PHIL_PROSE_SUPPLEMENT = {
    # argumentative-connective verbs
    'account','base','bear','claim','come','correct','count','explain',
    'follow','form','give','happen','hold','look','make','matter','mean',
    'need','occur','offer','provide','raise','remain','respond','result',
    'say','show','suggest','tell','turn','work',
    # generic scaffold nouns
    'aspect','basis','body','fact','form','ground','idea','instance',
    'kind','means','number','occasion','part','piece','point','purpose',
    'result','role','sense','situation','step','target','term','thing',
    'time','type','way',
    # generic adjectives / degree adverbs not in SMART
    'complete','direct','entire','general','highly','inclusive',
    'individual','large','mainly','natural','necessary','obvious',
    'particular','perfect','possible','prior','proper','properly',
    'pure','simply','single','small','solid','solidly','specific',
    'standard','strong','strongly','substantial','sufficient',
    'total','typically','unique','various','weak','wide',
}
```

**Note on language-specific supplement lists.** The list above is calibrated for
English philosophical prose. For Portuguese or other languages, maintain a separate
supplement file and load it instead. Do not apply this English list to non-English
corpora.

Report to the user:
- Report results to user, including the count of terms removed by **each**
  rule (A, B, C — broken down by stopwords / citation artifacts / unit
  abbreviations / author names separately — and E); ask for confirmation
  or need for correction. For Rule C's author-name sub-part specifically,
  present the excerpts `check_author_name_candidates` returned, not just
  a count or an asserted list — this is the disclosure Rule D's
  discipline requires.
  NOTE (fixed, 2026-07-14): previously only Rule E's count was required
  to be reported here; Rules A/B/C had no disclosure requirement at all,
  including Rule C's most judgment-dependent sub-parts. See
  `PEEL-Phase1-EpistemicThreats-Catalog.md`, T-3.2.
  **NOTE: report Rule A's two sources separately, not merged into
  one silent count** — the TSV-candidate count (`apply_rule_a`) and the
  raw-corpus-scan count (`apply_rule_a_corpus_scan`), plus how many of
  the corpus-scan tokens were *not* already in the TSV-candidate set
  (i.e. the count that would have been silently missed under the
  earlier version of this rule). This mirrors the same
  fixed-not-narrated-count discipline as the rest of this note.

  **HONESTY NOTE (fixed, live evidence, Delacroix 2026 verification,
  2026-07-15).** When asking the researcher to confirm Rule D's author-name
  candidates, do not phrase the question as "confirm which to *accept* as
  genuine author-name artifacts" — a real live run showed this reads two
  opposite ways at once: "accept" meaning *confirm this is a citation
  artifact, therefore exclude it* (the intended technical sense) versus the
  plain-English reading *"yes, this term is fine, keep it."* The researcher
  answered "accept ai" meaning "ai is a significant term, don't throw it
  away" — the exact opposite of what would have happened had that answer
  been applied literally under the intended sense (excluding the corpus's
  own dominant topic term). Caught only because the consequence was
  surprising enough to prompt a clarifying question before acting — ask
  explicitly using **EXCLUDE / KEEP** language instead ("which of these
  should I EXCLUDE from significant-term selection as citation artifacts,
  and which should I KEEP"), which has no symmetrical double meaning.

Corrections:
- If corrections are needed, correct and re-run step 3.1.
  When no corrections are needed, proceed to step 3.2.

---

### 3.2 Select N by coverage threshold (primary criterion)
From the filtered significant candidates, compute the cumulative token
coverage and select the smallest N such that the top N terms account for
a **researcher-confirmed percentage of the total token mass** of the
filtered set. **Default rule-of-thumb: 50%** — but this is a rough
trade-off estimate, not a validated target, and the researcher confirms
it (or overrides it) explicitly every run, informed by what that trade-off
actually costs and buys for her specific corpus. See the HONESTY NOTE
below for why this changed from an unconfirmed constant to a disclosed,
researcher-set choice.

**HONESTY NOTE (fixed, 2026-07-14).** Earlier versions of this file
applied 50% as a bare constant, with no rationale given anywhere in the
specification and no mechanism for the researcher to see, question, or
adjust it — see `PEEL-Phase1-EpistemicThreats-Catalog.md`, T-3.6. Checked
against a real corpus (GarciaOkonkwo2025, 2026-07-14): coverage-N
grows sharply non-linearly with the threshold (N=20 at 25%, N=111 at 50%,
N=300 at 75% — each 25-point increase costs substantially more terms than
the last, because term frequency follows a long-tailed distribution). The
50%-75% band was also visibly more diluted with generic academic
vocabulary than the 25%-50% band, though not purely noise. None of this
proves 50% is correct for any given corpus; it shows the trade-off has a
real, corpus-specific shape that a bare constant hides from the
researcher entirely. Rather than replace one unexamined constant with a
different one, this step now computes the trade-off explicitly and asks
her to decide, informed rather than blind — the same standard Section~4
of the paper this project supports argues for: not risk elimination, but
a more informed basis for the researcher's own judgment.

```python
# Finds the smallest N whose cumulative coverage is >= 50% (matching
# the prose above: "the smallest N such that the top N terms account
# for 50%"). Sorts by RawFrequency descending explicitly first --
# never trusts the TSV's arrival order. See Implementation Notes #4
# and #5 (appendix) for the two bugs this guards against.
filtered_df = filtered_df.sort_values('RawFrequency', ascending=False).reset_index(drop=True)
total_tokens = filtered_df['RawFrequency'].sum()
filtered_df['cumulative'] = filtered_df['RawFrequency'].cumsum()
filtered_df['coverage'] = filtered_df['cumulative'] / total_tokens

def N_at(threshold, df=filtered_df):
    return int((df['coverage'] < threshold).sum()) + 1

def compute_coverage_options(df, reference_thresholds=(0.25, 0.50, 0.75), sample_size=8):
    """Computes N at each reference threshold and a sample of terms in
    each marginal band, so the researcher sees concretely what a
    different threshold would gain or lose -- not just abstract
    percentages. Verified against real data, GarciaOkonkwo2025,
    2026-07-14."""
    Ns = {t: N_at(t, df) for t in reference_thresholds}
    sorted_thresholds = sorted(reference_thresholds)
    bands = {}
    for i in range(len(sorted_thresholds) - 1):
        lo, hi = sorted_thresholds[i], sorted_thresholds[i + 1]
        band = df.iloc[Ns[lo]:Ns[hi]]
        bands[(lo, hi)] = {
            "count": len(band),
            "sample": band['Term'].head(sample_size).tolist(),
        }
    return Ns, bands

Ns, bands = compute_coverage_options(filtered_df)
```

**Report to the user, before proceeding:**

```
Coverage-threshold choice for term selection

Default rule-of-thumb target: 50% of total token mass. This corpus's
actual trade-off, computed directly (not estimated):

  Threshold   N (terms)   Sample of terms gained relative to the row above
  --------------------------------------------------------------------------
  25%         {Ns[0.25]}          (starting point)
  50%         {Ns[0.50]}         +{bands[(0.25,0.50)]['count']} terms, e.g.: {bands[(0.25,0.50)]['sample']}
  75%         {Ns[0.75]}         +{bands[(0.50,0.75)]['count']} terms, e.g.: {bands[(0.50,0.75)]['sample']}
  (sample = first N by frequency in each band, not the full list)

Growth is not linear -- each step costs substantially more terms than the
last. The 50%->75% band typically shows more generic/incidental
vocabulary mixed in with genuine content terms than the 25%->50% band.

Accept the 50% default, or specify a different threshold? Whatever is
chosen is recorded, with these same reference numbers, in the permanent
Phase1-results.md report -- this is not a one-time silent choice.
```

**Do not proceed to Step 3.2b until the researcher has responded.**

```python
# coverage_threshold: set from the researcher's response above (0.50 if
# she accepts the default). This variable, once set, is what N and
# top_n below are actually computed from -- not a hardcoded 0.50.
N = N_at(coverage_threshold)
top_n = filtered_df.iloc[:N]

# top_n_terms is defined here, immediately alongside top_n, so the two
# can never drift out of sync (see Implementation Notes #6, appendix).
top_n_terms = sorted(set(top_n['Term'].tolist()) | set(researcher_keywords))
# researcher_keywords: from Step 0.1b, empty list if the researcher didn't
# supply any -- unioned in here even on this automated path, since she
# supplies them before Step 1c's branch point is reached. See Step 6.3's
# `## Term selection provenance` note: this means the section is not pure
# "N/A -- automated selection used this run" whenever researcher_keywords
# is non-empty, even on an otherwise-fully-automated run.

# NOTE (fixed, 2026-07-14): top_n_terms can be larger than N once
# researcher_keywords are unioned in, but Step 3.4's verification checks
# coverage against top_n (pre-union), not this list -- meaning the
# reported coverage percentage previously described a strict subset of
# what actually proceeds downstream, undisclosed. See
# PEEL-Phase1-EpistemicThreats-Catalog.md, T-3.8. Disclosed explicitly now:
_n_added_keywords = len(set(top_n_terms) - set(top_n['Term'].tolist()))
if _n_added_keywords:
    print(f"NOTE: {_n_added_keywords} researcher-supplied keyword(s) not "
          f"already in the top-{N} coverage set were added, for "
          f"{len(top_n_terms)} terms total. The {coverage_threshold:.0%} "
          f"coverage figure describes the {N} coverage-selected terms, "
          f"not all {len(top_n_terms)} delivered here.")
```

**Permanent disclosure (mandatory every run, not only when the researcher overrides the default):** carry the chosen `coverage_threshold`, the resulting `N`, and the three reference-threshold numbers from the table above forward into Phase1-results.md's `## Term selection provenance` section (Step 6.3) — the same permanent-report discipline already used for the WordNet grounding tally and escalation-limits disclosures. A future reader of the finished Spyral Notebook should be able to see what trade-off was actually chosen and what the alternatives would have looked like, not just the final N with no context.

---

### 3.2b — POS Filter and Example-Vocabulary Detection

Run immediately after the N selected terms are known (post-3.2, pre-3.3). Two
sub-steps in a single pass; both flag candidates for **batch user routing** to
excList. Present all flags at once in one confirmation request — do not ask
separately for each term.

#### Sub-step 1 — POS filter

POS-tag every selected term and flag all **verbs** and **adverbs** that are not
members of the domain-specific exempt set. The rationale: in philosophical prose
the conceptual backbone lives almost entirely in nouns and specialised adjectives;
verbs and adverbs that survive to this stage are almost always argumentative
connectors that Rule E failed to intercept.

```python
# NOTE (fixed): a real test run found `nltk.pos_tag([lookup])` -- tagging
# a single word with no sentence context -- is a known-bad condition for
# gerund/participle ambiguity. Confirmed concrete false positives:
# "learning" and "understanding" (core content nouns, tagged as verbs),
# "taking" (thematically central -- "Taking Responsibility" is a section
# title -- tagged as verb), and "sphere" (mistagged as an adverb, not
# even linguistically plausible). All four would have been wrongly
# stripped from incList. Fixed by tagging the term inside a real sentence
# sampled from the actual corpus text, not alone -- standard practice for
# exactly this class of tagger error. Sampled from multiple occurrences
# and majority-voted, since a single sampled sentence could itself be an
# atypical usage.
#
# NOTE (fixed, 2026-07-14): the HONESTY NOTE previously here claimed this
# fix "could not be executed against a real NLTK tagger... treat this as
# somewhat less rigorously verified than the rest of this file until it's
# actually run." That was true when written, but went stale: the
# GarciaOkonkwo2025 live run (260713b) executed this exact code
# against the real NLTK tagger and produced genuine Penn Treebank tags
# (VBG, VB, VBZ, VBN), not the heuristic-mode fallback format -- 13 real
# verb/adverb flags surfaced correctly. The note was never updated after
# that run. See PEEL-Phase1-EpistemicThreats-Catalog.md, T-3.9 -- a live
# instance of exactly the status-drift problem
# PEEL3-phase1-execution-status.md exists to prevent, found this time
# inside the skill file's own documentation. This fix is CODE-VERIFIED
# against real data, not merely logically checked.

import re

def _sample_sentences_with_term(corpus_text, term, max_samples=5):
    """Finds up to max_samples real sentences in the corpus containing
    this term as a whole word, case-insensitive."""
    sentences = re.split(r'(?<=[.!?])\s+', corpus_text)
    pattern = re.compile(rf'\b{re.escape(term)}\b', re.IGNORECASE)
    matches = [s for s in sentences if pattern.search(s)]
    return matches[:max_samples]

def _tag_term_in_context(term, corpus_text, pos_mode):
    """Tags a term using real sentence context sampled from the corpus,
    majority-voting across multiple occurrences rather than trusting a
    single sampled sentence. Falls back to isolated tagging only if no
    real occurrence can be found (should be rare, since the term came
    from this same corpus's own frequency list)."""
    samples = _sample_sentences_with_term(corpus_text, term)
    if not samples or pos_mode != 'nltk':
        # heuristic mode has no sentence-context capability -- same
        # fallback as before, already disclosed separately
        return None
    votes = []
    for sentence in samples:
        tokens = nltk.word_tokenize(sentence)
        tagged = nltk.pos_tag(tokens)
        match = next((t for w, t in tagged if w.lower() == term.lower()), None)
        if match:
            votes.append(match)
    if not votes:
        return None
    from collections import Counter
    return Counter(votes).most_common(1)[0][0]
```

**Read the raw corpus text once, at the start of this step, for sampling**
(no earlier step in this file keeps it loaded as a variable -- Steps
1-3.2 all work from the Voyant TSV exports, not the raw text directly):

```python
import glob
_txt_files = glob.glob('/mnt/user-data/uploads/*.txt')
corpus_text = ''
if _txt_files:
    with open(_txt_files[0], 'r', encoding='utf-8') as f:
        corpus_text = f.read()
```

```python
# Technical verbs / adverbs that ARE conceptually significant — keep these
EXEMPT_VERBS   = {
    'defer','exclude','preempt','justify','testify','believe','know',
    'defeat','aggregate','transmit','require','claim','affirm','assert',
    'infer','entitle','undermine','override',
}
EXEMPT_ADVERBS = {
    'epistemically','rationally','doxastically','propositionally',
    'normatively','defeasibly',
}

# Embedded fallback (used only if the NLTK tagger corpus is not already
# present locally -- no download is attempted, same reasoning as the
# Step 1b stopword fix). Lower recall than a real statistical tagger by
# design -- it is a deliberately disclosed degradation, not a silent one.
_COMMON_VERBS = {
    'is','are','was','were','be','been','being','have','has','had',
    'do','does','did','make','made','get','got','go','went','gone',
    'take','took','taken','see','saw','seen','come','came','know',
    'knew','known','give','gave','given','find','found','think',
    'thought','tell','told','become','became','show','showed','shown',
    'leave','left','feel','felt','put','bring','brought','begin',
    'began','begun','keep','kept','hold','held','write','wrote',
    'written','stand','stood','hear','heard','let','mean','meant',
    'set','meet','met','run','pay','paid','sit','sat','speak','spoke',
    'spoken','lie','lay','lain','lead','led','read','grow','grew',
    'grown','lose','lost','fall','fell','fallen','send','sent','build',
    'built','understand','understood','draw','drew','drawn','break',
    'broke','broken','spend','spent','cut','rise','rose','risen',
    'drive','drove','driven','buy','bought','wear','wore','worn',
    'choose','chose','chosen','seek','sought','throw','threw','thrown',
    'catch','caught','deal','dealt','win','won','offer','remain',
    'suggest','raise','base','reduce','establish','include','involve',
    'require','allow','add','continue','change','consider','appear',
    'turn','move','live','believe','happen','provide','claim',
}
_ADVERB_NOT_EXCEPTIONS = {
    'family','supply','apply','reply','imply','rally','bully','jelly',
    'belly','folly','ally','only','early','homely','lovely','lonely',
    'friendly','likely','elderly','ugly','holy','silly','july',
}

def _heuristic_tag(lookup):
    w = lookup.lower()
    if w.endswith('ly') and len(w) > 4 and w not in _ADVERB_NOT_EXCEPTIONS:
        return 'adverb'
    if w in _COMMON_VERBS:
        return 'verb'
    return None

_pos_mode = None
try:
    import nltk
    nltk.data.find('taggers/averaged_perceptron_tagger_eng')
    _pos_mode = 'nltk'
except (ImportError, LookupError):
    _pos_mode = 'heuristic'

pos_flags = []
_term_pos_tags = {}  # every term's tag, reused by Step 3.5 to restrict
                      # WordNet comparisons to the correct part of speech
for term in top_n_terms:
    # Strip wildcard suffix before tagging
    lookup = term.rstrip('*').rstrip('"').strip('"')
    if _pos_mode == 'nltk':
        tag = _tag_term_in_context(lookup, corpus_text, _pos_mode)
        if tag is None:
            # No real occurrence found in the sampled text (should be
            # rare -- term came from this corpus's own frequency list) --
            # fall back to isolated tagging as a last resort, disclosed.
            tag = nltk.pos_tag([lookup])[0][1]
            tag = f'{tag} (isolated -- no context sample found)'
        _term_pos_tags[lookup] = tag
        is_verb   = tag.startswith('VB') and lookup not in EXEMPT_VERBS
        is_adverb = tag.startswith('RB') and lookup not in EXEMPT_ADVERBS
    else:
        guess = _heuristic_tag(lookup)
        tag = f'heuristic:{guess}' if guess else 'heuristic:none'
        _term_pos_tags[lookup] = tag
        is_verb   = guess == 'verb'   and lookup not in EXEMPT_VERBS
        is_adverb = guess == 'adverb' and lookup not in EXEMPT_ADVERBS
    if is_verb or is_adverb:
        pos_flags.append((term, tag, 'verb' if is_verb else 'adverb'))

if _pos_mode == 'heuristic':
    print("WARNING: NLTK POS tagger data not available locally -- the "
          "POS filter ran in DEGRADED HEURISTIC MODE (suffix + common-"
          "verb-list matching, lower recall than the statistical "
          "tagger). This must be disclosed to the researcher in the "
          "Step 3.2b report below, not silently absorbed -- some "
          "genre-scaffold verbs/adverbs may have been missed and will "
          "survive into incList for the researcher to catch manually.")
```

**Carry this forward** into the Phase1-results.md report, into the same
permanent `## Environment fallbacks used` section as Step 1b's
stopword-source disclosure (not a new section per fallback — one place
the researcher can check everything that ran in a non-default mode):
record `_pos_mode` and, if `'heuristic'`, the same lower-recall caveat
given in the in-session report. Mandatory every run, same as Step 1b
and Step 3.5 — not only when the mode looks unusual.

#### Sub-step 2 — Example-vocabulary detection

Flag terms whose occurrences are concentrated (> 70 %) inside illustration
passages introduced by discourse markers of hypothetical or concrete example.
These terms are frequent because a single thought experiment recurs, not because
they are conceptually central.

```python
import re
from collections import Counter

EXAMPLE_MARKERS = re.compile(
    r'\b(suppose|consider|imagine|for example|for instance|let us|'
    r'let me|in this case|in the following case|call (?:her|him|it)|'
    r'assume that|picture a|think of)\b',
    re.IGNORECASE,
)

# NOTE (fixed, 2026-07-14): this line previously read
# `re.split(r'(?<=[.!?])\s+', txt)` -- `txt` is never defined anywhere in
# Step 3.2b; Sub-step 1 above loads and uses `corpus_text` instead. This
# would raise a NameError if run exactly as written. The real
# GarciaOkonkwo2025 live run (260713b) silently used `corpus_text`
# throughout, without that correction ever being fed back into this file
# -- unlike every other bug this file has found, which gets a disclosed
# NOTE (fixed) comment. See PEEL-Phase1-EpistemicThreats-Catalog.md,
# T-3.10.
sentences = re.split(r'(?<=[.!?])\s+', corpus_text)
example_sents = [s for s in sentences if EXAMPLE_MARKERS.search(s)]

all_counts  = Counter(w.lower() for s in sentences     for w in re.findall(r'\b\w+\b', s))
ex_counts   = Counter(w.lower() for s in example_sents for w in re.findall(r'\b\w+\b', s))

example_flags = []
for term in top_n_terms:
    lookup = term.rstrip('*').strip('"').lower()
    total  = all_counts.get(lookup, 0)
    in_ex  = ex_counts.get(lookup, 0)
    if total >= 3 and in_ex / total > 0.70:
        example_flags.append((term, in_ex, total,
                               f"{in_ex/total:.0%} of occurrences in example passages"))
```

#### Reporting and user confirmation

**If Step 3.2b's POS sub-step ran in heuristic mode** (no NLTK tagger data
locally available), say so explicitly, first, before presenting either
flag list — this is a disclosure the researcher needs in order to weigh
how much to trust the "unflagged means safe" assumption, not a footnote:

```
NOTE: NLTK's statistical POS tagger was not available in this session.
The verb/adverb filter below ran in a degraded heuristic mode (suffix
patterns + a common-verb list) instead. This catches the clearest cases
but has lower recall than the full tagger — some genre-scaffold verbs
or adverbs may NOT have been flagged and could still be sitting in the
candidate list below. Please scan the unflagged terms a bit more
carefully than usual before confirming.
```

Then present both flag lists together in one block:

```
POS filter — verbs / adverbs flagged as likely genre-scaffold:
  raise        [VBZ]              verb
  respond      [VBP]              verb
  provide      [VB]               verb
  simply       [RB]               adverb
  typically    [RB]               adverb
  ...

  -- or, in heuristic mode --
  raise        [heuristic:verb]   verb
  simply       [heuristic:adverb] adverb
  ...

Example-vocabulary — terms concentrated in illustration passages:
  red          (10/12 = 83% in example passages)
  widgets      ( 8/9  = 89% in example passages)
  ...

Default routing for all flagged terms: excList.
Override any term to incList by naming it explicitly.
Confirm, or list exceptions:
```

Do not proceed to Step 3.3 until the user has responded.


---

### 3.3 Cross-check with Zipf elbow (secondary criterion)
Independently compute the Zipf elbow — the point where the frequency/rank curve flattens —
and compare it to N from 3.2.

**NOTE (fixed):** a real test run found this spikes at tie-block
*boundaries*, not real distributional elbows, on corpora where a large
share of terms are hapax legomena (frequency 1) — a small, long-tailed
corpus produced a 150% divergence purely from this artifact. Root
cause: the raw per-rank second-difference-of-log-frequency detector
treats the transition into a long flat tie-plateau (e.g. freq=2→freq=1,
repeated across dozens of ranks) as a huge curvature spike, since
`np.diff` on a flat run followed by a drop produces exactly that shape
regardless of whether a real elbow exists there. Fixed by collapsing
ties first — computing the elbow on the curve of *distinct* frequency
values only, each mapped back to the rank where it first occurs, so a
long plateau of identical values contributes one point, not one point
per rank:

```python
import numpy as np
freqs = filtered_df['RawFrequency'].values
ranks = np.arange(1, len(freqs) + 1)

# Collapse ties: keep only the first rank at which each distinct
# frequency value occurs, removing tie-plateau boundary artifacts
distinct_freqs, distinct_start_ranks, seen = [], [], set()
for f, r in zip(freqs, ranks):
    if f not in seen:
        seen.add(f)
        distinct_freqs.append(f)
        distinct_start_ranks.append(r)
distinct_freqs = np.array(distinct_freqs)
distinct_start_ranks = np.array(distinct_start_ranks)

if len(distinct_freqs) >= 3:
    log_distinct = np.log(distinct_freqs)
    second_diff = np.diff(np.diff(log_distinct))
    elbow_idx = np.argmax(second_diff) + 2
    elbow_rank = int(distinct_start_ranks[min(elbow_idx, len(distinct_start_ranks) - 1)])
else:
    elbow_rank = len(freqs)  # too few distinct values for a meaningful elbow

zipf_N = elbow_rank
```

If more than half the filtered terms are hapax (frequency 1), disclose
this explicitly alongside the two N values — it means this corpus's
long tail is unusually flat, and the elbow cross-check is inherently
less informative here regardless of which method computes it, not just
a number to report without context.

Report both values to the user. If they are close (within ~10%), proceed with the coverage N.
If they diverge significantly, report the divergence and ask the user to decide.

---

### 3.3b — Multi-tool corroboration for borderline terms (tertiary criterion)

**Purpose.** Coverage-N (3.2) and the Zipf elbow (3.3) are both derived from
the same underlying signal — token frequency — and can agree with each
other while both under-weighting a term that is genuinely significant by
other measures. This step checks candidates just below the coverage-N
cutoff against two structurally different Voyant signals — phrase-anchoring
and collocate concentration — neither a frequency derivative — and surfaces
any the frequency-only criteria would otherwise silently drop.

**Scope, deliberately bounded.** Only terms ranked N+1 through
N+`RESCUE_WINDOW` (default 15, adjust per corpus size) are checked, not the
full remaining vocabulary — checking the entire tail would reproduce the
unbounded-cost problem Step 3.1's Rule D redesign was fixed to avoid.

**Step order note.** This step deliberately runs *after* Step 3.2b, not
before — Step 3.2b's POS/example-vocabulary filtering is not re-run for the
whole list here. Any term this step's researcher confirms for addition gets
its own small, separate POS-check below (reusing Step 3.2b's own tagging
logic), rather than restructuring existing step order. This means Step
3.2's own sequencing gap (coverage-N confirmed only later, at Step 3.3) is
not fixed by this addition — it remains open, tracked separately in
`PEEL-Phase1-EpistemicThreats-Catalog.md`, T-3.7.

#### Lever 1 — Phrase-anchoring (uses data already collected at Step 1b; no new researcher cost)

**NOTE (fixed, live evidence, another test corpus full-cycle test, 2026-07-31):**
a real run read the *raw* Step 1.2 Phrases TSV here instead of Step 1b's own
boundary-trimmed, deduplicated `candidates` DataFrame -- the parameter name
`phrases_df` and the docstring's "Phrases.tsv already exists by this point"
both read ambiguously enough to point at the raw file, and that is exactly
what got consulted. This reintroduces the boundary-stopword-padded and
n-gram-window-fragment noise Step 1b exists to remove: a raw bigram like
"the possibility" or "its conclusion" reads as a real phrase anchor here,
when Step 1b's own trimming would have stripped the boundary stopword and,
since a single remaining word doesn't qualify as a multi-word phrase,
dropped the row entirely. Confirmed concretely: this fabricated phrase-anchor
evidence for two terms in a live run, both of which the researcher then kept
in `top_n_terms` on evidence that was not real, caught and corrected only
several steps later. **Fixed by taking Step 1b's own `candidates` DataFrame
explicitly, by name, never the raw Phrases TSV** -- the parameter is now
named so it cannot be satisfied by the raw file, and the column names match
`candidates`' own (`trimmed`, `final_freq`), not the raw TSV's (`Phrase`,
`RawFrequency`).

```python
import re

def check_phrase_anchoring(candidate_terms, step1b_candidates_df, min_freq=3):
    """A candidate is phrase-anchored if it appears as a component word of
    any row in Step 1b's own trimmed `candidates` DataFrame, at or above
    min_freq. Zero additional data collection required -- `candidates`
    already exists by this point. Do NOT pass the raw Phrases TSV here --
    see the NOTE above for the live-run evidence of why that fabricates
    phrase-anchor evidence. Verified against real data,
    GarciaOkonkwo2025, 2026-07-14; the raw-vs-trimmed distinction
    verified against real data, another test corpus, 2026-07-31."""
    results = {}
    for term in candidate_terms:
        matches = step1b_candidates_df[step1b_candidates_df['trimmed'].str.contains(
            rf'\b{re.escape(term)}\b', case=False, regex=True, na=False)]
        strong = matches[matches['final_freq'] >= min_freq]
        results[term] = {
            "anchored": len(strong) > 0,
            "best_phrase": strong.sort_values('final_freq', ascending=False).iloc[0]['trimmed'] if len(strong) else None,
            "phrase_freq": int(strong.sort_values('final_freq', ascending=False).iloc[0]['final_freq']) if len(strong) else 0,
        }
    return results
```

#### Lever 2 — Collocate concentration (requires a new, narrowly-scoped Collocates export)

**HONESTY NOTE.** Threshold below (`min_max_count=3`) is derived from one
real corpus (GarciaOkonkwo2025, 2026-07-14) — confirmed-significant
terms all showed a max collocate count of 3 or higher with at least one
partner; two known-generic/uncertain test cases (`particular`,
`understanding`) both topped out at 2. Treat as a current default, not a
validated general threshold, until checked against a second corpus — same
discipline as Rule E's supplement list and the seed-list size guidance
elsewhere in this file.

**Data collection, scoped to this step's candidates only** (not the whole
vocabulary — same cost discipline as Lever 1): export CorpusCollocates for
exactly the N+1..N+RESCUE_WINDOW candidate terms, context window 5, query
as a single comma-separated string (do not use the array form — see the
CONTEXTS query-format finding elsewhere in this file; unconfirmed whether
CorpusCollocates shares that behavior, and untested is not the same as
safe).

```python
# NOTE (fixed, live evidence, 2026-07-14): exact-string column renaming
# against this tool's export broke on a Portuguese-locale header
# (`Co-ocorrência`) even when the rename dict's literal text looked
# correct -- an accented-character encoding mismatch, not a logic error.
# Same failure class as T-1.1/T-1.9 (this project's recurring
# locale-dependent column-naming problem), now confirmed for
# CorpusCollocates specifically, not just Phrases and Terms. Fixed by
# positional renaming, which does not depend on matching the literal
# header text at all.
collocates_df.columns = ['Term', 'TermFreq', 'ContextTerm', 'ContextTermCount']

def check_collocate_concentration(collocates_df, min_max_count=3):
    """A candidate is collocate-concentrated if its strongest single
    collocate partner co-occurs with it at least min_max_count times.
    Verified against real data, GarciaOkonkwo2025, 2026-07-14."""
    results = {}
    for term, group in collocates_df.groupby('Term'):
        top = group.sort_values('ContextTermCount', ascending=False).iloc[0]
        results[term] = {
            "concentrated": bool(top['ContextTermCount'] >= min_max_count),
            "strongest_partner": top['ContextTerm'],
            "max_count": int(top['ContextTermCount']),
        }
    return results
```

#### Lever 3 — Distribution spread: DESIGNED, NOT VALIDATED

**Do not offer this as available until tested against real data**, same
gating discipline this file already applies to Step 3.4c's Collocates
lever. The Terms TSV's `Distributions` column (relative frequency across
ten document segments) could in principle distinguish a term whose
frequency is earned by persistent relevance from one concentrated in a
single passage — but this has not been checked against any real corpus,
unlike Levers 1 and 2 above. This subsection exists to record the design,
not to be executed.

#### Reporting and confirmation

Present rescued candidates in one batched table, never auto-added:

```
Candidates below coverage-N showing independent significance signals:

  term          rank   phrase anchor              collocate strength
  ------------------------------------------------------------------
  <term>        N+3    "term phrase" (freq 4)      partner (count 5)
  ...

None of these are added automatically. Confirm which, if any, to add to
top_n_terms, and which you'd rather leave excluded.
```

**Do not proceed to Step 3.4 until the user has responded.**

#### POS-check for confirmed additions only

Any term the researcher confirms adding here bypassed Step 3.2b's
POS/example-vocabulary filter (see the step-order note above). Before
folding a confirmed term into `top_n_terms`, run it through the same check,
reusing Step 3.2b's own `_tag_term_in_context`/`_heuristic_tag` functions
and `EXEMPT_VERBS`/`EXEMPT_ADVERBS` sets rather than reimplementing them —
applied only to this small, confirmed set, not the whole candidate window:

```python
for term in confirmed_rescued_terms:
    lookup = term.rstrip('*').rstrip('"').strip('"')
    if _pos_mode == 'nltk':
        tag = _tag_term_in_context(lookup, corpus_text, _pos_mode) or nltk.pos_tag([lookup])[0][1]
        is_verb   = tag.startswith('VB') and lookup not in EXEMPT_VERBS
        is_adverb = tag.startswith('RB') and lookup not in EXEMPT_ADVERBS
    else:
        guess = _heuristic_tag(lookup)
        is_verb   = guess == 'verb'   and lookup not in EXEMPT_VERBS
        is_adverb = guess == 'adverb' and lookup not in EXEMPT_ADVERBS
    if is_verb or is_adverb:
        print(f"NOTE: '{term}' was confirmed via Step 3.3b but flags as "
              f"{'verb' if is_verb else 'adverb'} under Step 3.2b's own "
              f"criteria -- confirm this override is intentional before adding.")
```

---

### 3.4 Verify
```python
# NOTE (fixed): the previous version of this check was
# `assert len(top_n) == N`, but N was DEFINED as len(top_n) two lines
# earlier in 3.2 -- that assertion could never fail and verified
# nothing. This version independently recomputes the coverage mass
# for the selected N and for N-1, and checks both halves of the
# actual claim made in 3.2: that N achieves >=50% coverage, AND that
# N is the *smallest* such N (i.e. N-1 terms do not already reach it).
covered_mass = filtered_df['RawFrequency'].iloc[:N].sum() / total_tokens
assert covered_mass >= 0.50, (
    f"Top {N} terms cover only {covered_mass:.1%} of token mass, "
    f"expected >=50%"
)
if N > 1:
    prev_mass = filtered_df['RawFrequency'].iloc[:N-1].sum() / total_tokens
    assert prev_mass < 0.50, (
        f"N={N} is not minimal: top {N-1} terms already cover "
        f"{prev_mass:.1%} of token mass"
    )
print(f"Selected N={N} terms covering {covered_mass:.1%} of filtered "
      f"token mass (minimal N confirmed)")
print(f"Zipf elbow cross-check: {zipf_N} terms")
```

---

## Term selection provenance (mandatory, every run)

**REMOVED, 2026-07-31 (researcher-requested skill edit, live full-cycle
test): the researcher-seeded selection path (formerly Step 3s, comprising
seed intake, two sanity-check passes, a stem-family sweep, an optional
proper-name sweep, an abandoned lexname sweep, a WordNet similarity sweep,
batched confirmation, and a provenance tally) has been removed entirely.**
Term selection is automated-only now — see Step 1c above, which no longer
presents a path choice. This section is what remains of the old 3s.9's
mandatory disclosure requirement, stripped of the seed/expansion-sweep
provenance tags that no longer apply, since `researcher_keywords` (Step
0.1b) is independent of which selection path existed and is still tracked.

```python
selection_provenance = {}
for k in researcher_keywords:
    selection_provenance[k] = 'researcher-keyword'
# researcher_keywords: from Step 0.1b, empty list if none were supplied.

from collections import Counter
provenance_tally = Counter(selection_provenance.values())
print("Term selection provenance:")
print(f"  researcher-keyword: {provenance_tally.get('researcher-keyword', 0)}")
```

**Carry this tally forward** into the Phase1-results.md report as a
permanent `## Term selection provenance` section (mandatory every run —
when `researcher_keywords` is empty, this section states "N/A — automated
selection used this run"; when non-empty, it instead reports the
`researcher-keyword` count against the automated run, rather than falsely
claiming pure N/A — so its content is never ambiguous between "no
keywords supplied" and "this version doesn't track it," the same
discipline already applied to `## WordNet grounding`, `## Environment
fallbacks used`, `## Escalation verification limits`, and `## Cluster
assignment grounding`). This is process metadata, not term/cluster data
Phase 2/3 need to branch on, so it belongs in the MD report only, not the
five-key JSON contract (Step 6.1 is unchanged).

Proceed to Step 3.4b.

---

### 3.4b — WordNet precondition check (mandatory, before Step 3.5)

**NOTE (fixed):** the previous precondition here only checked whether a
data path existed, and only softly — "ask the user to upload
`wordnet.zip`" — with no explicit stop, and no coverage at all for the
WordNet *library* itself being absent, as opposed to just its data. This
is not hypothetical: a real test run hit exactly that case (`nltk` not
installed at all, not just missing corpora) and, with no protocol to
follow, improvised a pure-Python WordNet reader on the spot — the same
shape of failure that Step 0.9 exists to prevent for Python generally,
except here it governs a specific semantic decision (which *sense* of a
term gets used for categorization), arguably higher stakes than the
incident that originally motivated Step 0.9.

Actually attempt to use WordNet, not just check that a path exists —
this distinguishes "library not installed" from "data missing or
corrupted," which need different responses:

```python
def check_wordnet_availability():
    try:
        from nltk.corpus import wordnet as wn
    except ImportError as e:
        return False, f"WordNet library (nltk) is not installed at all: {e}"
    try:
        test_synsets = wn.synsets('test')
        if not test_synsets:
            return False, ("nltk is installed, but wn.synsets('test') "
                            "returned empty -- WordNet data is missing, "
                            "incomplete, or corrupted")
    except LookupError as e:
        return False, f"nltk is installed, but WordNet data is missing or not found: {e}"
    return True, None

wordnet_available, wordnet_failure_reason = check_wordnet_availability()
```

**If `wordnet_available` is `False`: STOP.** Do not proceed to Step 3.5
or any later step. Never silently substitute an improvised
reimplementation — this is exactly the failure this check exists to
prevent, and it applies here with the same force it applies to Step 0.9.
Report the specific reason (library absent vs. data absent — they need
different fixes) and offer the researcher these options, without
picking one on their behalf:

```
WordNet is not usable in this session: <wordnet_failure_reason>

1. If this is a DATA problem (library present, data missing): upload
   `wordnet.zip` and I will re-check.
2. If this is a LIBRARY problem (nltk not installed at all): switch to
   an environment confirmed to have nltk installed (e.g. claude.ai or
   Claude Desktop), and pause here.
3. Proceed fully unverified, explicitly labeled as such: every term's
   sense assignment in this run must carry a visible, standalone label
   — "UNVERIFIED — no WordNet library was available to confirm this
   sense" — in the delivered report and in every place a synset would
   normally be reported, not folded into a footnote.
4. You may explicitly request an alternate WordNet implementation
   (e.g. a pure-Python reader). Only if you ask for this directly —
   never offered as a silent default. If chosen, the actual generated
   code must be delivered as a real file, labeled "unaudited, generated
   on the spot for this session, not part of the tested skill, requires
   independent review before being trusted" — the same standard applied
   to every other disclosed fallback in this skill.
```

Record whichever option is chosen, and why, in the session log and in
the permanent `## Environment fallbacks used` section of the delivered
report — under a heading naming this specific gap, not folded into the
existing stopword/POS-tagger fallback entries, since this is a different
kind of gap (a missing capability entirely, not a designed degraded mode).

### 3.4c — Disambiguation bypass via confirmed context (optional)

**Runs after Step 3.4b and before Step 3.5.**

**Motivation.** Step 3.5's `disambiguate()` runs once per term in
`top_n_terms`, regardless of whether the term's sense is already obvious
from context no algorithm was needed to establish. An Ngram containing
an ambiguous term ("epistemic authority") fixes that term's sense by
virtue of the collocation itself — a human glancing at the Phrases
export sees this in seconds, no WordNet gloss-comparison required. This
step lets that observation skip Step 3.5's algorithm entirely for the
terms it covers, instead of running the full context-overlap/hypernym-
domain comparison and then discarding a foregone conclusion.

**This is a targeted bypass, not a replacement for Step 3.5.** It only
ever covers the subset of `top_n_terms` a researcher-flagged Ngram or a
confirmed collocate actually touches — every other term proceeds to Step
3.5 exactly as before.

#### (1) Researcher-flagged Ngrams — ready to use now

**NOTE (fixed, live evidence, another test corpus full-cycle test, 2026-07-31):**
this prompt previously said "glance at your exported Phrases/N-grams table
(from Step 1.2's TSV)" — read literally, and read live, this points at the
*raw* Phrases export, not Step 1b's boundary-trimmed `candidates` output.
The raw file still contains boundary-stopword-padded and n-gram-window
fragments Step 1b already filtered out (see Lever 1's own NOTE above for
the concrete evidence: this exact ambiguity fabricated phrase-anchor
evidence for two terms in a live run). Reworded below to name Step 1b's
`candidates` output explicitly.

Ask the researcher once, before this step's code runs:

> Optional: glance at Step 1b's confirmed candidate phrase list (the
> boundary-trimmed, deduplicated output — **not** the raw Phrases/N-grams
> TSV, which still contains fragments Step 1b already filtered out). If
> any phrase there is, in your judgment, unambiguous in this corpus's
> context (e.g. "epistemic authority", "delegated reading"), list the
> ones you want me to treat as already-disambiguated. This is optional
> and takes as little or as much time as you want to give it — an empty
> list is a valid answer.

For every Ngram she supplies:

```python
def apply_ngram_bypass(researcher_flagged_ngrams, top_n_terms):
    """Marks any top_n_terms term that is a component word of a
    researcher-flagged Ngram as context-fixed, no disambiguate() call.
    Returns {term: (source, evidence)} for reporting."""
    context_fixed = {}
    for ngram in researcher_flagged_ngrams:
        words = ngram.lower().split()
        for term in top_n_terms:
            lookup = term.rstrip('*').rstrip('"').strip('"').lower()
            if lookup in words and lookup not in context_fixed:
                context_fixed[lookup] = ("researcher-Ngram", ngram)
    return context_fixed
```

Her flagging an Ngram IS the confirmation. Never re-ask her to confirm a
term this step already fixed.

#### (2) Voyant Collocates-suggested bypass — designed, not yet validated (see HONESTY NOTE below)

**Do not offer this as available until the HONESTY NOTE's precondition
is met.** If Collocates data for `top_n_terms` has been collected (see
the Data Collection Notebook's Collocates cell) and a concrete
"distinctively specific" strength criterion has been derived from real
data for this corpus, terms whose strongest collocate clears that
criterion are *suggested*, never auto-accepted:

```
The following terms have a single, distinctively strong collocate in
this corpus, which may already fix their sense:

  term          strongest collocate    (strength)
  ------------------------------------------------
  <term>        <collocate>            <score>
  ...

Confirm which of these I should treat as already-disambiguated (skipping
Step 3.5's WordNet check for that term), and which you'd rather I check
normally. An empty confirmation is valid — every term then proceeds to
Step 3.5 as usual.
```

Only researcher-confirmed terms are marked context-fixed; anything not
confirmed (including anything not answered) proceeds to Step 3.5
unchanged — an automated suggestion, never a silent acceptance.

**HONESTY NOTE.** This lever is designed, not validated. This session's
live Voyant testing confirmed Correlations' full parameter shape
(`query`, `sort`, `dir`, `withDistributions`, `minInDocumentsCountRatio`,
`columns`, `termColors`, `stopList`, `docId`, `docIndex`) against a real
corpus — Collocates' parameter shape was never checked, and no concrete
numeric threshold for "distinctively specific" has been derived from
real data (the equivalent of the Zipf-elbow cross-check or the
seed-list size guidance elsewhere in this file — both grounded in an
actual run, not asserted in the abstract). Do not present lever (2) to
the researcher as available until: (a) a real Collocates export has been
inspected for this corpus or a comparable one, and (b) a strength
criterion has been derived from it the same way the Zipf elbow was.
Until then, this subsection exists to record the design, not to be
executed.

#### (3) CONTEXTS-derived consistency check — validated against a real corpus

**Unlike lever (2), this lever is validated, not just designed** — it
was demonstrated against a real corpus (GarciaOkonkwo2025), not merely
reasoned about in the abstract.

**Mechanism.** Given a Voyant CONTEXTS export scoped to `top_n_terms ∪
selected_phrases` (see the code note below for the query syntax), check
whether a term's *immediate* neighbor word — the last word of its Left
column, or the first word of its Right column — is the *same* word
across every occurrence of that term in the corpus. Total consistency
across enough occurrences to mean something is itself real, disclosable
evidence that the term's sense is fixed by that neighbor, without
needing an unvalidated statistical threshold the way lever (2) does:

```python
def contexts_consistency_bypass(contexts_export_rows, min_occurrences=3,
                                 consistency_threshold=1.0):
    """
    contexts_export_rows: list of (left, term, right) tuples from a
    CONTEXTS export scoped to top_n_terms ∪ selected_phrases.
    For each term with at least `min_occurrences` rows, checks whether a
    single immediate neighbor (last word of Left, or first word of
    Right) accounts for `consistency_threshold` (default 1.0 -- every
    single occurrence agrees) of its occurrences. Returns candidates for
    the researcher to confirm -- never auto-accepted.
    """
    from collections import defaultdict, Counter
    by_term = defaultdict(list)
    for left, term, right in contexts_export_rows:
        by_term[term.lower()].append((left, right))

    candidates = {}
    for term, occurrences in by_term.items():
        n = len(occurrences)
        if n < min_occurrences:
            continue  # too few occurrences for consistency to mean anything
        left_neighbors = Counter(l.strip().split()[-1].lower() for l, r in occurrences if l.strip())
        right_neighbors = Counter(r.strip().split()[0].lower() for l, r in occurrences if r.strip())
        for neighbors, side in ((left_neighbors, "left"), (right_neighbors, "right")):
            if not neighbors:
                continue
            top_neighbor, top_count = neighbors.most_common(1)[0]
            ratio = top_count / n
            if ratio >= consistency_threshold:
                candidates[term] = (top_neighbor, side, ratio, n)
    return candidates
```

Present results as a batched suggestion, same as lever (2) — this is
still Claude's own inference from data, not the researcher's own stated
judgment the way lever (1) is, so it is never auto-accepted:

```
The following terms show a single, consistent neighbor across every
occurrence in this corpus:

  term      neighbor    side    ratio
  ---------------------------------------
  systems   ai          left    6/6

Confirm which of these I should treat as already-disambiguated (skipping
Step 3.5's WordNet check), and which you'd rather I check normally.
```

**NOTE (fixed, live test).** The naive query config
`query: ['term1', 'term2', 'term3']` (a JS array of separate term
strings) silently returned results for only one term, not all three —
confirmed on a real Voyant instance. The working form is a
**single-element array holding one string**, using the tool's own
documented operator syntax: pipe-separated terms and quoted phrases
together, e.g. `query: ['authority|testimony|systems|"expert
testimony"']`. Always use this form when building a CONTEXTS query for
this lever (or lever handling more generally) — the array-of-terms form
must not be assumed to work, despite the tool's own reference doc
listing `query` as accepting `String | Array` without this distinction.

**What was validated, and what wasn't.** Confirmed on real data: a term
(`systems`) whose immediate left-neighbor (`ai`) was identical across
100% of its occurrences (6/6) — genuinely disambiguating, matching the
"AI systems" Ngram already present in the Phrases export. **Not yet
tested:** any `consistency_threshold` below 1.0 (unanimous). Default to
requiring full unanimity until a partial-consistency case has actually
been tested and shown to still produce a correct sense — do not assume
e.g. 0.8 behaves the same way just because 1.0 did.

#### Reporting

All three levers feed the same per-term evidence table Step 3.5 already
produces (see below) — a context-fixed term is not dropped from that
table, just given a different status and no synset:

```
term          | accepted synset | lex domain | status
--------------------------------------------------------------------------
authority     | —               | —          | context-fixed (researcher-Ngram: "epistemic authority")
systems       | —               | —          | context-fixed (contexts-consistency: "ai" left, 6/6 occurrences, researcher-confirmed)
```

Terms not covered by any lever proceed to Step 3.5's `disambiguate()`
exactly as before — this step never removes a term from `top_n_terms`,
it only pre-empts whether `disambiguate()` runs for it.

### 3.5 WordNet Sense Disambiguation

For each term in the filtered list, WordNet returns multiple synsets ordered by general
corpus frequency — **sense 1 is not necessarily the correct sense for this corpus.**
A disambiguation check is mandatory before any synset is accepted.

**Pre-condition:** see Step 3.4b above — `wordnet_available` must be `True`
before any code in this step runs. Do not re-check informally here.

**Pre-filter:** see Step 3.4c above — any term already present in
`context_fixed` skips this step's `disambiguate()` call entirely; its
status is recorded directly from Step 3.4c's evidence (see the driver
loop below).

#### Algorithm

```python
from nltk.corpus import wordnet as wn
import re

# NOTE (fixed): a live test run (2026-06-30/07-01) demonstrated a real
# failure mode of the single-criterion version of this function: raw
# context-overlap can score a WRONG sense higher than the right one
# whenever the wrong gloss happens to share more surface vocabulary
# with the local context -- e.g. 'soul' resolving to a music-genre
# sense, 'job' to "a state of difficulty" instead of a piece of work,
# 'person' to a grammatical category. These scored as confidently
# GROUNDED, not flagged -- they were only caught because an unrelated
# follow-up request happened to trace hypernym chains and exposed
# implausible ancestries. Nothing in this function's original design
# would have caught them on its own.
#
# Fix: hypernym-chain domain plausibility is now a genuine SECOND,
# independently-computed criterion, mirroring how Step 3.2/3.3 already
# cross-checks coverage-N against the Zipf elbow and escalates to the
# researcher on disagreement rather than trusting either signal alone.
# Where the two criteria agree, the sense is accepted automatically as
# before. Where they diverge, this is now escalated for a researcher
# decision instead of silently keeping the context-overlap pick. Where
# no hypernym chain exists at all (WordNet has no is-a hierarchy for
# adjectives/adverbs -- roughly half the vocabulary in practice), this
# is explicitly disclosed as an unchecked term, never silently treated
# as agreement.

def _gloss_words(s):
    return set(s.definition().lower().split()) | \
           set(' '.join(s.examples()).lower().split())

def _context_score(s, context_words):
    return len(context_words & _gloss_words(s))

def _hypernym_domain_words(synset, depth=4):
    """Collect ancestor lemma names + gloss words up to `depth` levels
    of the hypernym ('is-a') chain. Empty for parts of speech WordNet
    doesn't give an is-a hierarchy to (adjectives, adverbs)."""
    words = set()
    frontier = [synset]
    for _ in range(depth):
        nxt = []
        for s in frontier:
            for h in s.hypernyms():
                words |= set(h.definition().lower().replace(';', ' ').replace(',', ' ').split())
                words |= set(h.name().split('.')[0].split('_'))
                nxt.append(h)
        if not nxt:
            break
        frontier = nxt
    return words

def _hypernym_score(synset, context_words, depth=4):
    return len(context_words & _hypernym_domain_words(synset, depth))

def disambiguate(term, txt, pos=None):
    """
    Returns the most contextually appropriate synset for `term`
    given the corpus text `txt`, or None with a divergence status if
    the two independent criteria disagree and need researcher input.
    """
    synsets = wn.synsets(term, pos=pos)
    if not synsets:
        return None, "no synsets found"
    if len(synsets) == 1:
        return synsets[0], "unambiguous"

    # Step 1: collect context window from TXT
    sentences = re.split(r'(?<=[.!?])\s+', txt)
    context = [s for s in sentences if term.lower() in s.lower()][:5]
    context_words = set(' '.join(context).lower().split())

    # Step 2: primary criterion -- context-overlap score
    ctx_scores = sorted(
        ((_context_score(s, context_words), s) for s in synsets),
        key=lambda x: x[0], reverse=True
    )
    ctx_best_score, ctx_best = ctx_scores[0]

    if ctx_best_score == 0:
        return synsets[0], "flagged — no context overlap, defaulted to sense 1"

    # Step 3: secondary criterion -- hypernym-domain plausibility
    if not any(s.hypernyms() for s in synsets):
        return ctx_best, (
            f"context overlap score: {ctx_best_score} "
            f"(hypernym check unavailable — no is-a hierarchy for this "
            f"part of speech)"
        )

    hyp_scores = sorted(
        ((_hypernym_score(s, context_words), s) for s in synsets),
        key=lambda x: x[0], reverse=True
    )
    hyp_best_score, hyp_best = hyp_scores[0]

    # Step 4: escalate on divergence -- do not silently keep the
    # context-overlap pick just because it scored highest
    if hyp_best.name() != ctx_best.name() and hyp_best_score > 0:
        return None, (
            f"DIVERGENCE — context-overlap picks {ctx_best.name()} "
            f"(score {ctx_best_score}), hypernym-domain picks "
            f"{hyp_best.name()} (score {hyp_best_score})"
        )

    return ctx_best, f"context overlap score: {ctx_best_score} (hypernym-confirmed)"
```

**NOTE (fixed):** `disambiguate()` was fully defined but never actually
called anywhere — the same "defined, never driven" gap already found
and fixed elsewhere in this file (Phase 3's token/colour derivation).
This meant `pos` always defaulted to `None`, comparing synsets across
*all* parts of speech mixed together — manufacturing "divergences" that
were really just a noun-sense competing against an unrelated verb-sense
of the same spelling, not genuine sense ambiguity within one part of
speech. A real test run found this drove a 63% divergence rate, far
above the ~8-word incident that originally motivated this check. Fixed
by adding the actual driver loop, passing each term's real part of
speech — already determined in the now-fixed Step 3.2b — instead of
leaving every comparison unrestricted:

```python
PTB_TO_WORDNET_POS = {'NN': 'n', 'VB': 'v', 'JJ': 'a', 'RB': 'r'}

def ptb_tag_to_wordnet_pos(ptb_tag):
    """Maps a Penn Treebank tag (from Step 3.2b's in-context tagging) to
    a WordNet POS constant via its 2-letter prefix. Returns None only
    for tags WordNet doesn't cover at all (determiners, prepositions,
    etc.) -- should be rare for terms that survived this far."""
    if not ptb_tag:
        return None
    return PTB_TO_WORDNET_POS.get(ptb_tag[:2].upper())

disambiguation_results = {}
for term in top_n_terms:
    lookup = term.rstrip('*').rstrip('"').strip('"')
    if lookup.lower() in context_fixed:  # from Step 3.4c
        source, evidence = context_fixed[lookup.lower()]
        disambiguation_results[lookup] = (None, f'context-fixed ({source}: "{evidence}")')
        continue
    term_pos_tag = _term_pos_tags.get(lookup)  # from Step 3.2b's tagging pass
    wordnet_pos = ptb_tag_to_wordnet_pos(term_pos_tag)
    synset, status = disambiguate(lookup, corpus_text, pos=wordnet_pos)
    disambiguation_results[lookup] = (synset, status)
```

If Step 3.4c was skipped entirely (researcher declined both levers),
`context_fixed = {}` — the loop above behaves exactly as it did before
Step 3.4c existed.

This requires Step 3.2b to record each term's tag for reuse here, not
just its verb/adverb flag status — add `_term_pos_tags[lookup] = tag`
alongside the existing `pos_flags` logic in that step, for every term,
not only the ones flagged as verbs or adverbs.

#### Reporting

For every term, report:

```
term          | accepted synset        | lex domain       | status
--------------------------------------------------------------------------
inquiry       | inquiry.n.01           | noun.cognition   | context overlap score: 3 (hypernym-confirmed)
rational      | rational.s.01          | adj.all          | context overlap score: 2 (hypernym check unavailable — no is-a hierarchy for this part of speech)
job           | job.n.01               | noun.act         | context overlap score: 1 (user-resolved after divergence)
problems      | problem.n.01           | noun.state       | unambiguous
laypeople     | —                       | —                | no synsets found
authority     | —                       | —                | context-fixed (researcher-Ngram: "epistemic authority")
```

#### Escalation rules

- **Status = "flagged"** → bring the term to the user with the top 3 candidate synsets
  and their definitions, and ask the user to choose.
- **Status = "unambiguous"** → accept without review.
- **Status starts with "DIVERGENCE"** → bring the term to the user with BOTH
  candidates (the context-overlap pick and the hypernym-domain pick), their
  definitions, and — if available — a short rendering of each one's hypernym
  chain, and ask the user to choose. This is not optional and not resolvable
  by picking whichever criterion scored higher; a real, live test run showed
  that trusting context-overlap alone here produces confidently wrong senses
  for common polysemous words. Whichever sense the user confirms, record the
  status as `"context overlap score: N (user-resolved after divergence)"` so
  the resolution — and the fact that a divergence occurred at all — is part
  of the permanent record, not just the in-session decision.
  **At high divergence volume, a disclosed batch mode is a legitimate
  alternative to reviewing every term individually (added, live evidence,
  Delacroix 2026 verification, 2026-07-15):** a real run hit 59 divergences
  out of 148 terms (40%) — asking the researcher to review every one
  individually is a real cost, not just a formality. Present the researcher
  the option: she names the terms that matter most to the paper's argument
  for full individual review (gloss text, your own reasoned recommendation);
  everything else is resolved by taking the hypernym-domain pick as a
  disclosed default, explicitly NOT equivalent to her review. Record this
  status as `"DEFAULT (hypernym-domain pick, not individually reviewed): "`
  followed by the original divergence detail — never silently upgrade this
  to the same status string as a genuinely reviewed term. This is a
  disclosed shortcut under researcher-confirmed time constraints, not a
  substitute for review Claude may choose unprompted.
- **Status = "context overlap score: N (hypernym-confirmed)", N ≥ 1** → accept
  automatically. Both independent criteria agree.
  **"Agree" is not the same claim as "correct" (added, live evidence,
  Delacroix 2026 verification, 2026-07-15).** A real run found `disambiguate()`
  return `hypernym-confirmed` for the anchor `opacity` — both criteria
  converged on `opacity.n.03` ("the degree to which something reduces the
  passage of light," physical/optical opacity) — for a paper whose entire
  argument is about epistemic opacity, where the correct sense,
  `opacity.n.02` ("incomprehensibility resulting from obscurity of
  meaning"), exists in WordNet and was never even considered a divergence
  candidate, since both criteria happened to agree on the wrong one
  together. This was caught only because the term was central enough to
  the paper's argument that its accepted sense got read and checked
  directly against the actual text, not because either criterion, or their
  agreement, flagged anything. Two criteria agreeing is evidence the
  algorithm was internally consistent, not evidence the result is right —
  do not report `hypernym-confirmed` in a way that reads as a stronger
  correctness guarantee than that. If a `hypernym-confirmed` (or any
  "grounded") result is checked directly against the source text and found
  substantively wrong, correct it and record the status as
  `"researcher-corrected (was: <original status>; corrected to <new
  synset>)"` — a fourth category, distinct from "user-resolved after
  divergence" (which resolves a criterion disagreement) and from the
  disclosed DEFAULT above (which never claimed agreement at all). This is
  not a routine review step to run on every grounded term — that would
  defeat the entire point of having disambiguate() automate most of the
  work — but when a term is central enough to be checked by hand for any
  reason (as `opacity` was here, via the similarity sweep), a substantive
  correctness check takes priority over the algorithm's own self-report of
  agreement.

  **CONFIRMED LIMITATION, two mitigations tried and verified NOT to
  help (the test book chapter, 2026-08-06).** `disambiguate()` only ever
  compares the single top context-overlap synset against the single top
  hypernym-domain synset. On this real corpus, 5 terms (`accounts`,
  `field`, `terms`, `case`, `things`) had a demonstrably correct WordNet
  sense that was in neither top-1 slot — e.g. `field` should have
  resolved to `discipline.n.01` ("a branch of knowledge," matching "her
  field of expertise") but the algorithm only ever compared `field.n.10`
  (an algebraic field) against `field.n.05` (a physics field), because
  those were each criterion's own top pick. Two fixes were designed and
  tested against these exact 5 terms before concluding neither works,
  not assumed from reasoning alone:
  1. **Combined score across every sense, not just each criterion's
     top-1.** Summing context-overlap and hypernym-domain scores per
     synset and taking the highest-combined sense does not surface the
     correct answer either — the known-correct sense ranked 4th, 7th,
     7th, 9th, and 10th out of all senses for the five terms above,
     respectively. Gloss/hypernym-word overlap against a short local
     context window is simply not a strong enough signal for common,
     highly polysemous nouns, no matter how many candidates it's asked
     to rank.
  2. **Synset count as an elevated-risk warning flag.** The five
     problem terms do have high synset counts (10-22), but so do many
     terms this same run resolved correctly without incident (`order`
     has 24 synsets, `good` has 27, `rule`/`rules` have 19) — there is
     no clean threshold that flags the real problem cases without also
     flagging a larger number of terms that were never actually wrong.

  **Left as an open, evidenced limitation, not silently worked around
  with a fix that looks more sophisticated but does not verifiably
  help.** The practical mitigation that already exists in this skill's
  workflow — the researcher declining disambiguation for a term she
  judges unimportant (see the DEFAULT/researcher-declined paths above)
  — is the correct response today, not a future algorithmic fix. If a
  `hypernym-confirmed` or `DIVERGENCE`-resolved term is later found
  substantively wrong on a term the researcher does care about, the
  `researcher-corrected` path above is how to fix it after the fact;
  there is no reliable way to catch it beforehand for a generic,
  highly-polysemous noun.
- **Status = "context overlap score: N (hypernym check unavailable...)"** →
  accept automatically, but this term was NOT cross-checked — WordNet has no
  is-a hierarchy for its part of speech. Tracked separately in the grounding
  tally below; never silently presented as equally verified to a hypernym-
  confirmed term.
- **Status = "flagged — no context overlap..."** → flag for user review.
- **Status = "no synsets found"** → categorize this term from TXT context alone
  (Step 5.1, rule 3) rather than WordNet. Always tracked as `context_only` in
  the grounding tally below — never silently absorbed into another status.
- **Status starts with "context-fixed (researcher-Ngram"** → accept
  automatically, no further review — the researcher's own flagging of the
  Ngram at Step 3.4c already is the confirmation. Tracked as `grounded` in
  the tally below, and separately as not cross-checked (see below), since
  `disambiguate()` never ran for this term.
- **Status starts with "context-fixed (collocate-confirmed"** → accept
  automatically — the researcher already confirmed this specific term at
  Step 3.4c's batched suggestion step, distinct from (and requiring more
  scrutiny to have offered than) the researcher-Ngram case, since the
  candidate came from an automated heuristic, not her own unprompted
  reading. Tracked the same way as the researcher-Ngram case otherwise.
- **Status starts with "context-fixed (contexts-consistency"** → accept
  automatically once researcher-confirmed at Step 3.4c's batched
  suggestion step — validated against a real corpus (see
  Step 3.4c lever (3)), unlike the collocate-confirmed case, but still an
  automated inference requiring her confirmation, not her own unprompted
  judgment. Tracked the same way as the other two context-fixed cases.

#### WordNet grounding tally (mandatory, every run)

`wn.synsets(term, pos=pos)` queries the English WordNet only. For a
non-English corpus, or for heavily domain-specific/technical vocabulary in
any language, this call can return empty for most or all terms — meaning
WordNet contributes nothing to categorization even though Step 5.1 lists it
as the first input. This must be measured and disclosed every run, not
predicted upfront, since coverage gaps occur even within nominally
well-covered languages.

Classify every disambiguation result into one of three grounding tiers:

```python
def grounding_tier(status):
    if status == "no synsets found":
        return "context_only"          # WordNet contributed nothing
    if status.startswith("flagged"):
        return "weak"                  # synsets existed but no context match;
                                        # defaulted to sense 1, or user-resolved
                                        # from real WordNet candidates
    return "grounded"                  # unambiguous, hypernym-confirmed,
                                        # hypernym-unchecked-but-context-scored,
                                        # user-resolved after divergence,
                                        # context-fixed via Step 3.4c (Ngram or
                                        # confirmed collocate), or a disclosed
                                        # batch DEFAULT (hypernym-domain pick,
                                        # not individually reviewed) -- see
                                        # crosscheck_status below, which is
                                        # where these are told apart. A real
                                        # synset was assigned in every case,
                                        # which is what this tier measures --
                                        # whether it was individually verified
                                        # is a separate question.
```

**HONESTY NOTE (added, live evidence, Delacroix 2026 verification,
2026-07-15).** A batch DEFAULT status counts as "grounded" here because a
real synset genuinely was assigned (the hypernym-domain pick, not sense 1
or a guess) -- but folding it into "grounded" with no further distinction
would silently overstate how much of that count reflects actual review.
A real run found 34 of 137 "grounded" terms (25%) were batch-defaulted,
not reviewed at all -- large enough that reporting only the 99%-grounded
headline number would be misleading on its own. This is why
`crosscheck_status` below gives DEFAULT its own explicit label, not just
inside the tier count.

**Separately** (not a fourth grounding tier — this is about HOW a grounded
result was reached, not whether it counts as grounded), track the hypernym
cross-check outcome for every "grounded" result:

```python
def crosscheck_status(status):
    # NOTE: "researcher-corrected" must be checked before "hypernym-confirmed"
    # -- its status string embeds the original status verbatim (see the
    # escalation-rules HONESTY NOTE above), which can itself contain the
    # substring "hypernym-confirmed"; checking that branch first would
    # misclassify a corrected, substantively-wrong sense as merely agreed.
    if status.startswith("researcher-corrected"):
        return "CORRECTED -- algorithm's own agreement was substantively wrong, caught by direct verification"
    if "hypernym-confirmed" in status:
        return "cross-checked, agreed"
    if "user-resolved after divergence" in status:
        return "cross-checked, DIVERGED, researcher resolved"
    if "hypernym check unavailable" in status:
        return "not cross-checked (no is-a hierarchy for this POS)"
    if status.startswith("context-fixed"):
        return "not cross-checked (disambiguate() never run — bypassed at Step 3.4c)"
    if status.startswith("DEFAULT"):
        return "NOT REVIEWED (batch default, hypernym-domain pick applied unchecked)"
    return None  # unambiguous / flagged / no synsets -- crosscheck N/A
```

**Note the distinction between the two "not cross-checked" reasons.**
"No is-a hierarchy for this POS" means `disambiguate()` ran and did what
it could — the hypernym criterion simply had nothing to compare against.
"Bypassed at Step 3.4c" means `disambiguate()` never ran at all for this
term — the evidence behind its accepted sense is the researcher's own
Ngram judgment or her confirmation of a suggested collocate, not any
WordNet computation. Keep these separate in any summary that reports
"not cross-checked" counts; collapsing them would misstate what kind of
evidence stands behind a context-fixed term.

Tally and report before moving to Step 4:

```python
from collections import Counter

# NOTE (fixed, v2.12): disambig_results was referenced here and below but
# never defined anywhere -- only disambiguation_results (a dict keyed by
# term, populated a few steps above) exists. This is the same "referenced
# before defined" NameError class already caught and fixed elsewhere in
# this file (top_n_terms, word_to_num) -- found here while wiring the new
# Escalation verification limits section into the same data, itself never
# previously exercised end-to-end against a real Python execution. Fixed
# by deriving the (synset, status) pairs the tally code already expects
# from the dict's own values, once, here.
disambig_results = list(disambiguation_results.values())

tier_counts = Counter(grounding_tier(status) for _, status in disambig_results)
total = sum(tier_counts.values())

crosscheck_counts = Counter(
    c for _, status in disambig_results
    if (c := crosscheck_status(status)) is not None
)

print("WordNet grounding:")
print(f"  grounded     : {tier_counts['grounded']} ({tier_counts['grounded']/total:.0%})")
print(f"  weak/default : {tier_counts['weak']} ({tier_counts['weak']/total:.0%})")
print(f"  context-only : {tier_counts['context_only']} ({tier_counts['context_only']/total:.0%})")
print()
print("Hypernym cross-check (within grounded terms):")
for label, n in crosscheck_counts.items():
    print(f"  {label}: {n}")
```

This report is mandatory and unconditional — it appears for every run, not
only when coverage looks poor, so a well-grounded English run and a
context-only non-English run carry the same kind of evidence on the record,
just with different numbers. If `context_only` exceeds roughly a third of
selected terms, say so explicitly: semantic clustering for this corpus rested
substantially on Claude's own linguistic judgment rather than on the WordNet
lexical resource, and the user should weigh the epistemic authority of the
resulting clusters accordingly. Likewise, if a large share of grounded terms
were "not cross-checked" (typically corpora heavy in adjectives/adverbs),
say so explicitly too: those terms' senses rest on context-overlap alone,
the criterion already shown capable of confidently picking a wrong sense.
If a large share of the "not cross-checked" count is specifically the
Step 3.4c bypass (researcher-Ngram or collocate-confirmed) rather than
the adjective/adverb POS gap, say that explicitly and separately too —
it is a different kind of evidence gap (never checked at all, vs. checked
against only one of the two criteria) and the report should not let a
reader conflate the two just because both currently land in one Counter
label.

**Carry this tally forward** into the Phase1-results.md report (a permanent
`## WordNet grounding` section, not just a chat-turn message) and into the
Step 6.1 JSON contract as `wordnetGrounding`. The hypernym cross-check
breakdown is process metadata, not term/cluster data Phase 2/3 need to
branch on — carry it into the same permanent MD section, not the JSON
(consistent with how the Step 1b/3.2b environment-fallback disclosures
are handled: human-readable record, not the five-key machine contract).

**Also carry forward the full per-term disambiguation table** (term,
accepted synset, lex domain, status, including the cross-check outcome)
as a permanent appendix in Phase1-results.md, not merely a session working
file. A prior test run computed exactly this table, used it to catch and
correct 8 wrong senses via a manual hypernym review, and then delivered
none of it — the corrected senses' evidence existed only in that session's
chat log, unrecoverable from the three files actually delivered. A
researcher revisiting this corpus's incList in six months, wanting to
verify why a term landed in a particular cluster, needs this table to
still exist.

#### Escalation verification limits (mandatory, every run)

**This section is unconditional** — present every run, including when
no term required escalation, mirroring the WordNet grounding tally's own
"mandatory every run, not only when it looks questionable" discipline. A
missing section must never be mistaken for "nothing to disclose."

Motivated by a real test run (PetrovaLindqvist2024-ExampleCorpus,
2026-07-06): a blanket, researcher-approved resolution covering 113
divergent terms was disclosed honestly as a blanket decision, not
overstated as 113 individual confirmations — but independent
verification against live WordNet afterward found the resolution was
not, in fact, reliably safe. The corpus's own core-cluster term,
"character," resolved to `fictional_character.n.01` when neither of the
two escalated candidates was the correct sense at all —
`character.n.03`, the actual moral-character sense, was never nominated
by either scoring criterion and so never appeared as an option to
choose between. No amount of researcher diligence at the escalation
step itself could have caught that, since the correct answer was not on
the table being reviewed. This limitation is structural to the
escalation design, not a lapse in any particular run, and belongs in
every delivered report, not just the one that surfaced it.

```python
flagged_count  = sum(1 for _, status in disambig_results if status.startswith("flagged"))
diverged_count = sum(1 for _, status in disambig_results if "user-resolved after divergence" in status)
escalation_count = flagged_count + diverged_count

if escalation_count == 0:
    escalation_note = (
        "No terms required escalation this run — every accepted sense "
        "was either unambiguous or reached by unanimous agreement "
        "between the two independent criteria, so neither limitation "
        "below applied to any term in this table."
    )
else:
    escalation_note = (
        f"{escalation_count} term(s) in this run triggered a Step 3.5 "
        f"escalation (flagged: {flagged_count}; DIVERGENCE: {diverged_count}). "
        "Each is recorded above with a status such as \"user-resolved\" "
        "or as part of a researcher-approved blanket resolution covering "
        "several terms at once."
    )
```

**Carry this forward** into the Phase1-results.md report as a permanent
`## Escalation verification limits` section — mandatory every run, same
discipline as `## WordNet grounding` and `## Environment fallbacks used`
above, not conditioned on whether this run's `escalation_count` is zero:

```
## Escalation verification limits

{escalation_note}

**Those labels are self-reports.** They are generated by the same
system whose behavior they describe, in the same session, and nothing
in this document independently confirms that a genuine pause and
researcher response occurred for each one individually — as opposed to
the system resolving the matter and narrating that it had. This applies
equally to a single term-level escalation and to a blanket methodological
resolution covering many terms at once.

**The candidates compared are not guaranteed to include the correct
sense.** Where this step escalates a choice between two or three WordNet
candidates, both are themselves the output of automated scoring, and the
correct sense for this corpus is not guaranteed to be nominated by
either criterion — it can fail to appear as an option at all. A
confirmed or defaulted choice certifies only the best of what was shown,
not the best available in WordNet's full synset inventory for that term.
```

#### Integration point

This step runs **after 3.4 (term selection)** and **before 4.1 (wildcard stemming)**.
Its output is a verified `(term → synset)` mapping that feeds directly into categorization.

---

## 4. Compress to Wildcard Stems (incList)

### 4.1 Group by common stem prefix

**NOTE (fixed, 2026-07-14):** this step previously had no grouping algorithm at all —
only prose rules and a set of "examples from this workflow" that, checked against the
real GarciaOkonkwo2025 run's actual output, did not match it (the file showed
`distinct*`/`enhanc*`/`concept*`/`technolog*`/`function*`; the real run produced
`approach*`/`authorit*`/`epistemolog*`/`expert*`/`issue*`/`question*`/`testimon*` —
entirely different terms, with nothing establishing where the original examples
actually came from). Step 4.2's coverage check operated on a `groups` variable this
step never defined — the same "prose says X, the code that would produce X doesn't
exist" gap as Step 3.2b's undefined-variable bug (see
`PEEL-Phase1-EpistemicThreats-Catalog.md`, T-3.10), here affecting the step's entire
core algorithm, not one line. The real, tested implementation existed only in
`live_run_hauswald_step41_stemming.py`, built specifically to fix three documented bug
classes from the interrupted PetrovaLindqvist2024 run (case-fold duplication, e.g.
`Kant`/`kant`; a normally-resolved term grouped with an unresolved one, e.g.
`good`/`goods`, the same shape as the `Childress`/`child` and `Morals`/`morality`
failures already documented elsewhere in this project) plus a scope-creep check against
the full corpus vocabulary — executed successfully, never merged back into this file.
Merged below, verified against real data both before and after merging.

For each group of terms sharing a stem, assign a single `stem*` entry. Rules:
- A wildcard `*` is used **only when 2 or more terms share the same stem prefix**.
- Single-form terms keep their exact spelling — no wildcard.
- The stem must be the **longest common prefix** that still unambiguously identifies
  the group.
- Do not over-truncate: `analy*` covers `analysis/analytic/analyze` correctly;
  `an*` would not.

```python
from nltk.stem import PorterStemmer
from collections import defaultdict

stemmer = PorterStemmer()

def lcp(strings):
    """Longest common prefix that still unambiguously identifies the group."""
    if not strings:
        return ''
    s1, s2 = min(strings), max(strings)
    for i, c in enumerate(s1):
        if i >= len(s2) or c != s2[i]:
            return s1[:i]
    return s1

groups_by_stem = defaultdict(list)
case_variant_flags = []
seen_lower = {}
for term in top_n_terms:
    key = term.lower()
    if key in seen_lower and seen_lower[key] != term:
        case_variant_flags.append((seen_lower[key], term))
    seen_lower[key] = term
    groups_by_stem[stemmer.stem(key)].append(term)

groups = {}
singleton_terms = []
proper_noun_collision_flags = []
for stem, members in groups_by_stem.items():
    if len(members) < 2:
        singleton_terms.append(members[0])
        continue
    prefix = lcp([m.lower() for m in members])
    groups[prefix] = sorted(members)
    # A group mixing a normally-resolved term with an unresolved/no-fit one
    # (Childress/child, Morals/morality, good/goods) needs researcher
    # review, not silent acceptance -- this is disambiguation_results from
    # Step 3.5, already in scope, not reloaded or reimplemented here.
    synsets = [disambiguation_results.get(m, (None, ''))[0] for m in members]
    has_unresolved = any(s is None for s in synsets)
    has_normal = any(s is not None for s in synsets)
    if has_unresolved and has_normal:
        proper_noun_collision_flags.append(
            (prefix, members, [disambiguation_results.get(m, (None, ''))[1] for m in members])
        )

# Scope-creep check: does this wildcard prefix also match OTHER corpus
# vocabulary not actually selected into top_n_terms? A silent broadening
# risk if unnoticed -- reuses terms_df, already loaded at Step 1.1.
full_vocab = [str(t) for t in terms_df['Term']]
scope_creep_flags = []
for prefix, members in groups.items():
    also_matches = sorted([t for t in full_vocab if t.lower().startswith(prefix) and t not in members])
    if also_matches:
        scope_creep_flags.append((prefix, members, also_matches))
```

**Report to the user, before proceeding:** any `case_variant_flags`, `proper_noun_collision_flags`,
and `scope_creep_flags` found — none of these are silently resolved. Also report the
achieved stem-compression ratio (below) against the disclosed target range, since a large
divergence can itself be a useful signal about this corpus's morphological richness, or
about an upstream issue worth double-checking, not just a number to compute and discard.

**Do not proceed to Step 4.2 until the user has responded** (if all three flag lists are
empty, say so and proceed without waiting).

### 4.2 Verify coverage
```python
covered = set()
for members in groups.values():
    covered.update(members)
covered.update(singleton_terms)
assert covered == set(top_n_terms), f"Coverage mismatch: {set(top_n_terms) - covered} missing"
```

### 4.3 Sort alphabetically
```python
# NOTE (fixed, live evidence, another test corpus full-cycle test, 2026-07-31):
# this line previously read `sorted(groups.keys()) + sorted(singleton_terms)`
# -- `groups.keys()` are the bare LCP prefixes computed in 4.1 (e.g.
# "introspecti"), never starred. The wildcard `*` existed only as a display
# convention in Step 5.2's own reporting example, never actually appended to
# the stored string. This is not cosmetic: Voyant's wildcard search requires
# the literal `*` character to function as a wildcard at all, so serializing
# `stems_final` as-is at Step 6 would silently produce non-functional
# incList entries for every grouped stem. Fixed by appending `*` here, where
# the list is actually built, not left as an undocumented convention a
# downstream step has to remember to apply.
stems_final = sorted(p + '*' for p in groups.keys()) + sorted(singleton_terms)
```

**Target: approximately 70–75% of `len(stems_final)` relative to `len(top_n_terms)`,
for a given term input (ratio depends on corpus morphological richness) — a rough
expectation, not a validated general rule.** Checked against real data,
GarciaOkonkwo2025, 2026-07-14: the actual ratio was 93.1% (95 stems from 102
terms), well outside this range. Report the actual ratio achieved every run per the
disclosure requirement in 4.1 above, rather than silently letting a large divergence
from this rough expectation go unmeasured.

---

## 5. Semantic Categorization (clusterDefs source)

### 5.1 Assign each stem and phrase to a semantic category
Using the verified `(term → synset)` mapping from step 3.5, group stems into semantic
clusters. Also assign each confirmed phrase from Step 1b to the cluster whose theme it
best represents. Categorization is driven by:

1. **WordNet lexname** (e.g. `noun.cognition`, `noun.act`, `noun.state`) as a first-pass
   grouping signal for unigram stems.
2. **Hypernym chain** to identify shared conceptual ancestors across terms.
3. **TXT context** to resolve cases where lexname alone is insufficient.
4. **Your knowledge of the language** to name each cluster meaningfully.
5. **Phrase semantics** for confirmed N-grams: assign each `"quoted phrase"` to the
   cluster that captures its dominant meaning in this corpus.

**Do not force terms into pre-established categories.** Let the clusters emerge from the
data. Name each cluster after the conceptual theme it represents in *this* text.

**Handling unigrams that are components of a selected phrase:**
When a unigram stem (e.g. `common`) is also a component of a selected phrase
(e.g. `"common good"`), keep the unigram stem in the incList and assign the phrase
to a cluster. Do **not** remove the unigram stem solely because a phrase covers it —
both are valid independent search terms in Voyant.

**Recording assignments.** Categorization is judgment-driven by design — this
step deliberately has no algorithm dictating cluster membership, unlike Step
4.1's stemming — but the running record of *what was assigned where* is not
itself optional:

```python
clusters = {}  # cluster_name -> list of stems/phrases, populated as each
                # stem/phrase is assigned to a cluster through this section
```

### 5.1b — Cluster assignment grounding tally (mandatory, every run)

**Motivation.** Step 3.5 gives the researcher a per-term rationale trail
(synset, status, cross-check outcome) before any word sense is accepted.
Step 5.1's cluster assignment — arguably the more consequential judgment
call, since it sets the semantic categories the researcher will read the
corpus through — gave no equivalent trail: only the finished stem-to-
cluster table, with no record of which Step 5.1 signal (lexname,
hypernym, TXT context, or Claude's own linguistic judgment) placed each
stem where it landed. This step does not make cluster assignment itself
independently verifiable — unlike sense selection, "which cluster does
this stem belong to" has no second, independently-computed criterion the
way Step 3.5 has hypernym-domain plausibility. What it does instead is
disclose, per stem, which kind of signal was actually used, so the
researcher's review effort at Step 5.4 can be weighted toward the stems
least backed by an external signal, instead of spread evenly — or not at
all — across the whole table.

As each stem and confirmed phrase is assigned to a cluster in Step 5.1,
record which rule primarily justified the placement:

```python
def tag_cluster_grounding(term, wordnet_result, used_context, used_hypernym, is_phrase):
    """
    Called once per stem/phrase as Step 5.1's categorization proceeds --
    this is a disclosed SELF-REPORT of which signal Claude actually used,
    not an independently computed check, the same epistemic status as
    Step 3.5's own status field. Returns one of:
      'lexname'  -- WordNet lexname (Step 5.1 rule 1) was sufficient on
                    its own to place this stem in its cluster
      'hypernym' -- lexname alone was not decisive; the hypernym chain
                    (rule 2) supplied the actual link to this cluster's
                    theme. Caller sets `used_hypernym=True` explicitly
                    when this happens, the same way `used_context` is
                    set by the caller rather than inferred after the
                    fact -- this tag is never reachable without it.
      'context'  -- TXT context (rule 3) was used to resolve placement,
                    typically because this term's Step 3.5 grounding
                    tier was 'weak' or 'context_only'
      'judgment' -- no lexname/hypernym signal was decisive; placement
                    rests on rule 4 (Claude's own linguistic knowledge)
                    alone, with no external lexical signal behind it
      'phrase'   -- confirmed N-gram phrase (rule 5); phrase semantics do
                    not reduce to a WordNet lexname signal by
                    construction, so this is tracked separately, never
                    folded into 'judgment' as if it were a fallback
    `wordnet_result` is the (synset, status) pair from Step 3.5's
    `disambiguation_results` for this term, or None for phrases.
    `used_hypernym` is True when the lexname alone did not justify the
    placement and the hypernym chain supplied the actual link -- decide
    this at the same time as the placement itself, not retroactively.
    """
    if is_phrase:
        return 'phrase'
    if used_context:
        return 'context'
    if wordnet_result is None or wordnet_result[1] == 'no synsets found':
        return 'judgment'
    if used_hypernym:
        return 'hypernym'
    return 'lexname'  # default: a synset existed and its lexname alone
                       # was usable for grouping, with no hypernym-chain
                       # detour needed

cluster_grounding = {}  # term/phrase -> tag, populated during Step 5.1
```

**HONESTY NOTE:** this tagging is Claude's own account of which signal it
used, produced in the same pass as the categorization decision itself —
it is not, and cannot be, independently verified the way Step 3.5's
hypernym cross-check independently re-derives its second criterion from
WordNet data. State this plainly in the delivered report (below), the
same standard already applied to Step 3.5's "labels are self-reports"
disclosure.

#### Reporting

```python
from collections import Counter
grounding_tally = Counter(cluster_grounding.values())
total_assigned = sum(grounding_tally.values())

print("Cluster assignment grounding:")
for tag in ('lexname', 'hypernym', 'context', 'judgment', 'phrase'):
    n = grounding_tally.get(tag, 0)
    print(f"  {tag:9s}: {n} ({n/total_assigned:.0%})")
```

If `judgment` exceeds roughly a quarter of assigned stems, say so
explicitly, before Step 5.4's confirmation prompt: a large share of this
corpus's clustering rests on Claude's own linguistic judgment rather than
on an external lexical signal, and the researcher should weight their
review of the cluster table accordingly — the same discipline Step 3.5
already applies to its own `context_only` threshold.

**Carry this tally forward** into the Phase1-results.md report as a
permanent `## Cluster assignment grounding` section (mandatory every run,
same discipline as `## WordNet grounding`, `## Environment fallbacks
used`, and `## Escalation verification limits`) and as a full per-stem
appendix table (stem/phrase, cluster, grounding tag) — the same
durability fix v2.12 applied to Step 3.5's disambiguation table, for the
same reason: a researcher revisiting this corpus's clusters in six months
needs to see *why* a stem landed where it did, not just that it did.

### 5.2 Reporting format

Phrases appear as `"quoted"` entries alongside wildcard stems:

```
Cluster name        | Stems / Phrases
-----------------------------------------------------------------
Epistemic actions   | inquir*, know*, understand*, reason*, think*
Problem domain      | problem*, difficult*, challeng*, obstacl*
Normative values    | value*, wisdom*, ethic*, moral*, good*,
                    | "common good", "human dignity"
AI & Technology     | ai, technolog*, artificial, intelligence,
                    | "artificial intelligence", "machine learning"
...
```

### 5.3 Escalation rule

**Criterion: cascade non-convergence.** As each stem is assigned in Step 5.1,
the rule cascade (lexname → hypernym → TXT context → judgment) is checked in
priority order and stops at the first decisive signal — that decisive signal
is what `tag_cluster_grounding` records. Escalation applies whenever, in
addition to that decisive signal, **a different rule in the cascade would
plausibly place the same stem in a different cluster.** Concretely: before
finalizing a placement, check whether the hypernym chain, TXT context, or
Claude's own reading of the term would support a cluster other than the one
the decisive signal chose. If so, the cascade has not converged — do not
silently pick the higher-priority signal's answer. Escalate.

This is deliberately broader than "the WordNet synset itself is ambiguous" —
it also catches cases where a signal lower in the cascade (context, judgment)
disagrees with a higher one, which is exactly the shape the one real
execution on record missed: `dependent`/`independent`/`new`/`real`/`world`
were double-listed across clusters during categorization and then resolved
by an unwritten "keep first, drop duplicate" rule, with no record of the
alternative cluster or the researcher's input reaching the delivered report.

**On escalation:**

```python
ambiguity_log = []  # list of dicts, one per escalated stem/phrase:
                     # {term, candidate_clusters, evidence, resolution}
```

Present the stem to the user with **both (or all) candidate clusters** and
the specific TXT sentence(s) that support each candidate, then record the
researcher's actual decision in `ambiguity_log` before adding the stem to
`clusters`. **Do not resolve an escalated stem automatically** (no "keep
first," no cascade-priority tie-break) — the whole point of escalation is
that the cascade did not produce a decisive answer on its own, so the
researcher's judgment is the only thing that can.

**Carry `ambiguity_log` forward** into the Phase1-results.md report as a
permanent `## Cross-cluster ambiguity log` section (mandatory every run, same
discipline as `## Cluster assignment grounding`) — one row per escalated
stem: the stem, its candidate clusters, the TXT evidence shown, and the
researcher's resolution. If no stem was escalated in a given run, state that
explicitly rather than omitting the section, so its absence is legible as
"checked, none found" rather than "not run."

### 5.4 Await user confirmation

**Markdown-safe presentation (added v1.30, closes a real, confirmed
incident).** Every stem/phrase list this step (and Step 5.1/5.3's own
back-and-forth editing) presents back to the researcher contains
wildcard-form stems (`epistemic*`, `abducti*`) whose trailing `*` a
markdown renderer can silently interpret as italic-emphasis syntax and
strip, rather than display literally — confirmed live (the original test paper,
2026-08-05): a cluster pasted back for the researcher's own edit review
arrived with every asterisk missing, caught only because she happened
to notice the stems no longer looked like wildcards ("Look at wrong
stemming here... pasted back the cluster with all asterisks missing").
This is a chat-rendering risk, not something a Python fix can close —
**any stem/phrase list presented back to the researcher for
confirmation or editing (the cluster table below, intermediate
re-sends during Step 5.1/5.3 editing, anything else containing a raw
`*`) must be wrapped in a fenced code block (` ``` `) or inline code
spans (`` ` ``), never bare markdown text**, so the literal characters
survive rendering. If a list was already sent bare and the researcher
flags a discrepancy, do not assume she misread it — re-send the exact
same content code-fenced and confirm the asterisks were the actual
cause before treating it as a content error.

**Before proceeding to Step 6**, present the complete cluster table to the user,
**restate the Step 5.1b grounding tally first**, and then ask:

> "Cluster assignment grounding: [N] stems are backed by a WordNet lexname
> or hypernym signal, [N] were resolved from TXT context, [N] rest on my
> own linguistic judgment alone with no external signal behind them, and
> [N] are confirmed phrases (grounding not applicable). You may want to
> look at the judgment-only group more closely — see the appendix in
> Phase1-results.md for exactly which stems those are.
>
> Cross-cluster ambiguity: [N] stem(s) triggered escalation under the
> cascade-non-convergence rule and were resolved by your input above — see
> the `## Cross-cluster ambiguity log` appendix for the candidate clusters
> and evidence shown for each. [If N == 0: "None this run."]
>
> Do the clusters look correct? Please confirm, or request any moves, additions,
> or deletions before I serialize."

Do not proceed to Step 6 until the user has explicitly confirmed the clusters.
This is the last checkpoint before the inter-phase contract is written.

**Closure condition (added 2026-07-28, usability review — mirrors the
same-shaped fix already validated in Phase 2's Step 4.2):** this message
bundles three distinct things — the grounding tally, the ambiguity log,
and the cluster table itself — into one checkpoint, which carries real
rubber-stamp risk. A general approval signal ("looks good", "confirmed",
"proceed") does **not** close this checkpoint by itself. Before
serializing, the user's reply must visibly address each of the following
that applies to this run:
- the judgment-only grounding group (acknowledge it, or request changes to
  specific stems in it);
- **each** escalated stem in the ambiguity log individually (a blanket
  "accept all escalations" does not count — the whole reason a stem was
  escalated is that no automatic rule could resolve it, so each one needs
  its own visible disposition, same principle as Step 5.3's "do not resolve
  an escalated stem automatically");
- the cluster table itself (moves/additions/deletions, or explicit
  confirmation of the table as shown).

If the user's reply only addresses some of these, ask specifically about
the remaining ones before proceeding — do not infer their approval from
silence on an item this message raised.

#### Stem removal routing (mandatory)

When the user removes a stem from a cluster — whether by excluding an individual
stem or dropping an entire cluster — Claude must ask for an explicit routing
decision for **each removed stem** before serializing:

> "Where should `stem*` go — **incList** (kept as a Voyant search term, just
> not clusterized) or **excList** (excluded entirely)?"

This question must be asked once per removed stem (or once per batch if the user
removes several stems and their intent is clearly uniform). Claude must never
silently default to either list.

**Routing rules:**
- **incList** (default when analytically meaningful): stem stays in the
  `incList` array and remains available as a Voyant search term. It simply
  carries no cluster colour. Remove it from its cluster's `stems` list in
  `clusters` (Step 5.1) — no further bookkeeping needed, since it remains
  part of the base stem/phrase set Step 6.1 builds `incList` from either way.
- **excList**: stem is moved from `incList` to `excList` and will be treated
  as a non-significant term by Voyant tools that respect the stop list.
  Remove it from its cluster's `stems` list in `clusters`, **and** record it:

```python
excList_routed = []  # stems/phrases explicitly routed to excList in this
                      # section -- Step 6.1 builds excList from this list
                      # alone (narrow scope, decided 2026-07-14; see its
                      # HONESTY NOTE for what this does and does not cover)

# ... for each stem the researcher routes to excList:
excList_routed.append(stem)
```

Do not proceed to Step 6 until every removed stem has been explicitly routed.

**Finalizing the cluster table.** Once confirmation and all routing decisions
are complete, build the structure Step 5.5 consumes from the running
`clusters` record (Step 5.1), applying any moves/removals the researcher
requested:

```python
clusters_final = [
    {'name': name, 'stems': stems}
    for name, stems in clusters.items()
    if stems  # a cluster fully emptied by routing is dropped, not kept
              # as a blank row in the final table
]
```

### 5.5 Generate HTML cluster-table snippet

**After user confirmation and all routing decisions are complete**, generate an
HTML snippet showing the final cluster table with Tableau20 colours and deliver
it as a file alongside the JSON and MD.

**INLINE-STYLE ARCHITECTURE (mandatory, added v1.19).** All HTML produced by
this step must use only inline `style="..."` attributes -- no `<style>`
block, no CSS class names, no `<head>` element. The entire snippet is
wrapped in a single outer `<div>` so it is fully self-contained and cannot
be affected by, or bleed into, Voyant's own stylesheet when pasted into a
Spyral HTML cell. The output is a pure HTML fragment: no `<!DOCTYPE>`, no
`<html>`, no `<head>`, no `<body>`. Confirmed with the researcher
(2026-07-18): this step produces a single fragment only, injection-ready by
construction -- no separate standalone-preview file, unlike Phase 2's
`_spyral.html`/`_v3.html` pair.

The snippet uses the same format and colour assignment as the Phase 3 colour
legend, so it can be pasted directly into a Spyral HTML cell.

#### Algorithm

```python
import json
import html as _html

def esc(text):
    """Escape &, <, > for safe insertion into HTML body text. Quotes are
    left literal, matching the same convention used by the Phase 3 skill's
    own esc() (see peel3-phase3, "Converting the -results.md reports to
    HTML")."""
    return _html.escape(str(text), quote=False)

TABLEAU20 = [
    "#4E79A7","#F28E2B","#E15759","#76B7B2","#59A14F",
    "#EDC948","#B07AA1","#FF9DA7","#9C755F","#BAB0AC",
    "#499894","#A0CBE8","#FFBE7D","#FF9D9A","#86BCB6",
    "#8CD17D","#F1CE63","#D4A6C8","#FABFD2","#D7B5A6",
]

def hex_to_rgb(h):
    h = h.lstrip('#')
    return tuple(int(h[i:i+2], 16) for i in (0, 2, 4))

rows = []
for i, cluster in enumerate(clusters_final):
    name  = esc(cluster['name'])
    stems = cluster['stems']
    color = TABLEAU20[i % len(TABLEAU20)]
    r, g, b = hex_to_rgb(color)
    stems_str = ', '.join(f'<code>{esc(s)}</code>' for s in stems)
    rows.append(
        f'    <tr>\n'
        f'      <td style="padding:5px 12px 5px 0;">&nbsp;</td>\n'
        f'      <td style="padding:5px 12px 5px 0; color:rgb({r},{g},{b}); '
        f'font-weight:bold;">{name}</td>\n'
        f'      <td style="padding:5px 0; font-size:0.88em; color:#555;">'
        f'{stems_str}</td>\n'
        f'    </tr>'
    )

rows_html = '\n'.join(rows)
total_stems = sum(len(c['stems']) for c in clusters_final)

snippet = f"""<div style="font-family:Georgia,serif;color:#1c1a18;">
<h3 style="font-family:system-ui,sans-serif;font-size:1.05rem;font-weight:700;color:#1a5c7a;margin:0 0 0.5rem;">Semantic Clusters — Phase 1 results</h3>
<p style="font-style:italic; color:#666; font-size:0.9em; margin:0 0 0.8rem;">
  {corpus_name} &mdash; {len(clusters_final)} clusters &middot;
  {total_stems} stems &middot; Tableau20 palette
</p>
<table style="border-collapse:collapse; font-family:serif; font-size:14px;">
  <thead>
    <tr>
      <th style="padding:5px 12px 5px 0;">&nbsp;</th>
      <th style="padding:5px 12px 5px 0; text-align:left;">Cluster</th>
      <th style="padding:5px 0; text-align:left;">Stems</th>
    </tr>
  </thead>
  <tbody>
{rows_html}
  </tbody>
</table>
</div>"""

snippet_path = f'/mnt/user-data/outputs/{corpus_name}-{selection_method}-Phase1-clusters.html'
with open(snippet_path, 'w', encoding='utf-8') as f:
    f.write(snippet)
print(f"HTML cluster snippet written: {snippet_path}")
```

**HONESTY NOTE (added, live evidence, Delacroix 2026 verification, 2026-07-15).**
This filename previously used only `{corpus_name}`, with no `selection_method`
suffix. A real comparison test — running both the automated and seeded paths
against the same corpus specifically to compare their results, which this
file has always supported as a design (Step 1c) but never actually been run
for in a single session before — would have had its second run silently
overwrite the first run's delivered HTML (and, more seriously, the JSON
contract at Step 6.2 below) with no warning, since nothing in either step's
original path distinguished which `selection_method` produced it. Fixed by
making the path always encode `selection_method`, not just when a
collision happens to be detected — this also makes the delivered filename
self-documenting (`mycorpus-automated-Phase1-clusters.html` vs.
`mycorpus-seeded-...`) even for the common single-run-per-corpus case,
consistent with this file's existing preference for structural, always-on
disclosure over conditional cleverness (e.g. `_source`, `_pos_mode`, and
the coverage-threshold report are always shown, not only when they differ
from a default).

#### Delivery

Add the HTML snippet to the `present_files` call in Step 6.3, in this order:
1. `[corpus_name]-[selection_method]-Phase1-results.md`
2. `[corpus_name]-[selection_method]-phase1-state.json`
3. `[corpus_name]-[selection_method]-Phase1-clusters.html`

The snippet is generated **once**, after final confirmation. If the user
subsequently edits clusters and triggers a JSON re-write (see "Editing the JSON
before Phase 2"), re-generate the snippet from the updated `clusters_final` and
re-present all three files.

---

## 6. Serialize to JSON (inter-phase contract)

**This step is mandatory. It must run after every successful Phase 1, without
exception, after cluster confirmation in Step 5.4.**

### 6.1 — What the JSON encodes

The JSON file encodes exactly five keys. Nothing else is added.

```python
import json

# HONESTY NOTE (added 2026-07-14; RESOLVED 2026-08-06, see below).
# excList was, through v1.30, Step 5.4 routing ONLY -- stems/phrases the
# researcher explicitly saw and chose to discard at cluster confirmation.
# It did not include Step 3.1's mechanically-flagged terms (numerals,
# short tokens, stopwords/citations/units/author-names) or Step
# 3.2/3.2b's below-threshold non-selected terms, even though Step 3.1's
# own text calls those "excluded" too ("Default routing for all flagged
# terms: excList."). A comprehensive excList -- the true complement of
# incList, so that incList + excList accounts for every term with
# nothing able to silently fall through the gap -- was tracked as
# T-3.32, status DEFERRED: building it required wiring exclusion
# tracking across Steps 3.1, 3.2, 3.2b, and 5.4, none of which shared a
# running collection, and no real execution had ever computed that
# version to verify it against.
#
# RESOLVED (live evidence, the test book chapter, 2026-08-06): a researcher
# who had just confirmed a Phase 1 run with excList=0 flagged it, on
# sight, as reading like "nothing was excluded" when in fact 1,855 of
# 1,949 original terms had been -- exactly the confusion T-3.32
# anticipated. Built and verified against real data before merging here:
# `full_vocab` (every term Voyant's Terms export contains, unioned with
# Rule A's corpus-scan-only numeral tokens) minus the actual individual
# terms underlying the final incList (wildcard groups expanded back to
# their real corpus forms, e.g. `belief*` -> `belief`, `beliefs`).
# Round-tripped before trusting it: `exc_list ∪ inc_terms == full_vocab`
# (True) and `exc_list ∩ inc_terms == ∅` (0 overlap) on the real run.
# Scoped to **terms only** -- it does not extend to Step 1b's rejected
# phrase candidates, which this contract never claimed to track.
def build_comprehensive_exc_list(terms_df, rule_a_corpus_only, groups, singleton_terms):
    """rule_a_corpus_only: from Step 3.1 Rule A's mandatory corpus-scan
    pass -- numeral-shaped tokens found in the raw text but never
    appearing as their own Terms.tsv row. groups/singleton_terms: from
    Step 4.1/4.3, still in scope at this point in a single continuous
    run. Terms.tsv's own Term column is already lowercase (Voyant
    convention); groups/singleton_terms member forms are lowercased here
    to match it."""
    full_vocab = set(terms_df['Term'].astype(str).str.lower()) | set(rule_a_corpus_only)
    final_inc_terms = {t.lower() for t in singleton_terms}
    for members in groups.values():
        final_inc_terms.update(m.lower() for m in members)
    return sorted(full_vocab - final_inc_terms)

# NOTE (fixed, live evidence, another test corpus full-cycle test, 2026-07-31):
# `format_stem()` used to re-derive the wildcard here (`entry + '*' if entry
# in groups else entry`), because `stems_final` (Step 4.3) used to store bare
# prefixes without the star. Now that Step 4.3's own fix bakes the `*` into
# `stems_final` directly, this function's `entry in groups` check can never
# match (a starred string never equals a bare prefix key), so it silently
# degraded into a no-op that happened to still return the right string by
# coincidence -- dead code with a comment describing behavior it no longer
# performs. Removed; `stems_final` is already in its final display form.
base_terms = list(stems_final) + list(selected_phrases)
inc_list = sorted(t for t in base_terms if t not in excList_routed)
# excList_routed (Step 5.4) is not unioned in separately here: any term
# routed to excList at Step 5.4 was, by construction, already removed
# from stems_final/groups, so it is already part of the complement
# build_comprehensive_exc_list computes -- unioning it again would be
# redundant, not additive.
exc_list = build_comprehensive_exc_list(terms_df, rule_a_corpus_only, groups, singleton_terms)

phase1_state = {
    "corpusId":    corpus_id,            # str — the 32-char ID verified in Step 2;
                                          # lets Phase 3 read it instead of re-asking
    "incList":     inc_list,             # list of str — confirmed stems (Step 4.3) and
                                          # phrases (Step 1b), minus excList_routed
    "excList":     exc_list,             # list of str — Step 5.4 routing only; see
                                          # HONESTY NOTE above for what this omits
    "clusterDefs": [                     # list of dicts, one per cluster, in Phase 1 order
        {
            "name":  c['name'],          # str — full Phase 1 cluster name (not token)
            "stems": c['stems']          # list of str — stems exactly as in Step 5
        }
        for c in clusters_final
    ],
    "wordnetGrounding": {                # dict — tally from Step 3.5, carried forward
        "grounded":     tier_counts['grounded'],
        "weak":         tier_counts['weak'],
        "context_only": tier_counts['context_only'],
        "total":        total,
        "groundedUnreviewedDefaults": crosscheck_counts.get(
            "NOT REVIEWED (batch default, hypernym-domain pick applied unchecked)", 0),
            # int -- subset of `grounded` above that used Step 3.5's disclosed
            # batch-default mode (added 2026-07-15) rather than individual
            # researcher review or a genuine hypernym cross-check agreement.
            # Always present, 0 if the batch-default mode was never invoked
            # this run -- never omitted just because it's zero.
        "researcherCorrectedSenses": [
            {"term": t, "correctedStatus": s} for t, s in disambig_results
            if s.startswith("researcher-corrected")
        ],  # list of dicts, always present (empty list if none this run) --
            # terms where disambiguate()'s two criteria AGREED but were
            # found substantively wrong by direct verification against the
            # source text (added 2026-07-15; see the escalation-rules
            # HONESTY NOTE on `opacity`/`opacity.n.03` vs. `opacity.n.02`).
            # Deliberately a list, not a count -- knowing *which* terms had
            # an agreed-but-wrong sense caught and fixed matters more here
            # than how many, since this category is never systematically
            # swept for, only found when a term happens to get checked by
            # hand for some other reason.
    },
}
```

### 6.2 — Write and verify

**Filename always encodes `selection_method`** (added 2026-07-15 — see
Step 5.5's HONESTY NOTE for the real collision this prevents: running
both paths against the same corpus to compare them, which Step 1c has
always supported as a design, would otherwise have the second run
silently overwrite the first run's delivered JSON with no warning).

```python
output_path = f'/mnt/user-data/outputs/{corpus_name}-{selection_method}-phase1-state.json'

with open(output_path, 'w', encoding='utf-8') as f:
    json.dump(phase1_state, f, ensure_ascii=False, indent=2)

# Verify: reload and check counts
with open(output_path, 'r', encoding='utf-8') as f:
    verify = json.load(f)

assert isinstance(verify.get('corpusId'), str) and len(verify['corpusId']) == 32, \
    "corpusId missing or malformed"
assert len(verify['incList'])     == len(inc_list),          "incList length mismatch"
assert len(verify['excList'])     == len(exc_list),          "excList length mismatch"
assert len(verify['clusterDefs']) == len(clusters_final),    "clusterDefs count mismatch"
for c in verify['clusterDefs']:
    assert 'name'  in c and isinstance(c['name'],  str),  f"Missing name in cluster"
    assert 'stems' in c and isinstance(c['stems'], list), f"Missing stems in cluster {c['name']}"
wg = verify.get('wordnetGrounding', {})
assert {'grounded','weak','context_only','total','groundedUnreviewedDefaults',
        'researcherCorrectedSenses'} <= set(wg), "wordnetGrounding incomplete"

print(f"JSON written and verified: {output_path}")
print(f"  corpusId   : {verify['corpusId']}")
print(f"  incList    : {len(verify['incList'])} stems")
print(f"  excList    : {len(verify['excList'])} terms")
print(f"  clusterDefs: {len(verify['clusterDefs'])} clusters")
for c in verify['clusterDefs']:
    print(f"    {c['name']}: {len(c['stems'])} stems")
print(f"  wordnetGrounding: grounded={wg['grounded']} weak={wg['weak']} "
      f"context_only={wg['context_only']} (of {wg['total']}) -- "
      f"including {wg['groundedUnreviewedDefaults']} unreviewed batch defaults")
if wg['researcherCorrectedSenses']:
    print(f"  researcher-corrected senses ({len(wg['researcherCorrectedSenses'])}): "
          f"{[c['term'] for c in wg['researcherCorrectedSenses']]}")
```

### 6.2v — Report content verification (mandatory, run on the actual generated text)

**This step exists for the same reason Phase 2's Step 3.2v does.** Prose
instructions saying a section is "mandatory, every run" describe a target;
they do not guarantee the target was hit. A test run of this skill
(2026-07-01) delivered a Phase1-results.md that contained all of the
required *substance* — the WordNet grounding numbers, the environment
fallback disclosures — but reorganized it into a differently-named
`## Disclosed Limitations` section instead of the two headings specified
below, verbatim. The content was fine; the anchors weren't there. Nothing
caught that at the time because nothing checked the generated text against
the requirement — the requirement was only ever re-read as prose, the same
failure mode Step 3.2v was built to close in Phase 2.

Four literal headings are required to appear **verbatim**, as anchors, in
the generated Phase1-results.md content, in addition to whatever other
organization or summary sections (e.g. a consolidated "Disclosed
Limitations" section) are also useful for a human reader (v2.12 added the
third, `## Escalation verification limits`, to the two the 2026-07-01
incident originally motivated; v2.13 adds the fourth):

```python
required_headings = [
    "## WordNet grounding",
    "## Environment fallbacks used",
    "## Escalation verification limits",  # v2.12
    "## Cluster assignment grounding",    # v2.13
    "## Term selection provenance",       # PEEL 3 v1.0
]

missing = [h for h in required_headings if h not in md_report_text]

if missing:
    raise AssertionError(
        "Phase1-results.md is missing required verbatim heading(s): "
        + ", ".join(missing) +
        ". These are anchors other tooling (e.g. peel-protocol's "
        "verify_manifest.py) checks for mechanically. Reorganizing the "
        "same substance under a different heading name — as happened in "
        "the 2026-07-01 test run — passes a human read but silently "
        "breaks that checking. Add the missing heading(s) verbatim before "
        "presenting any files. A consolidated summary section elsewhere "
        "in the report is still fine and encouraged; it does not replace "
        "these anchors."
    )

print(f"Report content verification passed: all required headings present.")
```

Run this **after** `md_report_text` is fully assembled and **before**
`present_files` is called in Step 6.3. If it fails, fix the report text
and re-run this check — do not present a failing report and do not tell
the user it is ready.

### 6.3 — Report and present

Report to the user:
```
JSON inter-phase contract written:
  File       : [corpus_name]-[selection_method]-phase1-state.json
  corpusId   : <32-char ID> (carried forward — Phase 3 will not re-ask for it)
  incList    : <N> stems
  excList    : <N> terms
  clusterDefs: <N> clusters
    . <cluster 1 name> (<N> stems)
    . <cluster 2 name> (<N> stems)
    . ...
  WordNet grounding: <N> grounded, <N> weak/default, <N> context-only (of <N>)
  Cluster assignment grounding: <N> lexname, <N> hypernym, <N> context,
    <N> judgment-only, <N> phrase — see "## Cluster assignment grounding"
    in Phase1-results.md for the full per-stem rationale table
  Term selection provenance: <N/A -- automated selection, no researcher
    keywords supplied this run | <N> researcher-keyword> — see "## Term
    selection provenance" in Phase1-results.md
  Environment fallbacks used: <none | list, e.g. "boundary-trim stopwords:
    embedded portuguese list (no NLTK); POS filter: heuristic mode (no
    NLTK tagger)"> — see Phase1-results.md for full detail
  Escalations requiring researcher input: <N> (<N> flagged, <N> DIVERGENCE)
    — see "## Escalation verification limits" in Phase1-results.md for
    what these labels do and do not guarantee

Download this file. Upload it at the start of Phase 2.
If you edit the clusters before running Phase 2, edit the JSON
(or ask me to edit it and re-download) — do not rely on memory.
```

Use `present_files` to deliver:
1. `[corpus_name]-[selection_method]-Phase1-results.md` (human-readable
   record — includes the permanent `## WordNet grounding`, `## Environment
   fallbacks used`, `## Escalation verification limits`, `## Cluster
   assignment grounding`, and `## Term selection provenance` sections; all
   five are mandatory in every delivered report, present even when there
   is nothing to disclose (the last states "N/A — automated selection, no
   researcher keywords supplied this run" only when both conditions hold;
   a non-empty `researcher_keywords` list is reported regardless), so their
   absence is never itself ambiguous between "nothing happened" and "this
   version doesn't check")
2. `[corpus_name]-[selection_method]-phase1-state.json` (machine-readable
   inter-phase contract)
3. `[corpus_name]-[selection_method]-Phase1-clusters.html` (visual cluster
   table with Tableau20 colours)

The JSON is the authoritative input for Phase 2 and Phase 3. The MD is the
human-readable companion. The HTML snippet is a visual record of the final
cluster state and can be pasted into a Spyral HTML cell directly.


---

## Editing the JSON before Phase 2

If the user requests cluster corrections after Step 5.4 confirmation but before
running Phase 2, always edit the JSON programmatically (never manually in the
skill) and re-run Step 6.2 verification before presenting the updated file.

```python
# Example: move a stem from one cluster to another
with open(output_path, 'r', encoding='utf-8') as f:
    state = json.load(f)

# NOTE (fixed): the previous version of this example failed silently
# if the named cluster or stem didn't actually exist -- the loops
# would simply do nothing, with no error and no indication to the
# researcher that the edit they asked for did not happen. Both halves
# now confirm the change actually occurred before proceeding.

# Remove stem from source cluster
source = next((c for c in state['clusterDefs']
               if c['name'] == 'Source cluster name'), None)
assert source is not None, "Source cluster name not found in clusterDefs"
assert 'stem*' in source['stems'], (
    "'stem*' not found in source cluster -- nothing to move; "
    "check spelling against the confirmed cluster table"
)
source['stems'].remove('stem*')

# Add stem to target cluster
target = next((c for c in state['clusterDefs']
               if c['name'] == 'Target cluster name'), None)
assert target is not None, "Target cluster name not found in clusterDefs"
target['stems'].append('stem*')
target['stems'].sort()

# Re-verify and re-write
with open(output_path, 'w', encoding='utf-8') as f:
    json.dump(state, f, ensure_ascii=False, indent=2)
```

After every edit, re-run Step 6.2 verification, re-generate the HTML cluster
snippet (Step 5.5), and re-present all three files.
Never deliver an edited JSON without re-verification.


---

## Version History (appendix)

This appendix is a condensed changelog. Current behavior is documented in the
numbered steps above, not here — if this appendix and the steps above ever
appear to disagree, the steps above are authoritative. Version numbers below
follow this file's own history: v1.0 marks the start of the PEEL 3 series;
v2.0-v2.13 are inherited from the preceding PEEL 2 file and kept in sequence
for provenance; v1.1 onward continues the PEEL 3 line.

**v1.0.** Added a researcher-seeded term-selection path (Step 1c / Step 3s) as
an alternative to the fully-automated path: the researcher supplies seed
terms, expanded via disclosed stem-family and WordNet lexname/hypernym
sweeps. Co-occurrence/collocation-based expansion was considered and
explicitly not adopted, as structurally too close to delegated reading.
(This path was later removed entirely — see v1.28.)

**v2.0.** Added Step 6 (JSON serialization) as the mandatory final step,
producing the inter-phase contract for Phase 2.

**v2.1.** Step 5.4 now requires explicit routing of every removed stem to
incList or excList before serialization.

**v2.2.** Added Step 5.5: generate and deliver an HTML snippet of the final
cluster table immediately after confirmation.

**v2.3.** Added the Phrases TSV as a required input and Step 1b (N-gram
extraction and significance filtering), so significant multi-word collocates
are no longer invisible to the analysis.

**v2.4.** Added Step 0 (Corpus Cleanliness Inspection) to catch OCR/
manual-cleanup artifacts before Voyant tokenization; made phrase
boundary-trimming overlap-agnostic instead of depending on a Voyant export
setting; added permanent disclosure of the WordNet-grounded vs. context-only
term ratio to both the report and the JSON contract.

**v2.5.** Added three post-coverage-N filtering improvements: a
domain-specific stopword supplement (Rule E) for genre-infrastructure
vocabulary; a mandatory POS-filter pass flagging verbs/adverbs for batch
review; and example-vocabulary detection to catch concrete scene-words
inflated by a single recurring illustration or thought experiment.

**v2.6.** Six correctness fixes found by executing the code rather than
re-reading the prose: coverage-N selection undershot its stated 50% target;
a verification assert was tautological and could never fail; `top_n_terms`
was referenced but never defined; a cluster-editing example silently did
nothing on a missing name; a stopword-file dependency was loaded in the
wrong order; an unconditional NLTK download had no offline fallback. Added a
permanent "Environment fallbacks used" report section so a degraded-mode run
is visible after the fact, not just stated once mid-session.

**v2.7.** Found that single-criterion WordNet disambiguation could
confidently select the wrong sense for common polysemous words. Added an
independent hypernym-chain-plausibility cross-check: where the two criteria
agree, accept automatically; where they diverge, escalate to the researcher;
where no hypernym chain exists at all (common for adjectives/adverbs),
disclose the term as unchecked rather than counting it as agreement.

**v2.8.** The delivered report could reorganize required content under
different heading names, which would silently break any tooling checking for
the literal headings. Added Step 6.2v, a mechanical check on the assembled
report text asserting both required headings are present verbatim before
delivery.

**v2.9.** A missing Python execution environment could be silently
substituted with an unaudited reimplementation in another language,
presented with the same confidence as verified output. Added Step 0.9: a
mandatory precondition check, and on failure an explicit researcher choice
(switch environments; proceed fully unverified with every claim visibly
labeled as such; or, only if explicitly requested, an alternate-language
reimplementation delivered as an auditable file).

**v2.10.** The same class of gap existed specifically for WordNet: the
precondition check only confirmed a data path existed, not that the library
and data actually worked. Added Step 3.4b, mirroring Step 0.9's protocol and
distinguishing "library not installed" from "data missing or corrupted."

**v2.11.** Four algorithmic correctness bugs, found only by running the full
pipeline against real text and noticing the *results* looked wrong — not
visible from code review, since the code always ran and produced a
plausible-looking number. (1) The Zipf-elbow cross-check spiked at
tie-block boundaries rather than real elbows on high-hapax corpora; fixed
by collapsing ties before detecting the elbow. (2) The POS filter tagged
single words with no sentence context, a known-bad condition for
gerund/participle ambiguity; fixed by tagging in context from sampled real
sentences. (3) `disambiguate()` was fully defined but never actually driven
by any loop, so part-of-speech always defaulted to none and manufactured
false divergences; fixed by adding the driver loop. (4) Language
auto-detection picked whichever stopword list had the highest raw overlap
count, rewarding list size over fit; fixed by normalizing by list size.
Known limitation at the time: the POS-filter fix could not be executed
against a real tagger in the development environment, so it was verified for
logical correctness only, not by direct execution.

**v2.12.** A real run hit a disambiguation-escalation failure at a scale not
previously anticipated (many terms diverging, resolved by one blanket
decision). Independent verification then found a more serious problem: the
escalation mechanism can silently omit the correct WordNet sense from
consideration entirely — agreement between the two criteria is not the same
as correctness. No code fix in this version; the two-candidate escalation
design itself remains an open problem. Added a permanent "Escalation
verification limits" report section, present every run, disclosing this
residual risk regardless of whether the run's escalation count is zero.

**v2.13.** Found that Step 5's cluster-assignment review gave the researcher
only the finished stem-to-cluster table, with no record of which signal
(WordNet lexname, hypernym ancestry, TXT context, or judgment) placed each
stem, and no visible criterion for the ambiguity-escalation trigger. Added
Step 5.1b: a mechanical grounding-tier tag for every stem/phrase, assembled
into a permanent per-stem rationale table, plus a "Cluster assignment
grounding" report section. Known limitation at the time: not yet executed
against a real corpus; verified only for logical consistency with the
existing WordNet-grounding pattern.

**v1.1 (PEEL 3).** Reconciled this file with a real run that had diverged
from what v1.0 described. The lexname/hypernym sweep was formally abandoned
(confirmed structurally near-useless at scale — the ~45-category WordNet
lexname taxonomy collapses to touching most remaining vocabulary once a seed
list is large enough); a WordNet similarity sweep was added as its
replacement, disclosed as only a partial mitigation for wrong-sense
contamination; several unassigned/mistagged provenance variables were fixed;
concrete seed-list-size guidance was added after a 792-term seed list was
found to defeat the path's own accountability rationale; and the general
principle — disclosed linguistic relation only, never world knowledge — was
stated once explicitly rather than left implicit across separate cases.

**v1.2 (PEEL 3).** Substantially expanded Step 0 beyond OCR/wrap-artifact
scope. Added front-matter/publisher-metadata redaction (title and author
always kept, everything else redacted, located by content pattern since
position is unreliable — the same block can land mid-sentence in one
extraction and mid-abstract in another of the same source); made author
keywords redacted by default, with an option for the researcher to supply
her own; added footnote/endnote body-text detection and removal, matched to
in-text call numbers; broadened the footnote-call pattern to cover calls
fused onto trailing punctuation, not just words; added figure/table
handling (captions and calls always kept; numeric data tables dropped;
structured/categorical tables kept). Known limitation at the time: validated
by hand against real texts, but not yet implemented as executable code.

**v1.3 (PEEL 3).** Added Step 3.4c, a disambiguation-bypass pre-filter for
terms whose sense is already obvious from context, via two levers:
researcher-flagged N-grams (ready to use), and a Voyant Collocates-based
suggestion (recorded as designed but not validated against real data, and
not to be offered as available until it is).

**v1.4 (PEEL 3).** Added a third Step 3.4c lever, CONTEXTS-derived
consistency, and validated it against a real corpus. Also fixed a Voyant
CONTEXTS query-syntax error: a JS array of separate term strings silently
returns results for only one term; the working form is a single-element
array holding one pipe/quote-syntax string. Known limitation: only full
unanimous agreement across occurrences has been tested as the consistency
threshold.

**v1.5 (PEEL 3).** Corrected two wrong assumptions about the Terms TSV found
during a full-cycle execution test: the real column list differs from what
was documented, and the export is not reliably pre-sorted by frequency.
Step 3.2 now sorts explicitly in code rather than depending on upstream
Notebook configuration.

**v1.6 (PEEL 3).** Step 3.1's exclusion Rules A-D had no executable code at
all — every run had implemented them ad hoc from prose alone. This had a
real traced cost: a hardcoded author-name list missed a cited author, which
was then misresolved downstream to an unrelated WordNet sense. Added real
code for Rules A-D; Rule C's author-name check now requires inspecting a
candidate's actual occurrences in the source text rather than an asserted
list. Rules A/B/C's exclusion counts must now be disclosed, matching Rule
E's existing requirement. Known limitation: Rule B's short-token cutoff
still has no context-check exception path, so a short but significant term
(e.g. an acronym) cannot survive it.

**v1.7 (PEEL 3).** Added Step 3.3b, a corroboration check for terms ranked
just below the coverage-N cutoff, using phrase-anchoring and
collocate-concentration signals (both validated against real data). A third
lever, distribution-spread analysis, is recorded as designed but not
validated. Also fixed a collocate-export column-renaming bug: exact-string
header matching is unreliable across exports; switched to positional
renaming.

**v1.8 (PEEL 3).** The coverage-N threshold was a bare, unexplained 50%
constant with no researcher-facing confirmation. Replaced with an explicit
trade-off computation shown to the researcher every run (what a lower or
higher threshold would concretely gain or lose), with the chosen threshold
now part of the confirmation gate and the permanent report. Also disclosed:
`top_n_terms` can exceed the reported coverage-selected count once
researcher keywords are unioned in.

**v1.9 (PEEL 3).** Two fixes to the POS filter found by checking its real
execution against the file's own prose: a stale verification note still
claimed the tagger couldn't be executed in this environment after it
actually had been; and a real NameError-causing undefined-variable bug
existed in the example-vocabulary detector. Both fixed and re-verified
end-to-end.

**v1.10 (PEEL 3).** Step 4.1 (stem grouping) had no real algorithm and
referenced an undefined `groups` variable; its own worked examples didn't
match real output. Merged in a tested implementation: Porter-stem grouping,
longest-common-prefix computation, case-variant and
proper-noun/unresolved-term collision detection, and a scope-creep check.
These flags are now mandatory reporting, and the stated 70-75%
stem-compression target is now explicitly labeled a rough, corpus-dependent
expectation rather than a validated rule.

**v1.11 (PEEL 3).** Three fixes to Step 5 (semantic categorization):
`tag_cluster_grounding` could never actually return the 'hypernym' tag, due
to a missing parameter; Step 5.5's HTML-snippet code referenced a
`clusters_final` structure that nothing upstream ever built; and Step 5.3's
ambiguity-escalation rule had no operational definition of "ambiguous" and
no disclosure requirement, confirmed violated in practice (genuinely
ambiguous stems were silently resolved by an unwritten tie-break rule with
no record of the alternative or the reasoning). Added a "cascade
non-convergence" escalation criterion, a mandatory ambiguity log, and a
permanent "Cross-cluster ambiguity log" report section.

**v1.12 (PEEL 3).** Step 6 (JSON serialization) had never actually been
executable as written. Fixed three internal-consistency bugs in the
`clusterDefs`/`incList`/`excList` assembly logic, restoring real
executability and re-establishing Step 6.2's length assertion as a live,
mechanically-verified guarantee. Known limitation, left open deliberately:
whether `excList` should be comprehensive across all exclusion sources or
scoped narrowly to Step 5.4 routing — decided narrow for the time being
(later resolved comprehensively; see v1.31, item 5).

**v1.13 (PEEL 3).** Step 0 (0.1-0.4) was prose-only, with no executable
detection code at all. Implemented and verified against a real, messy raw
PDF extraction; found and fixed three bugs: the front-matter scanner's
search span was too narrow for real block placement; the
faulty-juxtaposition detector produced false positives on ordinary
inflected English; the typographic-noise detector conflated normal
typography with real encoding corruption. Known limitations disclosed: the
Notes/Endnotes detector doesn't cover per-page footnotes (a different
structural pattern), and figure/table handling was implemented but never
exercised against a corpus that actually contains figures or tables.
Separately fixed an unrelated markdown-fencing defect in Step 3.2b (a
missing opening fence caused a valid code block to render as prose).

**v1.14 (PEEL 3).** Steps 0.6/0.7 never explicitly instructed asking the
researcher to actually produce the TSVs via Voyant — a silent assumption
that data collection "just happens." Added an explicit instruction to ask
the researcher to run the Data Collection Notebook and upload the resulting
TSVs, since Claude cannot drive Voyant's native upload dialog itself.

**v1.15 (PEEL 3).** Two findings from a live run against a new corpus. (1)
A UTF-8 vs. cp1252 encoding check was misled by how a terminal renders an
undisplayable character rather than the actual bytes; the encoding-check
instruction now requires verifying by codepoint/byte inspection, not by how
a decoded string renders on screen. (2) The Rule D confirmation prompt's
"accept/reject" wording is ambiguous — it can mean either "confirm this is
a citation artifact" or "keep this term" — and produced a real near-miss.
Fixed by rephrasing with explicit EXCLUDE/KEEP language, which has no
symmetrical double meaning.

**v1.16 (PEEL 3).** A high divergence rate between disambiguation criteria
made full per-term review impractical on one run. Formalized a new
resolution mode — a disclosed default pick for unreviewed divergences —
with its own explicit status label so it can never be mistaken for genuine
agreement or researcher-confirmed review, and its own JSON field.

**v1.17 (PEEL 3).** Found a case where both disambiguation criteria
confidently agreed on the wrong WordNet sense for a term central to a
corpus's own argument — agreement is not the same as correctness. Added a
distinct "researcher-corrected" status, checked before the plain-agreement
check, so a hand-corrected sense is never misclassified as ordinary
agreement.

**v1.18 (PEEL 3).** Running both the automated and seeded selection paths
against the same corpus could silently overwrite one path's delivered
output with the other's, since output filenames didn't encode which path
produced them. Fixed by always encoding `selection_method` into output
filenames.

**v1.19 (PEEL 3).** The Step 5.5 HTML snippet did not comply with this
project's inline-style-only, fragment-first requirement for injection into
a Spyral text cell (an unstyled heading, no isolating wrapper) — injecting a
full HTML document instead corrupts Voyant's own stylesheet. Fixed by
wrapping the snippet and adding the missing inline style. A second bug found
while testing the fix: cluster names/stems were inserted unescaped, so an
ampersand in a name broke the output HTML — fixed with the same
HTML-escaping helper used elsewhere in this project.

**v1.20 (PEEL 3).** Steps 0.1-0.4 did no general spell-checking, so a plain
transposition typo would pass through undetected. Added Step 0.4b, flagging
unrecognized tokens as "likely typo" (with a suggested fix, for
low-frequency tokens) or "unrecognized recurring" (no suggested fix, treated
as possibly-intentional vocabulary). Fixed three bugs found while building
it against a synthetic test corpus: closed-class words were wrongly
flagged; plain Levenshtein distance didn't count transpositions as a single
edit; candidate ranking favored obscure dictionary matches over the
obviously-intended in-corpus word. Known limitations: real-word errors (a
typo landing on a different valid word) are structurally undetectable by
this method; false-positive/negative rates and runtime at real corpus scale
were not yet established.

**v1.21 (PEEL 3).** First real-corpus test of Step 0.4b found two bugs:
routine twice-cited author surnames were wrongly "corrected" (fixed by
raising the recurrence threshold so only tokens occurring exactly once are
typo-checked), and established `-ism`/`-ist` terminology had no
suffix-table entry (added). Known limitation: most remaining flagged rows
are proper nouns cited exactly once, a hard limit of a recurrence-based
heuristic, plus a few untranslated Latin phrases and residual morphology
gaps.

**v1.22 (PEEL 3).** Added a capitalization-based signal so hapax proper
nouns are rescued from typo-checking regardless of frequency, plus a small
hand-curated allowlist of common untranslated scholarly Latin terms. Known
limitation newly surfaced: a smart/curly apostrophe was not recognized by
the tokenizer's word-character class, splitting contractions like "doesn't"
and losing the trailing fragment entirely — disclosed as not yet fixed.

**v1.23 (PEEL 3).** Fixed the curly-apostrophe tokenization bug from v1.22.
This surfaced a second, previously-masked bug: correctly capturing
contractions as one token also meant correctly capturing possessives for
the first time, and neither the known-word check nor the capitalization
signal had ever handled a possessive — fixed by stripping a trailing `'s`
and re-checking the stem. Known limitation: the same missing-curly-apostrophe
pattern was confirmed to also exist in two other, separately-validated
steps, not touched by this fix.

**v1.24 (PEEL 3).** Fixed the curly-apostrophe bug at the two further sites
identified in v1.23's disclosure, correcting a mislabeling of which step
actually contained one of them. Known limitation: one of the two fixes could
only be verified in isolation, since a full end-to-end run wasn't available
for that corpus.

**v1.25 (PEEL 3).** Closed the remaining morphology gaps disclosed since
v1.20: five new derivational-suffix entries (each verified against real
WordNet output), plus a compound-split check kept local to Step 0.4b so it
cannot change the behavior of the separate faulty-juxtaposition check that
depends on the same shared known-word function. Considered and rejected a
generic `-ity` suffix entry after testing showed it doesn't actually resolve
the target case and creates a false-positive collision risk.

**v1.26 (PEEL 3).** Closed two further gaps found on a second real-corpus
test: one missing Latin-phrase entry, and a missing leading-prefix strip
(`un-`) that a suffix-only check couldn't catch. Known limitations: other
negation prefixes (`in-`/`im-`/`il-`/`ir-`, `non-`, `dis-`) remain
unhandled; a narrow edge case in the new prefix-strip logic was identified
and documented as not affecting real pipeline behavior.

**v1.27 (PEEL 3).** Merged in a fix to Step 3.1 Rule A (numeral exclusion):
the rule only ever queried the Terms TSV, missing numerals below Voyant's
own frequency cutoff and dotted subsection numbers the original pattern
couldn't match at any frequency. Fixed by adding a mandatory raw-corpus
regex scan run alongside the existing TSV-based check, with both sources'
counts now disclosed separately. Known limitation: verified by direct
execution against a synthetic test corpus; the original real-corpus
verification numbers could not be reproduced against this copy of the file.

**v1.28 (PEEL 3).** Four fixes from a full live run against a real corpus.
(1) The researcher-seeded term-selection path was removed entirely, at
explicit request — all path-branching and the former seed-intake/
expansion-sweep steps were deleted; the provenance tally survives in
simplified form. (2) Two steps read the raw, untrimmed Phrases TSV instead
of the boundary-trimmed candidate list, fabricating phrase-anchor evidence
for terms that should have been excluded — fixed to read the trimmed list.
(3) The mechanical stopword check didn't normalize curly vs. straight
apostrophes, letting contractions slip undetected into the final term set —
the third occurrence of this same bug class in different parts of this
file. (4) The wildcard `*` was never actually appended to grouped-stem
prefixes before serialization, which would have produced non-functional
Voyant search entries. Known limitation left open: whether proper-name
harvesting should require the same individual-confirmation discipline used
elsewhere, rather than bulk-including candidates.

**v1.29 (PEEL 3).** A scenario question surfaced a real gap: Step 0 assumes
a references/bibliography section has already been removed but never
actually detects or acts on one if present, so a large uncleaned
bibliography would distort every one of Step 3's statistical decisions
(coverage-N, Zipf elbow, WordNet grounding) before a later, too-late check
in Phase 2 could catch it. Known limitation, not fixed this pass: Phase 1
needs its own references/bibliography-section detector, analogous to the
existing Notes/Endnotes detector. In the meantime, this file and the
companion Phase 2 skill cross-reference the gap, and both researcher-facing
guides state the bibliography must be removed before Phase 1 begins.

**v1.30 (PEEL 3).** Three fixes from a cross-phase root-cause review after
a particularly troubled run. (1) Added a working-directory confirmation
step, since nothing previously resolved or disclosed the current directory
before the session-log script wrote to it, which had caused an unreconciled
split between phases' log locations. (2) Added a markdown-safe presentation
rule requiring stem/phrase lists shown to the researcher to be code-fenced,
after markdown italic-parsing was found to silently strip wildcard
asterisks from a pasted-back cluster list. (3) A separate incident (a
merged stopword list shipping with zero numeral exclusions) was traced to
this file's own earlier, deliberate decision to scope `excList` narrowly
rather than comprehensively — not reversed here (later resolved in v1.31);
the practical gap was instead closed downstream, in the companion Phase 3
skill.

**v1.31 (PEEL 3).** Five fixes from a single live test, each re-verified by
executing the actual edited function against a real corpus. (1) The
footnote-call regex only recognized a narrow set of characters immediately
before a digit, missing footnote calls landing after other punctuation —
widened, recovering over a third of real footnote-call sites that had been
silently missed. (2) The broken-hyphenation scan only checked for a hyphen
at the literal end of a line, finding zero breaks in a corpus where
line-wrap hyphens survive reflow mid-paragraph — generalized to a
corpus-wide scan. (2b) Closed a previously-disclosed gap: footnotes
interleaved throughout the body with no heading are now detected, along
with a classifier for whether removing that content splits a sentence
mid-word. (3) A possessive apostrophe-s form of an already-excludable short
token or stopword could survive both exclusion rules — fixed by stripping a
trailing `'s` and re-testing the base form. Known limitation: possessive
forms of excluded author names have the same gap but were confirmed to have
zero effect on the test run, so are left as a lower-priority follow-up. (4)
Investigated but did not fix a blind spot where the correct WordNet sense
never appears in either disambiguation criterion's top-ranked candidate;
two mitigations were tried and confirmed not to reliably help, and this is
documented as a confirmed open limitation rather than shipping an
ineffective fix. (5) Built and verified, for the first time, a
comprehensive version of `excList` covering all exclusion sources,
resolving the design question left open since v1.12/v1.30.
