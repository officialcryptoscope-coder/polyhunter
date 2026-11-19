import json, urllib.request
from .rpc import PolygonRPC, valid_address, checksum
EXPLORER="https://polygon.blockscout.com/api/v2/addresses/{}/transactions"
def recent_activity(address):
    try:
        req=urllib.request.Request(EXPLORER.format(address),headers={"User-Agent":"PolyHunter/0.2"})
        with urllib.request.urlopen(req,timeout=12) as r: data=json.loads(r.read())
        items=data.get("items",[])[:20]; failed=0; calls=0
        for tx in items:
            failed += tx.get("status")=="error" or tx.get("result")=="Error"
            dest=tx.get("to") or {}
            calls += isinstance(dest,dict) and bool(dest.get("is_contract"))
        return {"checked":len(items),"failed":int(failed),"contract_interactions":int(calls)}
    except Exception: return None
def audit(address,rpc_url=None,token=None,spender=None):
    if not valid_address(address): raise ValueError("Invalid wallet address")
    address=checksum(address); rpc=PolygonRPC(rpc_url); snap=rpc.snapshot(address)
    out={"network":"Polygon PoS","address":address,"snapshot":snap,"activity":recent_activity(address),"allowance":None,"findings":[],"limitations":[]}
    out["findings"].append({"severity":"INFO","title":"Contract address" if snap["is_contract"] else "Externally owned account","detail":"Bytecode is present." if snap["is_contract"] else "No contract bytecode found at the checked block."})
    if out["activity"] is None: out["limitations"].append("Blockscout transaction history unavailable; recent activity was not assessed.")
    elif out["activity"]["failed"]: out["findings"].append({"severity":"REVIEW","title":"Recent failed transactions","detail":"{} failed among {} indexed recent transactions; this alone does not indicate compromise.".format(out["activity"]["failed"],out["activity"]["checked"])})
    if bool(token)!=bool(spender): raise ValueError("Provide both --token and --spender")
    if token:
        if not valid_address(token) or not valid_address(spender): raise ValueError("Invalid token or spender address")
        amount=rpc.allowance(checksum(token),address,checksum(spender))
        out["allowance"]={"token":checksum(token),"spender":checksum(spender),"raw":str(amount),"maximum":amount==2**256-1}
        sev="HIGH" if amount==2**256-1 else ("REVIEW" if amount else "INFO")
        out["findings"].append({"severity":sev,"title":"ERC-20 allowance result","detail":"Raw allowance is {}. Check spender trust and revoke if unnecessary.".format(amount)})
    else: out["limitations"].append("Approvals were not enumerated. Supply a token and spender to check one specific ERC-20 allowance.")
    return out
def show(out):
    s=out["snapshot"]; print("\nPOLYHUNTER WALLET SECURITY\n"+"="*44)
    print("Network: Polygon PoS | chain {}".format(s["chain_id"])); print("Address: "+out["address"])
    print("POL balance: {:.8f}".format(s["balance_pol"])); print("Nonce: {} | Contract: {}".format(s["nonce"],s["is_contract"]))
    print("Code size: {} bytes | Block: {}".format(s["code_bytes"],s["block"]))
    if out["activity"]: print("Recent txs: {checked} checked, {failed} failed, {contract_interactions} contract calls".format(**out["activity"]))
    if out["allowance"]: print("Allowance raw units: "+out["allowance"]["raw"])
    for f in out["findings"]: print("[{}] {}: {}".format(f["severity"],f["title"],f["detail"]))
    for x in out["limitations"]: print("[LIMITATION] "+x)
    print("Screening only; this does not prove a wallet is safe or compromised.")
