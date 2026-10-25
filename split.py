"""SplitPot: atomic N-way payment split on Portaldot via utility.batchAll.

Default target: the public PortaldotV3 testnet (wss://test-node-v3.portaldot.dev).
The payer key is read from KEY_FILE (JSON with a "mnemonic" field) kept OUTSIDE
the repo. Nothing secret is printed or written to the output file.

  KEY_FILE=/path/to/key.json python split.py [TOTAL] [OUT]
  e.g. KEY_FILE=... python split.py 6 testnet_run.json   # split 6 tPOT 50/30/20
"""
import os, sys, json, datetime
from substrateinterface import SubstrateInterface, Keypair

RPC = os.environ.get("RPC", "wss://test-node-v3.portaldot.dev")
EXPLORER = os.environ.get("EXPLORER", "https://scanner-testnet-v3.portaldot.dev")
TOTAL = sys.argv[1] if len(sys.argv) > 1 else "6"
OUT = sys.argv[2] if len(sys.argv) > 2 else "testnet_run.json"
SHARES = [50, 30, 20]

s = SubstrateInterface(url=RPC, ss58_format=42)
dec = int(s.properties.get("tokenDecimals", 14)); D = 10 ** dec
sym = s.properties.get("tokenSymbol", "POT")
utc = lambda ms: datetime.datetime.fromtimestamp(ms / 1000, datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.%f")[:-3] + "Z"

me = Keypair.create_from_mnemonic(json.load(open(os.environ["KEY_FILE"]))["mnemonic"].strip(), ss58_format=42)
payees = [Keypair.create_from_uri(f"//SplitPayee{i}", ss58_format=42).ss58_address for i in range(len(SHARES))]
total = int(float(TOTAL) * D)
amounts = [total * sh // 100 for sh in SHARES]
amounts[-1] += total - sum(amounts)  # rounding dust goes to the last payee
free = lambda a: s.query("System", "Account", [a]).value["data"]["free"]

# legacy runtimes call it "transfer"; current Substrate runtimes use transfer_keep_alive
fn = "transfer_keep_alive" if s.get_metadata_call_function("Balances", "transfer_keep_alive") else "transfer"
calls = [s.compose_call("Balances", fn, {"dest": p, "value": a}) for p, a in zip(payees, amounts)]
call = s.compose_call("Utility", "batch_all", {"calls": calls})

before = {a: free(a) for a in [me.ss58_address] + payees}
print(f"chain {s.chain}  payer {me.ss58_address}  splitting {TOTAL} {sym} {'/'.join(map(str, SHARES))}")
r = s.submit_extrinsic(s.create_signed_extrinsic(call, me), wait_for_inclusion=True)
print("included:", r.extrinsic_hash, "in block", r.block_hash, flush=True)
ok = any(e.value["module_id"] == "System" and e.value["event_id"] == "ExtrinsicSuccess" for e in r.triggered_events)
fee = next((e.value["attributes"] for e in r.triggered_events if e.value["event_id"] == "TransactionFeePaid"), None)
blk = s.get_block_header(r.block_hash)["header"]["number"]
ts = s.query("Timestamp", "Now", block_hash=r.block_hash).value
after = {a: free(a) for a in before}

out = {
    "network": s.chain, "rpc": RPC, "spec": s.runtime_version,
    "status": "ExtrinsicSuccess" if ok else f"FAILED: {r.error_message}",
    "call": f"Utility.batch_all([Balances.{fn} x {len(payees)}])",
    "extrinsic_hash": r.extrinsic_hash, "extrinsic_index": f"{blk}-{r.extrinsic_idx}",
    "block_number": blk, "block_hash": r.block_hash, "block_time_utc": utc(ts),
    "explorer": {"extrinsic": f"{EXPLORER}/extrinsics/{blk}-{r.extrinsic_idx}", "block": f"{EXPLORER}/blocks/{blk}"},
    "token": sym, "decimals": dec, "total_split": str(total / D),
    "fee_charged_planck": fee["actual_fee"] if fee else None,
    "fee_charged": str(fee["actual_fee"] / D) if fee else None,
    "fee_source": "TransactionPayment.TransactionFeePaid event" if fee else None,
    "payer": {"address": me.ss58_address, "before": before[me.ss58_address], "after": after[me.ss58_address],
              "spent": before[me.ss58_address] - after[me.ss58_address]},
    "payees": [{"address": p, "share_pct": sh, "sent": a, "before": before[p], "after": after[p],
                "received": after[p] - before[p]} for p, sh, a in zip(payees, SHARES, amounts)],
    "events": [f'{e.value["module_id"]}.{e.value["event_id"]}' for e in r.triggered_events],
    "note": "Balances are in planck (1 %s = 10^%d planck). Payees are the project's fixed demo accounts //SplitPayee0..2." % (sym, dec),
}
print(json.dumps(out, indent=1)); json.dump(out, open(OUT, "w"), indent=1)
sys.exit(0 if ok else 1)
