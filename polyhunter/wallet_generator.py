import json, os
from pathlib import Path
from getpass import getpass
def Account():
    try:
        from eth_account import Account as A
        return A
    except ImportError: raise RuntimeError("Install dependencies first: pip install -r requirements.txt")
def folder():
    p=Path.home()/".polyhunter"/"keystores"; p.mkdir(parents=True,exist_ok=True)
    try: os.chmod(str(p),0o700)
    except OSError: pass
    return p
def password():
    a=getpass("Keystore password (hidden, min 12 chars): "); b=getpass("Confirm password: ")
    if len(a)<12 or a!=b: raise ValueError("Passwords must match and contain at least 12 characters")
    return a
def save(account,label="wallet"):
    enc=Account().encrypt(account.key,password()); path=folder()/("{}-{}.json".format(label,account.address[2:10].lower()))
    path.write_text(json.dumps(enc,indent=2),encoding="utf-8")
    try: os.chmod(str(path),0o600)
    except OSError: pass
    return path
def create():
    a=Account().create(); p=save(a); print("Address:",a.address)
    if input("Show private key ONCE? Type YES: ").strip()=="YES": print("PRIVATE KEY:",a.key.hex())
    print("Encrypted keystore:",p)
def multiple():
    n=int(input("Number of wallets (1-20): "))
    if not 1<=n<=20: raise ValueError("Choose 1 to 20")
    pw=password()
    for i in range(n):
        a=Account().create(); enc=Account().encrypt(a.key,pw); p=folder()/("wallet{}-{}.json".format(i+1,a.address[2:10].lower()))
        p.write_text(json.dumps(enc,indent=2)); os.chmod(str(p),0o600); print(a.address,"->",p)
def imported():
    a=Account().from_key(getpass("Private key (hidden): ").strip()); p=save(a,"imported"); print(a.address,"->",p)
def mnemonic():
    A=Account(); A.enable_unaudited_hdwallet_features()
    a=A.from_mnemonic(getpass("Mnemonic (hidden): ").strip()); p=save(a,"derived"); print(a.address,"->",p)
def menu():
    acts={"1":create,"2":multiple,"3":imported,"4":mnemonic}
    while True:
        print("\nWALLET GENERATOR\n[1] New wallet\n[2] Multiple wallets\n[3] Import private key\n[4] Derive mnemonic\n[5] List keystores\n[0] Back")
        c=input("Select: ").strip()
        if c=="0": return
        if c=="5":
            for p in sorted(folder().glob("*.json")): print(p.name)
            continue
        try:
            if c in acts: acts[c]()
            else: print("Invalid choice")
        except KeyboardInterrupt: print("Cancelled")
        except Exception as e: print("Error:",e)
