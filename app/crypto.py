import hashlib
import json
import time
import os
import base64
from flask import jsonify
from werkzeug.security import generate_password_hash, check_password_hash
wallet_data = {}

def is_transaction_dict(tx):
    """
    Checks if a given dictionary is in the format of a Transaction.
    :param tx: Dictionary to check.
    :return: True if the dictionary has 'amount', 'payer', and 'payee' keys, False otherwise.
    """
    required_keys = {"amount", "payer", "payee"}
    return isinstance(tx, dict) and required_keys.issubset(tx.keys())


def format_transactions(transactions):
    """
    Ensures that transactions are converted to a list of Transaction objects.
    :param transactions: Input transactions, either a list of dictionaries, a single dictionary, or already Transaction objects.
    :return: A list of Transaction objects.
    """
    if isinstance(transactions, list):  # If it's a list, process each element
        formatted = []
        for tx in transactions:
            if isinstance(tx, Transaction):
                formatted.append(tx)
            elif is_transaction_dict(tx):
                formatted.append(Transaction(tx["amount"], tx["payer"], tx["payee"]))
            else:
                raise ValueError(f"Invalid transaction format: {tx}")
        return formatted
    elif is_transaction_dict(transactions):  # If it's a single dictionary
        return [Transaction(transactions["amount"], transactions["payer"], transactions["payee"])]
    elif isinstance(transactions, Transaction):  # If it's already a Transaction object
        return [transactions]
    else:
        raise ValueError(f"Unsupported transaction format: {transactions}")


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
    def __init__(self, prev_hash, transactions, timestamp=None):
        self.prev_hash = prev_hash
        self.transactions = transactions  # List of transactions
        self.timestamp = timestamp
        self.nonce = 0

    def compute_hash(self):
        prev_hash = self.prev_hash if self.prev_hash else ""
        formatted_transactions = format_transactions(self.transactions)  # Ensure correct format
        block_string = json.dumps({
            "prev_hash": prev_hash,
            "transactions": [tx.to_dict() for tx in formatted_transactions],
            "timestamp": self.timestamp,
            "nonce": self.nonce,
        }, sort_keys=True).encode('utf-8')
        print("server side hash compute block data", block_string)
        return hashlib.sha256(block_string).hexdigest()

class Blockchain:
    difficulty = 0

    def __init__(self):
        self.chain = []
        self.pending_transactions = []
        self.pending_miner_rewards = []
        self.create_genesis_block()

    def create_genesis_block(self):
        genesis_transaction = Transaction(100000000000, "genesis", "Rune_Network")
        genesis_block = Block("0", [genesis_transaction], time.time())
        genesis_block.nonce = self.proof_of_work(genesis_block)
        self.chain.append(genesis_block)


    def proof_of_work(self, block):
        block.nonce = 0
        formatted_transactions = format_transactions(block.transactions)  # Ensure correct format
        block.transactions = formatted_transactions  # Replace with formatted transactions
        block_hash = block.compute_hash()
        while not block_hash.startswith("0" * self.difficulty):
            block.nonce += 1
            block_hash = block.compute_hash()
        return block.nonce

    def add_transaction(self, transaction):
        formatted_transaction = format_transactions(transaction)  # Ensure it's a list of Transaction objects
        self.pending_transactions.extend(formatted_transaction)
    def add_miner_rewards(self, transaction):
        formatted_transaction = format_transactions(transaction)  # Ensure it's a list of Transaction objects
        self.pending_miner_rewards.extend(formatted_transaction)

    def mine_pending_miner_rewards(self):
        if not self.pending_miner_rewards:
            return None

        for transaction in self.pending_miner_rewards:
            new_block = Block(self.chain[-1].compute_hash(), transaction)
            new_block.nonce = self.proof_of_work(new_block)
            self.chain.append(new_block)

        self.pending_miner_rewards.clear()
    def get_transaction_info(self):
        """
        Retrieves the first transaction from the pending_transactions list in FIFO order,
        converts it to a JSON string, and removes it from the list.

        :return: JSON string representation of the transaction if available, otherwise None.
        """
        if not self.pending_transactions:
            return None  # Return None if there are no pending transactions
        
        # Get the first transaction
        transaction = self.pending_transactions[0]
        return transaction
    def pop_transaction(self):
        self.pending_transactions.pop(0)
    def get_balance(self, wallet_address):
        """
        Calculates the balance of a given wallet address by iterating through the blockchain.
        :param wallet_address: The wallet address to calculate the balance for.
        :return: The calculated balance as an integer.
        """
        balance = 0

        # Iterate through all blocks in the chain
        for block in self.chain:
            # Ensure transactions are in the correct format
            transactions = format_transactions(block.transactions)
            
            for transaction in transactions:
                if transaction.payer == wallet_address:
                    balance -= transaction.amount
                if transaction.payee == wallet_address:
                    balance += transaction.amount

        return balance
    def reward_miner(self, miner_address):
        reward_transaction = Transaction(1, "Rune_Network", miner_address)
        self.add_miner_rewards(reward_transaction)
        self.mine_pending_miner_rewards()


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

def create_wallet_with_address(password, blockchain=Blockchain):
    """Generate a new wallet with an address."""
    address, private_key = generate_wallet_address()
    hashed_password = generate_password_hash(password)  # Hash the provided password
    wallet_data[address] = {
        "private_key": private_key,
        "password": hashed_password  # Store hashed password
    }
    save_wallets(wallet_data)  # Save to persistent storage
    # blockchain.add_transaction(Transaction(10, "Rune_Network", address))
    send_coin(10, "Rune_Network", address, blockchain)
    return address


def get_wallet_info(address, password):
    """Retrieve wallet information after verifying the password."""
    wallet = wallet_data.get(address)
    if wallet and check_password_hash(wallet["password"], password):
        return wallet
    else:
        return None

def get_wallet_balance(address, password, blockchain=Blockchain):
    """Retrieve only the wallet balance after verifying the password."""
    wallet = wallet_data.get(address)
    if wallet and check_password_hash(wallet["password"], password):
        return blockchain.get_balance(address)  # Return the balance directly as a float
    else:
        return None  # Return None if the wallet is not found or password is incorrect

def does_wallet_exist(address):
    """Retrieve only the wallet balance after verifying the password."""
    wallet = wallet_data.get(address)
    if wallet:
        return True # Return the balance directly as a float
    else:
        return None  # Return None if the wallet is not found or password is incorrect

def send_coin(amount, payer, payee, blockchain=Blockchain):
    transaction = Transaction(amount, payer, payee)
    blockchain.add_transaction(transaction)


# def update_wallet_balance(address, new_balance, password):
#     """Update the balance of a wallet after verifying the password."""
#     if address in wallet_data and check_password_hash(wallet_data[address]["password"], password):
#         wallet_data[address]["balance"] = new_balance
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