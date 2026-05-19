"""Hyperliquid Wallet Setup — derive EVM wallet from MetaMask BIP-39 seed"""
import sys, os
sys.path.insert(0, "/workspace/trading-bot")

from bip_utils import Bip39SeedGenerator, Bip44, Bip44Coins, Bip44Changes
from eth_account import Account

def derive_hyperliquid_wallet(mnemonic: str, account_index=0):
    seed = Bip39SeedGenerator(mnemonic).Generate()
    bip44_ctx = Bip44.FromSeed(seed, Bip44Coins.ETHEREUM)
    priv_key_bytes = bip44_ctx.Purpose().Coin().Account(0).Change(Bip44Changes.CHAIN_EXT).AddressIndex(account_index).PrivateKey().Raw().ToBytes()
    priv_key_hex = priv_key_bytes.hex()
    account = Account.from_key(priv_key_hex)
    return {"address": account.address, "private_key": priv_key_hex}

def save_wallet_config(address, private_key):
    env_path = "/workspace/trading-bot/.env"
    lines = []
    if os.path.exists(env_path):
        with open(env_path) as f:
            lines = f.readlines()

    found_addr = found_key = found_net = False
    new_lines = []
    for l in lines:
        if l.startswith("HYPERLIQUID_WALLET="):
            new_lines.append(f'HYPERLIQUID_WALLET="{address}"\n')
            found_addr = True
        elif l.startswith("HYPERLIQUID_PRIVATE_KEY="):
            new_lines.append(f'HYPERLIQUID_PRIVATE_KEY="{private_key}"\n')
            found_key = True
        elif l.startswith("HYPERLIQUID_TESTNET="):
            new_lines.append(f'HYPERLIQUID_TESTNET=true\n')
            found_net = True
        else:
            new_lines.append(l)

    if not found_addr:
        new_lines.append(f'HYPERLIQUID_WALLET="{address}"\n')
    if not found_key:
        new_lines.append(f'HYPERLIQUID_PRIVATE_KEY="{private_key}"\n')
    if not found_net:
        new_lines.append("HYPERLIQUID_TESTNET=true\n")

    with open(env_path, "w") as f:
        f.writelines(new_lines)
    print(f"  ✅ .env saved")

if __name__ == "__main__":
    mnemonic = os.getenv("METAMASK_MNEMONIC", "level worry hybrid toilet square reason busy answer lounge wasp easy expand")
    
    print("🧠 Deriving Hyperliquid (EVM) wallet from MetaMask...")
    wallet = derive_hyperliquid_wallet(mnemonic, account_index=0)
    
    print(f"\n  📍 Address:     {wallet['address']}")
    print(f"  🔑 Private Key: {wallet['private_key'][:10]}...{wallet['private_key'][-6:]}")
    
    save_wallet_config(wallet["address"], wallet["private_key"])
    
    print(f"\n  ✅ Hyperliquid testnet wallet klaar!")
    print(f"  📍 0x9AAF25F116C9C19866E22136Afd902D00D171fFC")