import os,sys,time
from substrateinterface import SubstrateInterface, Keypair
s=SubstrateInterface(url=os.environ.get("RPC","ws://127.0.0.1:9944"),ss58_format=42,type_registry_preset="substrate-node-template")
D=10**14; total=int(sys.argv[1]) if len(sys.argv)>1 else 6; shares=[50,30,20]
me=Keypair.create_from_mnemonic(open("key").read().strip(),ss58_format=42)
payees=[Keypair.create_from_uri(f"//SplitPayee{i}",ss58_format=42).ss58_address for i in range(3)]
bal=lambda p:s.query("System","Account",[p]).value["data"]["free"]/D
def show():
    for p,sh in zip(payees,shares): print(f"  {p}  ({sh}%)  {bal(p):.4f} POT")
print(f"Chain: {s.chain}   Payer: {me.ss58_address}"); time.sleep(1)
print("\n== Payee balances BEFORE =="); show(); time.sleep(2)
print(f"\n== Splitting {total} POT {'/'.join(map(str,shares))} via utility.batchAll (atomic) ==")
calls=[s.compose_call("Balances","transfer",{"dest":p,"value":total*D*sh//100}) for p,sh in zip(payees,shares)]
r=s.submit_extrinsic(s.create_signed_extrinsic(s.compose_call("Utility","batch_all",{"calls":calls}),me),wait_for_inclusion=True)
print("  status:", "SUCCESS" if r.is_success else r.error_message); print("  tx hash:", r.extrinsic_hash); print("  block:  ", r.block_hash); time.sleep(2)
print("\n== Payee balances AFTER =="); show()
