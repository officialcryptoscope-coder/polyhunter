# PolyHunter

Polygon Smart Contract Security Research Toolkit — a read-only, evidence-first CLI for Polygon PoS.

## Features
- Polygon chain ID 137 verification before RPC analysis.
- Read-only address inspection: bytecode, POL balance, transaction count.
- Optional verified Solidity source retrieval via Etherscan API V2.
- Heuristic checks for access control, reentrancy indicators, low-level calls, proxy upgrades, oracle/flash-loan references, input validation, and arithmetic.
- Address-list discovery (checks only addresses you supply).
- Markdown and JSON reports.
- No private keys, wallet signing, transaction sending, or exploit execution.

## Install in Termux
    pkg update -y
    pkg install -y python git
    git clone https://github.com/officialcryptoscope-coder/polyhunter.git
    cd polyhunter
    chmod +x install.sh
    ./install.sh

Run: python polyhunter.py --help

## Configure
Optional RPC:
    export POLYHUNTER_RPC_URL="https://polygon-rpc.com"

Optional verified-source API key:
    export ETHERSCAN_API_KEY="YOUR_API_KEY"

The API key is not required for RPC inspection or address-list discovery. Never commit API keys.

## Commands
    python polyhunter.py inspect 0xCONTRACT_ADDRESS
    python polyhunter.py analyze 0xCONTRACT_ADDRESS
    python polyhunter.py discover examples/addresses.txt
    python polyhunter.py analyze-file contracts/Vault.sol
    python polyhunter.py reports

Reports are saved in the reports directory by default.

## Important limitations
This is an early research assistant, not an audit tool. Pattern matches are leads, not confirmed vulnerabilities; no match does not prove safety. Review code context manually.
- No full-chain crawler, token/holder/liquidity ranking, fork testing, fuzzing, or symbolic execution in v0.1.0.
- Discovery checks only addresses in your input file.
- Source analysis requires verified source and an API key.
- Proxy detection is heuristic and may miss custom designs.

Use only on contracts and systems you are authorized to assess. No license has been selected; all rights remain with the repository owner.
