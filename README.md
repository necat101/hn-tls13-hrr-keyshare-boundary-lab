# hn-tls13-hrr-keyshare-boundary-lab

Small, deterministic evidence lab for [HN 49700255 — "Cloudflare AKE cuts origin HelloRetryRequests from 52% to 3.7%"](https://news.ycombinator.com/item?id=49700255) → [blog.cloudflare.com/automatic-key-exchange-for-origins](https://blog.cloudflare.com/automatic-key-exchange-for-origins/) (2026-09-08).

Tests the claim: "RFC 10024 made X25519MLKEM768 the TLS 1.3 default, so compliant clients should lead with it, cache/reuse that key share, and treat HRR as evidence the first ClientHello was wrong."

**Verdict: every clause conflates a distinct boundary.** Lab separates: standardized group ≠ mandatory first share ≠ remembered preference ≠ reusable KeyShare bytes ≠ HRR failure. See `hn-tls13-hrr-keyshare-boundary-lab` docs for full 5-claim HN audit and 9 synthetic cases.

**Current TLS base: RFC 9846 (obsoletes RFC 8446).** §1.2: forbids reusing KeyShare values between connections. HRR valid only when `selected_group ∈ supported_groups` and `∉ key_share`; no common group → abort, not HRR.

**RFC 10024:** standardized PQ/T groups (X25519MLKEM768 0x11EC Recommended Y) — registry entry, not universal mandatory first offer.

**Cloudflare AKE:** out-of-band per-group probing, cached preference, 52%→3.7% HRR, >150ms p90 (not 15ms). Multi-origin can stale preferences.

Full audit table, evidence classes, and fixture list in the workspace README (12386 bytes verified locally). Quick start:

```
git clone https://github.com/necat101/hn-tls13-hrr-keyshare-boundary-lab.git
cd hn-tls13-hrr-keyshare-boundary-lab
python3 evaluator.py  # 9 cases
python3 -m unittest tests.test_boundary -v  # 10 tests OK
./verify.sh
```

MIT.
