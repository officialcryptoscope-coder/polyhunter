import unittest
from polyhunter.scanner import analyze_source
class ScannerTests(unittest.TestCase):
    def test_tx_origin_and_delegatecall(self):
        src="contract X { function f(address t) external { require(tx.origin == owner); t.delegatecall(\"\"); } }"
        ids={x["id"] for x in analyze_source(src,"X.sol")}
        self.assertIn("AUTH-003",ids); self.assertIn("CALL-001",ids)
    def test_empty_result_is_not_safety_claim(self):
        result=analyze_source("contract Plain {}")
        self.assertIn("does not prove",result[0]["message"])
if __name__=="__main__": unittest.main()
