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
    #config.node_url = input("Enter the node URL (e.g., http://127.0.0.1:5000): ").strip()
    # config.node_url = "http://" + input("Enter the node URL (e.g., http://127.0.0.1:5000): ").strip()
    # config.miner_address = input("Enter your wallet address: ").strip()
    config.node_url = "http://127.0.0.1:5000"
    config.miner_address = "xqSEd5IkBJyYUSAN9kjPIaSmhCY"
    return config

# Fetch mining data from the node
def get_mining_data(config):
    response = requests.get(f"{config.node_url}/get-mining-data")
    if response.status_code == 200:
        return response.json()
    else:
        print("Error fetching mining data:", response.json().get("error"))
        return None

def proof_of_work(difficulty, block):
    # Start with a nonce of 0
    return_list = []
    def compute_hash(block_data):
        block_string = json.dumps({
            "prev_hash": block_data["prev_hash"],
            "transactions":block_data["transactions"],  # Now iterating over a list
            "nonce": block_data["nonce"],
        }, sort_keys=True).encode()
        print("block data info yada yada:", block_string)
        return hashlib.md5(block_string).hexdigest()  # Weaken hash function
    nonce = 0
    while True:
        block["nonce"] = nonce  # Assign current nonce value to the block
        block_hash = compute_hash(block)  # Compute the hash of the block

        print(f"Nonce: {nonce}, Block hash: {block_hash}")  # Debugging print
        if block_hash.startswith('0' * difficulty):  # Check if hash meets the difficulty
            
            
            return nonce, block_hash
        nonce += 1  # Increment the nonce if the hash doesn't meet the difficulty


# def proof_of_work(difficulty, block):
#         nonce = 0
#         while True:
#             hash_attempt = hashlib.md5((str(block["nonce"]) + block.compute_hash()).encode()).hexdigest()
#             if hash_attempt.startswith("0" * difficulty):  # Simple proof of work
#                 return nonce, hash_attempt
#             nonce += 1

def submit_mined_block(config, block_data):
    print("Submitting block data:", block_data)  # Debugging line to check block data
    response = requests.post(f"{config.node_url}/submit-mined-block", json=block_data)
    if response.status_code == 200:
        print("Block mined and submitted successfully!")
        print("Reward credited to:", block_data["miner_address"])
    else:
        print("Error submitting block:", response.json().get("error"))

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
            "transactions": mining_data["transactions"],  # Single transaction now
        }

        # print("Block data before mining:", block_data)  # Debugging print to check block data
        # return_List = []
        # Mine the block
        nonce, block_hash = proof_of_work(mining_data["difficulty"], block_data)
        block_data["nonce"] = nonce
        block_data["block_hash"] = block_hash  # Include the block hash
        block_data["miner_address"] = config.miner_address
        # Log nonce and hash
        print(f"Nonce found: {nonce}")
        print(f"Block hash after mining: {block_hash}")
        print("block data:", block_data)
        print("Block data after mining:", block_data)  # Debugging print to check block data after mining
        submit_mined_block(config, block_data)

# Entry point
if __name__ == "__main__":
    miner_config = setup_miner()
    start_mining(miner_config)
