#!/usr/bin/env python3
"""Fail if anything identifying is in this fork's own files or its own commits, ever.

    python3 scripts/check_no_pii.py            # from the repository root, no dependencies

Exit 0 clean, 1 on a finding, 2 when it could not do its job (shallow clone, git missing).

This repository is public because HACS installs only from public repositories. It is also a
fork, so most of its history and files are other people's: upstream's and the two carried pull
requests'. Their commits are scanned for content and private markers but not for identity. What
this script guards is the fork owner's part:

- the fork's own files (OUR_FILES: the operative docs, the scripts, this workflow), in the tree
  and in every version of them in history, plus every commit message since the upstream base;
- the author and committer of every commit that is ours (reachable from HEAD, not from the
  upstream base and not from a carried head): only the allowlisted identities;
- generic rules: an email address outside the RFC 2606 example domains, a MAC address, a
  private IPv4 address, a tailnet host name, a PETLIBRO device serial, a long token-like string;
- private markers: one literal per line in ~/.config/pii/markers.txt (or $PII_MARKERS), matched
  case-insensitively over the same tree and history. The list is private on purpose: a public
  checker that spells the names it looks for is itself the leak. CI has no list and runs the
  generic rules only.

A finding in history CANNOT be fixed by a commit: it needs a rewrite and a force-push. Findings
are printed masked, because a public repository has public CI logs.
"""

from __future__ import annotations

import os
import re
import subprocess
import sys
from pathlib import Path

UPSTREAM_BASE = "a28fe35"  # the upstream dev commit main is built on; move it when rebasing
CARRIED_HEADS = ("54f22aeb", "da70957")  # upstream PR #274's head and the Vision Duo line (other people's commits)
OUR_FILES = ("CLAUDE.md", "CHANGELOG.md", "README.md", "scripts", ".github/workflows/pii.yml")
README_SENTINEL = "Everything below is upstream's README."  # only the banner above it is ours
SELF = "scripts/check_no_pii.py"  # excluded: it names the things it looks for
ALLOWED_IDENTITIES = {
    "71735642+billyfw@users.noreply.github.com",  # the fork owner's GitHub noreply address
    "noreply@github.com",  # GitHub's own web merges
    "noreply@anthropic.com",  # the coding assistant's Co-Authored-By line
}
EXAMPLE_DOMAIN = re.compile(r"@(?:[\w-]+\.)*example(?:\.(?:com|org|net))?$", re.I)  # RFC 2606
RULES = {
    "email": re.compile(r"[\w.+-]+@[\w-]+(?:\.[\w-]+)+"),
    "mac-address": re.compile(r"\b(?:[0-9A-Fa-f]{2}[:-]){5}[0-9A-Fa-f]{2}\b"),
    "private-ipv4": re.compile(r"\b(?:10\.\d{1,3}|192\.168|172\.(?:1[6-9]|2\d|3[01]))\.\d{1,3}\.\d{1,3}\b"),
    "tailnet-name": re.compile(r"\b[\w-]+\.ts\.net\b"),
    "device-serial": re.compile(r"\b(?:AF|WF|LB)\d{2}[0-9A-Z]{10,}\b"),
    "long-secret": re.compile(r"\b[A-Za-z0-9_\-]{48,}\b"),
}
MARKERS_FILE = Path(os.environ.get("PII_MARKERS", Path.home() / ".config/pii/markers.txt"))


def git(*args: str) -> str:
    return subprocess.run(["git", *args], check=True, capture_output=True, text=True).stdout


def mask(value: str) -> str:
    return value[:2] + "*" * max(len(value) - 2, 3)


def our_path(path: str) -> bool:
    if path == SELF:
        return False
    return any(path == f or path.startswith(f.rstrip("/") + "/") for f in OUR_FILES)


def scan_text(text: str, where: str, markers: list[str], findings: list[str]) -> None:
    if where.split(":")[0].endswith("README.md") and README_SENTINEL in text:
        text = text.split(README_SENTINEL)[0]
    for n, line in enumerate(text.splitlines(), 1):
        for rule, rx in RULES.items():
            for m in rx.finditer(line):
                v = m.group(0)
                if rule == "email" and (EXAMPLE_DOMAIN.search(v) or v in ALLOWED_IDENTITIES):
                    continue
                findings.append(f"{rule}: {where} line {n}: {mask(v)}")
        low = line.lower()
        for mk in markers:
            if mk in low:
                findings.append(f"marker: {where} line {n}: {mask(mk)}")


def main() -> int:
    try:
        git("rev-parse", "--verify", "--quiet", f"{UPSTREAM_BASE}^{{commit}}")
    except subprocess.CalledProcessError:
        print(f"cannot see the upstream base {UPSTREAM_BASE}: shallow clone? (fetch-depth: 0)")
        return 2
    markers = []
    if MARKERS_FILE.exists():
        markers = [ln.strip().lower() for ln in MARKERS_FILE.read_text().splitlines() if ln.strip() and not ln.startswith("#")]
    findings: list[str] = []

    # 1. the tree
    for path in git("ls-files").splitlines():
        if our_path(path):
            scan_text(Path(path).read_text(errors="replace"), path, markers, findings)

    # 2. history since the upstream base: messages, identities, our files' every version
    commits = git("rev-list", "HEAD", f"^{UPSTREAM_BASE}").split()
    ours = set(git("rev-list", "HEAD", f"^{UPSTREAM_BASE}", *[f"^{h}" for h in CARRIED_HEADS]).split())
    for sha in commits:
        short = sha[:7]
        subject, ae, ce, body = git("show", "-s", "--format=%s%n%ae%n%ce%n%b", sha).split("\n", 3)
        scan_text(subject + "\n" + body, f"commit {short} message", markers, findings)
        if sha in ours:
            for who, email in (("author", ae), ("committer", ce)):
                if email not in ALLOWED_IDENTITIES:
                    findings.append(f"identity: commit {short} {who}: {mask(email)}")
        for path in git("diff-tree", "--no-commit-id", "--name-only", "-r", "-m", sha).split():
            if our_path(path):
                try:
                    blob = git("show", f"{sha}:{path}")
                except subprocess.CalledProcessError:
                    continue  # deleted in this commit
                scan_text(blob, f"commit {short}:{path}", markers, findings)

    for f in sorted(set(findings)):
        print(f)
    label = f"{len(markers)} private markers" if markers else "no private marker list (generic rules only)"
    print(f"{'FAIL' if findings else 'clean'}: {len(set(findings))} finding(s); {len(commits)} commits since {UPSTREAM_BASE}, {len(ours)} ours; {label}")
    return 1 if findings else 0


if __name__ == "__main__":
    sys.exit(main())
