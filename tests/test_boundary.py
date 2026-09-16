import json, pathlib, unittest, importlib.util, sys
ROOT = pathlib.Path(__file__).parent.parent
FIXTURES = ROOT / "fixtures" / "cases.json"
spec = importlib.util.spec_from_file_location("evaluator", str(ROOT / "evaluator.py"))
mod = importlib.util.module_from_spec(spec)
sys.modules["evaluator"] = mod
spec.loader.exec_module(mod)
def oracle(case):
    client_groups=case.get("client_supported_groups") or []; client_shares=case.get("client_key_shares") or []; server_groups=case.get("server_supported_groups") or []; hrr=case.get("server_hrr_selected_group"); selected=case.get("server_selected_group")
    share_groups=[s["group"] for s in client_shares]; common=[g for g in client_groups if g in server_groups]
    if hrr is not None:
        if hrr not in client_groups: return {"outcome":"invalid_hrr","hrr_valid":False}
        if hrr in share_groups: return {"outcome":"invalid_hrr","hrr_valid":False}
        if hrr not in common: return {"outcome":"invalid_hrr","hrr_valid":False}
        return {"outcome":"hrr_required","hrr_valid":True}
    if not common: return {"outcome":"abort","hrr_valid":None}
    if selected is not None:
        if selected not in common: return {"outcome":"abort","hrr_valid":None}
        if selected in share_groups: return {"outcome":"no_hrr_needed","hrr_valid":None}
        return {"outcome":"hrr_required","hrr_valid":None}
    share_common=[g for g in share_groups if g in common]
    if share_common: return {"outcome":"no_hrr_needed","hrr_valid":None}
    return {"outcome":"hrr_required","hrr_valid":None}
class TestBoundary(unittest.TestCase):
    def setUp(self):
        self.cases=json.loads(FIXTURES.read_text())
        self.by_id={c["id"]:c for c in self.cases}
        self.results={r["case_id"]:r for r in json.loads((ROOT/"results.json").read_text())} if (ROOT/"results.json").exists() else {}
    def _assert_outcome(self, case_id):
        case=self.by_id[case_id]
        self.assertIn(case_id,self.results,f"missing result for {case_id}")
        exp=oracle(case); got=self.results[case_id]
        self.assertEqual(got["outcome"],exp["outcome"],f"{case_id}: outcome mismatch exp={exp} got={got}")
        if exp["hrr_valid"] is not None: self.assertEqual(got.get("hrr_valid"),exp["hrr_valid"],f"{case_id} hrr_valid")
        direct=mod.evaluate_case(case)
        self.assertEqual(direct["outcome"],exp["outcome"],f"{case_id} direct evaluator mismatch")
    def test_common_matching_share_no_hrr(self): self._assert_outcome("common-matching-share-no-hrr")
    def test_common_group_no_share_hrr(self): self._assert_outcome("common-group-no-share-hrr")
    def test_no_common_abort(self): self._assert_outcome("no-common-abort")
    def test_hrr_invalid_absent_group(self):
        self._assert_outcome("hrr-invalid-absent-group")
        r=self.results["hrr-invalid-absent-group"]; self.assertFalse(r["hrr_valid"]); self.assertIn("not_in_client",r.get("hrr_invalid_reason",""))
    def test_hrr_invalid_already_offered(self):
        self._assert_outcome("hrr-invalid-already-offered")
        r=self.results["hrr-invalid-already-offered"]; self.assertFalse(r["hrr_valid"]); self.assertIn("already",r.get("hrr_invalid_reason",""))
    def test_prefers_pq_accepts_classical(self):
        self._assert_outcome("prefers-pq-accepts-classical")
        self.assertEqual(self.results["prefers-pq-accepts-classical"]["outcome"],"no_hrr_needed")
    def test_remembered_preference_fresh_share(self):
        self._assert_outcome("remembered-preference-fresh-share")
        self.assertEqual(self.results["remembered-preference-fresh-share"].get("key_share_reuse"),"compliant_new_keyshare")
    def test_reuse_keyshare_forbidden(self):
        self._assert_outcome("reuse-keyshare-forbidden")
        r=self.results["reuse-keyshare-forbidden"]; self.assertEqual(r.get("key_share_reuse"),"forbidden_by_rfc9846"); self.assertEqual(r["outcome"],"no_hrr_needed")
    def test_rfc10024_standardized_not_mandatory(self):
        self._assert_outcome("rfc10024-standardized-not-mandatory")
        r=self.results["rfc10024-standardized-not-mandatory"]; self.assertEqual(r["outcome"],"no_hrr_needed"); self.assertIn("RFC 10024",r.get("detail",""))
    def test_reuse_vs_preference_distinction(self):
        fresh=self.results["remembered-preference-fresh-share"]; reuse=self.results["reuse-keyshare-forbidden"]
        self.assertNotEqual(fresh.get("key_share_reuse"),reuse.get("key_share_reuse"))
        self.assertEqual(fresh.get("key_share_reuse"),"compliant_new_keyshare"); self.assertEqual(reuse.get("key_share_reuse"),"forbidden_by_rfc9846")
