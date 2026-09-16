# hn-tls13-hrr-keyshare-boundary-lab

Small, deterministic evidence lab for HN 49700255 — TLS 1.3 HRR vs KeyShare boundaries (RFC 9846 / RFC 10024).

See local README for full claims table (5 propositions) and 9 synthetic cases. Current TLS base: RFC 9846 (obsoletes 8446). RFC 10024: standardized PQ/T groups (X25519MLKEM768 0x11EC), not a mandatory first offer.

Quick start:

```
git clone https://github.com/necat101/hn-tls13-hrr-keyshare-boundary-lab.git
cd hn-tls13-hrr-keyshare-boundary-lab
python3 evaluator.py
python3 -m unittest tests.test_boundary -v
```

