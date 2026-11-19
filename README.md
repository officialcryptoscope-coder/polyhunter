# PolyHunter v0.3.0

Polygon Smart Contract Security Research Toolkit — a read-only Python CLI for Termux and desktop Linux.

## Four modules

1. Smart Contract Scanner: scans local Solidity files or verified Polygon source. Heuristic indicators include access control, privileged functions, reentrancy, low-level calls, delegatecall, selfdestruct, tx.origin, proxies, oracles, flash loans, pause controls, and token restrictions.
2. Token Risk Analyzer: reads ERC-20 metadata, supply, common owner/pause methods, EIP-1967 proxy slots, and scans verified source when available.
3. Wallet Security: reads public wallet balance, nonce, bytecode, recent indexed transactions, and optionally one specific ERC-20 token/spender allowance.
4. Wallet Generator: creates wallets, imports keys into encrypted local keystores, derives mnemonic accounts, and lists local keystores.

## Install on Termux — copy these commands

    pkg update -y && pkg upgrade -y
    pkg install -y git python
    git clone https://github.com/officialcryptoscope-coder/polyhunter.git
    cd polyhunter
    chmod +x install.sh
    ./install.sh

Start the interactive menu:

    python polyhunter.py

## If PolyHunter is already cloned

    cd ~/polyhunter
    git pull origin main
    python -m pip install -r requirements.txt --upgrade
    python polyhunter.py

## Help commands

    python polyhunter.py --help
    python polyhunter.py analyze-file --help
    python polyhunter.py analyze --help
    python polyhunter.py token-risk --help
    python polyhunter.py wallet-audit --help

## 1. Smart Contract Scanner

To scan a Solidity file saved on your phone, create a folder and open a new file:

    mkdir -p contracts
    nano contracts/Token.sol

Paste the Solidity source, save with CTRL+O, press ENTER, then exit with CTRL+X.

Run the scanner:

    python polyhunter.py analyze-file contracts/Token.sol

Save reports in a custom folder:

    python polyhunter.py analyze-file contracts/Token.sol --out my-reports

Scan a verified contract deployed on Polygon:

    python polyhunter.py analyze 0xCONTRACT_ADDRESS

If verified source is not available through Blockscout, configure an Etherscan API V2 key (optional):

    export ETHERSCAN_API_KEY="YOUR_ETHERSCAN_API_KEY"
    python polyhunter.py analyze 0xCONTRACT_ADDRESS

## 2. Token Risk Analyzer

    python polyhunter.py token-risk 0xTOKEN_CONTRACT_ADDRESS

Save reports in another directory:

    python polyhunter.py token-risk 0xTOKEN_CONTRACT_ADDRESS --out token-reports

## 3. Wallet Security

Basic public wallet audit:

    python polyhunter.py wallet-audit 0xPUBLIC_WALLET_ADDRESS

Check one token allowance for a specific spender:

    python polyhunter.py wallet-audit 0xWALLET --token 0xTOKEN --spender 0xSPENDER

Save JSON:

    python polyhunter.py wallet-audit 0xPUBLIC_WALLET_ADDRESS --json reports/wallet.json

## 4. Wallet Generator

Open its menu:

    python polyhunter.py wallet

Or choose option 4 in the main menu. Options include generating one/multiple wallets, importing a private key to an encrypted keystore, deriving from a mnemonic, and listing local keystores.

Wallet secrets are handled locally. Never share a private key or recovery phrase. Do not use a compromised phone for valuable wallets. Use a strong unique keystore password and back up recovery material securely.

## Optional Polygon RPC

Default endpoint: https://polygon-rpc.com

If it is rate-limited, set your own endpoint:

    export POLYGON_RPC_URL="https://YOUR_POLYGON_RPC_ENDPOINT"
    python polyhunter.py token-risk 0xTOKEN_ADDRESS

Or pass it to a single command:

    python polyhunter.py analyze 0xCONTRACT_ADDRESS --rpc "https://YOUR_RPC"
    python polyhunter.py token-risk 0xTOKEN_ADDRESS --rpc "https://YOUR_RPC"

## Run local tests

    python -m unittest discover -s tests -v

## Reports

Scanner and token analyzer save JSON and Markdown reports under reports/ by default. Use --out to choose another folder.

## Limitations

This is defensive screening, not a formal audit. Pattern matches can be false positives or miss vulnerabilities; no match does not mean safe. Generic RPC calls cannot prove token sellability, calculate taxes, establish honeypot status, or measure liquidity and holder concentration. Those require simulation, market data, and deeper review. Optional contract methods may be absent or misleading. Verify findings manually and only assess contracts you are authorized to review.

Scanner and token analysis do not sign or broadcast transactions. Wallet audit needs public addresses only. Never commit keystores, seed phrases, private keys, or API keys.
