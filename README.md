# PolyHunter
Polygon Smart Contract Security Research Toolkit. Python CLI designed for Termux.

## Wallet Security (menu 3)
- Checks Polygon chain ID 137, POL balance, transaction count, contract bytecode and latest block.
- Attempts a recent transaction summary from Polygon Blockscout.
- Checks one ERC-20 allowance when both token and spender are supplied.
- Reports limitations; it does not claim to enumerate all approvals or prove compromise.

## Wallet Generator (menu 4)
- Generate one or multiple EVM wallets.
- Import a private key into an encrypted local keystore.
- Derive an account from a mnemonic.
- Keystore files live in ~/.polyhunter/keystores with restrictive permissions where supported.
- Secrets are not uploaded. Keep backups securely and never share a private key or mnemonic.

## Termux install
~~~bash
pkg update -y
pkg install -y git python
git clone https://github.com/officialcryptoscope-coder/polyhunter.git
cd polyhunter
chmod +x install.sh
./install.sh
python polyhunter.py
~~~

## CLI audit
~~~bash
python polyhunter.py wallet-audit 0xYOUR_PUBLIC_ADDRESS
python polyhunter.py wallet-audit 0xYOUR_WALLET --token 0xTOKEN --spender 0xSPENDER
python polyhunter.py wallet-audit 0xYOUR_PUBLIC_ADDRESS --json reports/audit.json
~~~

Set a custom RPC with POLYGON_RPC_URL. Dependencies are listed in requirements.txt.

## Important limitations
This is a defensive screening tool, not a formal audit or guarantee of wallet safety. Activity data may be incomplete or unavailable. Allowance checks are specific to the token/spender pair supplied. Smart Contract Scanner and Token Risk Analyzer are planned menu entries, not implemented in this release.

## Security
Never commit keystores, private keys, mnemonics, or environment files. Do not generate wallets on a compromised device.
