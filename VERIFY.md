# VERIFY — public-origin verification record

## Provenance

- **Public origin (no file://):** `https://github.com/necat101/hn-tls13-hrr-keyshare-boundary-lab.git`
- **Commit C (reproducible-evidence target):** `ed8fa87f00ab94f4b385a6eed21f81b850e8a123` — `evidence: normalize results.json to evaluator output (C final)` (completes normalization of `RESULTS.md` + `results.json` to exact `python3 evaluator.py` output; generator fix `ensure_ascii=False`)
- **Prior verification targets:** A `33d66440dfceb4aa6efa42dc30dea17e6a0d08fe`, B `f0e0a50f74073618682d7e81c0bb83d7424d279e` (recorded A's fresh-clone execution; implementation logic traces to `168dc89811b4cb888a4686b8f0c77a16a21b3263` unchanged through C)
- **Implementation revision under test:** `168dc89811b4cb888a4686b8f0c77a16a21b3263` (evaluator / fixtures / tests logic unchanged through C; C only normalizes tracked generated evidence and fixes `ensure_ascii` for byte stability)
- **Verification method:** fresh, unauthenticated `git clone https://github.com/necat101/hn-tls13-hrr-keyshare-boundary-lab.git` followed by local execution on the clone's HEAD at C.

## Fresh-clone match (commit C)

```text
# executed from outside the workspace, https only, no file://
rm -rf /tmp/fresh-c-final
git clone https://github.com/necat101/hn-tls13-hrr-keyshare-boundary-lab.git /tmp/fresh-c-final
cd /tmp/fresh-c-final
git remote -v
git rev-parse HEAD
python3 --version
```

Actual output:

```text
origin	https://github.com/necat101/hn-tls13-hrr-keyshare-boundary-lab.git (fetch)
origin	https://github.com/necat101/hn-tls13-hrr-keyshare-boundary-lab.git (push)
ed8fa87f00ab94f4b385a6eed21f81b850e8a123
Python 3.12.3
```

- **Fresh-clone HEAD:** `ed8fa87f00ab94f4b385a6eed21f81b850e8a123`
- **HEAD equality (fresh clone == commit C):** true
- **File transport check:** no `file://` in `git remote -v`

## Execution (on the fresh clone at commit C)

### Evaluator (idempotence required)

```text
$ git status --porcelain   # before
(empty)
$ python3 evaluator.py
Evaluated 9 cases → /tmp/fresh-c-final/results.json + /tmp/fresh-c-final/RESULTS.md
$ git diff --exit-code -- RESULTS.md results.json; echo DIFF_CODE:$?
DIFF_CODE:0
$ git status --porcelain   # after
(empty)
```

- **Evaluator totals (from generated `results.json` / `RESULTS.md`):**
  - 9 cases: `no_hrr_needed` 5, `hrr_required` 1, `abort` 1, `invalid_hrr` 2
  - `forbidden_by_rfc9846` 1 (`reuse-keyshare-forbidden`), `compliant_new_keyshare` 1 (`remembered-preference-fresh-share`)
- **Reproducibility condition:** rerunning the deterministic evaluator leaves the tracked generated evidence unchanged — **met** (`git diff` exit 0 on `RESULTS.md` + `results.json`).

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

- **Unit tests:** 10 tests OK

### verify.sh

```text
$ bash verify.sh
=== hn-tls13-hrr-keyshare-boundary-lab verify ===
Current TLS base: RFC 9846 (obsoletes RFC 8446)
[1] evaluator
Evaluated 9 cases → /tmp/fresh-c-final/results.json + /tmp/fresh-c-final/RESULTS.md
[2] tests (independent oracle)
... 10 tests OK ...
[3] RESULTS.md snapshot
# RESULTS — hn-tls13-hrr-keyshare-boundary-lab
...
VERIFY_CODE:0
```

- **verify.sh:** exit 0

### Final working-tree state (after all executions on commit C)

```text
$ git diff --exit-code -- RESULTS.md results.json; echo DIFF_CODE:$?
DIFF_CODE:0
$ git status --porcelain
(empty — clean)
```

## Scope statement

- **Commit C was fresh-clone matched, executed, and regenerated its tracked evidence without diff; commit D records that evidence.** Commit D is a closure-record update to `VERIFY.md` only; it does not modify evaluator logic, fixtures, or generated results, and does not claim to have verified itself.
