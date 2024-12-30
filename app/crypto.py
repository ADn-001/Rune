import hashlib
import json
import time
import os
import base64
from flask import jsonify
from werkzeug.security import generate_password_hash, check_password_hash
wallet_data = {}
class Transaction:
    def __init__(self, amount, payer, payee):
        self.amount = amount
        self.payer = payer
        self.payee = payee

    def to_dict(self):
        return self.__dict__

    def __str__(self):
        return json.dumps(self.to_dict())


class Block:
    def __init__(self, prev_hash, transactions):
        self.prev_hash = prev_hash
        self.transactions = [tx.to_dict() for tx in transactions] # Ensure it's a list, even for a single transaction
        self.nonce = 0  # Simplified nonce

    def compute_hash(self):
        # Ensure transactions are in dictionary format
        # transactions = (
        #     [transaction.to_dict() for transaction in self.transactions]
        #     if hasattr(self.transactions[0], "to_dict")  # Check if to_dict exists
        #     else self.transactions  # Assume they are already dictionaries
        # )

        # # Prepare the block data
        # block_data = {
        #     "prev_hash": self.prev_hash,
        #     "transactions": transactions,
        #     "nonce": self.nonce,
        # }
        prev_hash = self.prev_hash if self.prev_hash else ""
        block_data = json.dumps({
            "prev_hash": prev_hash,
            "transactions": self.transactions,
            "nonce": self.nonce,
        }, sort_keys=True).encode('utf-8')
        # Serialize block data to a JSON string
        block_string = json.dumps(block_data, sort_keys=True).encode()
        print("block data going through compute_hash:", block_string)
        # Compute and return the hash
        return hashlib.md5(block_string).hexdigest()



class Blockchain:
    difficulty = 2  # Reduced difficulty for mining
    def __init__(self):
        self.chain = []
        self.pending_transactions = []
        self.create_genesis_block()

    def create_genesis_block(self):
        total_coin = 1000000000
        genesis_transaction = Transaction(total_coin, "genesis", "rune_network")
        genesis_block = Block("0", genesis_transaction)
        genesis_block.nonce = self.proof_of_work(genesis_block)
        self.chain.append(genesis_block)

    def proof_of_work(self, block):
        block.nonce = 0
        while True:
            hash_attempt = hashlib.md5((str(block.nonce) + block.compute_hash()).encode()).hexdigest()
            if hash_attempt.startswith("0" * self.difficulty):  # Simple proof of work
                return block.nonce, hash_attempt
            block.nonce += 1

    def add_transaction(self, transaction):
        self.pending_transactions.append(transaction)
    def pop_transaction(self):
        self.pending_transactions.pop(0)
    # def add_transaction(self, transaction):
    #     self.pending_transactions.append(transaction)

    # def mine_pending_transactions(self):
    #     if not self.pending_transactions:
    #         return None

    #     for transaction in self.pending_transactions:
    #         new_block = Block(self.chain[-1].compute_hash(), transaction)
    #         new_block.nonce = self.proof_of_work(new_block)
    #         self.chain.append(new_block)

    #     self.pending_transactions.clear()

    def get_balance(self, wallet_address):
        balance = 0 
        for block in self.chain:
            if block.transactions[0].payer == wallet_address:
                balance -= block.transactions[0].amount
            if block.transactions[0].payee == wallet_address:
                balance += block.transactions[0].amount
        return balance

# Persistent storage file for wallets
WALLET_STORAGE_FILE = "wallets.json"

# Load wallets from persistent storage
def load_wallets():
    if os.path.exists(WALLET_STORAGE_FILE):
        with open(WALLET_STORAGE_FILE, "r") as file:
            return json.load(file)
    return {}

# Save wallets to persistent storage
def save_wallets(wallet_data):
    with open(WALLET_STORAGE_FILE, "w") as file:
        json.dump(wallet_data, file, indent=4)

# Initialize wallet data
wallet_data = load_wallets()

def generate_wallet_address():
    """Generate a new wallet address using public key cryptography."""
    # Generate a random 256-bit private key
    private_key = os.urandom(32)

    # Derive a public key from the private key
    public_key = hashlib.sha256(private_key).digest()

    # Generate wallet address by hashing the public key
    wallet_hash = hashlib.new('ripemd160', public_key).digest()

    # Encode the hash in base58 for readability
    wallet_address = base64.b64encode(wallet_hash).decode('utf-8')
    
    return wallet_address, private_key.hex()

def create_wallet_with_address(password, blockchain):
    """Generate a new wallet with an address."""
    address, private_key = generate_wallet_address()
    hashed_password = generate_password_hash(password)  # Hash the provided password
    wallet_data[address] = {
        "private_key": private_key,
        "password": hashed_password  # Store hashed password
    }
    save_wallets(wallet_data)  # Save to persistent storage
    if(blockchain.get_balance("rune_network") > 100):
        transaction = Transaction(10, "rune_network", address)
        blockchain.add_transaction(transaction)
    return address


def get_wallet_info(address, password):
    """Retrieve wallet information after verifying the password."""
    wallet = wallet_data.get(address)
    if wallet and check_password_hash(wallet["password"], password):
        return wallet
    else:
        return None


def get_wallet_balance(address, password, blockchain):
    """Retrieve only the wallet balance after verifying the password."""
    wallet = wallet_data.get(address)
    if wallet and check_password_hash(wallet["password"], password):
        return blockchain.get_balance(address)  # Return the balance directly as a float
    else:
        return None  # Return None if the wallet is not found or password is incorrect

def get_wallet_balance_internal(address, blockchain):
    """Retrieve only the wallet balance after verifying the password."""
    wallet = wallet_data.get(address)
    if wallet:
        return blockchain.get_balance(address)  # Return the balance directly as a float
    else:
        return None  # Return None if the wallet is not found or password is incorrect

def send_money(payer_address, payee_address, amount, password, blockchain):
    """
    Facilitate sending money between wallets by creating and verifying a transaction.
    
    :param payer_address: The wallet address of the sender.
    :param payee_address: The wallet address of the recipient.
    :param amount: The amount to transfer.
    :param password: Password for the payer's wallet.
    :param blockchain: The instance of the blockchain to interact with.
    :return: A dictionary containing the result of the transaction.
    """
    # Verify payer's wallet exists and password is correct
    payer_wallet = get_wallet_info(payer_address, password)
    if not payer_wallet:
        return {"success": False, "message": "Invalid wallet address or password for payer."}

    # Verify payee's wallet exists
    if payee_address not in wallet_data:
        return {"success": False, "message": "Payee wallet address does not exist."}

    # Check payer's balance
    payer_balance = blockchain.get_balance(payer_address)
    if payer_balance < amount:
        return {"success": False, "message": "Insufficient funds in payer's wallet."}

    # Create and add the transaction
    transaction = Transaction(amount, payer_address, payee_address)
    blockchain.add_transaction(transaction)
    
    return {"success": True, "message": "Transaction added successfully.", "transaction": transaction.to_dict()}

def reward_miner(miner_address, blockchain):
    if(blockchain.get_balance("rune_network") > 10):
        transaction = Transaction(10, "rune_network", miner_address)
        blockchain.add_transaction(transaction)

# def sendMoney(payer, payee, new_balance, password):
#     """Update the balance of a wallet after verifying the password."""
#     if payee in wallet_data and check_password_hash(wallet_data[payee]["password"], password):
#         Blockchain.add_transaction(Transaction(new_balance, payee))
#         save_wallets(wallet_data)  # Save updated wallet data to persistent storage
#         return jsonify({"message": "Wallet balance updated successfully"})
#     else:
#         return jsonify({"error": "Wallet not found or incorrect password"}), 404

# def update_wallet_balance_internal(address, new_balance):
#     """Update the balance of payee."""
#     if address in wallet_data:
#         wallet_data[address]["balance"] = new_balance
#         save_wallets(wallet_data)  # Save updated wallet data to persistent storage
#         return jsonify({"message": "Wallet balance updated successfully"})
#     else:
#         return jsonify({"error": "Wallet not found"}), 404