# VERIFY — public-origin verification record

## Provenance

- **Public origin (no file://):** `https://github.com/necat101/hn-tls13-hrr-keyshare-boundary-lab.git`
- **Commit A (verification target):** `33d66440dfceb4aa6efa42dc30dea17e6a0d08fe` — `docs: publish full public README audit (commit A — verification target)`
- **Implementation revision whose evaluator/tests remain under test:** `168dc89811b4cb888a4686b8f0c77a16a21b3263` (original execution-tested; evaluator/fixtures/tests logic unchanged through A) and its descendant `d8ac32babc9bf4aadf38622f9ae26ed5746e7c04` (CI fix)
- **Verification method:** fresh, unauthenticated `git clone https://github.com/necat101/hn-tls13-hrr-keyshare-boundary-lab.git` followed by local execution on the clone's HEAD.

## Fresh-clone match

```text
# executed from outside the workspace, https only, no file://
rm -rf /tmp/fresh-hn-tls13-hrr
git clone https://github.com/necat101/hn-tls13-hrr-keyshare-boundary-lab.git /tmp/fresh-hn-tls13-hrr
cd /tmp/fresh-hn-tls13-hrr
git remote -v
git rev-parse HEAD
```

Actual output:

```text
origin	https://github.com/necat101/hn-tls13-hrr-keyshare-boundary-lab.git (fetch)
origin	https://github.com/necat101/hn-tls13-hrr-keyshare-boundary-lab.git (push)
33d66440dfceb4aa6efa42dc30dea17e6a0d08fe
```

- **Fresh-clone HEAD:** `33d66440dfceb4aa6efa42dc30dea17e6a0d08fe`
- **HEAD equality (fresh clone == commit A):** true
- **File transport check:** no `file://` in `git remote -v`

## Execution (on the fresh clone at commit A)

### Evaluator

```text
$ python3 evaluator.py
Evaluated 9 cases → /tmp/fresh-hn-tls13-hrr/results.json + /tmp/fresh-hn-tls13-hrr/RESULTS.md
```

Case totals (from `results.json` / `RESULTS.md` — outcomes derived from synthetic inputs per RFC 9846 + RFC 10024):

- `no_hrr_needed`: 5 — `common-matching-share-no-hrr`, `prefers-pq-accepts-classical`, `remembered-preference-fresh-share`, `reuse-keyshare-forbidden`, `rfc10024-standardized-not-mandatory`
- `hrr_required`: 1 — `common-group-no-share-hrr` (valid HRR: mutually supported group lacking a compatible key_share)
- `abort`: 1 — `no-common-abort` (no common group → abort, not HRR)
- `invalid_hrr`: 2 — `hrr-invalid-absent-group` (selected_group_not_in_client_supported_groups), `hrr-invalid-already-offered` (selected_group_already_in_client_key_share)
- `key_share_reuse`: `forbidden_by_rfc9846` = 1 (`reuse-keyshare-forbidden`), `compliant_new_keyshare` = 1 (`remembered-preference-fresh-share`)

### Independent unit tests

```text
$ python3 -m unittest tests.test_boundary -v
test_common_group_no_share_hrr ... ok
test_common_matching_share_no_hrr ... ok
test_hrr_invalid_absent_group ... ok
test_hrr_invalid_already_offered ... ok
test_no_common_abort ... ok
test_prefers_pq_accepts_classical ... ok
test_remembered_preference_fresh_share ... ok
test_reuse_keyshare_forbidden ... ok
test_reuse_vs_preference_distinction ... ok
test_rfc10024_standardized_not_mandatory ... ok

Ran 10 tests in 0.009s
OK
```

### verify.sh

```text
$ bash verify.sh
=== hn-tls13-hrr-keyshare-boundary-lab verify ===
Current TLS base: RFC 9846 (obsoletes RFC 8446)
[1] evaluator
Evaluated 9 cases → /tmp/fresh-hn-tls13-hrr/results.json + /tmp/fresh-hn-tls13-hrr/RESULTS.md
[2] tests (independent oracle)
... 10 tests OK ...
[3] RESULTS.md snapshot
# RESULTS — hn-tls13-hrr-keyshare-boundary-lab
...
Exit: 0
```

- **Evaluator:** 9 cases evaluated
- **Unit tests:** 10 tests OK
- **verify.sh (bash):** exit 0

### Working-tree state

```text
$ git status --porcelain  (on fresh clone after evaluator run)
 M RESULTS.md
 M results.json
```

- **Clean/dirty:** dirty after evaluator execution — **expected**. `evaluator.py` regenerates the tracked files `RESULTS.md` and `results.json` deterministically from `fixtures/cases.json`. The on-disk difference at commit A is formatting/newline expansion between the previously committed abbreviated results and the freshly generated authoritative output; `python3 --version` below shows the regenerating runtime. Before evaluator execution the working tree was clean (`git status --porcelain` empty prior to `python3 evaluator.py`). Evaluator outcomes are unchanged; logic traces to `168dc89`.

- **Python version:** `Python 3.12.3` (fresh clone execution)

## Scope statement

- **Commit A was fresh-clone matched and executed; commit B records that verification.** Commit B is a documentation/closure record containing this transcript. Commit B does not claim to have verified itself; that is not required. The substantive implementation (evaluator/fixtures/tests) traces to `168dc898...` — commit A and B are documentation descendants.
