import re
RULES = [
("ACCESS-001","Access control","high",r"function\s+\w+\s*\([^)]*\)\s*(?:public|external)","Public/external function found. Check whether privileged state changes are properly authorized."),
("ACCESS-002","Privileged role","info",r"\b(owner|onlyOwner|AccessControl|DEFAULT_ADMIN_ROLE|Ownable)\b","Ownership/role constructs found. Review assignment, revocation, and privileged functions."),
("REENT-001","External interaction","medium",r"\.(call|delegatecall|staticcall)\s*(?:\{[^}]*\})?\s*\(","Low-level external call found. Review checks-effects-interactions and reentrancy protections."),
("REENT-002","Value transfer","medium",r"\.(transfer|send)\s*\(","Native currency transfer found. Review state-update ordering and failure handling."),
("CALL-001","Call result","medium",r"(?:\.call|\.delegatecall)\s*(?:\{[^}]*\})?\s*\([^;]*\)\s*;","Review whether low-level call success and return data are checked."),
("PROXY-001","Upgradeability","info",r"\b(upgradeTo|upgradeToAndCall|_authorizeUpgrade|implementation|TransparentUpgradeableProxy|UUPSUpgradeable)\b","Proxy/upgradeability indicator found. Review authorization, initialization, and storage layout."),
("ORACLE-001","Oracle integration","info",r"\b(Chainlink|AggregatorV3Interface|latestRoundData|latestAnswer|TWAP|oracle)\b","Oracle indicator found. Review freshness, decimals, bounds, and manipulation resistance."),
("FLASH-001","Flash-loan integration","info",r"\b(flashLoan|flashBorrow|onFlashLoan|executeOperation)\b","Flash-loan indicator found. Review callback authentication and invariants."),
("INPUT-001","Input validation","info",r"\b(require|revert|assert)\s*\(","Validation statement found; this does not prove all inputs are validated."),
("MATH-001","Arithmetic","info",r"(?:\+\+|--|\+=|-=|\*=|/=|\*|/)","Arithmetic operators found. Review bounds, rounding, precision, and compiler version.")
]
def analyze_source(source, filename="<source>"):
    lines, findings = source.splitlines(), []
    for rid, category, severity, pattern, message in RULES:
        rx = re.compile(pattern, re.I)
        hits = [(i,line.strip()) for i,line in enumerate(lines,1) if rx.search(line)]
        if hits:
            findings.append({"id":rid,"category":category,"severity":severity,"message":message,
             "evidence":[{"file":filename,"line":n,"snippet":line[:240]} for n,line in hits[:12]],
             "occurrences":len(hits),"confidence":"low","status":"needs_manual_review"})
    if not findings:
        findings.append({"id":"INFO-000","category":"Static analysis","severity":"info",
         "message":"No configured patterns matched. This is not evidence that the contract is secure.",
         "evidence":[],"occurrences":0,"confidence":"low","status":"needs_manual_review"})
    return findings
