---
name: peel3-phase2
version: 2.0
description: >
  Given a TXT corpus file and a Phase 1 JSON state file, produces a
  semantically-aware condensed text at a user-specified condensation rate
  (5–30%), with typed injection analysis and a conversational epistemic
  checkpoint before final HTML delivery.

  v3.0 is a full architectural redesign over v2.x. The central change is
  the replacement of constraint-based generation (rules preventing injection)
  with diagnostic-based generation (free generation followed by typed
  injection analysis and user-driven decisions). The golden rule is reframed:
  not "no injection" but "no invisible C-type injection."

  v2.0 (PEEL 3's own numbering — this file forks from and retires the
  `peel2-phase2`/`peel3-phase2` naming split, not a continuation of PEEL2's
  v3.x line) is peel2-phase2-v3.25 as its base, plus six specific features
  cherry-picked from the since-superseded peel3-phase2-v1.9 fork: a
  redesigned item-level enumerative-consistency check, native per-paragraph
  provenance, a formal writing-quality gate re-run after every revision
  (Step 3.0v), plain-text summaries as a standard fourth deliverable,
  F/T/R/C taxonomy display order, and the gray/blue/gold/red highlight
  color scheme. Everything else -- v3.25's own condensation-rate tolerance,
  no Step 0.9/high-reach/borderline checks beyond what v3.25 already had,
  no ascending-bundle default -- is unchanged from v3.25 (see this skill's
  internal version history for full rationale).

  The condensation rate is fixed at 5–30%. Rates outside this range are not
  supported and will be refused with an explanation.

  Triggers: "Run Phase 2", "Condense", "Summarize", "Reduce", or similar
  imperatives after Phase 1 has been completed. This is now the single file
  that trigger should resolve to -- peel2-phase2-v3.25.md and the old
  peel3-phase2-v1.9-SUPERSEDED.md are historical-only (see this skill's
  internal version history).

  Full version history (all prior version changes, kept verbatim for
  provenance): see "Version History (appendix)" at the
  end of this file.
---

# new-peel-phase3 — Argument-Following Condensation with Typed Injection Analysis

(Version number intentionally not restated here — see the frontmatter
`version:` field above. This heading used to hardcode "v3.9" and went
stale the moment the frontmatter moved past it; removing the duplicate
is the fix, not remembering to update two places at once. The same
principle already applies to the meta table via `SKILL_VERSION`, v3.11.)

## Contents

*(Added 2026-07-28. A plain index, not hyperlinks — this file's rendering
environment isn't guaranteed to support markdown anchors, so section
titles are listed as they appear, to be located by text search.)*

- Step 0 — Session log setup
- Step 0.9 — Environment precondition check
- Overview · Injection taxonomy
- 0. Inputs (0.0 Ingest Phase 1 JSON · 0.1 Pre-flight noise detection)
- Step 1 — Integrity check
- Step 2 — Ask for condensation rate(s)
- Step 3 — Generate the condensation freely
  (3.0v Writing-quality gate, mandatory, re-run after every revision, v2.0 ·
  3.1 Injection analysis · 3.1b Enumerative consistency (item-level
  presence, redesigned v2.0) · 3.1c High-reach compression · 3.1d
  Borderline classification · 3.2 Build the HTML, including
  `esc()`/`render_spans()`/`render_provenance()` (native per-paragraph
  provenance, added v2.0)/cluster-coverage computation, and 3.2v artifact
  verification)
- Step 4 — Conversational epistemic checkpoint
  (4.1 Responding to actions · 4.2 Closure condition · 4.3 Cluster-coverage check)
- Step 5 — Post-approval review
- Compliance rules · Error conditions · Editing clusters before Phase 2
- What vX changes from vY (v3.0 through v3.9 comparison tables)
- Version History (appendix) — full versioned changelog (v3.1 onward),
  moved out of the frontmatter for readability

## Step 0 — Start the session log (mandatory, before any other step)

Before doing anything else — before reading inputs, before greeting the
user — start the session log:

```bash
python3 peel-protocol/scripts/session_log.py init "[corpus-or-topic]-phase2-[YYYY-MM-DD]"
```

Then, for the remainder of the session, after EVERY conversational
turn — both the user's message and this assistant's response — append
it immediately:

```bash
python3 peel-protocol/scripts/session_log.py append "[session]" --role user   --text "[verbatim user message]"
python3 peel-protocol/scripts/session_log.py append "[session]" --role claude --text "[verbatim assistant response, or a faithful summary if very long]"
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

**NOTE (v3.19):** unlike Phase 1, this file has no pre-existing,
independently-defined `## Environment fallbacks used` section with its
own established meaning (Phase 1's version carries specific NLTK/WordNet
degraded-mode disclosures this file has no equivalent of) — so there is
no risk of blending two distinct meanings here. Record the Step 0.9
outcome directly under `## Environment fallbacks used` in
`Phase2-results.md` (Step 3.2's results-report build), mandatory every
run: state plainly that Python was confirmed available via
`python3 -c "print(2+2)"` returning `4` in the ordinary case, or, on
failure, which of the three options above was chosen and why. Set
`environment_precondition_status` here, once, immediately after this
check resolves (pass or fail) — the results-report builder reads it
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

Phase 2 produces a condensed version of the corpus at a user-specified rate.
Unlike v2.x, it does not attempt to prevent injection through generation
constraints. Instead it generates freely — following the argument of the
source text — and then analyses what it produced, classifying every span
not traceable to the source into one of four typed injection categories.
The user reviews a single HTML artifact that already reveals classifications
*and* sources (via collapsed-by-default toggles, see v3.4) and makes the
epistemic decisions from there. Nothing is hidden and nothing is finalised
without explicit user approval. There is no separate "diagnostic" stage —
see v3.5 changelog for why that was removed.

**The reframed golden rule:** No C-type injection (compression) may be
invisible in the final output. Every C-type span surviving user approval
must have its source passage discoverable in one click, directly beneath
the paragraph that contains it — via a native `<details>/<summary>`
disclosure toggle, collapsed by default so it does not disrupt continuous
reading, but never hidden behind navigation, search, or a separate
appendix. The toggle itself uses no `<script>` and no `onclick`; it is
pure browser-native behaviour, since Spyral's click handling and sanitizer
cannot be relied upon to deliver anything JS-driven (see v3.3 changelog).
This balance — collapsed by default, one click to reveal, no JS — was
arrived at after testing directly in Voyant/Spyral (see v3.4 changelog).

**Condensation rate:** 5–30% of source word count. This is the range
within which condensation is both meaningful and practically useful.
Rates below 5% produce fragments too short to be argumentatively
coherent. Rates above 30% approach the source too closely to justify
the condensation effort.

**Convergence:** Phase 2 does not converge to a perfect condensation.
It converges to a condensation the user finds epistemically acceptable.
The checkpoint (Step 4) may run for as many rounds as the user requires.

---

## Injection taxonomy

Every span in the condensed text that does not correspond to a verbatim
passage in the source is classified as one of the following four types.
The classification must be justifiable on request.

**Listed in ascending risk order: F < T < R < C.** The display order in
every table, legend, and report in this skill must match this risk order —
do not list C before R, or T before F (see v3.6 changelog).

| Code | Name | Definition | Epistemic risk |
|---|---|---|---|
| **F** | Framing | Short connective or orientating phrase (typically 1–6 words) with no propositional content. Examples: "On this view", "A first necessary condition", "By contrast", "Crucially". Function words and discourse markers. | Low. Introduces no content from outside the text. |
| **T** | Transition | A sentence or clause that signals argumentative structure, summarises what follows, or draws a conclusion across sub-arguments. Metalinguistic in character — about the text's argument, not about the world. Examples: "This paper argues that...", "The following sections examine...", "These considerations allow us to answer the question with which we began." | Medium. Unauthorised but metalinguistic. Does not add object-level content. |
| **R** | Reformulation | A single source sentence paraphrased: meaning preserved, wording substantially changed. Distinguished from C by operating on a single source sentence rather than collapsing multiple. | Medium-high. Surface change may introduce subtle shifts in meaning. |
| **C** | Compression | A span where two or more source sentences have been collapsed into fewer words, with the surface form rewritten. The content is source-derived but the wording is not. This is the epistemically significant injection type. | High. Invisible to the reader. May silently alter emphasis, omit qualifications, or merge distinct claims. Must be made visible. |

**Classification rules:**
- A span is F if it is short (≤6 words), contains no content-bearing nouns
  or verbs, and its removal would not change the propositional content of
  the surrounding text.
- A span is T if it is sentence-level, metalinguistic, and refers to the
  structure or argument of the text being condensed.
- A span is C if it is adjacent to or surrounded by matched source material
  and its propositional content derives from more than one source sentence.
- A span is R if its propositional content derives from a single identifiable
  source sentence that it paraphrases.
- When in doubt between C and R, classify as C (more conservative).
- When in doubt between F and T, classify as T (more conservative).

---

## 0. Inputs

| File | Role | Format |
|---|---|---|
| `*.txt` | Corpus text | Plain UTF-8 |
| `*-phase1-state.json` | Phase 1 inter-phase contract | JSON |
| `peel3-phase2-v2.0.md` | This skill file | Markdown |

(A previous version of this table also listed `wordnet.zip` as an
optional input. It was never referenced anywhere else in this file --
a copy-paste leftover from Phase 1, which genuinely needs it for
WordNet sense disambiguation; Phase 2 has no such dependency. Removed
rather than left as a misleading suggestion that a researcher setting
up a Phase 2 run needs to supply it.)

**CRITICAL — The JSON is the authoritative source.**
Do not parse the Phase 1 MD as a fallback. If only the MD is available,
report this and ask the user to upload the JSON.

---

## 0.0 — Ingest Phase 1 JSON

```python
import json, glob

json_files = glob.glob('/mnt/user-data/uploads/*phase1-state.json')
if not json_files:
    raise FileNotFoundError(
        "No *-phase1-state.json found. Upload the JSON produced by Phase 1."
    )

# NOTE (fixed, v3.20): the original code took json_files[0] unconditionally
# -- no disambiguation when more than one *-phase1-state.json matches.
# Confirmed as a real, non-hypothetical gap during this file's first live
# run: this project routinely produces exactly this two-file collision for
# a single corpus (automated-path and seeded-path JSONs), and Python's
# glob() does not guarantee match order. Never silently pick one -- stop
# and ask, the same disambiguation discipline Phase 1 itself already
# applies to its own output-filename collision (T-3.39, v1.18).
if len(json_files) > 1:
    raise RuntimeError(
        "Multiple *-phase1-state.json files found: " + ", ".join(json_files) +
        ". STOP -- do not guess or default to the first match. Ask the "
        "researcher explicitly which file is the intended input for this "
        "run before proceeding."
    )

with open(json_files[0], 'r', encoding='utf-8') as f:
    phase1 = json.load(f)

inclist     = phase1['incList']
exclist     = phase1['excList']
clusterdefs = phase1['clusterDefs']

assert len(inclist) > 0,     "incList is empty — re-run Phase 1."
assert len(clusterdefs) > 0, "clusterDefs is empty — re-run Phase 1."
```

**If the researcher has not yet indicated which JSON is intended** (e.g.
this is the first time multiple candidates appear in a session), ask
explicitly before re-running this step — do not infer intent from file
timestamps, naming, or any other heuristic.

Report to the user:

```
Phase 1 JSON loaded:
  File        : [filename]-phase1-state.json
  incList     : N stems
  Clusters    : N clusters
    . [name] (N stems)
    . ...
```

---

## 0.1 — Pre-flight noise detection

Check for and ask the user whether to strip:
- Title / author metadata (first non-section lines)
- Abstract / keywords block (pre-heading block ≤120 words)
- Terminal references / bibliography
- Embedded footnotes / endnotes (≥5 footnote-pattern lines)

Report pre-flight decisions before proceeding:

```
Pre-flight summary:
  Title/author lines  : stripped N lines | kept
  Abstract/keywords   : stripped N words | kept
  References section  : stripped from line N | kept
  Footnotes/endnotes  : stripped N lines | kept
  Adjusted word count : N words (down from N words)
```

---

## Step 1 — Integrity check

Load and verify the cleaned corpus. Report word count and last line.
If cleaned input < 100 words: report FAILED, stop, wait for user.

Also at this step: build the **source lexicon** (all unique content words
in the cleaned text), extract **section headings**, and build the
**enumerative structure map**. All three will be used in the injection
analysis (Step 3) and the enumerative consistency check (Step 3.1b).

```python
import re

def normalize_apos(text):
    return (text.replace('‘',"'").replace('’',"'")
                .replace('ʼ',"'").replace('`',"'"))

def build_source_lexicon(text):
    text = normalize_apos(text)
    tokens = re.findall(r"[a-zA-Z']+", text.lower())
    return set(tokens)

source_lexicon = build_source_lexicon(cleaned_text)
```

**Enumerative structure map.** Detect explicit cardinal/enumerative claims
mechanically — pattern-based, not a judgment call, the same way headings
are extracted — so a later compression can be checked against them:

```python
ENUM_ANNOUNCE = re.compile(
    r'\b(there are|these are|the following)\s+'
    r'(one|two|three|four|five|six|seven|eight|nine|ten|\d+)\s+'
    r'(reasons?|ways?|conditions?|arguments?|considerations?|'
    r'factors?|points?|steps?|criteria|premises?)\b',
    re.IGNORECASE
)
ORDINAL_MARKERS = re.compile(
    r'\b(first|second|third|fourth|fifth|sixth|seventh|eighth|ninth|tenth)\b'
    r'|^\s*\(?\d+[\.\)]\s',
    re.IGNORECASE | re.MULTILINE
)

# NOTE (fixed): the original approach counted every ORDINAL_MARKERS match
# anywhere in the lookahead window, with no requirement that they appear
# in the order a genuine enumerated list would use. This overcounts
# whenever an unrelated ordinal word appears elsewhere in the window --
# e.g. "First, X. Second, Y. Third, Z. ...years later, the first attempt
# at reform failed, prompting a second wave of proposals" would count 5,
# not the real 3, because "first"/"second" recur later as ordinary prose,
# not list items. Fixed by requiring markers to appear in strict
# increasing sequence (second only counts if found AFTER first, third
# only after that, ...), which a stray, out-of-order later mention
# cannot satisfy. Tested against five scenarios, including this exact
# overcounting shape both before and after the real list, before being
# trusted -- confirmed correct on clean cases and confirmed it stops
# counting at the true list boundary on both overcounting cases.
_ORDINAL_WORDS = ['first', 'second', 'third', 'fourth', 'fifth',
                  'sixth', 'seventh', 'eighth', 'ninth', 'tenth']

def count_ordinal_items(window, max_gap=1500):
    """
    Count enumerated list items in `window` by requiring ordinal markers
    to appear in strict sequential order, not merely anywhere in the
    text. Tries both textual ordinals ("first", "second", ...) and
    digit-prefixed list markers ("1.", "2)", ...) as alternative list
    styles, returning the larger of the two counts (a genuine list
    typically uses one style consistently, not both for the same list).
    `max_gap` bounds how far past the previous marker the next one may
    be found, so the sequence can't drift arbitrarily far into unrelated
    later content.
    """
    text_lower = window.lower()

    pos = 0
    textual_count = 0
    for word in _ORDINAL_WORDS:
        idx = text_lower.find(word, pos)
        if idx == -1 or idx - pos > max_gap:
            break
        textual_count += 1
        pos = idx + len(word)

    digit_marker_re = re.compile(r'^\s*\(?(\d+)[\.\)]\s', re.MULTILINE)
    digit_matches = [(m.start(), int(m.group(1)))
                      for m in digit_marker_re.finditer(window)]
    digit_count, expected, last_pos = 0, 1, 0
    for pos_i, n in digit_matches:
        if n == expected and pos_i - last_pos <= max_gap:
            digit_count += 1
            expected += 1
            last_pos = pos_i
        elif n == expected:
            break

    return max(textual_count, digit_count)

# NOTE (added, v2.0): extract_ordinal_items() and _label_tokens() below
# support the item-level enumerative-consistency redesign in Step 3.1b --
# see the NOTE at check_enumerative_consistency() for why the inherited
# v3.x/v1.9 announcement-re-matching approach was replaced. This function
# deliberately mirrors count_ordinal_items()'s own strict-sequence marker
# logic (same ordinal words, same max_gap, same textual-vs-digit
# tie-break) so the two never disagree about *where* the list boundaries
# fall -- only about what gets extracted at each boundary. count_ordinal_
# items() itself is left unchanged and unused by 3.1b as of v2.0; kept in
# case a future check still needs a bare count.
_LABEL_STOPWORDS = {
    'the', 'a', 'an', 'of', 'to', 'is', 'are', 'was', 'were', 'be', 'been',
    'being', 'and', 'or', 'but', 'that', 'this', 'these', 'those', 'it',
    'its', 'as', 'by', 'in', 'on', 'at', 'for', 'with', 'from', 'into',
    'onto', 'than', 'then', 'so', 'not', 'no', 'can', 'could', 'will',
    'would', 'should', 'may', 'might', 'must', 'we', 'our', 'they',
    'their', 'he', 'she', 'his', 'her', 'you', 'your', 'my', 'which',
    'who', 'whom', 'whose', 'what', 'when', 'where', 'how', 'why',
}

def _label_tokens(span_text, max_tokens=6):
    """
    Reduce a raw item span to its salient content-word tokens, for
    presence-matching against the condensed text later -- not for
    display (span_text itself is kept separately for that). Short
    function words are dropped; the first `max_tokens` remaining tokens
    are kept in source order, since the earliest content words after an
    ordinal marker are typically the item's own name (e.g. for a list such
    as "First, extrapolation... Second, conversion... Third,
    augmentation...", each item's own name appears in exactly this
    position, confirmed by hand-tracing against real condensation
    drafts). Deliberately conservative: this is a presence check for the
    item's own name, not a paraphrase-matcher for the sentence that
    introduced it.
    """
    tokens = re.findall(r"[a-zA-Z']+", span_text.lower())
    content = [t for t in tokens if len(t) >= 4 and t not in _LABEL_STOPWORDS]
    return content[:max_tokens]

def extract_ordinal_items(window, max_gap=1500):
    """
    Like count_ordinal_items() above, but returns the actual item spans
    instead of just a count. Reuses the identical strict-sequence marker
    detection for both textual ("First, ... Second, ...") and digit
    ("1. ... 2. ...") list styles, then slices the window between
    consecutive markers to get each item's own text.
    """
    text_lower = window.lower()

    textual_positions = []
    pos = 0
    for word in _ORDINAL_WORDS:
        idx = text_lower.find(word, pos)
        if idx == -1 or idx - pos > max_gap:
            break
        textual_positions.append(idx)
        pos = idx + len(word)

    digit_marker_re = re.compile(r'^\s*\(?(\d+)[\.\)]\s', re.MULTILINE)
    digit_matches = [(m.start(), int(m.group(1)))
                      for m in digit_marker_re.finditer(window)]
    digit_positions, expected, last_pos = [], 1, 0
    for pos_i, n in digit_matches:
        if n == expected and pos_i - last_pos <= max_gap:
            digit_positions.append(pos_i)
            expected += 1
            last_pos = pos_i
        elif n == expected:
            break

    # Same style tie-break as count_ordinal_items()'s max(): use
    # whichever style found more items; on an exact tie prefer textual
    # (arbitrary but deterministic -- textual ordinals are the more
    # common style in this project's actual source material so far).
    positions = (textual_positions if len(textual_positions) >= len(digit_positions)
                 else digit_positions)
    if not positions:
        return []

    items = []
    for i, start in enumerate(positions):
        end = positions[i + 1] if i + 1 < len(positions) else min(start + 400, len(window))
        span_text = window[start:end]
        items.append({
            'span_text':  span_text.strip()[:200],  # for display only
            'key_tokens': _label_tokens(span_text),
        })
    return items

# NOTE (fixed): this function was called below but never defined anywhere
# in the file -- any source using a word-form cardinal ("there are four
# reasons") crashed this step outright with a NameError. ENUM_ANNOUNCE's
# own capture group can produce either a word (one-ten) or an arbitrary
# digit sequence (\d+), case-insensitively, so this must handle both --
# tested against all six shapes before being trusted.
_WORD_NUMS = {
    'one': 1, 'two': 2, 'three': 3, 'four': 4, 'five': 5,
    'six': 6, 'seven': 7, 'eight': 8, 'nine': 9, 'ten': 10,
}

def word_to_num(s):
    s = s.lower().strip()
    if s in _WORD_NUMS:
        return _WORD_NUMS[s]
    if s.isdigit():
        return int(s)
    raise ValueError(
        f"Cannot convert {s!r} to a number -- not a recognized word-form "
        f"cardinal (one-ten) or digit sequence. This means ENUM_ANNOUNCE "
        f"matched something this function was never taught to handle --"
        f" treat as a real gap in the pattern, don't silently swallow it."
    )

def build_enumerative_map(text):
    """
    Returns a list of dicts, one per detected cardinal announcement:
    { 'claim_text': str, 'declared_n': int, 'location': int,
      'items': list[{'span_text': str, 'key_tokens': list[str]}] }

    NOTE (changed, v2.0): 'items' replaces the v3.x/v1.9-inherited
    'ordinal_count' field -- Step 3.1b now checks presence of each named
    item individually rather than comparing a restated count to a
    re-found ordinal count. See the NOTE at check_enumerative_consistency
    (Step 3.1b) for the full rationale.
    """
    structures = []
    for m in ENUM_ANNOUNCE.finditer(text):
        declared_n = word_to_num(m.group(2))
        window = text[m.end(): m.end() + 4000]  # bounded lookahead
        structures.append({
            'claim_text': m.group(0),
            'declared_n': declared_n,
            'location':   m.start(),
            'items':      extract_ordinal_items(window),
        })
    return structures

enumerative_map = build_enumerative_map(cleaned_text)

# NOTE (fixed): Step 4.3's cluster-coverage check compares the condensed
# text's cluster coverage against a "source target" -- but nothing in
# this file ever computed that target; cluster_coverage() was only ever
# shown being called on the condensed text. As a hard, checkpoint-
# blocking condition with no way to produce half of its own comparison,
# it was not actually runnable as specified. Fixed here, not in Step
# 4.3, because everything this needs -- clusterdefs/inclist (already
# loaded in Step 0.0) and cleaned_text (already in scope in this step)
# -- is already available at this exact point, alongside the other
# things Step 1 derives once from the source (lexicon, headings,
# enumerative map). Computing it in Step 2 would mean loading the same
# inputs a second time for no benefit; Phase 1 is the wrong place
# entirely, since clusterDefs there is a static stem-to-cluster
# assignment, never a frequency measurement against any specific text --
# there is nothing to "recompute from Phase 1," this comparison has
# never been computed anywhere before now.
#
# cluster_coverage() itself is defined once, here, and reused unchanged
# by Step 4.3 against the condensed text -- not redefined there.

def stem_matches(stem, term):
    if stem.endswith('*'):
        return term.startswith(stem[:-1])
    return term == stem

def cluster_coverage(text, clusterdefs, inclist):
    tokens = re.findall(r"[a-zA-Z']+",
                        normalize_apos(text).lower())
    coverage = {}
    for cluster in clusterdefs:
        hits = sum(
            sum(1 for t in tokens if stem_matches(stem, t))
            for stem in cluster['stems']
        )
        coverage[cluster['name']] = hits
    total = sum(coverage.values())
    return {
        name: round(hits/total*100, 1) if total > 0 else 0.0
        for name, hits in coverage.items()
    }

source_coverage = cluster_coverage(cleaned_text, clusterdefs, inclist)
```

Report to the user alongside the lexicon/heading report:

```
Enumerative structures detected in source: N
  . "there are four reasons..." (declared 4, found 4 ordinal markers) — line 142
  . ...

Source cluster-coverage baseline (target for Step 4.3):
  [cluster name]  XX.X%
  ...
```

---

## Step 2 — Ask for condensation rate(s)

Ask the user to choose between a custom rate (or set of rates) and the
default bundle:

```
What condensation rate would you like? (5–30%)

  — Give me one or more specific rates (e.g. "20%", or "15% and 25%")
  — Or say "default bundle" for 10/15/20/25% — a four-point ladder useful
    for comparing how aggressively a source can be condensed before
    topical balance and argument structure start to break down

Typical single rates: 20% for a dense argument-following condensation,
                       25% for a fuller one that preserves more context.
```

**If the user requests the default bundle:** generate all four rates
(10%, 15%, 20%, 25%) by running Steps 3–4 for each, in ascending order.
Building each rate by expanding the previous rate's condensation (rather
than drafting each from scratch) is the expected, efficient approach: the
fixed costs of source ingestion (Step 1), the S[] style dictionary, and
the located source quotes used in toggles are shared across all four
builds, and adjacent rates share much of their drafted content and span
classifications. Do not silently drop 10% from the bundle to save effort —
the tightest rate is also the one most likely to surface a cluster-coverage
WARN or a structurally aggressive C-type span, which is exactly the kind
of result this comparison is meant to expose (see v3.7 changelog). Report
all four word counts, injection summaries, and cluster-coverage tables
together once all four are built, so the user can compare the ladder in
one view before opening the checkpoint (Step 4) on any individual rate.
**This comparison view is an additional chat-level summary table — it is
never a replacement for, or a simplified version of, any individual
rate's full Step 3.2 HTML build.** Each of the four rates still gets its
own complete structural/span-highlighted/toggle-equipped fragment and
standalone file, verified by Step 3.2v, exactly as a single custom rate
would. "Compare in one view" describes the chat report, not a different
HTML artifact.

**If the user requests one or more custom rates:** proceed exactly as in
prior versions — accept 5–30% for each requested rate. If any requested
rate falls outside this range, explain:
- Below 5%: too short to preserve argumentative coherence.
- Above 30%: too close to the source to justify the condensation effort.
  Suggest reading the source directly.

Ask for clarification if the rate (or the bundle-vs-custom choice) is
ambiguous.

---

## Step 3 — Generate the condensation freely

**This is the core architectural change from v2.x.**

Generate the condensed text by following the argument of the source,
not by scoring and stitching sentences. The goal is a text that:

1. Is readable and argumentatively coherent from beginning to end.
2. Faithfully represents the source's argument, structure, and conclusions.
3. Reaches the target word count (±5% tolerance at this stage).
4. Uses the source's own vocabulary wherever possible, but is not
   constrained to do so.

**Guidance for free generation:**

- Follow the argumentative structure of the source, not its sentence order.
  Select and compress content by asking: *what does the reader need to
  understand to follow the next step of the argument?*
- Preserve the source's key distinctions, qualifications, and conclusions.
  Do not flatten nuance for the sake of brevity.
- Use section headings from the source to signal argumentative transitions.
  Do not invent new section headings.
- When compressing, prefer to keep the source's own wording for the
  conceptually dense passages (definitions, distinctions, conclusions).
  Rewrite only where the source is redundant or where multiple sentences
  make the same point.
- Do not introduce examples, framings, or conclusions not present in
  the source.

After generating, compute the actual word count:

```bash
echo "[condensed text]" | wc -w
```

If outside ±5% of target: adjust before proceeding to Step 3.0v.

### 3.0v — Writing-quality gate (mandatory, added v2.0; re-run after every revision)

**Ported and generalized from peel3-phase2-v1.9-SUPERSEDED's Step 3.0v
("Coherence read-through," added there at v1.5), broadened here beyond
coherence alone to also cover spelling, grammar, and other cohesion
defects.** v1.9's original closed a real, confirmed gap: Step 3's own
stated goal #1 ("readable and
argumentatively coherent from beginning to end") had no corresponding
*check* — only the word-count tolerance above stood between free
generation and the researcher's checkpoint. v3.25 (this file's base)
never carried any version of this step at all — it goes straight from
word-count adjustment to injection analysis, the same gap v1.9 found and
closed, just never ported back.

**What this checks — four items inherited from v1.9, three added:**

1. **Sentence fragments** with no finite verb. *(v1.9)*
2. **Dangling transitions** — paragraph-opening sentences with no
   subject/anchor connecting them to what precedes. *(v1.9)*
3. **Grammaticality regressions introduced by trimming** — dropped
   articles, broken agreement, orphaned conjunctions. *(v1.9)*
4. **Uncaught classification gaps** — any span that was drafted but
   never logged for Step 3.1 classification. *(v1.9)*
5. **Spelling errors**, anywhere in the draft. *(added, v2.0)*
6. **Discourse-level redundancy** — two passages, anywhere in the draft,
   restating the same claim in near-identical wording. This is not
   merely a v1.9 gap category renamed: a checklist-style scan against
   fixed categories does not reliably catch it, because it only becomes
   visible when passages that were originally far apart in the source
   end up adjacent after intervening content is cut for length —
   collapsing that gap without checking what became adjacent is exactly
   what a genuine first read, not a checklist scan, is meant to catch.
   *(added, v2.0)*
7. **Dangling references** — a phrase referring back to content that was
   cut in a later edit (e.g. "the rest of *its many applications*" after
   the applications list itself was trimmed away). This is the same
   class of failure as item 6, but introduced by an edit made *after*
   the first 3.0v pass had already run and never re-checked — which is
   why item 8 below exists. *(added, v2.0)*

**Required action, unchanged from v1.9:** read the complete assembled
draft top-to-bottom as continuous prose, the way a first-time reader
would — not span-by-span, not by re-checking the word count, and not as
a checklist scan against the seven items above treated as boxes to tick.
Items 6 and 7 above are exactly the kind of defect a checklist-style,
pattern-matching pass misses, because the checker's memory of the
original intent stands in for a genuine reader's fresh encounter with
the text. A pass that finds nothing because it wasn't really read is not
a clean result — it's an unexamined one.

8. **Re-run after every revision, not once** *(changed, v2.0 — this is
   the generalization beyond what v1.9 itself specifies, not merely a
   port of it).* v1.9 places this gate once, between word-count
   adjustment and Step 3.1, and never revisits it. That is insufficient
   in practice: an edit made to fix a defect the gate already caught can
   itself introduce a new one (e.g. a dangling reference left behind
   after trimming) that the first pass has no way to see, since it ran
   before that edit existed. Any edit to the condensed text made
   anywhere in this skill's
   workflow — during the ±5%/±2% word-count loops, during Step 3.1b/c/d
   fixes, during post-checkpoint revision at Step 4 — requires a fresh
   full read-through before that edit's output is presented as final,
   not a re-check of only the lines that were touched.

**Placement.** After the ±5% word-count check above, before Step 3.1 —
unchanged from v1.9, and for the same reason: revising an over/under-
length draft first would just get re-broken by trimming; running this
after Step 3.1 risks span-text mismatches between recorded spans and the
actual condensation, since classification must run against final,
stable text.

**Loop condition.** If a fix changes the word count, return to the word-
count tolerance check above before re-attempting this read-through. Do
not proceed to Step 3.1 — or, per item 8, to delivery after any later
revision — until one full read-through produces no further fixes.

**Disclosure (mandatory, every run and every re-run).** Record this
step's outcome in the results report — what was found and fixed, or
"nothing found this run" if the read-through was clean — the same
pattern already used for `## Environment fallbacks used` and `##
Classification verification limits`. A clean read-through is a real,
reportable outcome, not something to omit for having nothing to say. On
a re-run triggered by a later revision, state explicitly what revision
triggered it (e.g. "re-run after the enumerative-check fix at Step
3.1b").

### 3.1 — Injection analysis

Identify every span in the condensed text that does not correspond to
a verbatim passage in the source. For each such span, assign an
injection type (F, T, C, or R) according to the taxonomy above.

**Mechanical alignment procedure:**

**NOTE (fixed, v3.20):** `in_source()` (a single-phrase membership test)
was real code, but the actual longest-matching-run *scan* that is
supposed to use it — described only as a comment ("For each token...
find the longest run of consecutive tokens that matches a passage in the
source") — was never implemented, the same PROSE-ONLY-disguised-as-done
shape as the structural block parser (see that section's own v3.20 fix
note). This mattered concretely once `source_verbatim_pct` needed a real,
independently-computed verbatim-overlap figure to be checked against (see
that metric's own v3.20 fix note below) — there was no code anywhere in
this file that could produce one. Fixed with an actual scan, re-verified
against real data: run against the real 10% condensation, it found 19.4%
of tokens verbatim-matched to the source (57 matched runs) — independently
confirming the divergence `source_verbatim_pct` had been silently masking.

```python
def in_source(chunk_words, source_lower, min_window=4):
    phrase = ' '.join(w.lower() for w in chunk_words)
    phrase_clean = re.sub(r'[^\w\s]', '', phrase)
    src_clean = re.sub(r'[^\w\s]', '', source_lower)
    return phrase_clean in src_clean

def scan_verbatim_overlap(condensed_text, source_text, min_window=4, max_window=40):
    """
    For each position in the condensed text, finds the longest run of
    consecutive tokens (capped at max_window for speed) that appears
    verbatim in the source, via in_source(). Tokens not covered by any
    matched run are unmatched. Returns (matched_token_count,
    total_token_count, matched_runs) -- matched_runs is a list of
    (start_idx, end_idx, tokens) for provenance/spot-checking.
    """
    source_lower = source_text.lower()
    cond_tokens = re.findall(r"[A-Za-z']+", condensed_text)
    i, matched_runs = 0, []
    while i < len(cond_tokens):
        best_len = 0
        for L in range(min(max_window, len(cond_tokens) - i), min_window - 1, -1):
            if in_source(cond_tokens[i:i + L], source_lower):
                best_len = L
                break
        if best_len >= min_window:
            matched_runs.append((i, i + best_len, cond_tokens[i:i + best_len]))
            i += best_len
        else:
            i += 1
    matched_token_count = sum(end - start for start, end, _ in matched_runs)
    return matched_token_count, len(cond_tokens), matched_runs

# For each token in the condensation, find the longest
# run of consecutive tokens that matches a passage in
# the source (minimum window = 4 tokens).
# Tokens not belonging to any matched run are unmatched
# and must be classified.
```

**Classification heuristics (in order of application):**

1. If the span is ≤6 words and contains no content-bearing nouns
   or verbs beyond those in the immediately surrounding matched spans
   → classify **F**.

2. If the span is sentence-level and its subject is the text, the
   argument, the paper, or the sections (metalinguistic subject)
   → classify **T**.

3. If the span's propositional content can be traced to a single
   identifiable source sentence that it paraphrases
   → classify **R**.

4. Otherwise (span compresses or merges multiple source sentences)
   → classify **C**.

5. When in doubt between C and R → **C**.
   When in doubt between F and T → **T**.

**For every classified span, record:**
- The span text and its type (F/T/R/C)
- For C-type and R-type: the source sentences it derives from (by
  paragraph and sentence index) and a one-sentence explanation of what
  was merged, omitted, or reworded
- For F-type and T-type: the span text alone is sufficient — there is no
  source passage to cite, since these types by definition introduce no
  content the source doesn't already establish

This record is used both to justify the classification at the checkpoint
and to build the inline source toggles in the HTML (Step 3.2) — there is
only one such record-to-HTML pass, not two (see v3.5 changelog).

**NOTE (fixed):** the injection-summary counts (F/T/R/C spans,
source-verbatim %) were only ever narrated as placeholders in the chat-
report template ("F (framing): N spans") -- no code anywhere actually
computed them, the same gap as several other findings today. `c_count`
and `r_count` were referenced in Step 3.2v via `c_spans_recorded`/
`r_spans_recorded`, but those were never formally defined either. Fixed
by collecting every classified span into one list as Step 3.1 runs:

```python
# all_spans: one dict per classified span, appended as Step 3.1's
# classification proceeds:
#   { 'span_id': str, 'type': 'F'|'T'|'R'|'C', 'text': str,
#     'source_refs': list[tuple[int, int]] (paragraph_idx, sentence_idx),
#     'justification': str (C/R only) }
all_spans = []  # populated during classification above

f_spans = [s for s in all_spans if s['type'] == 'F']
t_spans = [s for s in all_spans if s['type'] == 'T']
r_spans = [s for s in all_spans if s['type'] == 'R']
c_spans = [s for s in all_spans if s['type'] == 'C']
f_count, t_count, r_count, c_count = (len(f_spans), len(t_spans),
                                       len(r_spans), len(c_spans))

# c_spans_recorded / r_spans_recorded, referenced by Step 3.2v, are
# these same lists -- not separately maintained.
c_spans_recorded, r_spans_recorded = c_spans, r_spans

injected_words = sum(len(s['text'].split()) for s in all_spans)
condensed_words = len(condensed_text.split())

# NOTE (fixed, v3.20): this was previously called `source_verbatim_pct`
# and reported to the researcher as "Source-verbatim: N% of tokens" --
# but it measures "words NOT inside any classified F/T/R/C span," not
# actual verbatim overlap with the source. Those diverge sharply whenever
# a C/R span quotes source material inline (e.g. a compression span that
# embeds a direct quotation) -- confirmed by direct comparison on real
# data: this metric read 5.2% on the real 10% condensation, while an
# independent, mechanical token-alignment scan (scan_verbatim_overlap(),
# defined above) found 19.4% genuine verbatim overlap on the identical
# text. A researcher reading "Source-verbatim: 5.2%" would reasonably
# read that as "how much of this condensation is literally copied from
# the source" -- which is the wrong, higher number. Renamed to what it
# actually measures, and the real verbatim-overlap figure is now reported
# alongside it, not instead of it.
non_injected_pct = (
    round(100 * (1 - injected_words / condensed_words), 1)
    if condensed_words else 0.0
)
verbatim_matched, verbatim_total, _ = scan_verbatim_overlap(condensed_text, source_text)
verbatim_overlap_pct = (
    round(100 * verbatim_matched / verbatim_total, 1) if verbatim_total else 0.0
)
```

### 3.1b — Enumerative consistency check

Runs after 3.1, before the HTML is built (Step 3.2). For each structure in
`enumerative_map` (built in Step 1), check whether each item the source
individually named under that structure's cardinal claim still has a
surviving, identifiable trace somewhere in the condensed text.

**NOTE (redesigned, v2.0):** the v3.x/v1.9-inherited approach here worked
by re-finding a matching `ENUM_ANNOUNCE` sentence in the condensed text
and comparing its restated count to a re-counted number of ordinal
markers after it. Tested against several real condensation drafts,
this failed in two independent ways: (1) it does
not recognize legitimate paraphrases of the announcement sentence itself
("Humphreys identifies three ways" does not match `ENUM_ANNOUNCE`'s fixed
"there are/these are/the following N ..." phrasing, even when the
underlying claim survived intact); (2) even after widening the
announcement pattern, the ordinal-marker-counting fallback
cross-contaminated with an unrelated "First,...Second,..." pair elsewhere
in the same lookahead window, producing a false MISMATCH against
correctly-preserved content. Freely paraphrased condensation — exactly
what this skill is designed to produce — routinely breaks
announcement-sentence matching. What actually matters for document-level
consistency is whether the source's individually named items survived,
not whether the sentence that first announced them did in any
recognizable form. Redesigned around item-level presence instead,
using the `items` field `build_enumerative_map` (Step 1) now extracts
alongside `declared_n`. Verified by hand-tracing several real drafts'
actual wording against this redesign: every named item present was
correctly reported OK in each case.

```python
def item_present(item, condensed_lexicon):
    """
    True if this source item's own name survived into the condensed
    text, independent of whether the sentence that originally announced
    it survived in any recognizable form. `condensed_lexicon` is the
    same tokenization build_source_lexicon() (Step 1) already applies to
    the source, applied here to the condensed text -- one tokenization
    convention reused throughout the file, not a second one invented for
    this check alone. Returns None (not True/False) when the item has no
    extractable content word at all -- an unresolvable case, not a
    negative result.
    """
    if not item['key_tokens']:
        return None
    # Require the single longest key token (the most distinctive, least
    # likely to be a coincidental common-word match) to survive.
    strongest = max(item['key_tokens'], key=len)
    if strongest in condensed_lexicon:
        return True
    # Light suffix tolerance for minor morphological drift
    # (extrapolation/extrapolating, conversion/converts) -- deliberately
    # not full stemming, just enough to not flag a same-word inflection
    # change as a dropped item.
    for suffix in ('ions', 'ion', 'ing', 'es', 'ed', 's'):
        if strongest.endswith(suffix):
            stem = strongest[: -len(suffix)]
            if len(stem) >= 4 and any(tok.startswith(stem) for tok in condensed_lexicon):
                return True
    return False

def check_enumerative_consistency(enumerative_map, condensed_text):
    """
    For each structure detected in the source, check whether every item
    it individually named survived into the condensed text. Item-level,
    not count-level: a deliberate, correct revision that drops or merges
    a named item is exactly what this is meant to catch, the same intent
    the v3.x/v1.9-inherited count-comparison had, just implemented
    without depending on the announcement sentence's own wording
    surviving recognizably.
    """
    condensed_lexicon = build_source_lexicon(condensed_text)
    results = []
    for structure in enumerative_map:
        if not structure['items']:
            # Declared count was regex-detected but no item spans could
            # be extracted from the source window at all -- can't check
            # item-level presence. Escalate rather than assume
            # consistency, same conservative default used throughout
            # this skill (e.g. Step 3.1's "when in doubt, classify as C"
            # rule).
            results.append({**structure, 'item_status': [], 'status': 'UNRESOLVED'})
            continue

        item_status = [
            {**item, 'present': item_present(item, condensed_lexicon)}
            for item in structure['items']
        ]

        if any(s['present'] is None for s in item_status):
            status = 'UNRESOLVED'
        elif all(s['present'] for s in item_status):
            status = 'OK'
        else:
            status = 'MISMATCH'

        results.append({**structure, 'item_status': item_status, 'status': status})
    return results

enumerative_check = check_enumerative_consistency(enumerative_map, condensed_text)
```

```
Status:
- OK: every item the source individually named under this cardinal claim
  has a surviving, identifiable trace in the condensed text -- whether
  or not the sentence that originally announced the claim survived in
  any recognizable form.
- MISMATCH: at least one named item has no identifiable trace in the
  condensed text. Always flag; always await user decision before the
  checkpoint (Step 4) can close. Same severity tier as a DARK or WARN
  cluster (Step 4.3) — a blocking item, not a colored span the user
  might skim past.
- UNRESOLVED: this check could not extract clean item-level content from
  the source window (e.g. no content word survived stopword-stripping
  for one or more items), so item-level presence cannot be verified
  mechanically. Always flag; ask the researcher to confirm by reading,
  rather than silently passing or failing.
```

A C-type compression can be entirely correct by every rule in Step 3.1 —
adjacent to matched source material, derived from more than one source
sentence — and still leave the document self-contradictory if it merges
two items under an explicit "there are N reasons" claim that the source
itself asserts. The injection taxonomy classifies provenance span by
span; it has no mechanism for checking this document-level consequence.
That is what this step adds.

Report alongside the injection summary in Step 3.2, with equal visual
weight to the F/T/R/C counts:

```
Enumerative consistency:
  "there are four reasons..." (line 142): 3 of 4 named items found — MISMATCH
  → requires your decision before approval
```

### 3.1c — High-reach compression check

Runs after 3.1b, before the HTML is built (Step 3.2). For every C-type
span recorded in Step 3.1, compute its **reach**: the number of distinct
source paragraphs it draws from (already recorded as part of the C-type
span's source-sentence list in Step 3.1).

**NOTE (fixed):** this step had no code at all until now, only prose
describing what to compute — the same gap as several other findings
today (`word_to_num`, the cluster-coverage target, the enumerative
realized-count). Fixed using the `source_refs` tuples now formally
defined in Step 3.1:

```python
def compute_high_reach_spans(c_spans):
    results = []
    for s in c_spans:
        paragraphs = sorted(set(p for p, sent in s.get('source_refs', [])))
        reach = len(paragraphs)
        status = 'HIGH-REACH' if reach >= 3 else 'OK'
        results.append({
            'span_id': s['span_id'], 'reach': reach,
            'source_paragraphs': paragraphs, 'status': status,
        })
    return results

reach_report = compute_high_reach_spans(c_spans)
high_reach_spans = [r for r in reach_report if r['status'] == 'HIGH-REACH']
```

```
Status:
- OK: reach <= 2 (a span merging at most two source paragraphs — the
  ordinary, expected shape of a C-type compression).
- HIGH-REACH: reach >= 3. Always flag; always await user decision before
  the checkpoint (Step 4) can close. Same severity tier as an enumerative
  MISMATCH (Step 3.1b) and a DARK/WARN cluster (Step 4.3).
```

**Why reach, not span count or document position.** An empirical four-rate
comparison of the same source (10/15/20/25%) found no relationship between
where a span sits in the document and how risky it is — C-type spans were
consistently densest in the *first* third of every rate tested, not the
last, because the source's own structure (e.g. several parallel
sub-arguments early on) front-loads multi-sentence merges regardless of
condensation rate. Reach, not position, is what actually flagged the
single highest-risk spans in that test: at one rate (and only one — not
the tightest, not the loosest), the word budget was just large enough to
keep three separate source points alive but too small to give each its
own sentence, so the model folded all three into one span instead. That
is a materially different and more dangerous shape of compression than an
ordinary two-paragraph merge — three or more source paragraphs collapsed
into a single span is much more likely to silently flatten a distinction,
drop a qualification, or blend unrelated claims than a two-paragraph
merge is, yet the existing taxonomy has no way to tell the two apart by
type alone, since both are simply "C."

Report alongside the injection summary and the enumerative-consistency
report in Step 3.2, with equal visual weight:

```
High-reach compression check:
  c19 (reach 3): merges source §112, §114, §116 into one sentence
  → requires your decision before approval
```

### 3.1d — Borderline classification check

Runs after 3.1c, before the HTML is built (Step 3.2). **This check exists
because the F/T/R/C classification itself (Step 3.1) has no independent
second criterion** — unlike every other judgment call in this file, which
either cross-checks two independently-computed signals (Phase 1's sense
disambiguation) or verifies a claim mechanically against the source
(enumerative consistency, cluster coverage). Classification is applied via
a single fixed-order heuristic pass, and it is also the decision that
determines whether a source-reveal toggle exists at all: F and T spans
carry none, by the taxonomy's own rule (Step 3.1). A span that is really a
C-type compression but gets swept into T or F is therefore structurally
invisible — no toggle, no appendix entry, nothing to prompt the researcher
to ask for a justification.

This step does **not** solve classification correctness in general — no
second, independently-computed criterion exists for "is this really
metalinguistic" the way one exists for WordNet sense selection. What it
does instead is a targeted, mechanical heuristic check against the F and T
types' own stated definitions, to catch the specific, identified failure
shape: content quietly smuggled into a type that carries no citation
requirement.

```python
# NOTE (fixed, v3.20): confirmed by direct execution against real
# condensation text that this set omitted first/second-person pronouns
# ('i', 'you', 'your', 'my', 'our', 'one') despite already including
# third-person ones ('we', 'they', 'he', 'she', 'it', 'its') -- an
# internally inconsistent omission, not a deliberate design choice.
# This inflated content-word counts specifically for first-person
# academic prose ("I argue...", "our trust...") -- exactly PEEL's target
# register. In the run that found this, the gap never flipped a flagged/
# unflagged verdict (every affected span was already well past the
# threshold even before the fix), so it's a disclosed, real gap rather
# than a demonstrated wrong verdict -- but it could flip a genuinely
# borderline case in a future run.
FUNCTION_WORD_SET = {
    'a', 'an', 'the', 'this', 'that', 'these', 'those',
    'and', 'or', 'but', 'if', 'then', 'so', 'nor',
    'of', 'in', 'on', 'at', 'by', 'for', 'with', 'without', 'to', 'from',
    'as', 'is', 'are', 'was', 'were', 'be', 'been', 'being',
    'it', 'its', 'we', 'they', 'he', 'she', 'which', 'who', 'what',
    'i', 'you', 'your', 'my', 'our', 'one',
}

def flag_borderline_classifications(all_spans):
    """
    A partial, targeted mitigation, not a full independent classifier
    (see Step 3.1d prose above) -- flags F/T spans that exceed the
    taxonomy's own stated definition for their type, for batch
    researcher review. Unlike Step 3.1b/3.1c, this is a heuristic guess
    about content, not a mechanical fact about the source, and can
    false-positive on a legitimately verbose T-span -- see Step 4.2 for
    why this does NOT join the hard checkpoint-closure blockers.
    """
    flags = []
    for s in all_spans:
        if s['type'] not in ('F', 'T'):
            continue
        words = s['text'].split()
        content_words = [
            w for w in words
            if re.sub(r'[^a-zA-Z]', '', w).lower() not in FUNCTION_WORD_SET
            and re.sub(r'[^a-zA-Z]', '', w) != ''
        ]
        if s['type'] == 'F' and (len(words) > 6 or len(content_words) > 1):
            flags.append({
                'span_id': s['span_id'], 'type': 'F', 'text': s['text'],
                'reason': (f"{len(words)} words, {len(content_words)} "
                           f"content-bearing token(s) -- exceeds F's own "
                           f"definition (<=6 words, no content-bearing "
                           f"nouns/verbs beyond the surrounding matched "
                           f"spans)"),
            })
        elif s['type'] == 'T' and len(content_words) > 4:
            flags.append({
                'span_id': s['span_id'], 'type': 'T', 'text': s['text'],
                'reason': (f"{len(content_words)} content-bearing tokens "
                           f"-- unusually high for a metalinguistic span; "
                           f"may carry object-level content that belongs "
                           f"in R or C instead"),
            })
    return flags

borderline_flags = flag_borderline_classifications(all_spans)
```

```
Status:
- Not a MISMATCH/HIGH-REACH/DARK/WARN-tier finding. A flag here means
  "this span is denser than its assigned type's own definition allows,"
  not a confirmed error -- classify it as a required disclosure item, not
  a hard checkpoint-closure blocker (see Step 4.2).
```

Report alongside the injection summary in Step 3.2, with equal visual
weight to the other checks:

```
Borderline classification check:
  t7 (T): 6 content-bearing tokens -- unusually high for a
  metalinguistic span; may carry object-level content that belongs in
  R or C instead
  → flagged for your review; default is to keep as classified unless
    you request reclassification
```

### 3.2 — Build the HTML

**CRITICAL — INLINE STYLES ONLY. No `<style>` block. No CSS class names.
Every element must carry its visual properties as a `style="..."`
attribute. This is mandatory for Spyral compatibility.**

**This is the single HTML build step.** v3.0–v3.4 built a colour-only
"diagnostic" first and a separate source-revealing "final" HTML only after
checkpoint approval. v3.5 removes that split (see changelog): the
diagnostic could not be verified on its own terms (no source shown), and
once v3.4 made source-revealing toggles cheap and non-disruptive there was
no remaining reason to delay them behind a second build. This step
therefore builds the toggle-equipped, source-revealing HTML *directly*,
and it is rebuilt (not built-from-scratch-twice) at every round of the
checkpoint (Step 4) until approval.

**CRITICAL — FRAGMENT-FIRST.** The primary output is always an HTML
**fragment**: no `<!DOCTYPE>`, no `<html>`, no `<head>`, no `<body>`, no
`<style>` block, no CSS class names. Every visual property must be a
`style="..."` attribute on the element. This is the only format that
survives pasting into a Spyral HTML cell. A standalone browser-preview
file (fragment wrapped in `<html><body>`) is produced as a secondary
output, but the Spyral-injectable file is always the fragment.

#### Style dictionary S[]

**Before defining S[], set `SKILL_VERSION` from this file's own frontmatter
`name:` and `version:` fields — never hardcode either one.** A hardcoded
"peel2-phase2 v3.9" string sat in the meta-block template well after the
frontmatter itself moved to v3.10, meaning every artifact this skill
produced in between would have falsely self-reported its own version in
a permanent research record. Read both values fresh from the top of the
file you are currently following, right now, rather than reusing a value
remembered from an earlier point in this session or a previous session's
build:

```python
# Read fresh, every build. As of this specific version of the file (see
# the frontmatter `name:`/`version:` fields a few lines above the title),
# those values are "peel3-phase2"/"2.0" -- but do not hardcode either one
# here; look them up.
#
# NOTE (fixed, v2.0): the version *number* was already derived correctly
# (see the surrounding paragraph's own account of the v3.9/v3.10 drift
# incident), but the skill *name* half of this string was still a
# literal "peel2-phase2" -- the exact same drift bug, just in the other
# half of the same string, never caught before because the name had
# never actually changed until this file forked under a new one. Fixed
# by deriving both halves from the frontmatter, not just the version
# number.
SKILL_VERSION = FRONTMATTER_NAME + " v" + FRONTMATTER_VERSION  # e.g. "peel3-phase2 v" + whatever this file's frontmatter currently states
```

**Whenever the frontmatter `version:` field is bumped, no other edit is
required** — `SKILL_VERSION` is derived, not duplicated. Step 3.2v below
still asserts the produced fragment's meta table actually contains this
value, in case a future edit reintroduces a hardcoded string here instead
of the derivation.

Define this dictionary in Python before rendering any HTML block.
Every rendered element draws its styles from S[] — never hardcoded inline.

```python
S = {
    # Typography
    'wrap':    'font-family:Georgia,serif;max-width:820px;margin:0 auto;'

               'padding:0 0 4rem;line-height:1.85;color:#1c1a18;',
    'h1':      'font-family:system-ui,sans-serif;font-size:1.3rem;font-weight:700;'
               'line-height:1.2em;margin:0 0 0.3rem;color:#1c1a18;',
    'authors': 'font-family:system-ui,sans-serif;font-size:0.9rem;color:#666;'
               'margin:0 0 1.2rem;font-style:italic;',
    'h2':      'font-family:system-ui,sans-serif;font-size:1.05rem;font-weight:700;'
               'color:#1a5c7a;margin:2.2rem 0 0.5rem;'
               'border-bottom:1px solid #d0e4ed;padding-bottom:0.2rem;',
    'h3':      'font-family:system-ui,sans-serif;font-size:0.95rem;font-weight:600;'
               'color:#2a6080;margin:1.6rem 0 0.4rem;',
    'p':       'font-family:Georgia,serif;margin:0 0 0.3rem 0;line-height:1.85;'
               'color:#1c1a18;',
    'defn':    'font-family:Georgia,serif;background:#eef3f7;'
               'border-left:3px solid #1a5c7a;padding:0.7rem 1rem;'
               'margin:1rem 0;font-size:0.95rem;line-height:1.75;',

    # Metadata block
    'meta':    'font-size:0.8rem;color:#777;margin:1.5rem 0 0.8rem;'
               'border-left:3px solid #ccc;padding-left:1rem;',
    'meta_td1':'padding:0.18rem 0.9rem 0.18rem 0;vertical-align:top;'
               'color:#aaa;white-space:nowrap;min-width:7rem;',
    'meta_td2':'padding:0.18rem 0.9rem 0.18rem 0;vertical-align:top;',

    # Legend
    'legend':  'font-size:0.78rem;color:#555;margin:0.5rem 0 0;line-height:2.4;'
               'font-family:system-ui,sans-serif;',
    'sw':      'display:inline-block;width:1rem;height:0.8rem;border-radius:2px;'
               'vertical-align:middle;margin-right:3px;font-size:0;line-height:0;',
    'hr':      'border:none;border-top:1px solid #ddd;margin:0 0 1.5rem;',

    # Injection highlights — four distinct, mnemonic hues at light opacity
    # (v3.9). v3.6's sequential single-hue amber scale fixed the v3.0-v3.5
    # backwards-semiotics bug (see v3.6 changelog) but introduced two new
    # problems a user caught directly: the deepest step (C) read as too
    # dark/heavy against body text, and with only some types present in a
    # given condensation, adjacent shades of the same hue were easy to
    # mistake for one another — there was no hue-level mnemonic, only a
    # memorized lightness order. v3.9 replaces the single-hue scale with
    # four distinct, low-opacity hues chosen for built-in association
    # rather than memorized order: gray (F, neutral/structural), blue
    # (T, informational), gold (R, caution), red (C, risk). Risk ordering
    # is still communicated redundantly via border-bottom weight (none/
    # dotted/dashed/solid), exactly as in v3.6 — only the fill colours
    # changed, not the border-weight channel.
    'inj_f':   'background:rgba(140,140,135,0.18);',
    'inj_t':   'background:rgba(70,130,180,0.20);border-bottom:1px dotted #2f5d80;',
    'inj_r':   'background:rgba(212,160,23,0.22);border-bottom:1px dashed #8a6810;',
    'inj_c':   'background:rgba(196,68,68,0.22);border-bottom:2px solid #8a2f2f;',

    # Inline source toggles — collapsed-by-default provenance via native
    # <details>/<summary>. No <script>, no onclick: this is pure
    # browser-native disclosure behaviour, tested directly in Voyant/Spyral.
    'c_details':     'margin:0 0 1.2rem 0;font-size:0.85rem;',
    'c_summary':     'cursor:pointer;color:#2a7d3a;font-family:system-ui,'
                     'sans-serif;font-size:0.7rem;font-weight:600;'
                     'text-transform:uppercase;letter-spacing:0.03em;',
    'c_inset':       'background:#f0ede6;border-left:3px solid #2a7d3a;'
                     'padding:0.5rem 0.8rem;margin:0.3rem 0 0;'
                     'font-size:0.85rem;line-height:1.6;color:#444;'
                     'font-family:Georgia,serif;',
    'r_details':     'margin:0 0 1.2rem 0;font-size:0.85rem;',
    'r_summary':     'cursor:pointer;color:#4a6ea8;font-family:system-ui,'
                     'sans-serif;font-size:0.7rem;font-weight:600;'
                     'text-transform:uppercase;letter-spacing:0.03em;',
    'r_inset':       'background:#eef0f5;border-left:3px solid #4a6ea8;'
                     'padding:0.5rem 0.8rem;margin:0.3rem 0 0;'
                     'font-size:0.85rem;line-height:1.6;color:#444;'
                     'font-family:Georgia,serif;',

    # CSS-only checkbox-hack fallback (use only if a future Spyral update
    # is found to strip <details>/<summary>; requires a body-level <style>
    # block, which is a separate risk from the <head><style> already known
    # to be stripped — test before switching defaults)
    'cb_label':      'cursor:pointer;color:#2a7d3a;font-family:system-ui,'
                     'sans-serif;font-size:0.7rem;font-weight:600;'
                     'text-transform:uppercase;letter-spacing:0.03em;',

    # Cluster report
    'cr_div':  'margin-top:3rem;border-top:1px solid #ddd;padding-top:1rem;'
               'font-size:0.8rem;color:#888;font-family:system-ui,sans-serif;',
    'cr_th':   'padding:0.25rem 0.6rem;border-bottom:1px solid #eee;'
               'text-align:left;color:#aaa;font-weight:normal;',
    'cr_td':   'padding:0.25rem 0.6rem;border-bottom:1px solid #eee;text-align:left;',
    'cr_ok':   'padding:0.25rem 0.6rem;border-bottom:1px solid #eee;'
               'text-align:left;color:#2a7d3a;',
    'cr_warn': 'padding:0.25rem 0.6rem;border-bottom:1px solid #eee;'
               'text-align:left;color:#b07d2a;',
    'cr_dark': 'padding:0.25rem 0.6rem;border-bottom:1px solid #eee;'
               'text-align:left;color:#8b3a2a;font-weight:bold;',

    'app_h':   'font-size:0.85rem;color:#aaa;font-weight:normal;margin:0 0 0.5rem;',

    # Per-paragraph provenance marker (added v2.0) -- a small, always-
    # visible, native (no <details>, no JS) citation naming which source
    # paragraph(s) a condensed paragraph draws from. Complementary to the
    # c_*/r_* toggles above, not a replacement: those reveal a single
    # classified span's own quoted source text on click; this is a
    # coarser, whole-paragraph index visible without any interaction, so
    # a reader can tell where a paragraph comes from even when it
    # contains no C/R span at all (e.g. an F/T-only paragraph).
    'prov':    'font-size:0.68rem;color:#a8a49c;font-family:system-ui,'
               'sans-serif;margin-left:0.4rem;white-space:nowrap;',
}
```

#### Structural block parser

Before rendering, parse the condensed text into typed blocks.

**NOTE (fixed, v3.20):** this section previously defined `re_h1`/
`re_auth`/`re_h2`/`re_h3`/`re_defn` as real regexes, but the actual
line-by-line grouping algorithm that uses them was only ever a comment
("Parse lines into blocks... Flush accumulated buffer on blank lines or
structural lines") -- never executable code, through 19 prior versions
of active development. Confirmed by direct execution during this file's
first-ever live run: a naive stand-in (splitting on blank lines alone)
silently glued every section heading to its first paragraph, since real
corpora -- like this file's own source text -- typically have no blank
line between a heading and the paragraph that follows it. That in turn
caused spans inside the glued block to fail toggle rendering entirely.
Fixed with an actual line-by-line scanner, re-verified against real data
at two condensation rates (30 and 31 correctly-typed blocks, 0 unmatched
spans):

```python
import re

re_h2   = re.compile(r'^\s*(\d)\.?\s*[\t ]+(.+)$') # "1\tIntroduction" or "1. Introduction"
re_h3   = re.compile(r'^\s*(\d+\.\d+)\.?\s*[\t ]+(.+)$')  # "2.1\tTitle" or "2.1. Title"
re_defn = re.compile(r'^\s*Definition \d')
# NOTE (fixed, v3.23): the optional `\.?` before the whitespace is the fix --
# see the v3.23 changelog entry above. Without it, a real second corpus,
# numbered "1. Introduction" rather than "1\tIntroduction", matched 0 of
# its real section headings.
# NOTE (fixed, v3.20): re_auth (a pattern for "Name · Affiliation"
# middle-dot bylines) was removed here -- it was genuinely dead code, not
# just unreliable. It was never actually called anywhere in the parsing
# loop below; the positional fallback (line immediately after h1 is
# treated as 'authors') always fired regardless of whether re_auth would
# have matched, since either path led to the same 'authors' label. Kept
# would have been misleading -- it looked like an active check but never
# ran. DISCLOSED LIMITATION, not fixed here: the positional fallback
# itself assumes a single author-line immediately after the title, with
# nothing else (no subtitle, no abstract) between them -- true for the
# one real corpus this was tested against, not verified against a
# multi-author or subtitle-bearing paper.

def parse_condensed_blocks(condensed_text):
    """
    Returns a list of (block_type, text) tuples.
    block_type in {'h1', 'authors', 'h2', 'h3', 'defn', 'p'}.
    """
    lines = condensed_text.split('\n')
    blocks = []
    buf = []
    seen_h1 = False

    def flush():
        if buf:
            blocks.append(('p', ' '.join(buf).strip()))
            buf.clear()

    for line in lines:
        stripped = line.strip()
        if not stripped:
            flush()
            continue
        if not seen_h1:
            blocks.append(('h1', stripped))
            seen_h1 = True
            continue
        if blocks and blocks[-1][0] == 'h1' and not any(b[0] == 'authors' for b in blocks):
            # Positional author-line fallback -- see re_auth note above.
            blocks.append(('authors', stripped))
            continue
        if re_defn.match(line):
            flush()
            blocks.append(('defn', stripped))
        elif re_h3.match(line):
            flush()
            blocks.append(('h3', stripped))
        elif re_h2.match(line):
            flush()
            blocks.append(('h2', stripped))
        else:
            buf.append(stripped)
    flush()
    return blocks

blocks = parse_condensed_blocks(condensed_text)
```

**NOTE (fixed, usability/correctness review, 2026-07-28):** `esc()` was
called throughout this file (including in the v3.24 fix for unescaped
`&` in cluster names) but never defined anywhere — confirmed by a
whole-file search finding zero definitions. Any session following this
file as written would hit a `NameError` the first time it tried to
render a heading. Defined here, matching the same convention already
used by the sibling Phase 1 and Phase 3 skills (`html.escape(text,
quote=False)` — quotes left literal):

```python
import html as _html

def esc(text):
    return _html.escape(str(text), quote=False)
```

**NOTE (fixed, usability/correctness review, 2026-07-28).** `render_spans()`
— the function that actually paints the F/T/R/C highlight colours onto
text, i.e. the entire visual point of Phase 2 — was called below but
never defined anywhere in this file; only the one-sentence prose
description that used to follow this code block ("annotates each
sentence in a block with its injection type using inline styles from
S[]") existed, the same PROSE-ONLY-disguised-as-done shape this file's
own v3.20/v3.24 changelog entries already found and fixed elsewhere.
Implemented here: matches each classified span in `all_spans` (Step 3.1)
against its literal occurrence in the block's own text — safe because
blocks (the structural parser above) are built by re-joining
`condensed_text`'s own lines, so a span's recorded text is always a
literal substring of the block it was classified from — wraps the
longest non-overlapping matches in the appropriate `inj_*` style, and
escapes everything else via `esc()`. Verified against four synthetic
cases (plain T+C spans with plain text between them; no spans at all;
a span containing a literal `&`, confirming it is escaped exactly once
and not double-escaped; two overlapping candidate matches, confirming
the longer one wins and the shorter one is not separately re-wrapped)
— logically consistent with the file's own conventions and directly
executed, not merely reasoned about; not yet run against a real
corpus's `all_spans` output, since no live Phase 2 session is running
in this review:

```python
def render_spans(block_text):
    """Wraps every classified injection span (all_spans, Step 3.1) that
    occurs in this block's text in its S[] inj_* style, leaving
    everything else as plain escaped text. Does not handle a span whose
    text straddles a block boundary (e.g. spans two paragraphs) -- Step
    3.1's classification heuristics are sentence/sub-sentence level and
    blocks are paragraph-level, so this should not occur in practice,
    but this is a disclosed assumption, not independently verified
    against a real boundary-straddling case."""
    STYLE_BY_TYPE = {'F': S['inj_f'], 'T': S['inj_t'], 'R': S['inj_r'], 'C': S['inj_c']}

    relevant = sorted(
        (s for s in all_spans if s['text'] and s['text'] in block_text),
        key=lambda s: len(s['text']),
        reverse=True,  # longer spans get first claim on overlapping text
    )

    matches = []
    for s in relevant:
        start = 0
        while True:
            idx = block_text.find(s['text'], start)
            if idx == -1:
                break
            end = idx + len(s['text'])
            if not any(idx < m_end and end > m_start for m_start, m_end, _ in matches):
                matches.append((idx, end, s))
            start = idx + 1
    matches.sort(key=lambda m: m[0])

    out, pos = [], 0
    for start, end, s in matches:
        if start > pos:
            out.append(esc(block_text[pos:start]))
        out.append(f'<span style="{STYLE_BY_TYPE[s["type"]]}">{esc(block_text[start:end])}</span>')
        pos = end
    if pos < len(block_text):
        out.append(esc(block_text[pos:]))
    return ''.join(out)
```

**Added, v2.0 — native per-paragraph provenance.** Step 3.1 already
records each classified span's `source_refs` (paragraph_idx, sentence_idx
tuples), but nothing surfaced that data at the paragraph level — a reader
could only see where a *specific C/R span* came from, by opening its
toggle, not where a whole paragraph sits in the source at a glance,
including paragraphs with no C/R span at all. Built as a small,
always-visible, native citation reusing `all_spans` and `source_refs`
that already exist — no new data collection, only new rendering:

```python
def compute_block_provenance(block_text):
    """
    Returns a sorted list of distinct source paragraph indices (0-based,
    as recorded in each span's own source_refs -- Step 3.1) referenced
    by any classified span whose text occurs in this block. F-type spans
    are excluded -- they carry no propositional content and no
    meaningful source_refs by definition (Step 3.1's own taxonomy).
    """
    paragraphs = set()
    for s in all_spans:
        if s['type'] == 'F' or not s['text'] or s['text'] not in block_text:
            continue
        for (p_idx, _s_idx) in s.get('source_refs', []):
            paragraphs.add(p_idx)
    return sorted(paragraphs)

def render_provenance(block_text):
    """
    Renders compute_block_provenance()'s result as a compact, native
    (no <details>, no JS -- unlike the c_*/r_* toggles, this needs no
    disclosure since it's a short citation, not a full quoted passage)
    inline marker. Consecutive source paragraph indices are compressed
    into ranges (e.g. "¶3-5") rather than listed individually, since
    contiguous source material is the common case. Returns '' (renders
    nothing) when no span in this block carries any source_refs -- e.g.
    a purely F-type paragraph -- rather than showing an empty or
    misleading citation.
    """
    refs = compute_block_provenance(block_text)
    if not refs:
        return ''
    ranges, start, prev = [], refs[0], refs[0]
    for n in refs[1:]:
        if n == prev + 1:
            prev = n
            continue
        ranges.append((start, prev))
        start = prev = n
    ranges.append((start, prev))
    label = ', '.join(
        f"¶{a + 1}" if a == b else f"¶{a + 1}–{b + 1}"
        for a, b in ranges
    )
    return f'<span style="{S["prov"]}">[src {label}]</span>'
```

Render each block type with its S[] style:

```python
block_html = {
    'h1':      lambda t: f'<h1 style="{S["h1"]}">{esc(t)}</h1>',
    'authors': lambda t: f'<p style="{S["authors"]}">{esc(t)}</p>',
    'h2':      lambda t: f'<h2 style="{S["h2"]}">{esc(t)}</h2>',
    'h3':      lambda t: f'<h3 style="{S["h3"]}">{esc(t)}</h3>',
    'defn':    lambda t: f'<div style="{S["defn"]}">{render_spans(t)}{render_provenance(t)}</div>',
    'p':       lambda t: f'<p style="{S["p"]}">{render_spans(t)}{render_provenance(t)}</p>',
}
```

**NOTE:** `render_provenance` reuses `all_spans`' existing `text in
block_text` membership test rather than `render_spans`' already-computed
`matches` list, since the two functions are independent and called
separately per block by the lambdas above -- a disclosed, minor
inefficiency (each classified span is matched against block text twice,
once per function), not a correctness issue. Left as-is rather than
threading extra state through `block_html`'s lambda signatures, which
would complicate the one existing convention (each renderer takes only
`t`) for a performance gain that only matters at corpus sizes this skill
does not currently target.

#### Inline source toggles (C-type and R-type)

Immediately after each `<p>` (or `<defn>`) block that contains one or more
C-type or R-type spans, append one collapsed `<details>` toggle per span —
directly below the paragraph, so the reveal happens at the point of the
claim rather than in a separate appendix, but stays collapsed by default
so it does not interrupt continuous reading (v3.4). No click-dependent JS:
`<details>/<summary>` is native browser disclosure behaviour, and this
specific mechanism was confirmed to toggle correctly inside an actual
Spyral/Voyant HTML cell before being adopted as the default.

**CRITICAL — one source paragraph per toggle (v3.6).** Each toggle's quoted
excerpt must be a *contiguous* quotation from a single source paragraph.
Do not stitch sentences from two or more different source paragraphs into
one toggle with `...` between them — a user found this made toggles
unreadable, since opening one meant sorting out which quoted fragment
backed which clause of the condensed sentence. If a single condensed
sentence or paragraph compresses material from multiple source paragraphs
(common when a span merges several examples or sub-arguments), give it
*multiple* toggles instead of one wide one — e.g. `c8a`, `c8b`, `c8c` for
a condensed sentence drawing on three source paragraphs — each labelled
with the specific claim, example, or objection it backs (not just a list
of topics), so the reader knows what they are opening before they click.
An `...` is still permitted *within* a single source paragraph's quote
(to skip an unimportant clause), since that omission is local and does
not span a perspective shift; what is prohibited is using `...` to jump
between paragraphs.

```python
def render_c_toggle(span_id, source_sentences):
    items = ''.join(f'<p style="margin:0 0 0.3rem">{esc(s)}</p>'
                     for s in source_sentences)
    return (f'<details style="{S["c_details"]}">'
            f'<summary style="{S["c_summary"]}">'
            f'Show source (ᶜ{span_id})</summary>'
            f'<div style="{S["c_inset"]}">{items}</div></details>')

def render_r_toggle(span_id, source_sentence):
    return (f'<details style="{S["r_details"]}">'
            f'<summary style="{S["r_summary"]}">'
            f'Show source (ʳ{span_id})</summary>'
            f'<div style="{S["r_inset"]}">'
            f'<p style="margin:0">{esc(source_sentence)}</p></div></details>')
```

**Fallback (only if `<details>/<summary>` is later found to fail in a given
Spyral environment):** a CSS-only checkbox-hack toggle, using a hidden
`<input type="checkbox">` plus a `<label>` and a body-level `<style>` block
with sibling-selector rules (`.src-toggle:checked ~ .src-box{display:block}`).
This also tested successfully in Voyant/Spyral, but is more fragile (it
depends on a `<style>` block surviving, which is a separate risk from the
`<head><style>` already known to be stripped) and is therefore the
secondary option, not the default. Do not use both in the same document.

#### Meta + legend block

Insert this fragment immediately after the authors block, before §1:

```python
meta_legend = f"""
<div style="{S['meta']}">
  <table style="border-collapse:collapse">
    <tbody>
    <tr><td style="{S['meta_td1']}">Source</td>
        <td style="{S['meta_td2']}">[filename].txt &middot; [N] words</td></tr>
    <tr><td style="{S['meta_td1']}">Condensation</td>
        <td style="{S['meta_td2']}">[rate]% &middot; [N] words</td></tr>
    <tr><td style="{S['meta_td1']}">Phase&nbsp;1&nbsp;JSON</td>
        <td style="{S['meta_td2']}">[corpus]-phase1-state.json</td></tr>
    <tr><td style="{S['meta_td1']}">Injections</td>
        <td style="{S['meta_td2']}">F=[N] &middot; T=[N] &middot; R=[N] &middot; C=[N]</td></tr>
    <tr><td style="{S['meta_td1']}">Skill</td>
        <td style="{S['meta_td2']}">{SKILL_VERSION}</td></tr>
    </tbody>
  </table>
</div>
<div style="{S['legend']}">
  <span style="{S['sw']}background:rgba(140,140,135,0.85)">&nbsp;</span>
  <b>F &mdash; Framing</b>&nbsp;
  Short connective/orientating phrase, no propositional content.
  <em>Low epistemic risk.</em> &nbsp;&nbsp;&nbsp;
  <span style="{S['sw']}background:rgba(70,130,180,0.85);border-bottom:1px dotted #2f5d80">&nbsp;</span>
  <b>T &mdash; Transition</b>&nbsp;
  Metalinguistic sentence about the text's argument or structure.
  <em>Medium risk.</em> &nbsp;&nbsp;&nbsp;
  <span style="{S['sw']}background:rgba(212,160,23,0.85);border-bottom:1px dashed #8a6810">&nbsp;</span>
  <b>R &mdash; Reformulation</b>&nbsp;
  Single source sentence paraphrased. Click "Show source" directly below
  to reveal it.
  <em>Medium-high risk.</em> &nbsp;&nbsp;&nbsp;
  <span style="{S['sw']}background:rgba(196,68,68,0.85);border-bottom:2px solid #8a2f2f">&nbsp;</span>
  <b>C &mdash; Compression</b>&nbsp;
  Multiple source sentences collapsed. Click "Show source"
  directly below to reveal the passage it compresses &mdash; collapsed by
  default, one click to open, no JS.
  <em>High risk.</em>
</div>
<p style="font-size:0.7rem;color:#999;font-family:system-ui,sans-serif;margin:0.3rem 0 0;">Each type has a distinct, low-opacity colour (gray/blue/gold/red) for F/T/R/C respectively, chosen for memorable association rather than a scale to memorize; border style (none/dotted/dashed/solid) is a redundant, colour-independent cue for the same risk ordering. A small "[src &para;N]" marker after a paragraph names which source paragraph(s) it draws from (added v2.0) &mdash; separate from the "Show source" toggles below, which reveal a specific span's own quoted passage.</p>
<hr style="{S['hr']}">
"""
```

**Note:** every swatch `<span>` contains `&nbsp;` — never empty.
Spyral's HTML cell parser strips empty `<span>` elements entirely.

#### Cluster coverage table

Computed mechanically (same `cluster_coverage()` function defined in Step 1) and
included in every build of this HTML — there is no separate post-approval
stage that adds it later (see v3.5 changelog).

**NOTE (fixed, usability/correctness review, 2026-07-28):** `coverage_report`
is used by the row-building loop immediately below, and again later by
`build_phase2_report()` (Results report, further down this same Step
3.2). The code that actually produces it was, until this fix, written
under the **Step 4.3** heading — nearly 550 lines further down this
document, in reading order — even though Step 4.3's own prose already
says "Computed every time the HTML is built (Step 3.2) — it does not
wait for a separate post-approval stage." A session following this file
top-to-bottom would hit `coverage_report` undefined here. Moved to where
it is first actually needed and first actually runs; Step 4.3 below now
references these same values instead of recomputing them.

```python
actual_coverage = cluster_coverage(condensed_text, clusterdefs, inclist)

def coverage_status(source_coverage, actual_coverage):
    results = {}
    for name, target in source_coverage.items():
        actual = actual_coverage.get(name, 0.0)
        delta = round(actual - target, 1)
        if target == 0.0:
            # Cluster had no presence in the source at all -- nothing to
            # preserve, so its absence from the condensation is not a
            # coverage failure. Without this, a cluster Phase 1 defined
            # but that never actually appeared in this particular source
            # would be falsely flagged DARK on every single run.
            status = 'OK'
        elif actual == 0.0:
            status = 'DARK'
        elif abs(delta) <= 5.0:
            status = 'OK'
        else:
            status = 'WARN'
        results[name] = {
            'target': target, 'actual': actual,
            'delta': delta, 'status': status,
        }
    return results

coverage_report = coverage_status(source_coverage, actual_coverage)
```

**NOTE (fixed, v3.24):** the row-building loop below was never real code
in this file — only a bracketed placeholder comment describing it — the
same PROSE-ONLY-disguised-as-done shape v3.20 already found and fixed
elsewhere in this file. With no real code to follow, a live session
improvised the loop itself and spliced Phase 1 cluster names directly
into `<td>` content with no escaping, shipping unescaped `&` (e.g. `"AI &
Technology"`) in an already-delivered artifact before being caught, by
Phase 3's stricter verification, not this file's own Step 3.2v. Fixed by
writing the actual loop, routing `name` through `esc()` like every other
text fragment in this file:

```python
rows = []
for name, r in coverage_report.items():
    rows.append(
        f'<tr><td style="{S["cr_td"]}">{esc(name)}</td>'
        f'<td style="{S["cr_td"]}">{r["target"]}%</td>'
        f'<td style="{S["cr_td"]}">{r["actual"]}%</td>'
        f'<td style="{S["cr_td"]}">{r["delta"]:+.1f}pp</td>'
        f'<td style="{status_style(r["status"])}">{r["status"]}</td></tr>'
    )

def status_style(status):
    return {'OK': S['cr_ok'], 'WARN': S['cr_warn'], 'DARK': S['cr_dark']}[status]

cov_table = f"""
<div style="{S['cr_div']}">
  <p style="{S['app_h']}"><b>Cluster coverage</b></p>
  <table style="border-collapse:collapse;width:100%">
    <tbody>
    <tr>
      <th style="{S['cr_th']}">Cluster</th>
      <th style="{S['cr_th']}">Target</th>
      <th style="{S['cr_th']}">Actual</th>
      <th style="{S['cr_th']}">Delta</th>
      <th style="{S['cr_th']}">Status</th>
    </tr>
    {''.join(rows)}
    </tbody>
  </table>
</div>
"""
```

#### Final fragment assembly

`section_blocks` already contains every paragraph/heading block rendered
by `block_html`, with C-type and R-type spans followed by their collapsed
source toggles (`render_c_toggle` / `render_r_toggle`) — there is no
separate appendix to assemble, and no sidebar or `<script>` to append.

```python
fragment = f"""<div style="{S['wrap']}">
{h1_block}
{authors_block}
{meta_legend}
{section_blocks}
{cov_table}
</div>"""
```

#### 3.2v — Artifact verification (mandatory, run before writing any file)

**This step exists because prose-described HTML can silently fail to be
built.** Steps 3.1–3.2 describe a specific, multi-part artifact — typed
spans, per-span source toggles, structural blocks, legend, cluster table.
Describing that correctly is not the same as having actually produced it.
A degraded artifact (e.g. the entire condensation flattened into one `<p>`
inside a single rate-level `<details>`, with no per-span toggles, no
highlighting, no legend) can be written to disk and presented as if it
were compliant, and nothing else in this skill will catch that — the
compliance rules describe the target, they do not inspect the output.
This step closes that gap mechanically, on the actual `fragment` string,
not on a re-read of the rules:

```python
import re

# c_count, r_count already defined in Step 3.1, alongside f_count/t_count,
# non_injected_pct, and verbatim_overlap_pct (v3.20) -- not redefined here.

# NOTE (fixed): two compounding bugs found via an actual cross-machine
# test run, independently verified afterward against the real files --
# not caught by any test run in this skill's own development, because
# neither was ever checked against the REAL S[] dictionary with a
# realistic high-reach case.
#
# (1) S['c_details'] and S['r_details'] are BYTE-FOR-BYTE IDENTICAL
# strings ('margin:0 0 1.2rem 0;font-size:0.85rem;'). fragment.count()
# on either one counts ALL toggles, C and R combined -- it cannot
# distinguish them. The two checks below were comparing the SAME number
# against two DIFFERENT targets (c_count, r_count), which can only both
# pass if c_count == r_count, essentially never true in real output.
# Fixed by counting S['c_summary'] / S['r_summary'] instead -- these
# already carry genuinely distinct CSS (different colours), unlike
# c_details/r_details, so no visual design change was needed, only a
# correction to which style key the check counts.
#
# (2) Even with distinct keys, comparing toggle count to c_count/r_count
# (span counts) is the wrong equation. This skill's own v3.6 rule (see
# Step 3.2, "one source paragraph per toggle") means a single span
# merging N distinct source paragraphs renders as N separate toggles,
# not one -- so toggle count should equal the SUM of each span's
# paragraph-reach, not the number of spans. Fixed using the same
# distinct-paragraph-counting logic Step 3.1c already uses for reach.

def toggle_count_for_spans(spans):
    """Expected toggle count per the v3.6 'one toggle per source
    paragraph' rule: one toggle per DISTINCT paragraph a span's
    source_refs reference, not one toggle per span."""
    total = 0
    for s in spans:
        paragraphs = set(p for p, sent in s.get('source_refs', []))
        total += max(len(paragraphs), 1)
    return total

expected_c_toggles = toggle_count_for_spans(c_spans)
expected_r_toggles = toggle_count_for_spans(r_spans)

checks = {
    'structural blocks present (not one giant <p>)':
        len(re.findall(r'<h[123]\b', fragment)) >= 1,
    'every C-span paragraph-reference has its own toggle':
        fragment.count(S['c_summary']) == expected_c_toggles,
    'every R-span paragraph-reference has its own toggle':
        fragment.count(S['r_summary']) == expected_r_toggles,
    'no single details element wraps the whole document as plain text':
        not re.search(r'<details[^>]*>\s*<summary[^>]*>[^<]*%[^<]*'
                       r'click to expand[^<]*</summary>\s*<div[^>]*>'
                       r'\s*<p[^>]*>.{500,}</p>\s*</div>\s*</details>'
                       r'\s*$', fragment.strip()),
    'at least one inj_* highlight style present, if any non-F/T spans exist':
        (c_count + r_count == 0) or any(
            S[k] in fragment for k in ('inj_r', 'inj_c')
        ),
    # NOTE (fixed, v3.20): the original check was `'c_summary' in fragment
    # and S['legend'].split(';')[0] in fragment` -- the first clause tested
    # for the literal 7-character string "c_summary", a Python dict KEY
    # NAME, appearing verbatim in the rendered HTML. Confirmed by direct
    # execution: it never does, and structurally never could, since this
    # file's own INLINE-STYLES-ONLY / no-class-names rule (v3.2) means
    # dict keys are never emitted as literal HTML text -- only their CSS
    # values are. This made the check unconditionally unsatisfiable by any
    # compliant fragment, meaning it would have failed every real delivery,
    # forever, had it ever actually been run before this file's first live
    # execution. Fixed by dropping the unsatisfiable clause -- the legend-
    # divider style check was always the real signal.
    'legend block present':
        S['legend'].split(';')[0] in fragment,
    'cluster coverage table present':
        S['cr_div'].split(';')[0] in fragment,
    'meta table reports the version actually derived from this file\'s '
    'frontmatter, not a hardcoded/stale string':
        SKILL_VERSION in fragment,
}

failed = [name for name, ok in checks.items() if not ok]
if failed:
    raise AssertionError(
        "Artifact verification FAILED — do not write or present this "
        "file. The built fragment does not satisfy Step 3.2's required "
        "structure:\n" + "\n".join(f"  - {f}" for f in failed) +
        "\nGo back and actually build the missing piece(s); do not "
        "narrate a description of compliant HTML without producing it."
    )
```

If this check fails, **stop**. Do not write the files, do not present
them, and do not tell the user the artifact is ready. Rebuild the
fragment so it satisfies every check, then re-run this verification
before proceeding. This applies identically inside the default-bundle
workflow (Step 2) — each of the four rates gets its own full Step 3.2
build and its own passing run of this check; the bundle's "compare the
ladder in one view" (Step 2) refers to an *additional* chat-level summary
table of word counts, injection counts, and cluster coverage across the
four rates — it is never a substitute for, or a simplified replacement
of, any individual rate's full toggle-equipped, span-highlighted HTML.
A flattened, plain-text, single-accordion-per-rate artifact is not a
permitted bundle output under any framing.

#### Results report (Phase2-results.md)

**NOTE (fixed):** Enumerative consistency and high-reach compression
results were only ever reported in chat — never embedded in the
delivered HTML, never written to any file. This is the same class of
gap Phase 1 had before its `## Environment fallbacks used` fix: a
disclosure that exists only in a conversation nobody reopens is close
to no disclosure at all. F/T/C counts and source-verbatim % had the
same problem one level deeper — narrated as placeholders in the chat
template with no code anywhere actually computing them (see the NOTE in
Step 3.1, where `all_spans`, the per-type counts, and
`source_verbatim_pct` are now formally defined).

Fixed by building a fourth deliverable, mirroring Phase 1's
`Phase1-results.md` in both content and mechanical enforcement: a
self-contained, human-readable record that doesn't require opening the
HTML or a chat transcript to audit this rate's condensation.

```python
def build_phase2_report(corpus, rate, f_count, t_count, r_count, c_count,
                         non_injected_pct, verbatim_overlap_pct,
                         enumerative_check,
                         high_reach_spans, cluster_coverage_report,
                         all_spans, borderline_flags,
                         environment_precondition_status,
                         drafting_notes):  # mandatory prose, added v2.0
    lines = [f"# Phase 2 Results — {corpus} — {rate}% condensation\n"]

    lines.append("## Injection analysis\n")
    lines.append(f"- F (framing): {f_count} spans")
    lines.append(f"- T (transition): {t_count} spans")
    lines.append(f"- R (reformulation): {r_count} spans")
    lines.append(f"- C (compression): {c_count} spans")
    # NOTE (fixed, v3.20): "Source-verbatim %" was previously one number
    # (words outside any classified span) misleadingly labeled as if it
    # were verbatim overlap. Now two numbers, each labeled for what it
    # actually measures -- see the NOTE where non_injected_pct and
    # verbatim_overlap_pct are computed in Step 3.1.
    lines.append(f"- Non-injected (words outside any classified span): {non_injected_pct}% of tokens")
    lines.append(f"- Verbatim overlap with source (independently measured): {verbatim_overlap_pct}% of tokens\n")

    lines.append("## Enumerative consistency\n")
    if not enumerative_check:
        lines.append("No enumerative structures were detected in the source.\n")
    else:
        for e in enumerative_check:
            n_items = len(e.get('item_status', []))
            n_present = sum(1 for s in e.get('item_status', []) if s['present'])
            lines.append(f"- \"{e['claim_text']}\" (declared {e['declared_n']}): "
                         f"{n_present} of {n_items} named items found "
                         f"— {e['status']}")
        lines.append("")

    lines.append("## High-reach compression check\n")
    if not high_reach_spans:
        lines.append("No high-reach compressions (reach >= 3) were found.\n")
    else:
        for s in high_reach_spans:
            lines.append(f"- {s['span_id']} (reach {s['reach']}): merges "
                         f"{', '.join(s['source_paragraphs'])}")
        lines.append("")

    lines.append("## Borderline classification check\n")
    if not borderline_flags:
        lines.append("No F/T spans exceeded their type's own definition "
                      "(word count / content-word density) this run.\n")
    else:
        for f in borderline_flags:
            lines.append(f"- {f['span_id']} ({f['type']}): {f['reason']}")
        lines.append("")

    lines.append("## Cluster coverage\n")
    lines.append("| Cluster | Target | Actual | Delta | Status |")
    lines.append("|---|---|---|---|---|")
    for name, r in cluster_coverage_report.items():
        lines.append(f"| {name} | {r['target']}% | {r['actual']}% | "
                     f"{r['delta']:+.1f}pp | {r['status']} |")
    lines.append("")

    lines.append("## Classification verification limits\n")
    lines.append(
        "**F/T/R/C labels are self-reports.** They are generated by the "
        "same system whose output they classify, in the same pass, via a "
        "fixed heuristic order with no independently-computed second "
        "criterion -- unlike this file's other checks (enumerative "
        "consistency, cluster coverage), which verify a claim "
        "mechanically against the source. **Step 3.1d's borderline check "
        "is a targeted, partial mitigation, not proof of correct "
        "classification.** It catches F/T spans that are denser than "
        "their own stated definition allows; it cannot catch a span that "
        "is quietly over-compressed while still reading as plausibly "
        "metalinguistic or short. The absence of a Step 3.1d flag "
        "certifies only that this specific heuristic found nothing, not "
        "that every classification in this document is correct. This "
        "applies equally to a run with zero flags and a run with several.\n"
    )

    lines.append("## Environment fallbacks used\n")
    lines.append(environment_precondition_status + "\n")

    # NOTE (added, v2.0): every other section above is data -- counts,
    # tables, pass/fail statuses. None of it carries the reasoning that
    # actually explains what the data means: why a compression choice was
    # made, why a metric moved the way it did between rates, what a
    # drafting method risked and how that risk was checked. That reasoning
    # was routinely given in chat during live sessions and then lost --
    # Phase 3's automatic Spyral Notebook composition reads this file, not
    # the chat transcript, so anything left only in chat does not survive
    # into the final artifact. Same "chat-only disclosure is not durable"
    # problem this file already fixed for environment-precondition
    # outcomes (v3.19) and Phase 1 fixed for its own fallback disclosures
    # -- fixed here the same way: a mandatory section, not an optional one.
    lines.append("## Drafting & analysis notes\n")
    lines.append(
        "**Mandatory prose, every run.** Free-text explanation of the "
        "reasoning behind this rate's drafting choices and what its "
        "mechanical results mean -- not a restatement of the tables "
        "above. Required content, when applicable: why particular "
        "compressions or omissions were made; for a rate built by "
        "expanding a prior rate, what was added and how it was verified "
        "against the source rather than against the prior draft alone "
        "(see the source-drift risk this guards against); how this "
        "rate's metrics (injection mix, high-reach count, cluster "
        "coverage, verbatim overlap) compare to other rates already "
        "built in the same run and what that comparison indicates; any "
        "defect the writing-quality gate (Step 3.0v) found and fixed. "
        "If a run genuinely has nothing beyond the tables to add, say so "
        "explicitly -- do not omit the section.\n"
    )
    lines.append(drafting_notes + "\n")

    lines.append("## Injection appendix\n")
    lines.append("| Span ID | Type | Source reference | Justification |")
    lines.append("|---|---|---|---|")
    for s in all_spans:
        if s['type'] in ('C', 'R'):
            refs = '; '.join(f'§{p}.{sent}' for p, sent in s.get('source_refs', []))
            just = s.get('justification', '')
        else:
            refs, just = '—', '(no source reference needed for this type)'
        lines.append(f"| {s['span_id']} | {s['type']} | {refs} | {just} |")

    return '\n'.join(lines)

md_report_text = build_phase2_report(
    corpus, rate, f_count, t_count, r_count, c_count,
    non_injected_pct, verbatim_overlap_pct,  # renamed/split, v3.20
    enumerative_check, high_reach_spans, coverage_report, all_spans,
    borderline_flags,               # from Step 3.1d, v3.19
    environment_precondition_status,  # set once at Step 0.9, v3.19
    drafting_notes,                 # mandatory prose, v2.0 -- written by
                                     # the drafting agent, not derived
)
```

**Verification (mandatory, run before writing any file)** — same pattern
as Step 3.2v and Phase 1's Step 6.2v, checked against the actual
assembled text, not re-read as a prose requirement:

```python
required_headings = [
    "## Injection analysis",
    "## Enumerative consistency",
    "## High-reach compression check",
    "## Borderline classification check",       # v3.19
    "## Cluster coverage",
    "## Classification verification limits",    # v3.19
    "## Environment fallbacks used",             # v3.19
    "## Drafting & analysis notes",              # v2.0
    "## Injection appendix",
]
missing = [h for h in required_headings if h not in md_report_text]
if missing:
    raise AssertionError(
        "Phase2-results.md is missing required heading(s): "
        + ", ".join(missing) +
        ". Do not write or present this file until fixed."
    )
```

This report is rebuilt at every HTML build — the first round and every
checkpoint revision (Step 4) — exactly like the two HTML files, and in
the default bundle, each rate gets its own, exactly as each rate gets
its own complete HTML build (see v3.7/v3.10).

#### Output files

Write **four files** at every build of this HTML — the first round and
every revision round during the checkpoint (Step 4):

```python
# 1. Spyral-injectable fragment
frag_path = f'/mnt/user-data/outputs/{corpus}_condensed_{rate}pct_v3_spyral.html'
with open(frag_path, 'w', encoding='utf-8') as f:
    f.write(fragment)

# 2. Standalone browser preview
standalone_path = f'/mnt/user-data/outputs/{corpus}_condensed_{rate}pct_v3.html'
with open(standalone_path, 'w', encoding='utf-8') as f:
    f.write(f'<!DOCTYPE html>\n<html lang="en">\n'
            f'<head><meta charset="UTF-8">'
            f'<title>{corpus} — condensed {rate}%</title></head>\n'
            f'<body style="background:#f8f7f4;padding:2rem 1.8rem">\n'
            f'{fragment}\n</body></html>')

# 3. Human-readable results report
report_path = f'/mnt/user-data/outputs/{corpus}_condensed_{rate}pct-Phase2-results.md'
with open(report_path, 'w', encoding='utf-8') as f:
    f.write(md_report_text)

# 4. Plain-text summary (added v3.21) -- Title/Author/Summary, no
# injection markup. Built from `blocks` (the same typed-block list
# already parsed from `condensed_text` above, before any span-injection
# styling was applied) -- never by stripping tags from `fragment`.
title_text = next(t for btype, t in blocks if btype == 'h1')
author_text = next(t for btype, t in blocks if btype == 'authors')
body_blocks = [(btype, t) for btype, t in blocks if btype not in ('h1', 'authors')]
# NOTE (live-tested fix, v3.21): a heading (h2/h3) is immediately
# followed by its own paragraph in the original condensed_text, with no
# blank line between them -- only distinct paragraphs, and a paragraph
# followed by the next heading, get a blank line. A uniform '\n\n'.join()
# was tried first and found wrong by direct comparison against the real
# source text: it inserted a spurious blank line after every heading.
body_parts = []
for i, (btype, t) in enumerate(body_blocks):
    if i == 0:
        body_parts.append(t)
    else:
        prev_type = body_blocks[i - 1][0]
        sep = '\n' if prev_type in ('h2', 'h3') else '\n\n'
        body_parts.append(sep + t)
body_text = ''.join(body_parts)

summary_path = f'/mnt/user-data/outputs/{corpus}-Summary-{rate}pct.txt'
with open(summary_path, 'w', encoding='utf-8') as f:
    f.write(f'Title: {title_text}\nAuthor: {author_text}\nSummary:\n\n{body_text}\n')
```

Present all four files with `present_files`. Tell the user:
- `_spyral.html` → paste directly into a Spyral HTML cell
- `_v3.html` → open in browser for preview
- `-Phase2-results.md` → self-contained audit record: injection counts,
  enumerative consistency, high-reach compressions, cluster coverage,
  and the full per-span appendix, all in one file — does not require
  opening the HTML or scrolling back through chat to review this rate
- `-Summary-{rate}pct.txt` → plain Title/Author/Summary text, no
  injection markup — for direct injection into the notebook's separate
  plain-text Summary cell (Cell 5 of `PEEL2templateSN.html`), distinct
  from the annotated `_spyral.html` fragment injected into Cell 6

Also report in chat, summarizing what the file contains rather than
duplicating it in full:

```
Injection analysis:
  F (framing)        : N spans
  T (transition)     : N spans
  R (reformulation)  : N spans
  C (compression)    : N spans
  Non-injected       : N% of tokens (outside any classified span)
  Verbatim overlap   : N% of tokens (independently measured against source)

Enumerative consistency: [N OK / N MISMATCH / N DROPPED / N AMBIGUOUS —
  see Phase2-results.md for full detail]

High-reach compression check: [N found — see Phase2-results.md for
  full detail]

Borderline classification check: [N flagged — see Phase2-results.md
  "## Classification verification limits" for what this check does and
  does not guarantee]

Full record: {corpus}_condensed_{rate}pct-Phase2-results.md
```

---

## Step 4 — Conversational epistemic checkpoint

**This step has no fixed number of rounds. It closes only on explicit
user approval. Do not infer approval from silence.**

Deliver the HTML built in Step 3.2, then open the checkpoint with:

```
The condensation is ready, with sources for every compressed/reformulated
span revealable via the "Show source" toggles. Please read it through and:

  — Approve and treat this as final
  — Disapprove and request a revision of the condensation
  — Question any injection classification
  — Ask to see the source context for any span (you can also open the
    toggle yourself — it's the same source either way)
  — Request that a specific C-type or R-type span be revised or cut
  — Decide that a specific C-type span is acceptable as-is
  — Return to this checkpoint at any time after this point

What would you like to do?
```

**If Step 3.1b reported any MISMATCH, Step 3.1c reported any HIGH-REACH
span, or Step 4.3 reported any DARK or WARN cluster**, say so explicitly
before asking the question above, and treat it as a required item
alongside disputed C-type spans:

> "Before we go further: the source claims 'there are four reasons...' but
> the condensation now presents only three. This needs your decision —
> split the merged items back apart, revise the cardinal claim to match
> (e.g. 'three reasons'), or explicitly accept the mismatch with a stated
> reason."

> "Also: span `c19` merges three separate source paragraphs (§112, §114,
> §116) into one sentence — the highest-reach kind of compression. This
> needs your decision — split it into separate sentences/toggles, cut one
> of the three points, or explicitly accept the merge with a stated
> reason."

**If Step 3.1d flagged any borderline F/T spans**, present them together,
batched, in the same message — but framed differently from the three
items above, since 3.1d is a heuristic guess about content density, not a
mechanical fact about the source (see Step 3.1d and `## Classification
verification limits`):

> "Also: [N] span(s) classified as framing/transition are denser than
> that type's own definition allows — for example, `t7` has 6
> content-bearing tokens, more than a purely metalinguistic sentence
> usually carries. This may be a false positive (some T-spans are
> legitimately long), or it may mean object-level content is sitting in a
> span with no source toggle attached. Default is to keep these as
> classified; tell me which ones (if any) you want reclassified to R or
> C, or confirm the batch as-is."

### 4.1 — Responding to user actions at the checkpoint

**If the user questions a classification:**
State the classification code, the span text, the heuristic applied,
and the source evidence (or absence of it). Example:

> "I classified 'A first necessary condition it cannot satisfy' as **F**
> because it is a short orientating phrase (7 words) whose removal would
> not alter the propositional content of the surrounding passage. The
> words 'necessary condition' appear in the source at [location]."

If the user disagrees with a classification, accept the correction and
update the record. The user's classification overrides the agent's.

**If the user asks for source context of a span:**
Locate the source passage(s) the span derives from and quote them
verbatim (within copyright limits) in chat. State whether the span is a
verbatim selection, a compression, or a paraphrase of those passages.
(The same passage is also already available in the HTML's toggle for that
span — pointing this out is useful but answering in chat is not optional;
the user may be discussing the span without the file open.)

**If the user requests revision of a C-type or R-type span:**
Two options:

- **Cut the span**: remove it and verify the surrounding text still
  reads coherently. Adjust word count if needed.
- **Replace with verbatim**: find the source sentence(s) the span
  compresses and replace the span with a verbatim selection. This
  increases word count; adjust elsewhere if needed.

After any revision: re-run the injection analysis on the affected
passage, **rebuild the HTML (Step 3.2)** — same two files, same
toggle mechanism — and re-deliver it before continuing the checkpoint.

**If the user approves a C-type span as-is:**
Record it as approved. It will not be removed or revised. (Its toggle
remains in the HTML regardless — approval does not remove the toggle,
since the golden rule requires the source stay discoverable.)

**If the user requests a full revision of the condensation:**
Return to Step 3. Generate a new condensation, re-run the injection
analysis, rebuild the HTML, and re-deliver it. The checkpoint reopens.

**If the user approves:**
Record the approved state of the condensation (which C-type spans were
accepted, which were cut or replaced). The most recently delivered HTML
files are the final deliverable — no further build step follows.

### 4.2 — Checkpoint closure condition

The checkpoint closes when the user explicitly states approval.
Acceptable approval signals: "approved", "looks good", "proceed",
"that's final", or equivalent.

**NOTE (fixed, v2.0):** the compliance rules state "Tolerance is ±5% at
generation stage, ±2% for the approved condensation" — but until this
fix, the ±2% half of that rule had no corresponding mechanical check
anywhere in this file, unlike its ±5% counterpart (Step 3's explicit
`wc -w`-and-compare procedure). The same PROSE-ONLY-disguised-as-done
shape this file's own history has already found and fixed elsewhere
(the structural block parser, `render_spans`, `scan_verbatim_overlap` —
see their respective v3.20 notes): a compliance rule stated once in
prose, with nothing anywhere actually enforcing it. Confirmed by
searching this file for any word-count assertion outside Step 3's own
±5% check — none exists. Fixed by adding an explicit ±2% check as a
checkpoint-closure precondition, mirroring Step 3's own procedure:

```python
def check_final_tolerance(condensed_text, target_words):
    actual = len(condensed_text.split())  # wc -w is authoritative, per
                                           # this file's own compliance rule
    delta_pct = abs(actual - target_words) / target_words * 100
    return {
        'actual_words': actual,
        'target_words': target_words,
        'delta_pct':    round(delta_pct, 1),
        'status':       'OK' if delta_pct <= 2.0 else 'OUT-OF-TOLERANCE',
    }
```

**The checkpoint cannot close while any Step 3.1b MISMATCH, Step 3.1c
HIGH-REACH span, Step 4.3 DARK/WARN cluster, or an `OUT-OF-TOLERANCE`
`check_final_tolerance` result remains unresolved**, even if the user
gives a general approval signal. If the user says "approved" without
having addressed a flagged MISMATCH, high-reach span, cluster deviation,
or a final word count still outside ±2% of target, ask specifically
about it before treating the condensation as final. Run
`check_final_tolerance` against the draft's current word count at every
point Step 4.2 is evaluated — after the initial Step 3.2 build and again
after every revision — the same "re-check after every edit, not once"
discipline Step 3.0v (item 8) already applies to writing quality, for
the same reason: a revision that fixes one thing can silently drift the
word count past ±2% without anyone re-running `wc -w` to notice.

**Step 3.1d borderline flags are handled differently (v3.19).** They must
still be raised explicitly and cannot be closed by silence — a general
"approved" that has never seen the batch is not sufficient, the same
"never infer approval from silence" rule that governs everything else in
this checkpoint. But unlike the three hard blockers above, a single batch
response ("keep all as classified" or a list of exceptions) resolves all
of them at once; the checkpoint does not require a separate decision per
flagged span the way a MISMATCH or HIGH-REACH span does. This is a
deliberate difference in severity, not an oversight: 3.1d is a heuristic
that can false-positive on a legitimately verbose T-span, and treating
every flag as an individually-blocking item would risk eroding the
researcher's attention to the three checks that are mechanically exact.

If the user stops commenting without approving, ask:

> "Are you satisfied with this condensation, or would you like
> another revision or clarification?"

**Per-instance closure, not per-category (added 2026-07-28, usability
review).** The blocking rule above stops a blanket "approved" from closing
the checkpoint while *some* MISMATCH/HIGH-REACH/DARK/WARN item remains
unresolved — but when there is more than one instance of the same category
(e.g. two separate MISMATCHes, or a MISMATCH and a HIGH-REACH span
together), a single blanket response like "accept all flagged items" does
**not** resolve them. Each individual flagged instance needs its own
visible disposition (split/revise/accept-with-reason, per the guidance
above) before the checkpoint can close — the risk this guards against is
the same one Step 4's opening message already carries by bundling multiple
categories into one delivery: a reply that resolves the category in the
aggregate without the researcher actually having looked at each instance.
This is distinct from the 3.1d borderline batch immediately below, which
is deliberately eligible for one batch response — that difference in
severity is intentional, not an oversight.

### 4.3 — Cluster-coverage check

Computed every time the HTML is built (Step 3.2) — it does not wait for a
separate post-approval stage (see v3.5 changelog). For each cluster in
`clusterDefs`, count incList stem hits in the condensed text and compare
to the source proportions.

`cluster_coverage()` and `stem_matches()` are defined once, in Step 1,
where `source_coverage` is also computed. `actual_coverage`,
`coverage_status()`, and `coverage_report` (the comparison this check
reports on) are computed once, in Step 3.2's "Cluster coverage table"
subsection, at the point they are first actually needed — not here.

**NOTE (fixed, usability/correctness review, 2026-07-28):** this code
used to live under this heading, textually — but by the time a session
reaches Step 4.3 in reading order, `coverage_report` had already been
required (and used) twice, earlier in Step 3.2. Moved so the file's
actual code order matches its own stated execution order ("Computed
every time the HTML is built (Step 3.2)," directly above). This step now
only reports on and applies thresholds to the already-computed
`coverage_report` — it does not recompute it.

**Thresholds:**
- **OK**: actual within ±5 percentage points of source target (or the
  cluster had 0% presence in the source to begin with — see the code
  comment above for why that is not the same as a coverage failure).
- **WARN**: deviation >5pp. Report to user with explanation.
  A WARN may reflect a structural property of the source rather
  than a selection error. Ask the user: revise or accept?
- **DARK**: a cluster with real presence in the source (target > 0%) has
  0 hits in the condensation. Always flag; always await user decision
  before the checkpoint can close.

Report alongside the injection summary (Step 3.2) and at the checkpoint
(Step 4):

```
Cluster-coverage verification:
  Cluster                        Target   Actual   Delta   Status
  ------------------------------ ------   ------   -----   ------
  [name]                         XX.X%    XX.X%    ±X.Xpp  OK/WARN/DARK
  ...
```

A WARN or DARK cluster is a required checkpoint item exactly like an
enumerative MISMATCH (Step 3.1b/4.2) or a HIGH-REACH span (Step 3.1c/4.2):
the checkpoint cannot close on a general approval signal while one
remains unaddressed.

---

## Step 5 — Post-approval review

Approval at the checkpoint (Step 4) is not the end of Phase 2.

The user may return with observations, corrections, or requests after
having read the approved HTML again, or after pasting it into Spyral.
Handle these exactly as in Step 4 (conversational checkpoint): any
revision triggers a new injection analysis on the affected passage, a
rebuild of the HTML (Step 3.2), and a new approval.

Phase 3 may not begin until the user explicitly signals completion of
Phase 2. If the user stops commenting without signalling, ask:

> "Are you satisfied with this condensation and ready to move
> to Phase 3, or would you like to revisit anything?"

---

## Compliance rules

- **Session logging is Step 0, unconditionally.** No PEEL phase may skip
  it regardless of how small the session seems.
- **The environment precondition check (Step 0.9) is unconditional, and
  its failure protocol is not optional.** No PEEL phase may silently
  substitute a different language or tool for its specified Python
  logic, regardless of how confident the substitute looks. A real,
  documented incident (an on-the-spot Perl reimplementation, unaudited,
  presented with the same confidence as mechanically-verified output)
  is why this rule exists — not a hypothetical. See Step 0 above.
- **Rate 5–30% only.** Refuse rates outside this range with explanation.
- **Free generation.** Do not apply lexical constraints during Step 3.
  Constraints belong in the analysis (Step 3.1), not in the generation.
- **Classify before acting.** Every injection must be typed before
  any decision about it is proposed to the user.
- **Justify on request.** Every classification must be justifiable
  by citing source evidence or its absence.
- **User classification overrides agent classification.** If the user
  reassigns a type, update the record and proceed with the user's type.
- **No invisible C-type injections.** Every C-type span must carry a
  source-reveal mechanism reachable in one click, directly beneath the
  paragraph that contains it — by default a native `<details>/<summary>`
  toggle, collapsed until the reader opens it (v3.4). Never hide it
  behind navigation, search, or a separate appendix, and never depend on
  JS (`onclick`, `<script>`) or an anchor jump, since Spyral's click
  handling and sanitizer cannot be relied upon to deliver those.
  `<details>/<summary>` satisfies this because it is native browser
  disclosure behaviour, not JS-driven, and was confirmed working directly
  in Voyant/Spyral before being adopted as the default (see v3.4
  changelog). If a future Spyral environment is found to strip
  `<details>/<summary>`, fall back to the CSS-only checkbox-hack toggle
  documented in Step 3.2 — do not fall back to the v3.3 always-visible
  inset, which solves visibility at the cost of reading flow.
- **One HTML build step, not two.** There is no separate "diagnostic"
  artifact built before the checkpoint and a different "final" artifact
  built after. Step 3.2 builds the one toggle-equipped HTML; the
  checkpoint (Step 4) reviews and revises that artifact directly,
  rebuilding it each round (see v3.5 changelog).
- **No enumerative MISMATCH, no HIGH-REACH span, and no DARK/WARN cluster,
  may close the checkpoint unresolved.** All three are checkpoint-closure
  conditions of equal severity — see Step 3.1b, Step 3.1c, Step 4.2, and
  Step 4.3.
- **The F/T/R/C classification is a self-report with no independent
  second criterion, and this must be disclosed, not just true.** Step
  3.1d flags F/T spans denser than their own definition allows, as a
  targeted (not complete) mitigation; the permanent, unconditional
  `## Classification verification limits` section (Step 3.2's report
  build) must state this every run, including runs where 3.1d found
  nothing — an absence of flags is never itself evidence that every
  classification is correct. See v3.19 changelog.
- **Environment-precondition outcomes (Step 0.9) must land in the
  permanent report, not only in chat.** `environment_precondition_status`
  is set once at Step 0.9 and written into the mandatory
  `## Environment fallbacks used` section every run — this is the same
  "chat-only disclosure is not durable" discipline already applied to
  every other permanent section in this file. See v3.19 changelog.
- **Reach, not span count or document position, is the signal for
  compression risk.** A C-type span merging three or more source
  paragraphs (reach ≥ 3) is flagged regardless of where it falls in the
  document or how many other C-spans surround it — see Step 3.1c
  changelog (v3.8) for the empirical basis.
- **Never infer approval from silence.** Ask explicitly if the user
  stops commenting without approving.
- **wc -w is authoritative** for word counts.
- **Tolerance is ±5%** at generation stage, ±2% for the approved
  condensation.
- **INLINE STYLES ONLY. No exceptions.** Every HTML element must carry
  its visual properties as a `style="..."` attribute drawn from the S[]
  dictionary (Step 3.2). No `<style>` block. No CSS class names. This
  rule exists because Spyral's HTML cell parser discards `<head>` and all
  class-based rules. Violating this rule silently strips all styling from
  the output.
- **No `<script>`, no `onclick`, no anchor-jump navigation, anywhere.**
  Provenance for C-type and R-type spans must be delivered via the
  `<details>/<summary>` toggle (Step 3.2). Spyral's click-to-edit cell
  behavior and/or its sanitizer cannot be relied upon to let a click
  reach anything JS-driven inside a rendered cell — a mechanism that
  depends on this can appear compliant while being silently
  non-functional. `<details>/<summary>` is exempt from this rule because
  it is native browser disclosure behaviour, not a JS-driven click
  handler.
- **Fragment-first.** The Spyral-injectable file is always a pure HTML
  fragment. The standalone file is a secondary output. Both are always
  produced and presented together, at every build.
- **Structural markup mandatory.** The condensed text must be parsed
  into h1/authors/h2/h3/defn/p blocks before rendering. Flat `<p>`-only
  output is not acceptable.
- **The built artifact must be mechanically verified, not just described,
  before it is written or presented.** Run Step 3.2v on the actual
  `fragment` string after every build (first round and every checkpoint
  revision). A narrated description of compliant HTML is not evidence
  that compliant HTML was produced. If verification fails, fix the
  fragment and re-verify — never write or present a failing artifact,
  and never tell the user it is ready until it passes.
- **Taxonomy display order is F, T, R, C — ascending risk, never F, T, C, R.**
  Every table, legend, meta block, and chat report must list the four
  types in this order. The discrepancy (display order not matching the
  risk order stated in the same table) was a real bug a user caught;
  see v3.6 changelog.
- **Injection colours are four distinct, low-opacity hues, not a single-hue
  scale.** F is gray, T is blue, R is gold, C is red — chosen so each type
  is recognizable by association rather than by a memorized lightness
  order, and so distinctness never depends on having all four types
  present at once. Never use green for C or yellow for T (or any hue whose
  common cultural association — "safe," "caution" — fights the actual
  risk level it represents). Each level also carries a distinct
  border-bottom (none/dotted/dashed/solid) as a colour-independent
  redundant cue. Exact values are in the S[] dictionary, Step 3.2.
- **One source paragraph per `<details>` toggle.** Never stitch quoted
  sentences from two or more different source paragraphs into a single
  toggle with `...` between them. If a condensed sentence compresses
  material from multiple source paragraphs, split it into multiple
  toggles, each quoting one contiguous source paragraph and labelled
  with the specific claim or example it backs.

---

## Error conditions

| Condition | Action |
|---|---|
| JSON not found | Report FAILED. Ask user to upload `*-phase1-state.json`. |
| JSON missing incList / clusterDefs | Report which key is missing. Ask user to re-run Phase 1. |
| TXT file not found | Report FAILED, stop. |
| Cleaned input < 100 words | Report FAILED, ask user to review pre-flight decisions. |
| Rate outside 5–30% | Explain range, ask for clarification. |
| Cluster DARK after condensation | Always flag; always await user decision before checkpoint can close. |
| Cluster WARN after condensation | Flag with explanation; ask: revise or accept? |
| Enumerative MISMATCH (Step 3.1b) | Always flag; always await user decision before checkpoint can close. |
| HIGH-REACH span, reach >= 3 (Step 3.1c) | Always flag; always await user decision before checkpoint can close. |
| Borderline classification flag (Step 3.1d) | Always disclose, batched; await an explicit batch response (keep-as-classified or named exceptions) before checkpoint can close — does not require a separate decision per flagged span, unlike the three rows above. |
| C-type span disputed by user | Reclassify as instructed; rebuild HTML and re-deliver. |
| User requests revision after approval (Step 5) | Reopen checkpoint; re-run injection analysis on affected passage; rebuild HTML. |

---

## Editing clusters before Phase 2

If the user wants to adjust clusters after Phase 1 but before running
Phase 2, two workflows are supported:

**Workflow A — User edits JSON directly:**
The user opens the JSON, moves stems between cluster objects, saves,
and re-uploads. Phase 2 reads the modified file.

**Workflow B — User asks Claude to edit:**
The user uploads the original JSON and describes the change in chat.
Claude applies the edit, re-runs Phase 1 Step 6.2 verification, and
presents the corrected JSON for download before proceeding.

In both cases, Phase 2 reads whatever JSON is uploaded.
Claude never supplements it from memory or from the MD.

---

## What v3.0 changes from v2.5

| v2.5 | v3.0 |
|---|---|
| Generation is constrained: lexical audit, bridge suppression rules, single-pass rule, deictic opener rule | Generation is free: follow the argument, no generation-time constraints |
| Injection is prevented (rules) | Injection is analysed (taxonomy) and typed |
| User sees polished output; problems found in review | User sees diagnostic first; decisions made before final output |
| Step 11 review cycle: six problem categories, fix-type diagnosis | Step 4 conversational checkpoint: open-ended, no fixed categories, user-driven |
| Golden rule: no injection | Reframed golden rule: no invisible C-type injection |
| C-type compressions not distinguished from other injections | C-type compressions hypertext-linked to source in final HTML |
| Cluster coverage verified before delivery | Cluster coverage verified after checkpoint approval |
| Convergence to user satisfaction implicit | Convergence note explicit; checkpoint closure condition stated |
| Phase 3 gate: explicit approval | Phase 3 gate retained; post-delivery review (Step 7) added |

## What v3.2 changes from v3.1

| v3.1 | v3.2 |
|---|---|
| HTML uses `<head><style>` block with CSS class names | All styles inline via `style="..."` attributes — no `<style>` block, no class names |
| Single output file (standalone HTML) | Two output files: `_spyral.html` (fragment) + `_v3.html` (standalone) |
| Fragment compatibility with Spyral not guaranteed | Fragment-first: `_spyral.html` is a pure fragment, paste-ready for Spyral HTML cells |
| Flat `<p>`-only rendering | Structural block parsing: h1, authors, h2, h3, defn, p |
| S[] style dictionary absent | S[] dictionary defined; all render code draws from it |
| Swatch `<span>` fix noted in changelog but not enforced in template | `&nbsp;` in every swatch span enforced in template and compliance rules |
| Sidebar uses `.classList.add('open')` (class-based) | Sidebar open/close via direct `style.transform` (inline, class-free) |
| JS function names generic (`showSource`, `closeSidebar`) | JS names corpus-scoped (`showSrc`, `_closeSb_[corpus_id]`) to avoid collisions in multi-fragment notebooks |

## What v3.3 changes from v3.2

| v3.2 | v3.3 |
|---|---|
| Injection taxonomy operates span-by-span only; no check on document-level structural claims | New Step 3.1b: enumerative/cardinal consistency check, catching cases where a correct C-type merge leaves an explicit "there are N reasons" claim contradicted |
| C-type provenance delivered via sidebar + `onclick` + `<script>` | Sidebar/JS/onclick mechanism removed entirely. C-type and R-type spans carry statically visible inline source insets — no click required |
| R-span provenance delivered via a separate appendix with anchor-jump links (`#rN`) | R-span appendix removed; R-spans now carry the same inline insets as C-spans |
| Checkpoint (Step 4) closes on general user approval | Checkpoint cannot close while any Step 3.1b MISMATCH remains unresolved, regardless of general approval signal |
| Compliance rules silent on `<script>`/`onclick` as a class of risk | New compliance rule: no `<script>`, no `onclick`, no anchor-jump navigation anywhere, since Spyral's click-handling/sanitization cannot be relied upon |

## What v3.4 changes from v3.3

| v3.3 | v3.4 |
|---|---|
| C-type/R-type source passages rendered as an always-visible inline inset div beneath every paragraph | Source passages rendered inside a collapsed-by-default native `<details>/<summary>` toggle; reader opens each one on demand |
| Rationale: no click-dependent mechanism can be trusted in Spyral, so make everything statically visible | Rationale refined: always-visible insets were found to break continuous reading flow; a no-JS *toggle* (not a JS-driven click handler) solves both invisibility and reading flow at once |
| No mechanism tested directly inside Voyant/Spyral before being adopted | `<details>/<summary>` and a CSS-checkbox-hack alternative were both built as minimal test files and verified working directly in a Voyant/Spyral HTML cell before adoption; a title-attribute tooltip was tested and rejected |
| `c_inset`/`r_inset` always rendered open, no `c_summary`/`r_summary` styles in S[] | S[] adds `c_details`/`c_summary`/`r_details`/`r_summary` (default mechanism) and `cb_label` (documented fallback only) |
| Single rendering function (`render_c_inset`/`render_r_inset`) | Renamed `render_c_toggle`/`render_r_toggle`; wraps the same inset content in `<details><summary>...</summary>...</details>` |

## What v3.5 changes from v3.4

| v3.4 | v3.5 |
|---|---|
| Two HTML build stages: a colour-only "diagnostic" (Step 3.2) delivered before the checkpoint, and a source-revealing "final" HTML (Step 6) built only after checkpoint approval | One HTML build step (Step 3.2): the toggle-equipped, source-revealing HTML is built directly and rebuilt at every checkpoint round — no diagnostic-vs-final distinction |
| Diagnostic showed injection classifications but no source text — a classification could not be verified from the diagnostic alone | Every artifact shown to the user already reveals source via collapsed toggles, so review and verification happen on the same file from round one |
| Cluster-coverage verification was Step 5, run once after checkpoint approval, before the separate final-HTML build (Step 6) | Cluster-coverage check is Step 4.3, computed at every HTML build and folded into the checkpoint's closure conditions alongside enumerative MISMATCH |
| Step 6 ("Deliver final HTML") was a distinct step, run once | No separate delivery step — delivery happens at every round of Step 3.2/4; approval just means no further rounds are needed |
| Post-delivery review was Step 7 | Renumbered Step 5 (the steps it followed, old Steps 5–6, no longer exist as separate stages) |

## What v3.6 changes from v3.5

| v3.5 | v3.6 |
|---|---|
| Taxonomy table and every legend/meta block listed types as F, T, C, R | Reordered to F, T, R, C, matching the stated ascending risk order (F<T<R<C) — the display order did not match the risk order it was meant to communicate |
| Four discrete, unrelated hues (pink/yellow/green/blue) for F/T/C/R | Sequential single-hue amber scale, palest (F) to deepest (C); no hue carries an unrelated cultural safety/danger connotation |
| C (highest risk) rendered in green ("safe/go"); T (lower risk) rendered in yellow ("caution") — backwards in common colour semiotics | C is the deepest amber, T is a lighter amber; visual weight now increases with risk |
| Colour was the only channel encoding type/risk | Each type also carries a distinct border-bottom (none/dotted/dashed/solid) as a redundant, colour-independent cue |
| A `<details>` toggle could quote a collage of sentences stitched by `...` from two or more different source paragraphs | Each toggle quotes a contiguous excerpt from exactly one source paragraph; condensed spans drawing on multiple source paragraphs get multiple, individually labelled toggles (e.g. `c8a`/`c8b`/`c8c`) |

## What v3.7 changes from v3.6

| v3.6 | v3.7 |
|---|---|
| Step 2 only ever asked for a single rate at a time | Step 2 offers a choice: one or more custom rates, or a default bundle of 10/15/20/25% |
| No guidance on building multiple rates for the same corpus efficiently | Bundle workflow instructs building each rate by expanding the previous rate's condensation, reusing the fixed costs (source ingestion, S[] dictionary, located source quotes) already paid for the corpus |
| No documented rationale for which rates a default set should include | 10% is explicitly retained in the default bundle rather than dropped as "too costly" — it is also the rate most likely to surface a cluster-coverage WARN or a structurally aggressive C-span, making it diagnostically valuable, not merely expensive |

## What v3.8 changes from v3.7

| v3.7 | v3.8 |
|---|---|
| No check on how many source paragraphs a single C-type span merges — a two-paragraph and a four-paragraph compression were both just "C" | New Step 3.1c computes each C-span's "reach" (distinct source paragraphs merged) and flags reach >= 3 as HIGH-REACH |
| Compression risk was implicitly assumed to track document position or raw C-span count | An empirical four-rate test rejected both: C-spans were densest in the *first* third of every rate, and reach spiked at only one rate (15%) — a budget-tension artifact, not a positional or rate-monotonic one |
| Checkpoint closure conditions: enumerative MISMATCH (3.1b) and DARK/WARN cluster (4.3) | Adds HIGH-REACH span (3.1c) as a third closure condition of equal severity |

## What v3.9 changes from v3.8

| v3.8 | v3.9 |
|---|---|
| Sequential single-hue amber scale (pale F to deep C) | Four distinct hues at light opacity: gray (F), blue (T), gold (R), red (C) |
| C's fill was the deepest/darkest step, read as too heavy against body text | All four types use light opacity (0.18-0.22); C is no longer darker than the others, just a different hue |
| Distinctness relied on a memorized lightness order, which broke down when not all four types were present in a given condensation | Distinctness comes from hue alone — any subset of types remains unambiguous, no order to remember |
| Border-bottom weight (none/dotted/dashed/solid) as colour-independent redundant cue | Unchanged — same border-weight channel, only fill colours changed |


---

## Version History (appendix)

This appendix preserves a condensed versioned changelog for this file. **Current behavior is documented in the numbered steps above, not here** — if this appendix and the steps above ever appear to disagree, the steps above are authoritative for current behavior; this appendix is a historical record only.

- **v3.1** — Legend swatch fix: Spyral's HTML cell parser strips empty `<span>` elements, so every swatch span now contains `&nbsp;`. Legend text expanded to the verbose form (type label plus full definition and risk level). R-span appendix link added.

- **v3.2** (critical Spyral-compatibility fix) — Switched to an inline-style-only HTML architecture: no `<style>` block, no CSS class names, no `<head>`, because Spyral's parser discards `<head>` and therefore all class-based rules, leaving output unstyled. Output is now fragment-first: a pure HTML fragment (Spyral-ready) plus a separate standalone browser-preview file. Condensed text is parsed into typed structural blocks (h1, authors, h2, h3, definition, paragraph), each rendered from a style dictionary, replacing flat `<p>`-only rendering.

- **v3.3** — Added Step 3.1b, an enumerative/cardinal-consistency check: a C-type compression can correctly merge two enumerated items while leaving an explicit "there are N reasons" claim unchanged, which span-by-span injection classification cannot see on its own. A MISMATCH is a hard checkpoint-closure blocker. Replaced the sidebar+`onclick`+`<script>` source-reveal mechanism (broken under Spyral's click handling/sanitization) with always-visible inline source insets.

- **v3.4** — Replaced v3.3's always-visible insets (a reading-flow regression — the reader had to step over interleaved source blocks) with collapsed-by-default native `<details>/<summary>` toggles, opened on demand. Tested directly inside Spyral/Voyant before adoption; a CSS-only checkbox-hack toggle is kept as a documented fallback in case a future Spyral update drops `<details>/<summary>`. A title-attribute tooltip was tested and rejected as unusable.

- **v3.5** — Merged the two-stage diagnostic-then-final HTML workflow into one artifact: once v3.4 made source revelation cheap and non-disruptive, there was no remaining cost reason to delay it behind a separate low-commitment diagnostic build. Cluster-coverage verification (previously a separate post-approval stage) is now computed at every HTML build and folded into the checkpoint's closure conditions.

- **v3.6** — Taxonomy display order corrected to F/T/R/C everywhere (ascending risk order), replacing an inconsistent F/T/C/R ordering. Replaced four unrelated, semiotically backwards hues (e.g. the highest-risk type in green, conventionally "safe") with a sequential single-hue amber scale so visual weight tracks risk directly. Added a border-bottom-style redundancy (none/dotted/dashed/solid) so risk ordering survives for colorblind or grayscale viewing. Each source-reveal toggle now quotes a contiguous excerpt from exactly one source paragraph; a span compressing multiple source paragraphs gets multiple, individually labeled toggles instead of one collaged quote.

- **v3.7** — Step 2 now offers a default 10/15/20/25% rate bundle alongside custom rates: source ingestion, the style dictionary, and located source quotes are fixed per-corpus costs shared across a rate ladder, so building several rates is not simply N times the cost of one. The most aggressive default rate (10%) is deliberately kept rather than dropped as "too costly," since it is empirically the rate most likely to surface a cluster-coverage warning.

- **v3.8** — Added Step 3.1c, a high-reach compression check: a C-type span merging three or more distinct source paragraphs is flagged and blocks checkpoint closure. Reach was found not to track document position (early hypothesis rejected) or rate monotonically — it spikes specifically at whichever rate's word budget creates the tightest multi-point squeeze.

- **v3.9** — Replaced the v3.6 single-hue amber scale with four distinct low-opacity hues (gray=F, blue=T, gold=R, red=C): the darkest step of a single-hue scale read too heavy against body text, and shades became hard to distinguish when not all four types appeared in a given condensation. Border-weight redundancy from v3.6 is unchanged.

- **v3.10** — Fixed a stale F/T/C/R ordering that persisted in the Step 3.2 chat-report template despite v3.6's rule. Added Step 3.2v, a mandatory mechanical artifact-verification pass (toggle counts vs. recorded spans, structural tags present, no single-`<details>`-wraps-everything shape) run before any file is written, after a delivered artifact was found flattened into one plain-text block missing all required markup. Clarified that a multi-rate comparison is an additional chat-level summary, never a replacement for any individual rate's full build. Added the Step 0 session-logging instruction, shared with Phase 1 via the peel-protocol component.

- **v3.11** — `SKILL_VERSION` is now derived from this file's own frontmatter at build time rather than hardcoded in the meta-table template, after a hardcoded version string was found to have gone stale past a version bump.

- **v3.12** — Fixed a `NameError` crash: `word_to_num()` was called in the enumerative-map builder but never defined, so any source using a word-form cardinal ("four" rather than "4") crashed the step outright. Removed a redundant hardcoded version number from the document's own title (the frontmatter field is authoritative). Standing rule adopted: never restate the version number anywhere except the frontmatter or a value derived from it at build time.

- **v3.13** — Step 4.3's cluster-coverage check compared condensed-text coverage against a source-side target that nothing in the file actually computed, so it was not runnable as specified. Fixed by computing `source_coverage` in Step 1 and implementing the OK/WARN/DARK comparison in Step 4.3, including an edge case: a cluster genuinely absent from the source is now OK rather than falsely flagged DARK.

- **v3.14** — Step 3.1b's "realized count" side was prose only, with no algorithm, unlike its mechanical "declared count" side; given the same regex/ordinal-marker-count treatment. The comparison now runs against the condensed text's own restated count rather than the source's original count, since a deliberate, internally consistent revision (source says "four," condensation correctly says "three" after a merge) is not itself an error. Added explicit AMBIGUOUS-MATCH and DROPPED (always escalates) statuses. Removed a stale `wordnet.zip` input reference left over from Phase 1.

- **v3.15** — `ORDINAL_MARKERS` counted every ordinal-word/digit match anywhere in a lookahead window with no ordering requirement, overcounting whenever an unrelated ordinal word recurred later as ordinary prose. Fixed with `count_ordinal_items()`, requiring markers to appear in strict increasing sequence; defined once and shared by Step 1 and Step 3.1b instead of duplicated logic.

- **v3.16** — Added a fourth deliverable, `Phase2-results.md`, a permanent human-readable report of injection-summary counts and enumerative/high-reach results that previously existed only in chat. Building it surfaced that the underlying span-tracking (`all_spans`, `c_count`/`r_count`) and Step 3.1c's high-reach computation had never been implemented as code, only narrated in prose; both were formalized.

- **v3.17** — Added Step 0.9, a mandatory environment precondition check (a trivial Python execution attempted before Step 1). Known failure mode this closes: without it, a missing code-execution environment can lead to an unaudited reimplementation of this skill's mechanical checks in another language, presented with the same confidence as verified numbers — including at least one real discrepancy that the substitute's own self-verification narrative did not catch. On failure, the researcher must be given an explicit choice (switch environments, proceed fully unverified with every claim visibly labeled, or an auditable alternate-language reimplementation only if requested) — never chosen silently on their behalf.

- **v3.18** — Fixed the Step 3.2v toggle-count check: `S['c_details']`/`S['r_details']` are byte-identical strings, so counting them could not distinguish C-type from R-type toggles; and toggle count was being compared against span count rather than the sum of each span's distinct-paragraph reach (a high-reach span produces multiple toggles, not one). Fixed by counting the genuinely distinct `c_summary`/`r_summary` style keys and comparing against a helper summing per-span paragraph-reach.

- **v3.19** — Added Step 3.1d, a targeted heuristic flagging F/T spans that exceed their own stated word-count/density definitions, since the F/T/R/C classification has no independent second criterion the way other checks in this skill do — a C-type span could in principle be misclassified into a low-risk type with no toggle and nothing prompting review. Because the heuristic is prone to false positives on legitimately verbose T-spans, it is disclosed for batch researcher review rather than a hard checkpoint blocker. Added a permanent `## Classification verification limits` section stating that F/T/R/C labels are self-reports and that the absence of a Step 3.1d flag does not certify a span's type is correct. Also implemented a real `## Environment fallbacks used` section wired into the required-headings check — previously referenced in the shared Step 0.9 protocol text but never actually built into this file, so an unverified run's disclosure had no durable home. **Known limitation at the time:** neither fix had yet been exercised against a real condensation.

- **v3.20** — Six issues found and fixed during this file's first live execution, each confirmed by direct execution against real data: (1) ambiguous Phase 1 JSON selection (`json_files[0]` taken unconditionally) now stops and asks when more than one candidate file matches; (2) the structural block parser's line-grouping algorithm was prose only, never executable code — replaced with a real line-by-line scanner, since a naive blank-line split glued section headings to their following paragraph; (3) Step 3.2v's "legend block present" check tested for a literal Python dict key name that could never appear in inline-styled HTML, making it unconditionally unsatisfiable — corrected to test the actual CSS value instead; (4) the mechanical verbatim-alignment scan was also prose only — implemented as `scan_verbatim_overlap()`; (5) the metric labeled "Source-verbatim %" actually measured "words outside any classified span," undercounting overlap that appears inside quoting C/R spans — renamed to `non_injected_pct` and now reported alongside the real `verbatim_overlap_pct`; (6) `FUNCTION_WORD_SET` omitted first/second-person pronouns, inflating content-word counts for first-person academic prose; (7) a dead "Name · Affiliation" byline regex was removed, since the positional author-line fallback fired regardless of whether it matched. **Known limitation carried forward:** the positional author-line fallback assumes a single author line immediately after the title with nothing between them, verified against only one real corpus.

- **v3.21** — Added a fourth output file: a plain Title/Author/Summary text deliverable with no injection markup, built natively from the same typed-block list Step 3.2 already parses, rather than by stripping tags from the finished HTML. Fixed a joining bug found while verifying this: joining body blocks with a uniform blank-line separator inserted a spurious blank line after every heading; fixed to insert a blank line only when the previous block was not itself a heading.

- **v3.22** — Fixed `<h1>` line-height (1.35 → 1.2em), which was too tight for a title that wraps to two lines in Spyral's rendering context.

- **v3.23** — The structural block parser's heading patterns assumed a section number is followed directly by a tab or space (e.g. "1\tIntroduction"). A second real corpus numbered sections "1. Introduction" with a literal period, matching none of its headings. Fixed by making the period optional; verified against both formats.

- **v3.24** — The cluster-coverage table's row-building loop was never real code, only a placeholder comment; an improvised implementation spliced cluster names directly into `<td>` content unescaped, so a name containing `&` broke the HTML. Fixed by routing every cluster name through the existing `esc()` primitive. **Known gap:** Step 3.2v still has no generic unescaped-`&`/`<`/`>` scan of its own, so the same bug shape elsewhere in this file's HTML-building code would not be caught by this skill's own verification.

- **v3.25** — Both hand-built tables (the metadata table and the cluster-coverage table) opened `<table>` with no `<tbody>` wrapper. Valid HTML, but it triggers a spurious parser warning on Spyral import (no data loss — Spyral silently self-heals by inserting the missing tag). Fixed by wrapping both tables' rows in `<tbody>`.

- **v2.0** — Retired the `peel2-phase2`/`peel3-phase2` naming split. This file is the actively maintained v3.25 lineage plus six features cherry-picked from a since-superseded parallel fork (`peel3-phase2-v1.9`). Three of the six turned out to already be present in v3.25 unchanged — the fork had simply inherited them at the point it branched, rather than adding them itself: F/T/R/C display order, the gray/blue/gold/red highlight color scheme, and plain-text summaries as a fourth deliverable. The other three were genuine new work, present in neither line before this file:
  - the enumerative-consistency check (Step 3.1b) redesigned around item-level presence — the inherited approach re-matched an announcement sentence and compared restated-vs-recounted ordinal markers, which missed legitimate paraphrases of the announcement and cross-contaminated with unrelated ordinal sequences elsewhere in the lookahead window; replaced with a check of whether each individually named source item has a surviving trace anywhere in the condensed text, independent of the announcement sentence's own fate;
  - native per-paragraph provenance (Step 3.2, `render_provenance`) — a small, always-visible, native citation naming which source paragraph(s) each condensed paragraph draws from, distinct from and complementary to the existing per-span toggles;
  - the writing-quality gate (Step 3.0v) broadened beyond coherence alone to also cover spelling, grammar, and discourse cohesion, and changed from a one-time check to a mandatory re-run after every revision anywhere in the workflow, since a later edit can introduce a new defect (e.g. a dangling reference) that an earlier single pass has no way to see.

  Two further gaps were closed in the same pass: the ±2% "approved condensation" tolerance was a compliance rule with no enforcing code anywhere in the file, fixed at Step 4.2's closure-condition check; and `build_phase2_report`'s sections were all data (counts, tables, statuses) with no reasoning, so a mandatory `## Drafting & analysis notes` section was added for the interpretive explanation of compression and metric choices, since Phase 3's automatic notebook composition reads this file rather than the chat transcript.

  **Known limitation at the time of writing:** the three genuinely new v2.0 items above (redesigned Step 3.1b, native provenance, revised Step 3.0v) had not yet been exercised against a real corpus when first drafted; treat them as less rigorously verified than the rest of this file until run.
