import requests
import json
import hashlib
import time

# Configuration for miner
class MinerConfig:
    def __init__(self):
        self.node_url = None
        self.miner_address = None

# Miner setup
def setup_miner():
    config = MinerConfig()
    print("=== Miner Setup ===")
    # config.node_url = input("Enter the node URL (e.g., http://127.0.0.1:5000 or http://runes): ").strip()
    # config.node_url = "http://" + input("Enter the node URL (e.g., http://127.0.0.1:5000): ").strip()
    # config.miner_address = input("Enter your wallet address: ").strip()
    config.node_url = "http://127.0.0.1:5000"
    config.miner_address = "5E7nTmeDUPKYQN48ymXlvC6FX2E="
    return config

class Transaction:
    def __init__(self, amount, payer, payee):
        self.amount = amount
        self.payer = payer
        self.payee = payee

    def to_dict(self):
        return self.__dict__

    def __str__(self):
        return json.dumps(self.to_dict())

def json_to_transaction(json_string):
    # Parse the JSON string into a dictionary
    data = json.loads(json_string)
    
    # Create a Transaction object using the parsed data
    transaction = Transaction(amount=data['amount'], payer=data['payer'], payee=data['payee'])
    
    return transaction

class Transaction:
    def __init__(self, amount, payer, payee):
        self.amount = amount
        self.payer = payer
        self.payee = payee

    def to_dict(self):
        return self.__dict__

    def __str__(self):
        return json.dumps(self.to_dict())

def json_to_transaction(json_string):
    # Parse the JSON string into a dictionary
    data = json.loads(json_string)
    
    # Create a Transaction object using the parsed data
    transaction = Transaction(amount=data['amount'], payer=data['payer'], payee=data['payee'])
    
    return transaction

# Fetch mining data from the node
def get_mining_data(config):
    response = requests.get(f"{config.node_url}/get-mining-data")
    if response.status_code == 200:
        return response.json()
    else:
        print("Error fetching mining data:", response.json().get("error"))
        return None

# Compute proof-of-work
def proof_of_work(block_data, difficulty):
    nonce = 0
    while True:
        block_data["nonce"] = nonce
        block_string = json.dumps(block_data, sort_keys=True).encode()
        print("client side hash compute bock data", block_string)
        print("client side hash compute bock data", block_string)
        block_hash = hashlib.sha256(block_string).hexdigest()
        if block_hash.startswith("0" * difficulty):
            return nonce, block_hash
        nonce += 1

# Submit mined block
def submit_mined_block(config, block_data):
    response = requests.post(f"{config.node_url}/submit-mined-block", json=block_data)
    if response.status_code == 200:
        print("Block mined and submitted successfully!")
        print("Reward credited to:", block_data["miner_address"])
    else:
        print("Error submitting block:", response.json().get("error"))

# Main mining loop
def start_mining(config):
    print("Starting mining process...")
    while True:
        mining_data = get_mining_data(config)
        if not mining_data:
            time.sleep(10)  # Wait before retrying
            continue

        print("Mining data received. Mining in progress...")
        block_data = {
            "prev_hash": mining_data["prev_hash"],
            "transactions": [json_to_transaction(mining_data["transactions"]).to_dict()],
            "timestamp": mining_data["timestamp"],
            "transactions": [json_to_transaction(mining_data["transactions"]).to_dict()],
            "timestamp": mining_data["timestamp"],
        }
        nonce, block_hash = proof_of_work(block_data, mining_data["difficulty"])

        block_data["nonce"] = nonce
        block_data["miner_address"] = config.miner_address
        block_data["block_hash"] = block_hash  # Include the block hash
        block_data["timestamp"] = mining_data["timestamp"]
        print("submitted mining data", block_data)
        block_data["block_hash"] = block_hash  # Include the block hash
        block_data["timestamp"] = mining_data["timestamp"]
        print("submitted mining data", block_data)
        submit_mined_block(config, block_data)
# Entry point
if __name__ == "__main__":
    miner_config = setup_miner()
    start_mining(miner_config)
