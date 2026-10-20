#!/usr/bin/env bash
# SplitPot terminal demo against local Portaldot dev node
cd "$(dirname "$0")"
if ! curl -s -H 'Content-Type: application/json' -d '{"id":1,"jsonrpc":"2.0","method":"system_health"}' http://127.0.0.1:9944 >/dev/null; then
  echo ">> starting local node..."; (cd portaldot-testnet-ubuntu && nohup ./portaldot_dev --dev --alice --rpc-cors all --base-path /workspace/portaldot/chain >>/workspace/portaldot/node.log 2>&1 &); sleep 10
fi
clear 2>/dev/null; echo "=============================================="; echo "  SplitPot on Portaldot - atomic payment split"; echo "=============================================="; sleep 1
venv/bin/python -W ignore demo_split.py "${1:-6}"
echo; echo "Done: one extrinsic, three payouts, all-or-nothing."
