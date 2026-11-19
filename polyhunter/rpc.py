import json, os, urllib.request, urllib.error
DEFAULT_RPC = "https://polygon-rpc.com"
class RPCError(RuntimeError): pass
class PolygonRPC:
    def __init__(self, url=None, timeout=20):
        self.url = url or os.getenv("POLYHUNTER_RPC_URL", DEFAULT_RPC)
        self.timeout, self.counter = timeout, 0
    def call(self, method, params=None):
        self.counter += 1
        body = json.dumps({"jsonrpc":"2.0","id":self.counter,"method":method,"params":params or []}).encode()
        req = urllib.request.Request(self.url, data=body, headers={"Content-Type":"application/json","User-Agent":"PolyHunter/0.1.0"})
        try:
            with urllib.request.urlopen(req, timeout=self.timeout) as r: data = json.loads(r.read().decode())
        except (urllib.error.URLError, TimeoutError, json.JSONDecodeError) as e:
            raise RPCError(f"RPC request failed: {e}") from e
        if "error" in data: raise RPCError(str(data["error"]))
        return data.get("result")
    def ensure_polygon(self):
        chain = int(self.call("eth_chainId"), 16)
        if chain != 137: raise RPCError(f"Wrong network: chain ID {chain}; Polygon PoS chain ID 137 required.")
    def inspect(self, address):
        self.ensure_polygon()
        code = self.call("eth_getCode", [address, "latest"]) or "0x"
        balance = int(self.call("eth_getBalance", [address, "latest"]), 16)
        nonce = int(self.call("eth_getTransactionCount", [address, "latest"]), 16)
        return {"address":address,"is_contract":code not in ("0x","0x0",""),
                "bytecode_bytes":max(0,(len(code)-2)//2),"native_balance_wei":str(balance),
                "native_balance_pol":balance/10**18,"transaction_count":nonce,"chain_id":137}
