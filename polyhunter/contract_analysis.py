"""Smart contract scanning entry points."""
from datetime import datetime,timezone
from pathlib import Path
from .rpc import PolygonRPC,valid_address,checksum
from .explorer import get_verified_source
from .scanner import analyze_source
def analyze_file(path):
    p=Path(path); source=p.read_text(encoding="utf-8",errors="replace")
    return {"tool":"PolyHunter","module":"Smart Contract Scanner","generated_at":datetime.now(timezone.utc).isoformat(),
      "network":"Local Solidity source","address":None,"contract_name":p.name,
      "metadata":{"source_file":str(p.resolve()),"source_bytes":len(source.encode())},
      "findings":analyze_source(source,p.name)}
def analyze_contract(address,rpc_url=None):
    if not valid_address(address): raise ValueError("Invalid contract address")
    address=checksum(address); rpc=PolygonRPC(rpc_url)
    chain=int(rpc.call("eth_chainId"),16)
    if chain!=137: raise RuntimeError("Expected Polygon chain ID 137; received {}".format(chain))
    code=rpc.call("eth_getCode",[address,"latest"])
    if code in ("0x","0x0",""): raise ValueError("No contract bytecode at this address")
    src=get_verified_source(address)
    if not src: raise RuntimeError("Verified source unavailable. Try a local .sol file or configure ETHERSCAN_API_KEY.")
    return {"tool":"PolyHunter","module":"Smart Contract Scanner","generated_at":datetime.now(timezone.utc).isoformat(),
      "network":"Polygon PoS (chain ID 137)","address":address,"contract_name":src.get("contract_name","Unknown"),
      "metadata":{"bytecode_bytes":(len(code)-2)//2,"compiler_version":src.get("compiler_version"),
        "source_verified":True,"source_explorer":src.get("explorer"),"proxy":src.get("proxy"),
        "implementation":src.get("implementation")},
      "findings":analyze_source(src["source"],src.get("contract_name","verified-source"))}
