import argparse, json, os, re, sys
from datetime import datetime, timezone
from .rpc import PolygonRPC, RPCError
from .explorer import get_verified_source, ExplorerError
from .analyzers import analyze_source
from .reporting import save_report
ADDR=re.compile(r"^0x[a-fA-F0-9]{40}$")
def address(value):
    if not ADDR.fullmatch(value): raise argparse.ArgumentTypeError("Expected 0x plus 40 hexadecimal characters.")
    return value
def banner():
    print("\033[96mPOLYHUNTER | POLYGON PoS | READ-ONLY RESEARCH\033[0m")
def report_base(addr=None):
    return {"tool":"PolyHunter","version":"0.1.0","network":"Polygon PoS (chain ID 137)","address":addr,
      "generated_at":datetime.now(timezone.utc).isoformat(),"metadata":{},"findings":[]}
def inspect_cmd(a):
    data=PolygonRPC(a.rpc).inspect(a.address)
    print(json.dumps(data,indent=2))
def analyze_cmd(a):
    meta=PolygonRPC(a.rpc).inspect(a.address); r=report_base(a.address); r["metadata"].update(meta)
    src=get_verified_source(a.address)
    if src:
        r["contract_name"]=src["contract_name"]
        r["metadata"].update({k:v for k,v in src.items() if k!="source"})
        r["findings"]=analyze_source(src["source"],src["contract_name"]+".sol")
    else:
        r["findings"]=[{"id":"INFO-SOURCE","category":"Source availability","severity":"info",
         "message":"Verified source unavailable. Set ETHERSCAN_API_KEY and check explorer verification.",
         "evidence":[],"occurrences":0,"confidence":"low","status":"needs_manual_review"}]
    jp,mp=save_report(r,a.out)
    print(f"Contract bytecode: {meta['bytecode_bytes']} bytes | Findings: {len(r['findings'])}")
    print(f"JSON: {jp}\nMarkdown: {mp}")
def file_cmd(a):
    with open(a.file,encoding="utf-8",errors="replace") as f: source=f.read()
    r=report_base(); r["contract_name"]=os.path.basename(a.file)
    r["metadata"]={"source_file":os.path.abspath(a.file),"source_bytes":len(source.encode())}
    r["findings"]=analyze_source(source,a.file)
    jp,mp=save_report(r,a.out); print(f"Findings: {len(r['findings'])}\nJSON: {jp}\nMarkdown: {mp}")
def discover_cmd(a):
    rpc=PolygonRPC(a.rpc); rpc.ensure_polygon()
    with open(a.address_file,encoding="utf-8") as f:
        addresses=[x.strip() for x in f if x.strip() and not x.lstrip().startswith("#")]
    results=[]
    for addr in addresses:
        if not ADDR.fullmatch(addr): print(f"[skip] Invalid address: {addr}"); continue
        try:
            item=rpc.inspect(addr); results.append(item)
            print(f"[{'CONTRACT' if item['is_contract'] else 'EOA'}] {addr} | {item['bytecode_bytes']} bytes")
        except RPCError as e: print(f"[error] {addr}: {e}")
    os.makedirs(a.out,exist_ok=True)
    path=os.path.join(a.out,"discovery-"+datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")+".json")
    with open(path,"w",encoding="utf-8") as f: json.dump({"chain_id":137,"results":results},f,indent=2)
    print("Saved:",path)
def reports_cmd(a):
    if not os.path.isdir(a.out): print("No reports folder yet."); return
    for name in sorted(os.listdir(a.out)): print(os.path.join(a.out,name))
def main():
    p=argparse.ArgumentParser(prog="polyhunter",description="Read-only Polygon smart-contract research toolkit.")
    p.add_argument("--rpc",help="RPC URL; alternatively set POLYHUNTER_RPC_URL.")
    s=p.add_subparsers(dest="command",required=True)
    q=s.add_parser("inspect",help="Inspect a Polygon address."); q.add_argument("address",type=address); q.set_defaults(func=inspect_cmd)
    q=s.add_parser("analyze",help="Inspect address and analyze verified source."); q.add_argument("address",type=address); q.add_argument("--out",default="reports"); q.set_defaults(func=analyze_cmd)
    q=s.add_parser("analyze-file",help="Analyze local Solidity source."); q.add_argument("file"); q.add_argument("--out",default="reports"); q.set_defaults(func=file_cmd)
    q=s.add_parser("discover",help="Check addresses listed in a text file."); q.add_argument("address_file"); q.add_argument("--out",default="reports"); q.set_defaults(func=discover_cmd)
    q=s.add_parser("reports",help="List report files."); q.add_argument("--out",default="reports"); q.set_defaults(func=reports_cmd)
    a=p.parse_args(); banner()
    try: a.func(a)
    except (RPCError,ExplorerError,OSError,ValueError) as e: print("[!] "+str(e),file=sys.stderr); return 1
    return 0
