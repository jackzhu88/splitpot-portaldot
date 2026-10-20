# SplitPot on Portaldot

Atomic payment splitter for the Portaldot Network (Ecosystem DApps track, Portaldot Hacker House 2026). A port of [SplitEscrow on Arc](https://github.com/jackzhu88/splitescrow-arc).

One payer sends a total amount, and it is split by percentage shares across N payees in a single `utility.batchAll` extrinsic. If any transfer fails, the whole batch reverts. It uses native Portaldot pallets (`balances`, `utility`), and fees are paid in POT (14 decimals).

## Run
```bash
wget https://github.com/portaldotVolunteer/Portaldot-node/raw/main/portaldot-testnet-ubuntu.tar.gz
tar xzf portaldot-testnet-ubuntu.tar.gz && cd portaldot-testnet-ubuntu
./portaldot_dev --dev --alice --rpc-cors all
pip install substrate-interface
python split.py     # creates a throwaway key, funds it from //Alice, then splits 10 POT 50/30/20
```
The results of a real run are in `testnet_run.json`, and there is a demo page in `index.html`. Note: the node uses the legacy `LookupSource` type, so connect with `type_registry_preset="substrate-node-template"`.

Author: jackzhu88
