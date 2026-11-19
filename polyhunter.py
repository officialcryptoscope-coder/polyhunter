#!/usr/bin/env python3
"""PolyHunter Polygon security toolkit."""
import argparse,json,sys
from pathlib import Path
from polyhunter import __version__
from polyhunter.wallet_security import audit,show
from polyhunter.wallet_generator import menu as wallet_menu
from polyhunter.contract_analysis import analyze_file,analyze_contract
from polyhunter.token_risk import analyze_token
from polyhunter.reporting import save_report
def emit(report,out="reports",stem="polyhunter"):
    jp,mp=save_report(report,out,stem)
    print("Findings:",len(report.get("findings",[]))); print("JSON:",jp); print("Markdown:",mp)
def interactive():
    while True:
        print("\\nPOLYHUNTER v{} | POLYGON SECURITY".format(__version__))
        print("[1] Smart Contract Scanner\\n[2] Token Risk Analyzer\\n[3] Wallet Security\\n[4] Wallet Generator\\n[0] Exit")
        c=input("Select option: ").strip()
        try:
            if c=="0": return 0
            if c=="1":
                target=input("Polygon contract address or local .sol file: ").strip()
                emit(analyze_file(target) if Path(target).is_file() else analyze_contract(target),stem="contract-scan")
            elif c=="2": emit(analyze_token(input("Polygon token contract address: ").strip()),stem="token-risk")
            elif c=="3":
                addr=input("Public wallet address: ").strip(); token=input("ERC-20 token (optional): ").strip() or None
                spender=input("Spender (optional): ").strip() or None; report=audit(addr,token=token,spender=spender); show(report)
                if input("Save JSON report? [y/N]: ").strip().lower()=="y":
                    Path("reports").mkdir(exist_ok=True); p="reports/wallet-{}.json".format(addr[-8:])
                    Path(p).write_text(json.dumps(report,indent=2),encoding="utf-8"); print("Saved:",p)
            elif c=="4": wallet_menu()
            else: print("Invalid option.")
        except KeyboardInterrupt: print("\\nCancelled.")
        except Exception as e: print("Error:",e)
def main():
    p=argparse.ArgumentParser(prog="polyhunter",description="Read-only Polygon security toolkit")
    s=p.add_subparsers(dest="cmd")
    q=s.add_parser("analyze-file",help="Scan local Solidity source"); q.add_argument("file"); q.add_argument("--out",default="reports")
    q=s.add_parser("analyze",help="Scan verified Polygon contract source"); q.add_argument("address"); q.add_argument("--rpc"); q.add_argument("--out",default="reports")
    q=s.add_parser("token-risk",help="Analyze Polygon token metadata and risk indicators"); q.add_argument("address"); q.add_argument("--rpc"); q.add_argument("--out",default="reports")
    q=s.add_parser("wallet-audit",help="Audit public wallet"); q.add_argument("address"); q.add_argument("--token"); q.add_argument("--spender"); q.add_argument("--rpc"); q.add_argument("--json",dest="json_path")
    s.add_parser("wallet",help="Open wallet generator")
    a=p.parse_args()
    try:
        if a.cmd=="analyze-file": emit(analyze_file(a.file),a.out,"contract-scan")
        elif a.cmd=="analyze": emit(analyze_contract(a.address,a.rpc),a.out,"contract-scan")
        elif a.cmd=="token-risk": emit(analyze_token(a.address,a.rpc),a.out,"token-risk")
        elif a.cmd=="wallet-audit":
            r=audit(a.address,a.rpc,a.token,a.spender); show(r)
            if a.json_path:
                Path(a.json_path).parent.mkdir(parents=True,exist_ok=True)
                Path(a.json_path).write_text(json.dumps(r,indent=2),encoding="utf-8"); print("JSON:",a.json_path)
        elif a.cmd=="wallet": wallet_menu()
        else: return interactive()
        return 0
    except Exception as e:
        print("Error:",e,file=sys.stderr); return 1
if __name__=="__main__": raise SystemExit(main())
