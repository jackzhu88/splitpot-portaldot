import os,json,sys
from substrateinterface import SubstrateInterface, Keypair
s=SubstrateInterface(url=os.environ.get("RPC","ws://127.0.0.1:9944"),ss58_format=42,type_registry_preset="substrate-node-template")
print("chain",s.chain,s.runtime_version, "props",s.properties)
if not os.path.exists("key"):
    m=Keypair.generate_mnemonic(); open("key","w").write(m); os.chmod("key",0o600)
me=Keypair.create_from_mnemonic(open("key").read().strip(),ss58_format=42)
alice=Keypair.create_from_uri("//Alice",ss58_format=42)
D=10**14
def send(kp,mod,fn,params):
    c=s.compose_call(mod,fn,params); x=s.create_signed_extrinsic(c,kp)
    r=s.submit_extrinsic(x,wait_for_inclusion=True)
    print(mod,fn,r.extrinsic_hash,r.block_hash,"ok" if r.is_success else r.error_message); return r
out={"payer":me.ss58_address}
out["fund"]=send(alice,"Balances","transfer",{"dest":me.ss58_address,"value":100*D}).extrinsic_hash
payees=[Keypair.create_from_uri(f"//SplitPayee{i}",ss58_format=42).ss58_address for i in range(3)]
shares=[50,30,20]; total=10*D
calls=[s.compose_call("Balances","transfer",{"dest":p,"value":total*sh//100}) for p,sh in zip(payees,shares)]
r=send(me,"Utility","batch_all",{"calls":calls})
out.update(split=r.extrinsic_hash,block=r.block_hash,payees=payees,shares=shares)
out["balances"]={p:s.query("System","Account",[p]).value["data"]["free"]/D for p in payees}
print(json.dumps(out,indent=1)); json.dump(out,open("result.json","w"),indent=1)
