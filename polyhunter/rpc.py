import json, os, urllib.request, urllib.error
DEFAULT_RPC="https://polygon-rpc.com"
class RPCError(RuntimeError): pass
class PolygonRPC:
    def __init__(self,url=None): self.url=url or os.getenv("POLYGON_RPC_URL",DEFAULT_RPC); self.i=1
    def call(self,method,params=None):
        body=json.dumps({"jsonrpc":"2.0","id":self.i,"method":method,"params":params or []}).encode(); self.i+=1
        req=urllib.request.Request(self.url,data=body,headers={"Content-Type":"application/json","User-Agent":"PolyHunter/0.2"})
        try:
            with urllib.request.urlopen(req,timeout=20) as r: data=json.loads(r.read())
        except Exception as e: raise RPCError("Polygon RPC failed: {}".format(e))
        if data.get("error"): raise RPCError(data["error"].get("message","RPC error"))
        return data["result"]
    def snapshot(self,address):
        chain=int(self.call("eth_chainId"),16)
        if chain!=137: raise RPCError("Expected Polygon chain ID 137; got {}".format(chain))
        bal=int(self.call("eth_getBalance",[address,"latest"]),16)
        nonce=int(self.call("eth_getTransactionCount",[address,"latest"]),16)
        code=self.call("eth_getCode",[address,"latest"])
        block=int(self.call("eth_blockNumber"),16)
        return {"chain_id":chain,"balance_wei":bal,"balance_pol":bal/10**18,"nonce":nonce,"is_contract":code not in ("0x","0x0"),"code_bytes":max(0,(len(code)-2)//2),"block":block}
    def allowance(self,token,owner,spender):
        data="0xdd62ed3e"+owner[2:].lower().rjust(64,"0")+spender[2:].lower().rjust(64,"0")
        return int(self.call("eth_call",[{"to":token,"data":data},"latest"]),16)
def valid_address(v):
    if not isinstance(v,str) or len(v)!=42 or not v.startswith("0x"): return False
    try: int(v[2:],16); return True
    except ValueError: return False
def checksum(v):
    if not valid_address(v): raise ValueError("Invalid EVM address")
    try:
        from eth_utils import to_checksum_address
        return to_checksum_address(v)
    except ImportError: return v.lower()
