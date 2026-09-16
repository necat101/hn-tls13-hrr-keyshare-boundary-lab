# RESULTS — hn-tls13-hrr-keyshare-boundary-lab

Evaluator derives outcomes from synthetic inputs per **RFC 9846** (current TLS 1.3, obsoletes 8446) and **RFC 10024** group definitions. No live TLS.

| case | outcome | hrr_valid | reuse | detail |
|---|---|---|---|---|
| common-matching-share-no-hrr | no_hrr_needed | — | — | Common group x25519 has matching initial key_share → no HRR needed; preference ≠ mandatory retry. |
| common-group-no-share-hrr | hrr_required | — | — | Mutually supported group p256 but no compatible initial key_share → HRR required per RFC 9846. |
| no-common-abort | abort | — | — | No common supported_groups → handshake aborts (not HRR). Server cannot select a mutually supported group. |
| hrr-invalid-absent-group | invalid_hrr | False | — | HRR selects p384 absent from ClientHello supported_groups → invalid per RFC 9846 (must be mutually supported). |
| hrr-invalid-already-offered | invalid_hrr | False | — | HRR selects x25519 already present in ClientHello key_share → invalid per RFC 9846 (HRR must request a new group). |
| prefers-pq-accepts-classical | no_hrr_needed | — | — | Common group x25519 has matching initial key_share → no HRR needed; preference ≠ mandatory retry. |
| remembered-preference-fresh-share | no_hrr_needed | — | compliant_new_keyshare | Common group x25519mlkem768 has matching initial key_share → no HRR needed; preference ≠ mandatory retry. |
| reuse-keyshare-forbidden | no_hrr_needed | — | forbidden_by_rfc9846 | Common group x25519 has matching initial key_share → no HRR needed; preference ≠ mandatory retry. |
| rfc10024-standardized-not-mandatory | no_hrr_needed | — | — | Common group x25519 has matching initial key_share → no HRR needed; preference ≠ mandatory retry. RFC 10024 standardizes |

## Per-case detail
### common-matching-share-no-hrr — Common group with matching initial key_share — no HRR needed
- **outcome:** `no_hrr_needed`
- **detail:** Common group x25519 has matching initial key_share → no HRR needed; preference ≠ mandatory retry.
### common-group-no-share-hrr — Mutually supported selected group but no compatible initial key_share — HRR
- **outcome:** `hrr_required`
- **detail:** Mutually supported group p256 but no compatible initial key_share → HRR required per RFC 9846.
### no-common-abort — No common supported group — abort, not HRR
- **outcome:** `abort`
- **detail:** No common supported_groups → handshake aborts (not HRR).
### hrr-invalid-absent-group — HRR selecting a group absent from original supported_groups — invalid
- **outcome:** `invalid_hrr`; **hrr_valid:** `False` (selected_group_not_in_client_supported_groups)
### hrr-invalid-already-offered — HRR selecting a group already present in original key_share — invalid
- **outcome:** `invalid_hrr`; **hrr_valid:** `False` (selected_group_already_in_client_key_share)
### prefers-pq-accepts-classical — Server prefers PQ but accepts classical key_share
- **outcome:** `no_hrr_needed`
### remembered-preference-fresh-share — Remembered preference without reusing bytes
- **outcome:** `no_hrr_needed`; **key_share_reuse:** `compliant_new_keyshare`
### reuse-keyshare-forbidden — Reusing same KeyShare bytes
- **outcome:** `no_hrr_needed`; **key_share_reuse:** `forbidden_by_rfc9846` (RFC 9846 §1.2)
### rfc10024-standardized-not-mandatory — X25519MLKEM768 standardized but not mandatory first offer
- **outcome:** `no_hrr_needed`

---
**Current TLS base RFC:** RFC 9846 (obsoletes RFC 8446). **RFC 10024 status:** Standardized PQ/T hybrid groups (X25519MLKEM768 0x11EC Recommended Y). Does not mandate universal first-offer.

