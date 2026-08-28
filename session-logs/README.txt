This folder is where you keep your own durable session-log archive --
distinct from peel-logs/, which is where session_log.py writes the
live, working copy of a log during a session (that script can only
write inside the current working directory; it does not archive
anything on its own).

Convention: at the end of a session, the finished log at
peel-logs/<session-name>/log.md is copied here, renamed to

    <session-name>-log.md

e.g. peel-logs/YourCorpus-phase1-2026-08-06/log.md becomes
session-logs/YourCorpus-phase1-2026-08-06-log.md

<session-name> itself already follows the PEEL protocol's own naming
pattern: [corpus-or-topic]-[phase]-[YYYY-MM-DD], so this folder's
filenames sort chronologically and by track without needing a separate
index. If a second session runs against the same corpus/phase/date, use
the protocol's own letter-suffix convention (...-2026-08-06b-log.md,
etc.) rather than overwriting the first.

The peel-logs/ copy is not deleted or treated as disposable once
archived here -- both copies are the same content; this folder is just
the one meant to persist and be searched across sessions.
