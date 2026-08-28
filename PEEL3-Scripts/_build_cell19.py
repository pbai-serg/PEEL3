# Deliverable 8 (Section 6b, peel3-phase3-v0.1-DRAFT.md v2.29) -- builds
# Cell 19's five-tool "Source vs Summary" comparison pattern from real
# Phase 1/Phase 3 config values.
#
# This is the first real implementation of the pattern that session's
# hand-built, hand-verified cell19-injection.html was designed against --
# tested below by generating a real an earlier test corpus instance and checking its
# structure (tag balance, palette/lang presence, iframe/code parameter
# sync) rather than assuming the code is correct because it was written
# carefully.
#
# REDESIGNED 2026-07-24 (a later pilot test, researcher-directed
# design pass). The original CONTEXTS mechanism -- researcher picks one
# term from C01/C02/C03, Claude deterministically picks a "companion
# cluster" (earliest remaining in C01-C03 order) and three companion terms
# from it by array position -- had two real, confirmed problems, found by
# actually testing it against real data rather than by reading the design:
#
#   1. Structural bias: C03 can never be selected as companion cluster,
#      for any researcher choice (C01 or C02 is always "earliest
#      remaining"). Disclosed at the time, not silently left broken, but
#      never fixed.
#   2. No evidence the resulting pairs actually collocate in the source at
#      all. "Maximize formal/cluster variety" and "these two terms
#      actually appear near each other in the source text" are different
#      properties -- confirmed empirically: most of the deterministically-
#      derived disjuncts returned zero live Voyant results, because the
#      terms were never observed to co-occur in the first place. A
#      collocation-loss comparison is meaningless if there was no
#      collocation to begin with.
#
# New design principle, developed with the researcher against real
# the later pilot test corpus data: empirically scan the source text for real
# cross-cluster collocations among C01/C02/C03's significant terms, rank
# by actual hit count, flag candidates confounded by a disproportionately
# frequent term (e.g. "ai" in an AI paper co-occurs with nearly everything
# by base rate, not because of a specific relationship), and PRESENT the
# ranked, flagged candidates to the researcher for final selection --
# deliberately not an auto-pick of the top score, since the confound case
# shows raw frequency alone can mislead. See find_source_collocations(),
# flag_confounded(), and format_collocation_candidates() below.
#
# Two hard platform constraints, both confirmed empirically against real
# Voyant output this same session, both now encoded in the query-building
# functions rather than left to be rediscovered by trial and error:
#
#   - A wildcard-shaped term (e.g. "generati*") cannot appear inside a
#     quoted phrase/proximity expression at all -- "\"term generati*\"~N"
#     silently returns zero results even when real matches exist. Must be
#     resolved to its dominant real literal forms first (resolve_literal_
#     forms()) and combined via the cartesian product of both sides'
#     forms (build_proximity_clauses()).
#   - Multiple complete proximity clauses must be combined with PIPE (|),
#     never comma. Comma silently drops real matches when joining
#     multiple full phrase-proximity clauses (confirmed: an identical
#     clause set returned 21 results with comma, 44 with pipe, against
#     live Voyant). Comma appears reserved for combining genuinely
#     different syntax types (a standalone wildcard term alongside a
#     phrase, per Voyant's own documentation example) -- a narrower case
#     this design doesn't need, since every wildcard here is pre-resolved
#     to literal forms before combination.

# 2026-08-01 fix (another test corpus corpus, real live-Voyant incident): _iframe()
# and build_bubblelines_block() hardcoded "https://voyant.inf.puc-rio.br" as the
# tool-iframe host for every Cell 19 visualization. This was correct for the
# an earlier test corpus and the later pilot test corpus sessions this module was developed against,
# both of which really did use that production instance -- but a later
# researcher session ran against a local Voyant instance instead
# (http://<local-voyant-instance>), and nothing here ever asked which host was actually
# in use. The delivered notebook's Cell 19 failed with Voyant's own "A corpus
# was specified but does not exist, could not be migrated and could not be
# recreated" error -- a completely accurate error, since the corpus really
# didn't exist on the assumed (wrong) server; the corpus/categories IDs
# themselves were confirmed correct by direct comparison against the
# researcher's own genuine Voyant-exported iframe. Fixed by making the host an
# explicit, required `voyant_host` parameter threaded through every
# iframe-building function (_iframe, build_trends_block,
# build_bubblelines_block, build_cirrus_block, build_contexts_block,
# build_collocates_block, build_cell19_content) -- no default value, so a
# caller must supply it explicitly rather than silently inheriting a
# production-instance assumption. skills/peel3-phase3-v2.54.md's own Step 1.3
# combined elicitation round is the intended place to actually ask the
# researcher for this value (see that file's own changelog for this same
# date). Verified against real data: rebuilt this session's actual delivered
# notebook with the corrected host, confirmed the 11 real tool-iframe URLs
# switched from the wrong host to the researcher's real one while the 44
# legitimate documentation/Spyral-guide links (which correctly point at the
# real puc-rio.br docs server regardless of which Voyant instance serves the
# corpus) were left untouched.

import re
import html as _html
import statistics
from collections import Counter
from datetime import date
from itertools import combinations
from urllib.parse import quote as _urlquote


def esc(text):
    return _html.escape(str(text), quote=False)


def _today():
    # v2.42: generation-time date stamp for auto-generated disclosure
    # notes (e.g. the missing-companion-shape note in build_contexts_block)
    # -- matches this project's existing convention of a literal date in
    # disclosure text, computed at run time rather than hand-typed.
    return date.today().isoformat()


# ---------------------------------------------------------------------------
# Step 1 -- empirically-grounded collocation discovery (v2.49, 2026-07-24)
# ---------------------------------------------------------------------------

def _c01_c03(clusterDefs):
    return [c for c in clusterDefs if re.match(r'^C0[1-3]', c['token'])]


def classify_term(term):
    """Three lexical shapes a Phase 1 term can take: a wildcard-form stem
    ('expert*'), a plain single-word term ('expertise'), or a multi-word
    N-gram/expression ('black box'). Order of these checks matters: a
    term could in principle contain both a space and a '*' (not seen in
    real data yet, but not impossible), so stem is checked first."""
    if '*' in term:
        return 'stem'
    if ' ' in term:
        return 'ngram'
    return 'word'


def _tokenize(source_text):
    return re.findall(r"[A-Za-z']+", source_text.lower())


def _term_positions(term, words):
    """Token-index positions where `term` occurs in `words`. Handles all
    three lexical shapes: stem (prefix wildcard, e.g. 'generati*' matches
    'generation'/'generative'/'generations'), N-gram (sequential
    multi-word match), and plain word (exact match)."""
    term = term.strip('"').lower()
    if term.endswith('*'):
        prefix = term[:-1]
        return [i for i, w in enumerate(words) if w.startswith(prefix)]
    if ' ' in term:
        parts = term.split()
        n = len(parts)
        return [i for i in range(len(words) - n + 1) if words[i:i + n] == parts]
    return [i for i, w in enumerate(words) if w == term]


def find_source_collocations(source_text, clusterDefs, proximity_n=5):
    """Empirically scans the real source text for cross-cluster
    co-occurrences among C01/C02/C03's significant terms -- never
    same-cluster (2026-07-21 finding: pairing near-synonyms from one
    cluster isn't analytically interesting). Replaces the old
    deterministic "earliest remaining cluster, front-of-cluster salience"
    derivation, which had no evidence behind it that the resulting pairs
    ever actually co-occur.

    Uses gap <= proximity_n + 1 as the match threshold, matching Voyant's
    own confirmed proximity-operator semantics (Lesson 19,
    peel3-phase3-v0.1-DRAFT.md: "~N means N words *between* the two
    terms -- a token-index gap of N+1, not N" -- confirmed twice
    independently against real data), so candidate ranking here reflects
    what the actual '~N' query will find, not a naive off-by-one guess.

    Returns a list of dicts sorted by real hit count descending:
    {hits, cluster_a, term_a, freq_a, cluster_b, term_b, freq_b}.
    freq_a/freq_b (each term's own total occurrence count in the source)
    are carried through for flag_confounded() to use."""
    words = _tokenize(source_text)
    clusters = _c01_c03(clusterDefs)
    gap_max = proximity_n + 1

    positions = {}
    for c in clusters:
        for t in c['stems']:
            positions[(c['token'], t)] = _term_positions(t, words)

    results = []
    for ca, cb in combinations(clusters, 2):
        for ta in ca['stems']:
            pa = positions[(ca['token'], ta)]
            if not pa:
                continue
            for tb in cb['stems']:
                pb = positions[(cb['token'], tb)]
                if not pb:
                    continue
                hits = sum(1 for x in pa for y in pb if abs(x - y) <= gap_max)
                if hits:
                    results.append({
                        'hits': hits,
                        'cluster_a': ca['token'], 'term_a': ta, 'freq_a': len(pa),
                        'cluster_b': cb['token'], 'term_b': tb, 'freq_b': len(pb),
                    })
    results.sort(key=lambda r: -r['hits'])
    return results


def flag_confounded(candidates, ubiquity_multiple=5):
    """Flags a candidate as confounded when either term's own raw source
    frequency is disproportionately high relative to other candidate
    terms -- real, observed failure mode (that later pilot test's 'ai', 180
    occurrences, co-occurred with nearly every other significant term by
    base rate alone, not because of any specific relationship; it
    dominated the top of a pure hits-ranked list without being
    analytically interesting). Heuristic, not a hard science, disclosed
    as such in its own output: flags a term whose frequency exceeds
    `ubiquity_multiple` times the MEDIAN frequency across every term
    appearing in any candidate pair. Mutates and returns `candidates`."""
    all_freqs = sorted({c['freq_a'] for c in candidates} | {c['freq_b'] for c in candidates})
    median_freq = statistics.median(all_freqs) if all_freqs else 0
    threshold = median_freq * ubiquity_multiple
    for c in candidates:
        a_over = c['freq_a'] > threshold
        b_over = c['freq_b'] > threshold
        c['confounded'] = a_over or b_over
        c['confound_reason'] = None
        if c['confounded']:
            culprit, culprit_freq = (c['term_a'], c['freq_a']) if a_over else (c['term_b'], c['freq_b'])
            c['confound_reason'] = (
                f"{culprit!r} appears {culprit_freq} times in the source "
                f"(>{ubiquity_multiple}x the median candidate-term frequency, "
                f"{median_freq:.0f}) -- co-occurrence with it is not necessarily "
                f"meaningful, just likely by base rate."
            )
    return candidates


def format_collocation_candidates(candidates, top_n=10):
    """Human-readable, ranked, confound-flagged presentation of real
    collocation candidates -- for the researcher to choose from, not for
    Claude to auto-pick. Deliberate design choice: raw frequency ranking
    alone can mislead (the 'ai' case would put a confounded pair at rank
    1), so final selection of which relationship is worth testing stays
    a researcher decision, informed by real data rather than either
    guessed blind or derived by an opaque mechanical rule."""
    lines = [
        '| Rank | Hits | Term A (cluster) | Term B (cluster) | Note |',
        '|---|---|---|---|---|',
    ]
    for i, c in enumerate(candidates[:top_n], 1):
        note = f"possibly confounded -- {c['confound_reason']}" if c['confounded'] else ''
        lines.append(
            f"| {i} | {c['hits']} | `{c['term_a']}` ({c['cluster_a']}) | "
            f"`{c['term_b']}` ({c['cluster_b']}) | {note} |"
        )
    return '\n'.join(lines)


# ---------------------------------------------------------------------------
# Step 2 -- shared building blocks
# ---------------------------------------------------------------------------

def build_category_legend_comment(clusterDefs):
    """The 12-line (or however many clusters) reference comment listing
    every available @Category token with its full Phase 1 name -- a
    reference for the researcher, not a constraint on the active query
    (Section 6.3's own rule)."""
    lines = ['// Available @Category queries for this corpus:']
    token_strs = [f'"@{c["token"]}"' for c in clusterDefs]
    pad = max(len(t) for t in token_strs) + 2
    for c, tok in zip(clusterDefs, token_strs):
        lines.append(f'//   {tok.ljust(pad)}{esc(c["name"])}')
    return '<br />\n'.join(lines)


def _iframe(tool_path, params, height, voyant_host):
    qs = '&amp;'.join(f'{k}={v}' for k, v in params.items())
    return f'<p><iframe src="{voyant_host}/tool/{tool_path}/?{qs}" style="width: 100%; height: {height}px;"></iframe></p>'


# ---------------------------------------------------------------------------
# Step 3 -- Family 1: TRENDS / BUBBLELINES (single iframe, built-in drill-down)
# ---------------------------------------------------------------------------

def build_trends_block(comparison_corpus_id, categories_id, category_tokens, clusterDefs, description, voyant_host):
    query_csv = ','.join(category_tokens)
    iframe = _iframe('Trends', {
        'palette': 'Tableau20',
        'categories': categories_id,
        'lang': 'en',
        'query': _urlquote(query_csv, safe=''),
        'bins': '5',
        'corpus': comparison_corpus_id,
    }, 432, voyant_host)
    legend = build_category_legend_comment(clusterDefs)
    query_js = ', '.join(f'"{t}"' for t in category_tokens)
    code = (
        f'<p><code>// ── TRENDS ───────────────────────────────────────────────────────────────────<br />\n'
        f'{legend}</code></p>\n\n'
        f'<p><code>let config = {{<br />\n'
        f'&nbsp; lang:&nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; "en",<br />\n'
        f'&nbsp; categories:&nbsp; &nbsp; &nbsp; &nbsp; catsId,<br />\n'
        f'&nbsp; query:&nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp;[{query_js}],<br />\n'
        f'&nbsp; withDistributions: "relative",<br />\n'
        f'&nbsp; chartType:&nbsp; &nbsp; &nbsp; &nbsp; &nbsp;"barline",<br />\n'
        f'&nbsp; bins:&nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; 5,<br />\n'
        f'&nbsp; palette: "Tableau20",<br />\n'
        f'}};</code></p>\n\n'
        f'<p><code>loadCorpus(myComparisonCorpus).tool("Trends", config);</code></p>'
    )
    return (
        f'<h1><strong>TRENDS</strong></h1>\n\n<blockquote>\n'
        f'<p>{description}</p>\n\n{iframe}\n\n'
        f'<p>Use this code in the empty code cell next to this one to reproduce the visualization we show for the comparison.</p>\n\n'
        f'{code}\n\n<p>&nbsp;</p>\n</blockquote>\n\n<p>&nbsp;</p>'
    )


def build_bubblelines_block(comparison_corpus_id, categories_id, category_tokens, clusterDefs, description, voyant_host):
    query_params = '&amp;'.join(f'query={_urlquote(t)}' for t in category_tokens)
    iframe_url = (
        f'{voyant_host}/tool/Bubblelines/?palette=Tableau20&amp;'
        f'categories={categories_id}&amp;lang=en&amp;bins=5&amp;{query_params}&amp;'
        f'corpus={comparison_corpus_id}'
    )
    iframe = f'<p><iframe src="{iframe_url}" style="width: 100%; height: 705px;"></iframe></p>'
    legend = build_category_legend_comment(clusterDefs)
    query_js = ', '.join(f'"{t}"' for t in category_tokens)
    code = (
        f'<p><code>// ── BUBBLELINES ───────────────────────────────────────────────────────────────<br />\n'
        f'{legend}</code></p>\n\n'
        f'<p><code>let config = {{<br />\n'
        f'&nbsp; lang:&nbsp; &nbsp; &nbsp; &nbsp;"en",<br />\n'
        f'&nbsp; categories: catsId,<br />\n'
        f'&nbsp; query:&nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp;[{query_js}],<br />\n'
        f'&nbsp; bins:&nbsp; &nbsp; &nbsp; &nbsp;5,<br />\n'
        f'&nbsp; palette: "Tableau20",<br />\n'
        f'}};</code></p>\n\n'
        f'<p><code>loadCorpus(myComparisonCorpus).tool("Bubblelines", config);</code></p>'
    )
    return (
        f'<h1><strong>BUBBLELINES</strong></h1>\n\n<blockquote>\n'
        f'<p>{description}</p>\n\n{iframe}\n\n'
        f'<p>Use this code in the empty code cell next to this one to reproduce the visualization we show for the comparison.</p>\n\n'
        f'{code}\n\n<p>&nbsp;</p>\n</blockquote>\n\n<p>&nbsp;</p>'
    )


# ---------------------------------------------------------------------------
# Step 4 -- Family 2: CIRRUS / CONTEXTS / COLLOCATES (docIndex-split, 3 iframes)
# ---------------------------------------------------------------------------

def _doc_labels(approved_rates):
    labels = ['Source'] + [f'Summary at {r}%' for r in approved_rates]
    comment = '; '.join(f'{i}: {l}' for i, l in enumerate(labels)) + ';'
    return labels, comment


def build_cirrus_block(comparison_corpus_id, stoplist_id, approved_rates, voyant_host):
    labels, doc_comment = _doc_labels(approved_rates)
    iframes = []
    for i, label in enumerate(labels):
        h3 = 'Visualization of the Source' if i == 0 else f'Visualization of the {label}'
        iframe = _iframe('Cirrus', {
            'palette': 'Tableau20', 'lang': 'en', 'categories': 'none',
            'stopList': stoplist_id, 'visible': '100', 'docIndex': str(i),
            'corpus': comparison_corpus_id,
        }, 400, voyant_host)
        iframes.append(f'<h3>{h3} (docIndex = {i})</h3>\n\n{iframe}')
    code = (
        '<p><code>// ── CIRRUS ──────────────────────────────────────────────────────────────────</code></p>\n\n'
        '<p><code>let config = {<br />\n'
        '&nbsp; lang:&nbsp; &nbsp; &nbsp; &nbsp; &nbsp;"en",<br />\n'
        '&nbsp; categories: "none",&nbsp; // category coloring did not render as expected for Cirrus<br />\n'
        '&nbsp; visible:&nbsp; &nbsp; 100,<br />\n'
        f'&nbsp; stopList:&nbsp; &nbsp;excListFull,<br />\n'
        f'&nbsp; docIndex: 0, // {doc_comment}<br />\n'
        '&nbsp; palette: "Tableau20",<br />\n'
        '};</code></p>\n\n'
        '<p><code>loadCorpus(myComparisonCorpus).tool("Cirrus", config);</code></p>'
    )
    caveat = (
        'Word color and position in the three clouds below are assigned independently '
        'for each visualization and carry no comparative meaning &mdash; the same term '
        'can appear in a different color and a different spot in each cloud. Only '
        'relative size (word frequency) is comparable across the three; see the SUMMARY '
        "tool&#39;s results in the cell above, for easily comparable word-frequency "
        'information across all documents in this comparison.'
    )
    return (
        '<h1><strong>CIRRUS</strong></h1>\n\n<blockquote>\n'
        '<p>CIRRUS produces word clouds, a popular representation of the most frequent terms in a document.</p>\n\n'
        f'<p>{caveat}</p>\n\n'
        + '\n\n'.join(iframes) + '\n\n'
        '<p>Use this code in the empty code cell next to this one to reproduce the visualizations we show for the comparison.</p>\n\n'
        f'{code}\n\n<p>&nbsp;</p>\n</blockquote>\n\n<p>&nbsp;</p>'
    )


def resolve_literal_forms(term, words, min_share=0.9, max_forms=3):
    """If `term` is a stem (wildcard), resolves it to its dominant real
    literal forms in the source -- Voyant's proximity operator cannot
    accept a wildcard inside a quoted phrase at all (confirmed 2026-07-23,
    that later pilot test pilot, researcher-tested: '"term generati*"~N' returns
    zero results even when real matches exist -- a hard platform
    constraint, not a quoting bug this session's earlier fixes could
    reach). Returns the fewest literal forms covering at least `min_share`
    of the term's real occurrences (ranked by real frequency, not
    alphabetically), capped at `max_forms` so a long-tail wildcard
    doesn't explode the resulting query combinatorially. Plain words and
    N-grams pass through unchanged as a single-item list."""
    term_bare = term.strip('"')
    if not term_bare.endswith('*'):
        return [term_bare]
    prefix = term_bare[:-1]
    counts = Counter(w for w in words if w.startswith(prefix))
    total = sum(counts.values())
    if total == 0:
        return [term_bare]  # no real occurrences -- caller should have filtered this candidate out already
    forms, covered = [], 0
    for form, n in counts.most_common(max_forms):
        forms.append(form)
        covered += n
        if covered / total >= min_share:
            break
    return forms


def build_proximity_clauses(term_a, term_b, words, proximity_n=5):
    """Builds the quoted proximity clause(s) for one candidate pair,
    expanding any wildcard-shaped side into its real literal forms first
    (resolve_literal_forms) -- the cartesian product of both sides'
    resolved forms, since a wildcard cannot appear inside the phrase
    itself. For two plain terms this is a single clause; for two
    wildcards it can be up to max_forms x max_forms clauses."""
    forms_a = resolve_literal_forms(term_a, words)
    forms_b = resolve_literal_forms(term_b, words)
    return [f'"{a} {b}"~{proximity_n}' for a in forms_a for b in forms_b]


def build_collocation_comparison_query(selected_pairs, words, proximity_n=5):
    """Combines every selected pair's proximity clause(s) into one query
    string. Uses PIPE, never comma, to combine multiple complete
    proximity clauses -- confirmed 2026-07-24 (that later pilot test pilot,
    researcher-tested against live Voyant): an identical six-clause set
    returned 21 real matches with comma, 44 with pipe -- comma was
    silently dropping matches, not just for the wildcard-resolved
    clauses but for the plain-word ones too. Comma appears reserved for
    combining genuinely different syntax types (a standalone wildcard
    term alongside a phrase, per Voyant's own documentation example) --
    a narrower case this function doesn't need, since every wildcard
    here is pre-resolved to literal forms before this point.

    selected_pairs: list of candidate dicts (as returned by
    find_source_collocations/flag_confounded), or plain (term_a, term_b)
    tuples -- either is accepted."""
    all_clauses = []
    for pair in selected_pairs:
        if isinstance(pair, dict):
            term_a, term_b = pair['term_a'], pair['term_b']
        else:
            term_a, term_b = pair
        all_clauses.extend(build_proximity_clauses(term_a, term_b, words, proximity_n))
    return '|'.join(all_clauses)


def build_contexts_block(comparison_corpus_id, stoplist_id, categories_id, approved_rates,
                          selected_pairs, source_text, clusterDefs, voyant_host, proximity_n=5):
    """selected_pairs: the researcher's chosen real, source-confirmed
    collocations (candidate dicts from find_source_collocations, after
    the researcher picked from format_collocation_candidates' ranked
    list) -- NOT a deterministic single-cluster derivation.

    REDESIGNED 2026-07-24 (a later pilot test, researcher-
    directed). The old design (one companion cluster, deterministically
    tie-broken to "earliest remaining in C01-C03 order," three companion
    terms picked by array position) produced pairs with no evidence they
    ever co-occur in the source -- confirmed empirically to return zero
    live-Voyant results for most of its own disjuncts. This version only
    ever builds queries around pairs already confirmed, by direct scan
    of the real source text, to actually collocate -- see
    find_source_collocations() and the module docstring for the two
    platform constraints (wildcard-in-phrase, comma-vs-pipe) this
    function's query construction encodes."""
    words = _tokenize(source_text)
    labels, doc_comment = _doc_labels(approved_rates)
    query_str = build_collocation_comparison_query(selected_pairs, words, proximity_n)

    iframes = []
    for i, label in enumerate(labels):
        h3 = 'Contexts in the Source' if i == 0 else f'Contexts in the {label} condensation rate'
        iframe = _iframe('Contexts', {
            'palette': 'Tableau20', 'lang': 'en', 'categories': categories_id,
            'query': _urlquote(query_str), 'docIndex': str(i), 'context': '8',
            'expand': '100', 'columns': 'left%2Cterm%2Cright', 'sort': 'right',
            'dir': 'asc', 'termColors': 'terms', 'corpus': comparison_corpus_id,
        }, 500, voyant_host)
        iframes.append(f'<h3>{h3}</h3>\n\n{iframe}')

    def _pair_terms(p):
        return (p['term_a'], p['term_b']) if isinstance(p, dict) else p

    pairs_list = ' and '.join(
        f'&quot;{esc(a)}&quot;/&quot;{esc(b)}&quot;' for a, b in (_pair_terms(p) for p in selected_pairs)
    )
    description = (
        f'In this CONTEXTS configuration, we see all occurrences of {pairs_list} within '
        f'{proximity_n} words of each other. Unlike a query built purely to maximize term '
        'variety, these pairs were selected because they are real, confirmed collocations in '
        'the source text -- so this comparison tests whether an existing relationship survives, '
        'is altered, or is lost in each summary, not whether an arbitrary pairing happens to '
        'appear anywhere. Click on any row of the table to see the expanded context of the '
        'occurrence (i.e. what that document says) and create your own search expressions to '
        'check source content against summary content.'
    )
    query_comment_terms = ', '.join(f'{a} near {b}' for a, b in (_pair_terms(p) for p in selected_pairs))
    code = (
        '<p><code>// ── CONTEXTS ──────────────────────────────────────────────────────────────────<br />\n'
        + build_category_legend_comment(clusterDefs) + '</code></p>\n\n'
        '<p><code>let config = {<br />\n'
        '&nbsp; lang:&nbsp; &nbsp; &nbsp; &nbsp; &nbsp;"en",<br />\n'
        '&nbsp; categories: catsId,<br />\n'
        "&nbsp; columns: ['left', 'term', 'right'],<br />\n"
        '&nbsp; context: 8,<br />\n'
        '&nbsp; expand: 100,<br />\n'
        "&nbsp; dir: 'asc',<br />\n"
        f'&nbsp; docIndex: 0, // {doc_comment}<br />\n'
        f'&nbsp; query: \'{query_str}\', // {query_comment_terms} (within {proximity_n} words, any branch)<br />\n'
        '&nbsp; sort: "right",<br />\n'
        '&nbsp; termColors: "terms",<br />\n'
        '&nbsp; palette: "Tableau20",<br />\n'
        '};</code></p>\n\n'
        '<p><code>loadCorpus(myComparisonCorpus).tool("Contexts", config);</code></p>'
    )

    evidence_items = []
    for p in selected_pairs:
        a, b = _pair_terms(p)
        hits = p.get('hits') if isinstance(p, dict) else None
        confound_flag = ' (researcher-accepted despite the confound flag)' if (isinstance(p, dict) and p.get('confounded')) else ''
        if hits is not None:
            evidence_items.append(f'&quot;{esc(a)}&quot;/&quot;{esc(b)}&quot;: {hits} real co-occurrences in the source{confound_flag}')
    evidence_note = ''
    if evidence_items:
        evidence_note = (
            '<p style="background:#eef3f7;border:1px solid #cfe0ea;padding:6px 10px;">'
            f'<strong>Why these pairs ({_today()}):</strong> ' + '; '.join(evidence_items) +
            ' -- confirmed by direct scan of the real source text, not assumed or picked to '
            'maximize formal/cluster variety alone.</p>\n\n'
        )

    return (
        '<h1><strong>CONTEXTS</strong></h1>\n\n'
        f'{evidence_note}<blockquote>\n'
        f'<p>{description}</p>\n\n'
        + '\n\n'.join(iframes) + '\n\n'
        '<p>Use this code in the empty code cell next to this one to reproduce the visualizations we show for the comparison.</p>\n\n'
        f'{code}\n\n<p>&nbsp;</p>\n</blockquote>\n\n<p>&nbsp;</p>'
    )


def build_collocates_block(comparison_corpus_id, stoplist_id, categories_id, approved_rates, term, voyant_host):
    labels, doc_comment = _doc_labels(approved_rates)
    iframes = []
    for i, label in enumerate(labels):
        h3 = 'Collocates in the Source' if i == 0 else f'Collocates in the {label} condensation rate'
        iframe = _iframe('CorpusCollocates', {
            'palette': 'Tableau20', 'lang': 'en', 'categories': categories_id,
            'stopList': stoplist_id, 'query': _urlquote(term), 'docIndex': str(i),
            'context': '5', 'columns': 'term%2CrawFreq%2CcontextTerm%2CcontextTermRawFreq',
            'corpus': comparison_corpus_id,
        }, 400, voyant_host)
        iframes.append(f'<h3>{h3}</h3>\n\n{iframe}')
    description = (
        f'<strong>COLLOCATES</strong> show how frequently one term -- in the comparisons below, '
        f'the term&nbsp;<em>{esc(term)}</em>&nbsp;-- occurs within the range of so many words to its right '
        'or left -- in our case, 5 words (i.e. which words&nbsp;<em>go together</em>). Collocation is '
        'a patterned&nbsp;<em>relation</em>&nbsp;between terms, which may correspond to semantic relations '
        '(to see if this is the case, search collocated terms with CONTEXTS).'
    )
    glossary = (
        '<p>Table Columns Headings:</p>\n\n<ul>\n'
        '\t<li><em>Term</em>: this is the keyword (or keywords) being searched</li>\n'
        '\t<li><em>Count</em> is the frequency of the keyword term in this document</li>\n'
        '\t<li><em>Collocate</em>: these are the words found in proximity of each keyword</li>\n'
        '\t<li><em>Count (context)</em>: this is the frequency of the collocate occurring in proximity to the keyword</li>\n'
        '</ul>'
    )
    code = (
        '<p><code>// ── COLLOCATES ──────────────────────────────────────────────────────────────────</code></p>\n\n'
        '<p><code>let config = {<br />\n'
        '&nbsp; lang:&nbsp; &nbsp; &nbsp; &nbsp; &nbsp;"en",<br />\n'
        "&nbsp; columns: ['term', 'rawFreq', 'contextTerm', 'contextTermRawFreq'],<br />\n"
        '&nbsp; context: 5,<br />\n'
        f'&nbsp; docIndex: 0, // {doc_comment}<br />\n'
        f"&nbsp; query: '{term}', // Change this to whatever search expression you wish to test.<br />\n"
        '&nbsp; stopList: excListFull,<br />\n'
        '&nbsp; categories: catsId,<br />\n'
        '&nbsp; palette: "Tableau20",<br />\n'
        '};</code></p>\n\n'
        '<p><code>loadCorpus(myComparisonCorpus).tool("CorpusCollocates", config);</code></p>'
    )
    return (
        '<h1><strong>COLLOCATES</strong></h1>\n\n<blockquote>\n'
        f'<p>{description}</p>\n\n{glossary}\n\n'
        + '\n\n'.join(iframes) + '\n\n'
        '<p>Use this code in the empty code cell next to this one to reproduce the visualizations we show for the comparison.</p>\n\n'
        f'{code}\n\n<p>&nbsp;</p>\n</blockquote>\n\n<p>&nbsp;</p>'
    )


# ---------------------------------------------------------------------------
# Step 5 -- assembly
# ---------------------------------------------------------------------------

def build_cell19_content(clusterDefs, comparison_corpus_id, stoplist_id, categories_id,
                          approved_rates, selected_pairs, source_text, voyant_host, primary_term=None):
    """clusterDefs: list of {token, full_name, terms} dicts, C01..Cnn, Phase 1 order.
    approved_rates: list of ints/strs, e.g. [10, 25].

    selected_pairs: the researcher's chosen real collocation(s) -- candidate
    dicts from find_source_collocations()/flag_confounded(), after she
    picked from format_collocation_candidates()'s ranked, confound-flagged
    list (see the elicitation flow in the module docstring). Replaces the
    old single `researcher_term` -- there is no longer a single "companion
    cluster" derivation; every pair here is independently source-confirmed.

    source_text: the real cleaned corpus text, needed to resolve any
    wildcard-shaped term in selected_pairs to its real literal forms
    before building CONTEXTS' query (see resolve_literal_forms).

    primary_term: the single term COLLOCATES (which shows one term's
    collocates, not a pairwise comparison) is built around. Defaults to
    the first selected pair's term_a -- a simplification, disclosed here
    rather than silently chosen: COLLOCATES' own single-term design
    doesn't map cleanly onto a multi-pair selection, so it anchors on
    whichever term the researcher's first-ranked real collocation
    started from."""
    if primary_term is None:
        first = selected_pairs[0]
        primary_term = first['term_a'] if isinstance(first, dict) else first[0]

    c01_c03_tokens = [f"@{c['token']}" for c in _c01_c03(clusterDefs)]  # default query: first three, Section 6.3

    skeleton_top = (
        '<table align="left" border="2" cellpadding="3" cellspacing="1" style="width: 50px;">\n'
        '\t<tbody>\n\t\t<tr>\n\t\t\t<td style="background: #8AC29C; width: 50px;">&nbsp;</td>\n'
        '\t\t</tr>\n\t</tbody>\n</table>\n\n<p>&nbsp;</p>\n\n<p>&nbsp;</p>\n\n'
    )

    trends_desc = (
        'TRENDS shows how the frequency distributions of the selected categories in the '
        'source compare to those in the summaries &mdash; that is, how similar or dissimilar '
        'their trends are across segments.'
    )
    bubblelines_desc = (
        'BUBBLELINES shows how the counts and ratios of terms from selected categories '
        'compare across document segments &mdash; that is, how similar or dissimilar the '
        'summaries are to the source. Check the &quot;Separate lines for terms&quot; option '
        'to evaluate ratios and proportions in source and summaries.'
    )

    blocks = [
        build_trends_block(comparison_corpus_id, categories_id, c01_c03_tokens, clusterDefs, trends_desc, voyant_host),
        build_bubblelines_block(comparison_corpus_id, categories_id, c01_c03_tokens, clusterDefs, bubblelines_desc, voyant_host),
        build_cirrus_block(comparison_corpus_id, stoplist_id, approved_rates, voyant_host),
        build_contexts_block(comparison_corpus_id, stoplist_id, categories_id, approved_rates,
                              selected_pairs, source_text, clusterDefs, voyant_host),
        build_collocates_block(comparison_corpus_id, stoplist_id, categories_id, approved_rates,
                                primary_term, voyant_host),
    ]

    content = skeleton_top + '\n\n'.join(blocks)

    def _pair_summary(p):
        if isinstance(p, dict):
            return {'term_a': p['term_a'], 'cluster_a': p['cluster_a'],
                     'term_b': p['term_b'], 'cluster_b': p['cluster_b'],
                     'hits': p['hits'], 'confounded': p.get('confounded', False)}
        return {'term_a': p[0], 'term_b': p[1]}

    return content, {
        'selected_pairs': [_pair_summary(p) for p in selected_pairs],
        'primary_term': primary_term,
    }


# ---------------------------------------------------------------------------
# Step 6 -- Cells 14, 15-18, 20: the fixed, corpus-independent parts of
# Deliverable 8 (Section 6b.1, 6b.2, 6b.4). Added v2.32, wiring Deliverable 8
# into populate_notebook() for the first time -- these five cells previously
# existed only as one-off, hand-delivered injection files
# (cell14/15/16/17-injection.{html,js} from the 2026-07-19 session), never as
# reusable functions Deliverable 6's assembly step could call.
# ---------------------------------------------------------------------------

def build_cell14_content():
    """Cell 14 -- comparison intro (6b.1). Fixed, corpus-independent."""
    return (
        '<div style="background:#0081AD; color: #FBFBFB; padding: 5px; height: 50px;">'
        '<h1><strong>Comparing Source and Summaries</strong></h1></div>\n\n'
        '<p>Comparing source and summaries shows how summaries differ from the source. '
        'By definition, source and summaries are - and must be - different. The question '
        'is: what can we infer from these differences with respect to how the summaries '
        'represent the source. What is omitted, what is highlighted, what is simplified, '
        'what is repeated verbatim, and so on.</p>'
    )


def build_cell15_content():
    """Cell 15 -- Documents tool description, rewired to the comparison corpus
    (6b.2). Content confirmed against the researcher's real, live, saved
    notebook (PEEL3-SN-Ready-V1-2.html, cell id o3wrqaye) -- verbatim except
    for one fix applied here: the live cell hardcodes document count
    ("both approved condensation summaries", "lists all three documents side
    by side"), which is a real, pre-existing violation of this file's own
    Pre-Generation Checklist item ("No cell in the 14-20 block references a
    hardcoded document count in prose... where a count-agnostic phrase would
    do") -- present in the live notebook, not just an old draft. Rephrased
    count-agnostically here, matching 6b.2's own rationale text ("Documents
    lists every document side by side")."""
    return (
        '<h1>DOCUMENTS</h1>\n\n'
        '<div style="background:#eeeeee;border:1px solid #cccccc;padding:5px 10px;">'
        'The <a href="https://voyant.inf.puc-rio.br/docs/tutorial-documents.html" target="_blank">DOCUMENTS</a> '
        'tool is used to manage documents in a <em>corpus</em>. Documents can be added, deleted, and reordered.<br />\n'
        'The output of the code cell below is fully effective. All interactive controls and optional parameter settings can be used.&nbsp;</div>\n\n'
        '<p><br />\n'
        '<strong>This cell runs on the comparison corpus (the source text and every approved condensation summary), '
        'not the single-document source corpus used below &mdash; so here the Documents tool is genuinely useful: '
        'it lists every document side by side, letting you confirm which is which before running the comparison tools that follow.</strong></p>\n\n'
        '<p>Here is what the column headers mean in the Documents table:</p>\n\n'
        '<ul>\n'
        '\t<li><em>Title</em>: the document&#39;s title (or its filename if no better title was found)</li>\n'
        '\t<li><em>Words</em>: the number of individual words (tokens) found in the document (e.g. each occurrence of &quot;the&quot; is counted)</li>\n'
        '\t<li><em>Types</em>: the number of word forms found in the document (e.g. all occurrences of &quot;the&quot; are counted as one word form)</li>\n'
        '\t<li><em>Ratio</em>: the ratio of types to tokens (types/tokens), expressed as a percentage &ndash; higher numbers generally mean greater vocabulary diversity</li>\n'
        '\t<li><em>Words/Sentence</em>: an approximation of the average number of words per sentence (words tokens / sentences count); the way that sentences are calculated should be considered very approximate, especially because of complications with abbreviations and other uses of punctuation (parsing of sentences is performed by <a href="https://docs.oracle.com/javase/tutorial/i18n/text/about.html" target="_blank">Java&#39;s BreakIterator</a> class, and also depends on accurate language detection)</li>\n'
        '</ul>\n\n'
        '<p>&nbsp;</p>\n\n'
        '<p>(See <tt><strong><a href="https://voyant.inf.puc-rio.br/docs/index.html" target="_blank">online tutorials and documentation</a></strong></tt> for more information).</p>\n\n'
        '<table align="left" border="2" cellpadding="3" cellspacing="1" style="width: 50px;">\n'
        '\t<tbody>\n\t\t<tr>\n\t\t\t<td style="background: #8AC29C; width: 50px;">&nbsp;</td>\n\t\t</tr>\n\t</tbody>\n</table>\n\n'
        '<p>&nbsp;</p>'
    )


def build_cell16_content():
    """Cell 16 -- Documents tool code cell, rewired to myComparisonCorpus
    (6b.2). Confirmed verbatim against the real, live, saved notebook
    (cell id j33xw4rk) -- matches this skill's own 6b.2 spec exactly
    (`height: 250`); the older `cell15-injection.js` artifact on disk
    (no `height` key, commented `sort`/`dir` instead) is stale relative to
    what the researcher actually has live and is not used as the source
    here."""
    return (
        '// ── DOCUMENTS ─────────────────────────────────────────────────────────────────\n'
        '// Runs on myComparisonCorpus (source + every approved summary), not myCorpus\n'
        '// -- this cell is part of the "Source vs Summary" block.\n\n'
        'let config = {\n'
        '  lang:       "en",\n'
        '  categories: "none",\n'
        '  height:     250,\n'
        '};\n'
        'loadCorpus(myComparisonCorpus).tool("Documents", config);'
    )


def build_cell17_content():
    """Cell 17 -- Summary tool description, rewired to the comparison corpus
    (6b.2). Confirmed verbatim against the real, live, saved notebook
    (cell id jrs8uj1x) -- no document-count language present, so no
    count-agnostic rephrase is needed here, unlike Cell 15."""
    return (
        '<h1>SUMMARY</h1>\n\n'
        '<p>The <a href="https://voyant.inf.puc-rio.br/docs/tutorial-summary.html" target="_blank">SUMMARY</a> '
        'tool shows a quantitative profile of the linguistic&nbsp;<em>corpus</em>.<br />\n'
        'The output of the code cell below is fully effective. All interactive controls and optional parameter settings can be used.&nbsp;</p>\n\n'
        '<p>(See <tt><strong><a href="https://voyant.inf.puc-rio.br/docs/index.html" target="_blank">online tutorials and documentation</a></strong></tt> for more information).</p>\n\n'
        '<table align="left" border="2" cellpadding="3" cellspacing="1" style="width: 50px;">\n'
        '\t<tbody>\n\t\t<tr>\n\t\t\t<td style="background: #8AC29C; width: 50px;">&nbsp;</td>\n\t\t</tr>\n\t</tbody>\n</table>\n\n'
        '<p>&nbsp;</p>'
    )


def build_cell18_content():
    """Cell 18 -- Summary tool code cell, rewired to myComparisonCorpus
    (6b.2). Confirmed verbatim against the real, live, saved notebook
    (cell id oggheb4j) -- matches `cell17-injection.js` and this skill's own
    6b.2 spec exactly."""
    return (
        '// ── SUMMARY ───────────────────────────────────────────────────────────────────\n'
        '// Runs on myComparisonCorpus (source + every approved summary), not myCorpus\n'
        '// -- this cell is part of the "Source vs Summary" block.\n'
        '// stopList stays excListFull -- the merged stopword list filters common\n'
        '// words regardless of which corpus is loaded, so this value is unaffected\n'
        '// by the rewire.\n\n'
        'let config = {\n'
        '  lang:       "en",\n'
        '  categories: "none",  // Explicitly cancel Voyant\'s default category colouring\n'
        '  limit:      100,\n'
        '  stopList:   excListFull,\n'
        '};\n'
        'loadCorpus(myComparisonCorpus).tool("Summary", config);'
    )


def build_cell20_content():
    """Cell 20 -- empty paired code cell (6b.4). Fixed, corpus-independent.
    Confirmed verbatim against the real, live, saved notebook (cell id
    tv9gwc6z)."""
    return (
        '////////////////////////////////////////////////////////////////////////////////////////\n'
        '// This is an empty code cell, placed here for users to write and test their own code //\n'
        '////////////////////////////////////////////////////////////////////////////////////////'
    )


# ---------------------------------------------------------------------------
# Verification
# ---------------------------------------------------------------------------

def verify(content):
    checks = {}
    for tag in ['table', 'tbody', 'tr', 'td', 'p', 'h1', 'h3', 'blockquote', 'code', 'iframe', 'ul', 'li']:
        o = len(re.findall(r'<' + tag + r'(?:\s[^>]*)?>', content))
        c = len(re.findall(r'</' + tag + r'>', content))
        checks[tag] = (o, c, o == c)
    checks['palette_in_every_iframe'] = content.count('<iframe') == content.count('palette=Tableau20')
    checks['lang_in_every_iframe'] = content.count('<iframe') == content.count('lang=en')
    checks['five_h1_blocks'] = len(re.findall(r'<h1><strong>', content)) == 5
    return checks


if __name__ == '__main__':
    import json
    import os

    # Real the later pilot test corpus data -- the actual corpus this redesign
    # was developed and live-Voyant-verified against this same session,
    # loaded from disk, not re-typed from memory.
    base = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    with open(os.path.join(base, 'later-pilot-test-corpus-phase1-state.json'), encoding='utf-8') as f:
        p1 = json.load(f)
    with open(os.path.join(base, 'dell-acqua2026-CLEAN.txt'), encoding='utf-8') as f:
        source_text = f.read()

    tokens = ['C01AI', 'C02Jagged', 'C03Knowledge', 'C04Human', 'C05Experimental',
              'C06Performance', 'C07Participants', 'C08Assessment', 'C09Statistics', 'C10Communication']
    TABLEAU20 = ['#4E79A7', '#F28E2B', '#E15759', '#76B7B2', '#59A14F',
                 '#EDC948', '#B07AA1', '#FF9DA7', '#9C755F', '#BAB0AC']
    clusterDefs = [
        {'token': tok, 'name': c['name'], 'stems': c['stems'], 'color': color}
        for tok, c, color in zip(tokens, p1['clusterDefs'], TABLEAU20)
    ]

    print('=== Step 1: find real cross-cluster collocations ===')
    candidates = find_source_collocations(source_text, clusterDefs, proximity_n=5)
    flag_confounded(candidates)
    print(format_collocation_candidates(candidates, top_n=15))
    print()

    # Sanity checks against what this session actually confirmed live in Voyant:
    top = candidates[0]
    assert {top['term_a'], top['term_b']} == {'ai', 'task*'}, \
        f"expected the 'ai'-confounded pair to still rank #1 by raw hits, got {top}"
    assert top['confounded'], "'ai'-involving top candidate should be flagged confounded"
    frontier_task = next(c for c in candidates if {c['term_a'], c['term_b']} == {'frontier', 'task*'})
    assert frontier_task['hits'] > 0
    # NOTE: frontier/task* also gets flagged confounded here -- 'task*' itself
    # is high-frequency (167 occurrences), same threshold rule as 'ai'. This
    # is honest, not a bug: the mechanical filter can't distinguish "common
    # because thematically central" (task, in a paper about task assignment)
    # from "common because generically ubiquitous" (ai) -- that distinction
    # is exactly the judgment call left to the researcher, who reviewed the
    # real numbers and picked this pair anyway. The filter's job is to
    # surface the real frequency, not to make the final call.
    print(f"Confirmed: top candidate ({top['hits']} hits) is 'ai'-confounded. "
          f"frontier/task* ({frontier_task['hits']} hits) is ALSO flagged (task* itself is "
          f"high-frequency) -- the researcher reviewed both flags and chose it anyway, "
          f"exactly the human-judgment step this design keeps in front of her.")
    print()

    # Step 2: researcher's actual selection this session -- the two pairs
    # confirmed, live, to produce real, meaningful (non-confounded, or
    # confound-understood) results.
    generati_task = next(c for c in candidates if {c['term_a'], c['term_b']} == {'generati*', 'task*'})
    selected_pairs = [frontier_task, generati_task]

    print('=== Step 2: build the query from the selected pairs ===')
    words = _tokenize(source_text)
    query_str = build_collocation_comparison_query(selected_pairs, words, proximity_n=5)
    print(query_str)
    # Order (frequency-descending, from resolve_literal_forms' Counter.most_common)
    # isn't semantically load-bearing -- OR is commutative -- so check the set of
    # clauses, not a specific presentation order.
    expected_clauses = {
        '"frontier task"~5', '"frontier tasks"~5',
        '"generation task"~5', '"generation tasks"~5',
        '"generative task"~5', '"generative tasks"~5',
    }
    assert set(query_str.split('|')) == expected_clauses, \
        f"clause set mismatch:\n  got:      {sorted(query_str.split('|'))}\n  expected: {sorted(expected_clauses)}"
    assert ',' not in query_str, "must combine with pipe, never comma"
    print('Confirmed: same six clauses verified live in Voyant this session (44 real matches).')
    print()

    comparison_corpus_id = 'f7c858f039f01068bee4ec11028c4f4d'
    stoplist_id = 'keywords-9de67e9a60a1d9a9026c44ee40dc3c85'
    categories_id = 'eaf32c2afed4634737d1c0c9e9c84178'
    approved_rates = [25]
    voyant_host = 'https://voyant.inf.puc-rio.br'  # this test's own historical session's real host

    print('=== Step 3: build full Cell 19 content ===')
    content, elicitation = build_cell19_content(
        clusterDefs, comparison_corpus_id, stoplist_id, categories_id,
        approved_rates, selected_pairs, source_text, voyant_host)

    print('Elicitation resolution:', elicitation)
    print()
    checks = verify(content)
    all_ok = True
    for name, result in checks.items():
        if isinstance(result, tuple):
            o, c, ok = result
            print(f'{name:12s} open={o} close={c} {"OK" if ok else "MISMATCH"}')
            all_ok = all_ok and ok
        else:
            print(f'{name}: {result}')
            all_ok = all_ok and result
    print()
    print('ALL CHECKS PASS' if all_ok else 'FAILURES FOUND')
    print(f'Generated content length: {len(content)} chars')
    assert all_ok, 'structural verification failed'

    with open('_build_cell19_TESTOUTPUT.html', 'w', encoding='utf-8', newline='') as f:
        f.write(content)
    print('Written: _build_cell19_TESTOUTPUT.html')
