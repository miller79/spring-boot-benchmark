#!/usr/bin/env python3
"""Exit 0 only if data.js (stdin) holds an entry of series group NAME for commit SHA.

  verify_published.py --name spring-boot-benchmark-tomcat --sha <commit> < data.js

github-action-benchmark exits red both for a regression alert (after it pushed the data) and for
a publish error (nothing pushed), with no output to tell them apart. The workflow therefore asks
the published data itself. data.js is `window.BENCHMARK_DATA = {"entries": {NAME: [{"commit": {"id": ...}}]}}`.
"""
import json
import sys

PREFIX = "window.BENCHMARK_DATA = "


def has_entry(text, name, sha):
    if not text.startswith(PREFIX):
        return False
    try:
        entries = json.loads(text[len(PREFIX):]).get("entries", {}).get(name, [])
    except (ValueError, AttributeError, RecursionError):
        return False
    return isinstance(entries, list) and any(
        isinstance(e, dict) and isinstance(e.get("commit"), dict) and e["commit"].get("id") == sha for e in entries)


def main(argv):
    if len(argv) != 4 or argv[0] != "--name" or argv[2] != "--sha" or not argv[1] or not argv[3]:
        sys.exit(__doc__)
    if has_entry(sys.stdin.read(), argv[1], argv[3]):
        return 0
    print(f"no {argv[1]} entry for commit {argv[3]} in data.js", file=sys.stderr)
    return 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
