#!/usr/bin/env python3
import argparse,json,sys
from pathlib import Path
from polyhunter.wallet_security import audit,show
from polyhunter.wallet_generator import menu as wallet_menu
from polyhunter import __version__
def main():
    p=argparse.ArgumentParser(description="PolyHunter Polygon toolkit"); sub=p.add_subparsers(dest="cmd")
    a=sub.add_parser("wallet-audit"); a.add_argument("address"); a.add_argument("--token"); a.add_argument("--spender"); a.add_argument("--rpc"); a.add_argument("--json",dest="out")
    sub.add_parser("wallet")
    args=p.parse_args()
    if args.cmd=="wallet-audit":
        try:
            r=audit(args.address,args.rpc,args.token,args.spender); show(r)
            if args.out:
                Path(args.out).parent.mkdir(parents=True,exist_ok=True); Path(args.out).write_text(json.dumps(r,indent=2)); print("Saved",args.out)
        except Exception as e: print("Audit error:",e,file=sys.stderr); return 1
        return 0
    if args.cmd=="wallet": wallet_menu(); return 0
    while True:
        print("\nPOLYHUNTER v{} | POLYGON SECURITY".format(__version__))
        print("[1] Smart Contract Scanner (planned)\n[2] Token Risk Analyzer (planned)\n[3] Wallet Security\n[4] Wallet Generator\n[0] Exit")
        c=input("Select: ").strip()
        if c=="0": return 0
        if c=="4": wallet_menu()
        elif c=="3":
            addr=input("Public wallet address: ").strip(); token=input("Token contract (optional): ").strip() or None; spender=input("Spender (optional): ").strip() or None
            try:
                r=audit(addr,token=token,spender=spender); show(r)
                if input("Save JSON report? [y/N]: ").lower()=="y":
                    Path("reports").mkdir(exist_ok=True); f="reports/wallet-{}.json".format(addr[-8:]); Path(f).write_text(json.dumps(r,indent=2)); print("Saved",f)
            except Exception as e: print("Audit error:",e)
        else: print("That module is planned for a later release.")
if __name__=="__main__": raise SystemExit(main())
