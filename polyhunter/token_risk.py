"""Read-only Polygon token metadata, owner, proxy, and verified-source screening."""
from datetime import datetime,timezone
from .rpc import PolygonRPC,valid_address,checksum
from .explorer import get_verified_source
from .scanner import analyze_source
IMPL_SLOT="0x360894a13ba1a3210667c828492db98dca3e2076cc3735a920a3ca505d382bbc"
ADMIN_SLOT="0xb53127684a568b3173ae13b9f8a6016e243e63b6e8ee1178d6a717850b5d6103"
def read_word(rpc,address,selector):
    try: return int(rpc.call("eth_call",[{"to":address,"data":selector},"latest"]),16)
    except Exception: return None
def read_string(rpc,address,selector):
    try:
        raw=rpc.call("eth_call",[{"to":address,"data":selector},"latest"])
        if not raw or raw=="0x": return None
        b=bytes.fromhex(raw[2:])
        if len(b)==32: return b.rstrip(b"\0").decode("utf-8","replace") or None
        offset=int.from_bytes(b[:32],"big"); size=int.from_bytes(b[offset:offset+32],"big")
        return b[offset+32:offset+32+size].decode("utf-8","replace")
    except Exception: return None
def slot_address(rpc,address,slot):
    try:
        raw=rpc.call("eth_getStorageAt",[address,slot,"latest"]); v=raw[-40:]
        return "0x"+v if int(v,16) else None
    except Exception: return None
def analyze_token(address,rpc_url=None):
    if not valid_address(address): raise ValueError("Invalid token contract address")
    address=checksum(address); rpc=PolygonRPC(rpc_url)
    chain=int(rpc.call("eth_chainId"),16)
    if chain!=137: raise RuntimeError("Expected Polygon chain ID 137; got {}".format(chain))
    code=rpc.call("eth_getCode",[address,"latest"])
    if code in ("0x","0x0",""): raise ValueError("No contract bytecode at this address on Polygon")
    m={"name":read_string(rpc,address,"0x06fdde03"),"symbol":read_string(rpc,address,"0x95d89b41"),
       "decimals":read_word(rpc,address,"0x313ce567"),"total_supply_raw":None,
       "owner":None,"paused":None,"eip1967_implementation":slot_address(rpc,address,IMPL_SLOT),
       "eip1967_admin":slot_address(rpc,address,ADMIN_SLOT),"code_bytes":(len(code)-2)//2}
    supply=read_word(rpc,address,"0x18160ddd"); m["total_supply_raw"]=str(supply) if supply is not None else None
    owner=read_word(rpc,address,"0x8da5cb5b")
    m["owner"]=("0x"+format(owner,"040x")[-40:]) if owner else None
    paused=read_word(rpc,address,"0x5c975abb"); m["paused"]=bool(paused) if paused is not None else None
    findings=[]
    if m["eip1967_implementation"]: findings.append({"id":"PROXY-001","category":"Upgradeability","severity":"REVIEW","message":"EIP-1967 implementation slot is populated; review implementation and upgrade authority.","evidence":[],"occurrences":1,"status":"needs_manual_review"})
    if m["eip1967_admin"]: findings.append({"id":"PROXY-002","category":"Upgradeability","severity":"REVIEW","message":"EIP-1967 admin slot is populated; identify who controls upgrades.","evidence":[],"occurrences":1,"status":"needs_manual_review"})
    if m["owner"] and int(m["owner"],16): findings.append({"id":"OWNER-001","category":"Ownership","severity":"REVIEW","message":"owner() returned a non-zero address; inspect its privileges and governance.","evidence":[],"occurrences":1,"status":"needs_manual_review"})
    if m["paused"] is True: findings.append({"id":"PAUSE-001","category":"Transfer controls","severity":"REVIEW","message":"paused() returned true at the checked block.","evidence":[],"occurrences":1,"status":"needs_manual_review"})
    try: src=get_verified_source(address)
    except Exception: src=None
    if src: findings.extend(analyze_source(src["source"],src.get("contract_name","verified-source")))
    else: findings.append({"id":"SOURCE-001","category":"Source availability","severity":"INFO","message":"Verified source unavailable; bytecode-only checks cannot reveal all token controls, fees, or honeypot behavior.","evidence":[],"occurrences":0,"status":"needs_manual_review"})
    return {"tool":"PolyHunter","module":"Token Risk Analyzer","generated_at":datetime.now(timezone.utc).isoformat(),
      "network":"Polygon PoS (chain ID 137)","address":address,"contract_name":(src or {}).get("contract_name","Unknown"),
      "metadata":m,"verified_source":bool(src),"source_explorer":(src or {}).get("explorer"),
      "findings":findings,"limitations":[
       "This does not prove a token is sellable or calculate buy/sell tax; that requires simulation and market/liquidity data.",
       "Owner and pause methods are optional conventions and may be absent or misleading.",
       "This is read-only screening, not an audit or guarantee against honeypots."]}
