#!/usr/bin/env python3
"""
session_log.py — append-only PEEL session log.

WHY THIS EXISTS
----------------
PEEL's entire design is about accountability — a researcher must be
able to return to and answer for the interpretive steps that produced
her results. That requirement does not stop at the artifacts; it
includes the conversational process that produced them. A log
reconstructed from memory at the end of a session is not a trustworthy
trace, and Claude has no memory across sessions by this researcher's
explicit choice — so the log is the ONLY durable record of what was
actually said and decided, and it has to be written turn by turn, not
reconstructed after the fact.

This script is not a substitute for the discipline of calling it every
turn. It only guarantees that *if* called every turn, the result is a
clean, append-only, timestamped, role-tagged record.

USAGE
-----
    python3 session_log.py init <session_name>
    python3 session_log.py append <session_name> --role user   --text "..."
    python3 session_log.py append <session_name> --role claude --text "..."
    python3 session_log.py append <session_name> --role user   --file turn.txt

Every call appends to:
    peel-logs/<session_name>/log.md

The file is created with a header on first use. It is NEVER truncated
or overwritten by this script — only appended to.

DELIVERY NOTE
-------------
This script can only write inside the current sandboxed working
directory. It cannot write to the researcher's own machine. At the end
of every session, the calling skill MUST present peel-logs/<session>/
log.md via present_files and remind the researcher to archive it
herself in her own iteratively-updated log folder.
"""
import sys
import datetime
import argparse
from pathlib import Path

LOG_ROOT = Path("peel-logs")


def log_path(session_name):
    d = LOG_ROOT / session_name
    d.mkdir(parents=True, exist_ok=True)
    return d / "log.md"


def init_session(session_name):
    p = log_path(session_name)
    if not p.exists():
        p.write_text(
            f"# PEEL session log — {session_name}\n\n"
            f"Started: {datetime.datetime.now().isoformat()}\n\n"
            f"---\n\n",
            encoding="utf-8",
        )
        print(f"Initialized: {p}")
    else:
        print(f"Log already exists, continuing to append: {p}")
    # Fixed 2026-08-06 (the original test paper cycle retrospective): this script writes
    # peel-logs/<session>/ relative to whatever directory is current when it
    # runs -- correct behavior, but silent about it. A real incident this
    # same cycle had Phase 1 run with a different cwd than Phase 2/Phase 3,
    # scattering one cycle's logs across two locations with nothing calling
    # it out at the time. Printing the resolved absolute path on every call
    # makes a cwd mismatch visible immediately, in the tool output itself,
    # instead of only discoverable later by manually searching the disk.
    print(f"Absolute path: {p.resolve()}")
    return p


def append_entry(session_name, role, text):
    p = log_path(session_name)
    if not p.exists():
        init_session(session_name)
    ts = datetime.datetime.now().isoformat(timespec="seconds")
    with open(p, "a", encoding="utf-8") as f:
        f.write(f"### [{ts}] {role}\n\n{text}\n\n---\n\n")
    print(f"Appended {role} turn to {p}")
    print(f"Absolute path: {p.resolve()}")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd", required=True)

    p_init = sub.add_parser("init")
    p_init.add_argument("session_name")

    p_app = sub.add_parser("append")
    p_app.add_argument("session_name")
    p_app.add_argument("--role", required=True, choices=["user", "claude"])
    p_app.add_argument("--text")
    p_app.add_argument("--file")

    args = ap.parse_args()

    if args.cmd == "init":
        init_session(args.session_name)
    elif args.cmd == "append":
        if args.file:
            text = Path(args.file).read_text(encoding="utf-8")
        elif args.text:
            text = args.text
        else:
            print("Provide --text or --file")
            sys.exit(2)
        append_entry(args.session_name, args.role, text)
