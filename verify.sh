#!/bin/sh
set -eu
ROOT="$(cd "$(dirname "$0")" && pwd)"
echo "=== hn-tls13-hrr-keyshare-boundary-lab verify ==="
echo "Current TLS base: RFC 9846 (obsoletes RFC 8446)"
echo ""
echo "[1] evaluator"
python3 "$ROOT/evaluator.py"
echo ""
echo "[2] tests (independent oracle)"
python3 -m unittest tests.test_boundary -v
echo ""
echo "[3] RESULTS.md snapshot"
cat "$ROOT/RESULTS.md"
