import json, os, urllib.request, urllib.error
DEFAULT_RPC = "https://polygon-rpc.com"
# EIP-1967 standard storage slots.
IMPLEMENTATION_SLOT = "0x360894a13ba1a3210667c828492db98dca3e2076cc3735a920a3ca505d382bbc"
ADMIN_SLOT = "0xb53127684a568b3173ae13b9f8a6016e243e63b6e8ee1178d6a717850b5d6103"

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
            with urllib.request.urlopen(req, timeout=self.timeout) as r:
                data = json.loads(r.read().decode())
        except (urllib.error.URLError, TimeoutError, json.JSONDecodeError) as e:
            raise RPCError(f"RPC request failed: {e}") from e
        if "error" in data:
            raise RPCError(str(data["error"]))
        return data.get("result")

    def ensure_polygon(self):
        chain = int(self.call("eth_chainId"), 16)
        if chain != 137:
            raise RPCError(f"Wrong network: chain ID {chain}; Polygon PoS chain ID 137 required.")

    def _slot_address(self, address, slot):
        raw = self.call("eth_getStorageAt", [address, slot, "latest"]) or "0x0"
        value = raw[-40:].lower()
        if not value or int(value, 16) == 0:
            return None
        return "0x" + value

    def inspect(self, address):
        self.ensure_polygon()
        code = self.call("eth_getCode", [address, "latest"]) or "0x"
        balance = int(self.call("eth_getBalance", [address, "latest"]), 16)
        nonce = int(self.call("eth_getTransactionCount", [address, "latest"]), 16)
        implementation = admin = None
        if code not in ("0x", "0x0", ""):
            implementation = self._slot_address(address, IMPLEMENTATION_SLOT)
            admin = self._slot_address(address, ADMIN_SLOT)
        return {
            "address": address,
            "is_contract": code not in ("0x", "0x0", ""),
            "bytecode_bytes": max(0, (len(code) - 2) // 2),
            "native_balance_wei": str(balance),
            "native_balance_pol": balance / 10**18,
            "transaction_count": nonce,
            "chain_id": 137,
            "eip1967_implementation": implementation,
            "eip1967_admin": admin,
            "eip1967_proxy_signal": bool(implementation),
        }
