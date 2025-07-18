import json
import time
from web3 import Web3

with open("config.json") as f:
    config = json.load(f)

w3 = Web3(Web3.HTTPProvider(config["rpc_url"]))
account = w3.eth.account.from_key(config["private_key"])
token_address = Web3.toChecksumAddress(config["token_address"])
contract_abi = [
    {
        "constant": False,
        "inputs": [
            {"name": "_to", "type": "address"},
            {"name": "_value", "type": "uint256"}
        ],
        "name": "transfer",
        "outputs": [{"name": "", "type": "bool"}],
        "type": "function"
    }
]

contract = w3.eth.contract(address=token_address, abi=contract_abi)

def send_token(to, amount):
    nonce = w3.eth.getTransactionCount(account.address)
    tx = contract.functions.transfer(Web3.toChecksumAddress(to), amount).buildTransaction({
        'from': account.address,
        'nonce': nonce,
        'gas': 100000,
        'gasPrice': w3.eth.gas_price,
    })
    signed_tx = account.sign_transaction(tx)
    try:
        tx_hash = w3.eth.sendRawTransaction(signed_tx.rawTransaction)
        receipt = w3.eth.waitForTransactionReceipt(tx_hash, timeout=120)
        print(f"Sent {amount} tokens to {to} in tx {tx_hash.hex()}")
        return receipt.status == 1
    except Exception as e:
        print(f"Error sending to {to}: {e}")
        return False

def main():
    for recipient in config["recipients"]:
        retries = 3
        success = False
        while retries > 0 and not success:
            success = send_token(recipient["address"], recipient["amount"])
            if not success:
                retries -= 1
                print(f"Retrying... attempts left: {retries}")
                time.sleep(5)

if __name__ == "__main__":
    main()
