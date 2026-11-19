"""Verified source retrieval from Polygon Blockscout, with optional Etherscan V2 fallback."""
import json,os,urllib.parse,urllib.request,urllib.error
BLOCKSCOUT="https://polygon.blockscout.com/api/v2/smart-contracts/{}"
ETHERSCAN="https://api.etherscan.io/v2/api"
class ExplorerError(RuntimeError): pass
def get_json(url):
    req=urllib.request.Request(url,headers={"User-Agent":"PolyHunter/0.3"})
    try:
        with urllib.request.urlopen(req,timeout=25) as r: return json.loads(r.read().decode())
    except (urllib.error.URLError,TimeoutError,OSError,ValueError) as e:
        raise ExplorerError("Explorer request failed: {}".format(e)) from e
def get_verified_source(address):
    try:
        d=get_json(BLOCKSCOUT.format(address))
        source=d.get("source_code")
        if source and d.get("is_verified",True):
            return {"source":source,"contract_name":d.get("name") or "Unknown",
              "compiler_version":d.get("compiler_version") or "Unknown","verified":True,"explorer":"Polygon Blockscout"}
    except ExplorerError: pass
    key=os.getenv("ETHERSCAN_API_KEY")
    if not key: return None
    q=urllib.parse.urlencode({"chainid":"137","module":"contract","action":"getsourcecode","address":address,"apikey":key})
    d=get_json(ETHERSCAN+"?"+q); rows=d.get("result")
    if not isinstance(rows,list) or not rows or not rows[0].get("SourceCode"): return None
    row=rows[0]
    return {"source":row.get("SourceCode",""),"contract_name":row.get("ContractName") or "Unknown",
      "compiler_version":row.get("CompilerVersion") or "Unknown","proxy":row.get("Proxy")=="1",
      "implementation":row.get("Implementation") or None,"verified":True,"explorer":"Etherscan API V2"}
