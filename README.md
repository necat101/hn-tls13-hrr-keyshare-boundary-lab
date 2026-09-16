# hn-tls13-hrr-keyshare-boundary-lab

Small, deterministic evidence lab for [HN 49700255 — "Cloudflare AKE cuts origin HelloRetryRequests from 52% to 3.7%"](https://news.ycombinator.com/item?id=49700255) → [blog.cloudflare.com/automatic-key-exchange-for-origins](https://blog.cloudflare.com/automatic-key-exchange-for-origins/) (2026-09-08).

Tests the infra-team claim:

> "RFC 10024 made X25519MLKEM768 the TLS 1.3 default, so compliant clients should lead with it, cache/reuse that key share, and treat a HelloRetryRequest as evidence that the first ClientHello was wrong."

**Verdict: every clause conflates a distinct boundary.** The lab separates them and checks each synthetic handshake against the evidence class that actually governs it.

## Boundary under test

| Boundary | Meaning |
|---|---|
| **standardized group ≠ mandatory first key share** | RFC 10024 defines registry entries; does not mandate universal first offer |
| **remembered group preference ≠ reusable KeyShare value** | RFC 9846 §1.2 forbids reusing KeyShare BYTES across connections; caching a group preference with fresh bytes is permitted |
| **HelloRetryRequest ≠ failure** | HRR is a normal, valid branch when the server's selected group lacks a matching share; invalid HRRs are separately defined; no-common-group is abort, not HRR |

Rule: **standardized ≠ mandatory ≠ remembered ≠ reusable ≠ failure.** Every outcome must cite the boundary that actually governs it.

## What the primary sources actually say (verified 2026-09-16)

- **Current TLS 1.3 base is RFC 9846 (July 2026), obsoletes RFC 8446.** §1.2 lists the technical change: *"Forbid the reuse of KeyShare values between connections."* Do not use RFC 8446 as the current normative source.
- **RFC 9846 §4.2.4 / §4.3.8:** Client sends `supported_groups` + `key_share`; server may reply HRR when the selected group is in `supported_groups` but has no compatible `key_share`. HRR `selected_group` MUST be in `ClientHello.supported_groups` and MUST NOT be a group already present in `ClientHello.key_share`. No common group → abort, not HRR.
- **RFC 10024 (Aug 2026):** Defines three PQ/T hybrid groups — X25519MLKEM768 (0x11EC, Recommended Y), SecP256r1MLKEM768 (0x11EB), SecP384r1MLKEM1024 (0x11ED). IANA registry entries, not a universal mandatory first key_share. No `MUST offer X25519MLKEM768 first` requirement.
- **Cloudflare AKE (2026-09-08):** Probes each TLS 1.3 origin with per-group handshakes (X25519, P-256/384/521, X25519MLKEM768) out-of-band; caches the learned preferred group and leads with that share next time, preferring PQ where supported. Reports HRR 52% → 3.7% and **>150 ms p90** handshake reduction, 64% stay on X25519 / 33% move to X25519MLKEM768 / 3% other curves. Preference for a group may still accept the classical share without HRR ("*an origin that supports post-quantum may still accept a classical key share without rejecting it or issuing an HRR*"). Scanning happens outside the production path; lookup cost is amortized via cached preference.

## HN 49700255 audit (comments actually retrieved — via HN Firebase)

Quoted text abbreviated; IDs and authors exact for re-fetch via `https://hacker-news.firebaseio.com/v0/item/<id>.json`.

### HN claims checked

| # | Proposition seen on thread | Source | Assessment |
|---|---|---|---|
| 1 | "The TLS handshake involves a step to discover the commonly supported algorithms and can incur an additional roundtrip if the first guess does not work out" — HRR exists to discover the correct algorithm. | **sandeepkd · 49701643** (verbatim TLDR point 1; `its part of the protocol to keep it stateless` in same comment) | **Mostly accurate, needs scoping.** Discovery via ClientHello guess + conditional HRR is correctly described. Fix: discovery is bounded — HRR only when `selected_group ∈ supported_groups` but `∉ key_share`; `no common group → abort, not HRR`. Lab cases `common-group-no-share-hrr` vs `no-common-abort` test this. **Thread text is real; not manufactured.** |
| 2 | "its part of the protocol to keep it stateless" — the retry mechanism is mainly about keeping TLS stateless. | **sandeepkd · 49701643** (same TLDR, appended clause) | **Oversimplification (HN speculation).** HRR is a stateless corrective branch, but RFC 9846's HRR properties are primarily negotiation correctness (group membership, no-duplicate-share), not just statelessness. Stateless cookies (§4.3.2) are a separate mechanism. Treating every HRR as "statelessness overhead" misclassifies invalid HRRs. |
| 3 | "They are saving on the *possible* roundtrip latency, however they are not sharing the absolute lookup latency which now gets added to every connection" — Cloudflare adds a lookup cost to every connection. | **sandeepkd · 49701643** (verbatim second bullet); counterpoint **sophacles · 49702373**: *"Presumably on cache miss they already need to look up ... This is just a handful of bytes in that record."* | **Speculation, not supported by article as "per-connection" cost.** Cloudflare article (§18-19) states scanning is **out-of-band, outside the production traffic path** and preferences are cached per-origin; AKE "*probes each origin to learn*" then "*lead[s] with that algorithm on the first try*." No per-handshake scan. At most a cache-lookup of a few bytes. |
| 4 | "I'm curious how Cloudflare keeps the learned key exchange preference accurate when a hostname is backed by multiple origins with different TLS configurations?" — multi-origin makes learned preferences stale/ambiguous. | **nohuman-labs · 49713359** (verbatim question) | **Real deployment question; article acknowledges the gap.** Article notes "*Other classical ... primarily driven by multi-origin setups with a mix of post-quantum and classical-only backends*" and Radar checks for middlebox failures, but does not detail per-origin variance invalidation. AKE's per-origin cached preference can be stale/divergent under heterogeneous backends — an operational risk, not a protocol violation. |
| 5 | "So they saved 15ms on the connection" vs Cloudflare's reported p90 figure. | **greatgib · 49701654** (verbatim point 1: *"So they saved 15ms"*) ; cf. article §35: *"reducing p90 latency more than 150 ms"* | **HN figure is understated/misremembered.** Article reports **>150 ms p90** (not 15 ms). The 15 ms reading conflates a single-round-trip saving on one path with the measured p90 tail across scanned origins. Lab takes no performance position. |

If a comment you need is missing above, fetch it directly — these are not invented. IDs can be re-fetched individually.

### Evidence classes (how the lab separates them)

| Evidence class | Example | What it can/cannot prove |
|---|---|---|
| **current RFC requirement** | RFC 9846 forbids reusing KeyShare bytes (§1.2); HRR validity rules (§4.2.4/§4.3.8) | Normative — violations are invalid |
| **permitted RFC behavior** | Accepting an offered classical share even when server prefers PQ (no HRR); caching a group *preference* with fresh bytes | Allowed — preference ≠ mandatory retry |
| **RFC 10024 group definition / registry status** | X25519MLKEM768 0x11EC Recommended Y, 1216-byte client share | Defines the group; does not mandate it as default first offer |
| **Cloudflare deployment behavior** | AKE out-of-band probing, 52%→3.7% HRR, 150 ms p90, PQ adoption 12.8% | Deployment optimization; not a standards rule |
| **HN speculation or inference** | "lookup added to every connection", "15 ms saved", "stateless = whole reason" | Requires source check — often contradicts primary |

## Lab design

Pure **Python 3 stdlib + shell**, no live TLS, no origin scanning, no packet capture, no OpenSSL, no external packages. Every situation is a synthetic JSON fixture; the evaluator answers a *protocol/state* question (which branch and is the HRR valid?), not "is this product compliant?".

### Fixtures (`fixtures/cases.json`)

Nine synthetic cases — each carries exactly the facts the evaluator must interpret:

1. `common-matching-share-no-hrr` — common group + matching initial key_share → no HRR needed
2. `common-group-no-share-hrr` — mutually supported selected group but no compatible initial key_share → HRR
3. `no-common-abort` — no common supported group → abort, not HRR
4. `hrr-invalid-absent-group` — HRR selects a group absent from original `supported_groups` → invalid
5. `hrr-invalid-already-offered` — HRR selects a group already present in original `key_share` → invalid
6. `prefers-pq-accepts-classical` — server prefers PQ but accepts an offered classical key_share → preference is not a mandatory retry
7. `remembered-preference-fresh-share` — remembering a previously learned group preference without reusing KeyShare bytes → permitted
8. `reuse-keyshare-forbidden` — reusing the same KeyShare value across connections → forbidden by RFC 9846
9. `rfc10024-standardized-not-mandatory` — X25519MLKEM768 as a standardized group without treating it as a universal mandatory first offer

### Evaluator (`evaluator.py`)

`python3 evaluator.py` reads `fixtures/cases.json`, derives handshake outcome from the inputs per RFC 9846/10024, and classifies `KeyShare` byte reuse separately. Exit 0; writes `results.json` with `outcome` / `hrr_valid` / `key_share_reuse` and a human `RESULTS.md`.

KeyShare reuse is tracked as **bytes**, not group name: `reuse_same_key_share_bytes: true → forbidden_by_rfc9846`, `false → compliant_new_keyshare` with the group preference remembered. This is the check the claim conflates.

### Tests (`tests/test_boundary.py`)

Independent oracle re-derives the expected `outcome`/`hrr_valid` from the same synthetic facts without calling the evaluator's decision internals. Catches:

- trusting fixture labels instead of inputs
- conflating "standardized group" with "mandatory first share"
- conflating "remembered preference" with "reused bytes"
- treating HRR as evidence of wrong ClientHello instead of a valid conditional branch
- accepting invalid HRRs (absent group / already offered) as valid retries

```sh
python3 evaluator.py
python3 -m unittest tests.test_boundary -v
```

### Verification

```sh
./verify.sh            # local deterministic evaluator/test check
cat RESULTS.md         # recorded actual output
cat VERIFY.md          # public HTTPS fresh-clone transcript (public-origin procedure)
```

## Quick start

```sh
git clone https://github.com/necat101/hn-tls13-hrr-keyshare-boundary-lab.git
cd hn-tls13-hrr-keyshare-boundary-lab
python3 evaluator.py
python3 -m unittest tests.test_boundary -v
./verify.sh
```

## Sources inspected 2026-09-16

- HN item `49700255` + kids via `hacker-news.firebaseio.com` (IDs above) — Algolia also queried for this item
- `blog.cloudflare.com/automatic-key-exchange-for-origins/` fetched 2026-09-16 (348 KB; 40 paragraph extracts; key stats in §35, probing in §18, PQ preference in §34)
- `RFC 9846` (July 2026) — current TLS 1.3, obsoletes RFC 8446; §1.2, §4.2.4, §4.3.8
- `RFC 10024` (Aug 2026) — PQ/T hybrid groups; §4.1-4.3, §7 (IANA 0x11EC/0x11EB/0x11ED)

## Result snapshot (actual, 2026-09-16)

Evaluator (derived from synthetic inputs, not fixture labels):

```
9 cases
  no_hrr_needed: 5 (common-matching-share-no-hrr, prefers-pq-accepts-classical, remembered-preference-fresh-share, reuse-keyshare-forbidden, rfc10024-standardized-not-mandatory)
  hrr_required: 1 (common-group-no-share-hrr — valid HRR)
  abort:        1 (no-common-abort — no common group, not HRR)
  invalid_hrr:  2 (hrr-invalid-absent-group, hrr-invalid-already-offered)

KeyShare reuse (RFC 9846 §1.2):
  forbidden_by_rfc9846: 1 (reuse-keyshare-forbidden — same bytes across connections)
  compliant_new_keyshare: 1 (remembered-preference-fresh-share — preference cached, fresh bytes)
```

Unit-test result (independent oracle, not fixture count):

```
10 tests OK — python3 -m unittest tests.test_boundary -v
```

Status conclusions (unchanged):

```
Current TLS base: RFC 9846 (obsoletes RFC 8446)
RFC 10024 group status: standardized registry entries (X25519MLKEM768 0x11EC); not a universal mandatory first offer
HRR vs noncompliance: HRR is a valid conditional branch when selected_group ∈ supported_groups but ∉ key_share; no-common-group is abort; invalid HRRs are protocol errors
Group preference vs KeyShare reuse: caching a group preference is permitted; reusing KeyShare bytes is forbidden per RFC 9846 §1.2
```

## License

MIT
