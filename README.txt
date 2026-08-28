PEEL3 — Tester Package
====================================================

Current skill versions: phase1 v1.31, phase2 v2.0, phase3 v2.57.
If you have an older copy of this package anywhere on your system,
replace it -- do not run two copies side by side.

This package contains everything needed to run PEEL3 yourself: the three
phase skill files, the Researcher Guides, supporting scripts, the Voyant
notebook template, and the standard stopword list.

Read the documentation online before you start:

  Why PEEL is built this way (Core Concepts)
  https://voyant.inf.puc-rio.br/spyral/pbai-serg@gh/PEEL3-Documentation-Concepts/

  How to run Phase 1
  https://voyant.inf.puc-rio.br/spyral/pbai-serg@gh/PEEL3-Documentation-Phase1/

  How to run Phase 2
  https://voyant.inf.puc-rio.br/spyral/pbai-serg@gh/PEEL3-Documentation-Phase2/

  How to run Phase 3
  https://voyant.inf.puc-rio.br/spyral/pbai-serg@gh/PEEL3-Documentation-Phase3/

  Example / worked notebook
  https://voyant.inf.puc-rio.br/spyral/pbai-serg@gh/PEEL3-NotebookDemo/

  Tips and known issues
  https://voyant.inf.puc-rio.br/spyral/pbai-serg@gh/PEEL3-Documentation-Tips/

The pages above are the same content as PEEL3-Researcher-Guides.zip below,
just easier to read and navigate. The Core Concepts page explains the
reasoning behind PEEL's design; the three phase pages are the actual
step-by-step instructions.

Note: the online Phase 2 page has not yet been updated to describe v2.0's
behavior -- until it is, treat it as describing the prior pipeline. The
Researcher Guides zip in this package already reflects v2.0.

What's in this package:

  PEEL3-Skills/                 The three phase skill files Claude reads
                                 to run PEEL3 (peel3-phase1/2/3), as plain
                                 files in this folder -- not a nested zip.
                                 Phase 2 is `peel3-phase2-v2.0.md` -- use
                                 this one. `peel2-phase2-v3.25-SUPERSEDED.md`
                                 and `peel3-phase2-v1.9-SUPERSEDED.md` are
                                 earlier lineages kept only for reference;
                                 do not run either directly.
  PEEL3-Researcher-Guides.zip   Plain-text versions of the three phase
                                 guides linked above
  PEEL3-Scripts/                Supporting scripts (_build_cell19.py,
                                 session_log.py), as plain files in this
                                 folder -- not a nested zip
  PEEL3templateSN.html          Blank master Spyral notebook template
  PEEL-DataCollection.html      Data Collection notebook, for the Voyant
                                 round-trips Phase 1 and Phase 3 need
  stop.en.smart.txt             Standard English stopword list
  session-logs/README.txt       Explains the convention for archiving
                                 your own session logs once you start
                                 running PEEL3 -- an empty folder ready
                                 for your own logs
