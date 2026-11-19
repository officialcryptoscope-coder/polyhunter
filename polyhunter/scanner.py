"""Heuristic Solidity source scanner; matches require manual review."""
import re
RULES=[
("AUTH-001","Access control","REVIEW",r"\b(?:owner|onlyOwner|onlyRole|AccessControl|DEFAULT_ADMIN_ROLE)\b","Ownership or role-control code found. Trace privileged functions and role administration."),
("AUTH-002","Privileged functions","HIGH",r"\bfunction\s+\w*(?:mint|pause|unpause|blacklist|setFee|setTax|setTrading|upgradeTo|setImplementation)\w*\s*\([^)]*\)\s*(?:public|external)","Sensitive public/external function found. Verify authorization and bounds."),
("REENT-001","Reentrancy","REVIEW",r"\.(?:call|delegatecall|staticcall)\s*(?:\{[^}]*\})?\s*\(","Low-level external call found. Review reentrancy protection, state ordering, and return values."),
("CALL-001","Delegatecall","HIGH",r"\.delegatecall\s*(?:\{[^}]*\})?\s*\(","delegatecall found. Verify target trust and storage-context safety."),
("CALL-002","Low-level call","REVIEW",r"\.call\s*(?:\{[^}]*\})?\s*\([^;]*\)\s*;","Low-level call found. Confirm success and return data are checked."),
("DESTR-001","Destructive operation","HIGH",r"\bselfdestruct\s*\(","selfdestruct found. Review intended destruction and balance transfer behavior."),
("AUTH-003","Authentication","HIGH",r"\btx\.origin\b","tx.origin found. Do not use it as the sole authorization mechanism."),
("PROXY-001","Upgradeability","REVIEW",r"\b(?:upgradeTo|upgradeToAndCall|_authorizeUpgrade|TransparentUpgradeableProxy|UUPSUpgradeable|implementation)\b","Proxy/upgradeability indicator found. Review upgrade authority, initialization, and storage layout."),
("ORACLE-001","Oracle","INFO",r"\b(?:latestRoundData|latestAnswer|AggregatorV3Interface|Chainlink|TWAP|oracle)\b","Oracle integration found. Check freshness, decimals, bounds, and manipulation resistance."),
("FLASH-001","Flash loans","INFO",r"\b(?:flashLoan|onFlashLoan|executeOperation)\b","Flash-loan callback found. Authenticate callbacks and preserve protocol invariants."),
("TOKEN-001","Token restrictions","REVIEW",r"\b(?:blacklist|whitelist|setFee|setTax|maxTx|maxWallet|tradingEnabled|setTrading)\b","Token restriction/fee controls found. Check whether owner can block transfers or change fees."),
("PAUSE-001","Pause controls","INFO",r"\b(?:pause|unpause|whenNotPaused|Pausable)\b","Pause controls found. Check who can pause and whether users can exit.")
]
def analyze_source(source,filename="<source>"):
    lines=source.splitlines(); findings=[]
    for rid,category,severity,pattern,message in RULES:
        rx=re.compile(pattern,re.I); hits=[]
        for number,line in enumerate(lines,1):
            if rx.search(line): hits.append({"file":filename,"line":number,"snippet":line.strip()[:240]})
        if hits:
            findings.append({"id":rid,"category":category,"severity":severity,"message":message,
              "evidence":hits[:20],"occurrences":len(hits),"confidence":"heuristic","status":"needs_manual_review"})
    if not findings:
        findings.append({"id":"INFO-000","category":"Static analysis","severity":"INFO",
          "message":"No configured patterns matched. This does not prove the contract is secure.",
          "evidence":[],"occurrences":0,"confidence":"heuristic","status":"needs_manual_review"})
    return findings
