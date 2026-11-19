import json, os, urllib.parse, urllib.request, urllib.error
BASE = "https://api.etherscan.io/v2/api"
class ExplorerError(RuntimeError): pass
def get_verified_source(address):
    key = os.getenv("ETHERSCAN_API_KEY")
    if not key: return None
    q = urllib.parse.urlencode({"chainid":"137","module":"contract","action":"getsourcecode","address":address,"apikey":key})
    req = urllib.request.Request(BASE+"?"+q, headers={"User-Agent":"PolyHunter/0.1.0"})
    try:
        with urllib.request.urlopen(req, timeout=25) as r: data = json.loads(r.read().decode())
    except (urllib.error.URLError, TimeoutError, json.JSONDecodeError) as e:
        raise ExplorerError(f"Explorer request failed: {e}") from e
    rows = data.get("result")
    if not isinstance(rows,list) or not rows or not rows[0].get("SourceCode"): return None
    row = rows[0]
    return {"source":row.get("SourceCode",""),"contract_name":row.get("ContractName") or "Unknown",
            "compiler_version":row.get("CompilerVersion") or "Unknown","proxy":row.get("Proxy")=="1",
            "implementation":row.get("Implementation") or None,"license":row.get("LicenseType") or "Unknown"}
