#!/usr/bin/env python3
"""Commit files to the shared repo through the GitHub API (no local git state).

Two agents work on the same repository from different machines. Pushing with `git push`
means each agent carries a local branch that can conflict with the other's. Creating the
commit through the API from the *current* remote head avoids that entirely: the parent is
always whatever is on the remote at the moment of the call.

Usage:
    python3 scripts/gh_commit.py -m "message" file1 file2 ...
    python3 scripts/gh_commit.py -m "message" --repo Liamlol1919/touch-steno -b main .
    python3 scripts/gh_commit.py --dry-run -m "message" file...

Requires `gh auth status` to be logged in.
"""
from __future__ import annotations

import argparse
import base64
import json
import subprocess
import sys
from pathlib import Path

DEFAULT_REPO = "Liamlol1919/touch-steno"
DEFAULT_BRANCH = "main"


def gh(*args, input_json=None):
    cmd = ["gh", *args]
    proc = subprocess.run(cmd, capture_output=True, text=True,
                          input=input_json if input_json is not None else None)
    if proc.returncode != 0:
        sys.stderr.write(proc.stderr)
        raise SystemExit(f"gh {' '.join(args[:2])} failed: {proc.stderr.strip()}")
    return proc.stdout


def collect(paths):
    """Expand directories into (repo_relative_path, bytes) pairs, honouring .gitignore."""
    import fnmatch
    root = Path.cwd()
    ignore = set()
    gi = root / ".gitignore"
    if gi.is_file():
        for line in gi.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            if line.endswith("/"):
                ignore.add(line[:-1] + "/**")
            else:
                ignore.add(line)
    out = []
    for p in paths:
        path = Path(p)
        files = sorted(path.rglob("*")) if path.is_dir() else [path]
        for f in files:
            if not f.is_file() or ".git/" in str(f):
                continue
            rel = str(f.relative_to(root)) if f.is_absolute() else str(f)
            if any(fnmatch.fnmatch(rel, pat) or rel.startswith(pat.rstrip("*"))
                   for pat in ignore if pat):
                continue
            out.append((rel, f.read_bytes()))
    return out


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("paths", nargs="+")
    ap.add_argument("-m", "--message", required=True)
    ap.add_argument("--repo", default=DEFAULT_REPO)
    ap.add_argument("--branch", default=DEFAULT_BRANCH)
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()

    files = collect(args.paths)
    if not files:
        print("nothing to commit")
        return 1
    head = json.loads(gh("api", f"repos/{args.repo}/commits/{args.branch}"))
    head_sha, base_tree = head["sha"], head["commit"]["tree"]["sha"]
    print(f"remote head: {head_sha[:10]}  files: {len(files)}")
    if args.dry_run:
        for rel, data in files:
            print(f"  {rel}  ({len(data)} B)")
        return 0

    entries = []
    for rel, data in files:
        blob = json.loads(gh("api", f"repos/{args.repo}/git/blobs", "-X", "POST",
                            "--input", "-",
                            input_json=json.dumps({
                                "content": base64.b64encode(data).decode(),
                                "encoding": "base64"})))
        entries.append({"path": rel, "mode": "100644", "type": "blob",
                        "sha": blob["sha"]})
    tree = json.loads(gh("api", f"repos/{args.repo}/git/trees", "-X", "POST",
                         "--input", "-",
                         input_json=json.dumps({"base_tree": base_tree,
                                                "tree": entries})))
    commit = json.loads(gh("api", f"repos/{args.repo}/git/commits", "-X", "POST",
                           "--input", "-",
                           input_json=json.dumps({
                               "message": args.message,
                               "tree": tree["sha"],
                               "parents": [head_sha]})))
    # The other agent can push between our head read and this ref update. A non-fast-forward
    # here means the commit was built on a stale parent, so we must NOT force it: re-read the
    # head and rebuild the whole commit on top of it. Losing that race twice is a signal to
    # stop, not to retry forever.
    for attempt in range(1, 4):
        proc = subprocess.run(
            ["gh", "api", f"repos/{args.repo}/git/refs/heads/{args.branch}",
             "-X", "PATCH", "--input", "-"],
            capture_output=True, text=True, input=json.dumps({"sha": commit["sha"]}))
        if proc.returncode == 0:
            print(f"committed {commit['sha'][:10]} -> {args.repo}@{args.branch}")
            print(args.message)
            return 0
        if "not a fast forward" not in proc.stderr:
            sys.stderr.write(proc.stderr)
            raise SystemExit("ref update failed")
        if attempt == 3:
            sys.stderr.write(proc.stderr)
            raise SystemExit(
                "lost the push race 3 times - the collaborator is committing faster than "
                "we can publish; stop and coordinate rather than retry")
        print(f"  push race lost (attempt {attempt}); rebuilding on the new remote head...")
        new = json.loads(gh("api", f"repos/{args.repo}/commits/{args.branch}"))
        head_sha, base_tree = new["sha"], new["commit"]["tree"]["sha"]
        entries = []
        for rel, data in files:
            blob = json.loads(gh("api", f"repos/{args.repo}/git/blobs", "-X", "POST",
                                 "--input", "-",
                                 input_json=json.dumps({
                                     "content": base64.b64encode(data).decode(),
                                     "encoding": "base64"})))
            entries.append({"path": rel, "mode": "100644", "type": "blob",
                            "sha": blob["sha"]})
        tree = json.loads(gh("api", f"repos/{args.repo}/git/trees", "-X", "POST",
                             "--input", "-",
                             input_json=json.dumps({"base_tree": base_tree,
                                                    "tree": entries})))
        commit = json.loads(gh("api", f"repos/{args.repo}/git/commits", "-X", "POST",
                               "--input", "-",
                               input_json=json.dumps({"message": args.message,
                                                      "tree": tree["sha"],
                                                      "parents": [head_sha]})))
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
