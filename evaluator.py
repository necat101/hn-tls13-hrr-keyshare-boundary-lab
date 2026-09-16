#!/usr/bin/env python3
"""
Deterministic evaluator for hn-tls13-hrr-keyshare-boundary-lab.
No live TLS, no network, no external deps — stdlib only.
"""
import json, pathlib
ROOT = pathlib.Path(__file__).parent
FIXTURES = ROOT / "fixtures" / "cases.json"
RESULTS_JSON = ROOT / "results.json"
RESULTS_MD = ROOT / "RESULTS.md"
KNOWN_GROUPS = {
    "x25519": {"rfc": "RFC 9846 / RFC 7748", "size_client": 32},
    "p256": {"rfc": "RFC 9846", "size_client": 65},
    "p384": {"rfc": "RFC 9846", "size_client": 97},
    "p521": {"rfc": "RFC 9846", "size_client": 133},
    "x25519mlkem768": {"rfc": "RFC 10024 (0x11EC)", "size_client": 1216},
    "secp256r1mlkem768": {"rfc": "RFC 10024 (0x11EB)", "size_client": 1249},
    "secp384r1mlkem1024": {"rfc": "RFC 10024 (0x11ED)", "size_client": 1665},
}
def evaluate_case(c):
    cid=c["id"]; client_groups=c.get("client_supported_groups") or []; client_shares=c.get("client_key_shares") or []; server_groups=c.get("server_supported_groups") or []; hrr_selected=c.get("server_hrr_selected_group"); server_selected=c.get("server_selected_group"); reuse_same_bytes=c.get("reuse_same_key_share_bytes"); remembered_preference=c.get("remembered_group_preference"); claims_mandatory_first=c.get("claims_mandatory_first_offer")
    client_share_groups=[s["group"] for s in client_shares]
    reuse_violation=None
    if reuse_same_bytes is True: reuse_violation="forbidden_by_rfc9846"
    elif reuse_same_bytes is False: reuse_violation="compliant_new_keyshare"
    common=[g for g in client_groups if g in server_groups]
    outcome={"case_id":cid,"client_supported_groups":client_groups,"client_key_share_groups":client_share_groups,"server_supported_groups":server_groups,"common_groups":common}
    detail_parts=[]
    if hrr_selected is not None:
        if hrr_selected not in client_groups:
            outcome["hrr_valid"]=False; outcome["hrr_invalid_reason"]="selected_group_not_in_client_supported_groups"; outcome["outcome"]="invalid_hrr"
            detail_parts.append(f"HRR selects {hrr_selected} absent from ClientHello supported_groups → invalid per RFC 9846 (must be mutually supported).")
        elif hrr_selected in client_share_groups:
            outcome["hrr_valid"]=False; outcome["hrr_invalid_reason"]="selected_group_already_in_client_key_share"; outcome["outcome"]="invalid_hrr"
            detail_parts.append(f"HRR selects {hrr_selected} already present in ClientHello key_share → invalid per RFC 9846 (HRR must request a new group).")
        else:
            if hrr_selected in common:
                outcome["hrr_valid"]=True; outcome["outcome"]="hrr_required"
                detail_parts.append(f"Valid HRR: server selects {hrr_selected} which is mutually supported but had no compatible key_share → client retries with new share.")
            else:
                outcome["hrr_valid"]=False; outcome["hrr_invalid_reason"]="selected_group_not_mutually_supported"; outcome["outcome"]="invalid_hrr"
                detail_parts.append(f"HRR selects {hrr_selected} not mutually supported → invalid.")
        outcome["detail"]=" ".join(detail_parts)
        if reuse_violation:
            outcome["key_share_reuse"]=reuse_violation
            outcome["detail"]+= " Reusing same KeyShare bytes across connections is forbidden by RFC 9846 §1.2." if reuse_violation=="forbidden_by_rfc9846" else " Remembered group preference with fresh KeyShare bytes is permitted; group ≠ bytes."
        if hrr_selected in ("x25519mlkem768","secp256r1mlkem768","secp384r1mlkem1024"):
            outcome["rfc10024_note"]="RFC 10024 defines this as a standardized group/registry entry; does not mandate it as universal first offer."
        return outcome
    if not common:
        outcome["outcome"]="abort"; outcome["hrr_valid"]=None
        outcome["detail"]="No common supported_groups → handshake aborts (not HRR). Server cannot select a mutually supported group."
        if reuse_violation: outcome["key_share_reuse"]=reuse_violation
        return outcome
    if server_selected is not None:
        if server_selected not in common: outcome["outcome"]="abort"; outcome["detail"]=f"Server selected {server_selected} not in common groups → abort."
        elif server_selected in client_share_groups: outcome["outcome"]="no_hrr_needed"; outcome["detail"]=f"Common group {server_selected} has matching initial key_share → no HRR needed; preference ≠ mandatory retry."
        else: outcome["outcome"]="hrr_required"; outcome["detail"]=f"Mutually supported group {server_selected} but no compatible initial key_share → HRR required per RFC 9846."
        if server_selected in ("x25519mlkem768","secp256r1mlkem768","secp384r1mlkem1024"):
            outcome["rfc10024_note"]="RFC 10024 defines this as a standardized group; not a mandatory first key_share for all clients."
    else:
        share_common=[g for g in client_share_groups if g in common]
        if share_common: outcome["outcome"]="no_hrr_needed"; outcome["detail"]=f"At least one common group {share_common} has a matching key_share → no HRR needed."
        else: outcome["outcome"]="hrr_required"; outcome["detail"]=f"Common groups {common} exist but none have a matching key_share → HRR required."
    if reuse_violation:
        outcome["key_share_reuse"]=reuse_violation
        outcome["detail"]+= " Reusing same KeyShare bytes across connections is forbidden by RFC 9846 §1.2 (distinct from caching a group preference)." if reuse_violation=="forbidden_by_rfc9846" else " Caching/remembering a group preference without reusing KeyShare bytes is permitted."
    if remembered_preference is not None:
        outcome["remembered_preference"]=remembered_preference
        if not reuse_violation: outcome["detail"]+=f" Remembered preference '{remembered_preference}' may inform next ClientHello's supported_groups/key_share choice, but fresh key material MUST be generated."
    if claims_mandatory_first is not None:
        outcome["claims_mandatory_first_offer"]=claims_mandatory_first
        if claims_mandatory_first=="x25519mlkem768": outcome["detail"]+=" RFC 10024 standardizes X25519MLKEM768 (Recommended Y, 0x11EC) but does not make it a mandatory first key_share for all TLS 1.3 clients."
    pq_involved=any(g in KNOWN_GROUPS and "10024" in KNOWN_GROUPS[g]["rfc"] for g in client_groups+server_groups)
    if pq_involved: outcome["rfc10024_registry"]="RFC 10024 defines PQ/T hybrid groups (X25519MLKEM768 etc.) as standardized registry entries; deployment/negotiation policy is separate."
    return outcome
def main():
    import json
    cases=json.loads(FIXTURES.read_text()); results=[]
    for c in cases:
        r=evaluate_case(c); r["title"]=c.get("title",""); results.append(r)
    RESULTS_JSON.write_text(json.dumps(results,indent=2, ensure_ascii=False)+"\n")
    lines=["# RESULTS — hn-tls13-hrr-keyshare-boundary-lab",""]
    lines.append("Evaluator derives outcomes from synthetic inputs per **RFC 9846** (current TLS 1.3, obsoletes 8446) and **RFC 10024** group definitions. No live TLS.")
    lines.append(""); lines.append("| case | outcome | hrr_valid | reuse | detail |"); lines.append("|---|---|---|---|---|")
    for r in results:
        hv=r.get("hrr_valid"); hv_s=str(hv) if hv is not None else "—"; reuse=r.get("key_share_reuse") or r.get("remembered_preference") or "—"; d=r.get("detail","").replace("|","/")[:140]
        lines.append(f"| {r['case_id']} | {r['outcome']} | {hv_s} | {reuse} | {d} |")
    lines.append(""); lines.append("## Per-case detail")
    for r in results:
        lines.append(f"### {r['case_id']} — {r.get('title','')}")
        lines.append(f"- **outcome:** `{r['outcome']}`")
        if r.get("hrr_valid") is not None: lines.append(f"- **hrr_valid:** `{r['hrr_valid']}`"+(f" ({r.get('hrr_invalid_reason')})" if r.get('hrr_invalid_reason') else ""))
        if r.get("key_share_reuse"): lines.append(f"- **key_share_reuse:** `{r['key_share_reuse']}`")
        if r.get("rfc10024_note"): lines.append(f"- **RFC 10024 note:** {r['rfc10024_note']}")
        if r.get("rfc10024_registry"): lines.append(f"- **registry:** {r['rfc10024_registry']}")
        lines.append(f"- **detail:** {r['detail']}"); lines.append("")
    lines.append("---")
    lines.append("**Current TLS base RFC:** RFC 9846 (obsoletes RFC 8446). Key change from 8446: §1.2 forbids reuse of KeyShare values between connections.")
    lines.append("**RFC 10024 status:** Standardized PQ/T hybrid groups (X25519MLKEM768 0x11EC Recommended Y). Defines groups/registry; does not mandate universal first-offer.")
    lines.append("**Evaluator scope:** Protocol/state facts only. No product-compliance or performance conclusions.")
    RESULTS_MD.write_text("\n".join(lines)+"\n")
    print(f"Evaluated {len(results)} cases → {RESULTS_JSON} + {RESULTS_MD}")
if __name__=="__main__": main()
