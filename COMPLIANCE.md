# SplitPot compliance notes

- Public identity: **jackzhu88** only. Contact (if needed): Telegram `@jackzhu8888`.
- Keys stay outside the repo (`KEY_FILE=…`). Never commit `.env`, keystores, mnemonics, or `*key*.json`.
- Public PortaldotV3 testnet proof: extrinsic `0xc13806ef8b6dfd916c33c64c60028e063946f74d0f7e6313d747f897e1b83d88` — see `testnet_run.json` and the explorer link in the README.
- Payee URIs `//SplitPayee0..2` are public Substrate **dev** URIs. They are acceptable for **tPOT self-tests on testnet only**.
- **Mainnet must NEVER use `//SplitPayee0..2` (or any other public Substrate development URI) as payees or signers.** Use independently generated keys kept outside the repo. Do not run mainnet transactions from this project until that is in place.
- Older local/dev hashes in the deck or index are labeled as local/dev and are not public-network proofs.
