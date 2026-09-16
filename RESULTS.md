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
| remembered-preference-fresh-share | no_hrr_needed | — | compliant_new_keyshare | Common group x25519mlkem768 has matching initial key_share → no HRR needed; preference ≠ mandatory retry. Caching/remembering a group prefer |
| reuse-keyshare-forbidden | no_hrr_needed | — | forbidden_by_rfc9846 | Common group x25519 has matching initial key_share → no HRR needed; preference ≠ mandatory retry. Reusing same KeyShare bytes across connect |
| rfc10024-standardized-not-mandatory | no_hrr_needed | — | — | Common group x25519 has matching initial key_share → no HRR needed; preference ≠ mandatory retry. RFC 10024 standardizes X25519MLKEM768 (Rec |

## Per-case detail
### common-matching-share-no-hrr — Common group with matching initial key_share — no HRR needed
- **outcome:** `no_hrr_needed`
- **detail:** Common group x25519 has matching initial key_share → no HRR needed; preference ≠ mandatory retry.

### common-group-no-share-hrr — Mutually supported selected group but no compatible initial key_share — HRR
- **outcome:** `hrr_required`
- **detail:** Mutually supported group p256 but no compatible initial key_share → HRR required per RFC 9846.

### no-common-abort — No common supported group — abort, not HRR
- **outcome:** `abort`
- **detail:** No common supported_groups → handshake aborts (not HRR). Server cannot select a mutually supported group.

### hrr-invalid-absent-group — HRR selecting a group absent from original supported_groups — invalid
- **outcome:** `invalid_hrr`
- **hrr_valid:** `False` (selected_group_not_in_client_supported_groups)
- **detail:** HRR selects p384 absent from ClientHello supported_groups → invalid per RFC 9846 (must be mutually supported).

### hrr-invalid-already-offered — HRR selecting a group already present in original key_share — invalid
- **outcome:** `invalid_hrr`
- **hrr_valid:** `False` (selected_group_already_in_client_key_share)
- **detail:** HRR selects x25519 already present in ClientHello key_share → invalid per RFC 9846 (HRR must request a new group).

### prefers-pq-accepts-classical — Server prefers PQ but accepts an offered classical key_share — preference is not a mandatory retry
- **outcome:** `no_hrr_needed`
- **registry:** RFC 10024 defines PQ/T hybrid groups (X25519MLKEM768 etc.) as standardized registry entries; deployment/negotiation policy is separate.
- **detail:** Common group x25519 has matching initial key_share → no HRR needed; preference ≠ mandatory retry.

### remembered-preference-fresh-share — Remembering a previously learned group preference without reusing KeyShare bytes
- **outcome:** `no_hrr_needed`
- **key_share_reuse:** `compliant_new_keyshare`
- **RFC 10024 note:** RFC 10024 defines this as a standardized group; not a mandatory first key_share for all clients.
- **registry:** RFC 10024 defines PQ/T hybrid groups (X25519MLKEM768 etc.) as standardized registry entries; deployment/negotiation policy is separate.
- **detail:** Common group x25519mlkem768 has matching initial key_share → no HRR needed; preference ≠ mandatory retry. Caching/remembering a group preference without reusing KeyShare bytes is permitted.

### reuse-keyshare-forbidden — Reusing the same KeyShare value across connections — forbidden by RFC 9846
- **outcome:** `no_hrr_needed`
- **key_share_reuse:** `forbidden_by_rfc9846`
- **detail:** Common group x25519 has matching initial key_share → no HRR needed; preference ≠ mandatory retry. Reusing same KeyShare bytes across connections is forbidden by RFC 9846 §1.2 (distinct from caching a group preference).

### rfc10024-standardized-not-mandatory — X25519MLKEM768 as a standardized RFC 10024 group without treating it as a universal mandatory first offer
- **outcome:** `no_hrr_needed`
- **registry:** RFC 10024 defines PQ/T hybrid groups (X25519MLKEM768 etc.) as standardized registry entries; deployment/negotiation policy is separate.
- **detail:** Common group x25519 has matching initial key_share → no HRR needed; preference ≠ mandatory retry. RFC 10024 standardizes X25519MLKEM768 (Recommended Y, 0x11EC) but does not make it a mandatory first key_share for all TLS 1.3 clients.

---
**Current TLS base RFC:** RFC 9846 (obsoletes RFC 8446). Key change from 8446: §1.2 forbids reuse of KeyShare values between connections.
**RFC 10024 status:** Standardized PQ/T hybrid groups (X25519MLKEM768 0x11EC Recommended Y). Defines groups/registry; does not mandate universal first-offer.
**Evaluator scope:** Protocol/state facts only. No product-compliance or performance conclusions.
