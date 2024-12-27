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
    def __init__(self, prev_hash, transaction, timestamp=None):
        self.prev_hash = prev_hash
        self.transaction = transaction
        self.timestamp = timestamp or time.time()
        self.nonce = 0

    def compute_hash(self):
        block_string = json.dumps({
            "prev_hash": self.prev_hash,
            "transaction": self.transaction.to_dict(),
            "timestamp": self.timestamp,
            "nonce": self.nonce,
        }, sort_keys=True).encode()
        return hashlib.sha256(block_string).hexdigest()


class Blockchain:
    difficulty = 4

    def __init__(self):
        self.chain = []
        self.pending_transactions = []
        self.create_genesis_block()

    def create_genesis_block(self):
        genesis_transaction = Transaction(0, "genesis", "network")
        genesis_block = Block("0", genesis_transaction)
        genesis_block.nonce = self.proof_of_work(genesis_block)
        self.chain.append(genesis_block)

    def proof_of_work(self, block):
        block.nonce = 0
        while not block.compute_hash().startswith("0" * self.difficulty):
            block.nonce += 1
        return block.nonce

    def add_transaction(self, transaction):
        self.pending_transactions.append(transaction)

    def mine_pending_transactions(self, miner_address):
        if not self.pending_transactions:
            return None

        for transaction in self.pending_transactions:
            new_block = Block(self.chain[-1].compute_hash(), transaction)
            new_block.nonce = self.proof_of_work(new_block)
            self.chain.append(new_block)

        self.pending_transactions.clear()
        reward_transaction = Transaction(1, "network", miner_address)
        self.add_transaction(reward_transaction)

    def get_balance(self, wallet_address):
        balance = 0
        for block in self.chain:
            if block.transaction.payer == wallet_address:
                balance -= block.transaction.amount
            if block.transaction.payee == wallet_address:
                balance += block.transaction.amount
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

def create_wallet_with_address(password):
    """Generate a new wallet with an address."""
    address, private_key = generate_wallet_address()
    hashed_password = generate_password_hash(password)  # Hash the provided password
    wallet_data[address] = {
        "balance": 100,
        "private_key": private_key,
        "password": hashed_password  # Store hashed password
    }
    save_wallets(wallet_data)  # Save to persistent storage
    return address


def get_wallet_info(address, password):
    """Retrieve wallet information after verifying the password."""
    wallet = wallet_data.get(address)
    if wallet and check_password_hash(wallet["password"], password):
        return wallet
    else:
        return None


def get_wallet_balance(address, password):
    """Retrieve only the wallet balance after verifying the password."""
    wallet = wallet_data.get(address)
    if wallet and check_password_hash(wallet["password"], password):
        return wallet["balance"]  # Return the balance directly as a float
    else:
        return None  # Return None if the wallet is not found or password is incorrect

def get_wallet_balance_internal(address):
    """Retrieve only the wallet balance after verifying the password."""
    wallet = wallet_data.get(address)
    if wallet:
        return wallet["balance"]  # Return the balance directly as a float
    else:
        return None  # Return None if the wallet is not found or password is incorrect

def update_wallet_balance(address, new_balance, password):
    """Update the balance of a wallet after verifying the password."""
    if address in wallet_data and check_password_hash(wallet_data[address]["password"], password):
        wallet_data[address]["balance"] = new_balance
        save_wallets(wallet_data)  # Save updated wallet data to persistent storage
        return jsonify({"message": "Wallet balance updated successfully"})
    else:
        return jsonify({"error": "Wallet not found or incorrect password"}), 404

def update_wallet_balance_internal(address, new_balance):
    """Update the balance of payee."""
    if address in wallet_data:
        wallet_data[address]["balance"] = new_balance
        save_wallets(wallet_data)  # Save updated wallet data to persistent storage
        return jsonify({"message": "Wallet balance updated successfully"})
    else:
        return jsonify({"error": "Wallet not found"}), 404