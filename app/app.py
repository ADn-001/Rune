from flask import Flask, render_template, request, jsonify
from crypto import Blockchain, create_wallet_with_address, get_wallet_balance, get_wallet_balance_internal, send_money, Block
import hashlib
import json
app = Flask(__name__)


# Instantiate Blockchain
blockchain = Blockchain()

@app.route("/")
def home():
    return render_template("index.html")


@app.route("/wallet", methods=["POST"])
def create_wallet_route():
    """API route to create a new wallet."""
    password = request.json.get("password")
    if not password:
        return jsonify({"error": "Password is required"}), 400

    address = create_wallet_with_address(password, blockchain)
    if address:
        return jsonify({"message": "Wallet created successfully!", "address": address}), 201
    else:
        return jsonify({"error": "Failed to create wallet"}), 500

@app.route("/wallet/<address>", methods=["POST"])
def get_wallet_info_route(address):
    """API route to retrieve wallet information."""
    password = request.json.get("password")
    wallet = get_wallet_balance(address, password)
    if wallet:
        return jsonify({"address": address, "balance": wallet["balance"]})
    else:
        return jsonify({"error": "Invalid address or password"}), 404

@app.route("/wallet/balance", methods=["POST"])
def get_balance():
    address = request.json.get("address")
    password = request.json.get("password")
    balance = get_wallet_balance(address, password, blockchain)
    if balance is not None:
        return jsonify({"address": address, "balance": balance})
    else:
        return jsonify({"error": "Invalid address or password"}), 404


@app.route("/transaction", methods=["POST"])
def create_transaction():
    payer = request.json.get("payer")
    payee = request.json.get("payee")
    amount = float(request.json.get("amount"))
    password = request.json.get("password")

    payer_balance = blockchain.get_balance(payer)
    if payer_balance is None or payer_balance < amount:
        return jsonify({"error": "Insufficient balance or invalid password"}), 400

    if get_wallet_balance_internal(payee) is None:  # Password not required for payee check
        return jsonify({"error": "Payee wallet not found"}), 404

    # Update wallet balances
    send_money(payer, payee, amount, password, blockchain)

    return jsonify({"message": "Transaction added to pending transactions"})


# @app.route("/mine", methods=["GET"])
# def mine():
#     miner_address = request.args.get("miner")
#     blockchain.mine_pending_transactions(miner_address)
#     return jsonify({"message": "Block mined successfully!", "miner": miner_address})

@app.route("/get-mining-data", methods=["GET"])
def get_mining_data():
    """API route to provide miners with the latest block data, difficulty, and pending transactions."""
    if not blockchain.pending_transactions:
        return jsonify({"error": "No pending transactions to mine"}), 400

    latest_block = blockchain.chain[-1]
    mining_data = {
        "prev_hash": latest_block.compute_hash(),
        "transactions":[transaction.to_dict() for transaction in blockchain.pending_transactions] ,  # Single transaction
        "difficulty": blockchain.difficulty
    }
    return jsonify(mining_data), 200


@app.route("/submit-mined-block", methods=["POST"])
def submit_mined_block():
    data = request.json
    # print("Received block data:", data)  # Debugging line to check received block data

    required_fields = ["prev_hash", "transactions", "nonce", "miner_address", "block_hash"]
    if not all(field in data for field in required_fields):
        return jsonify({"error": "Incomplete block data"}), 400

    prev_hash = data["prev_hash"]
    transactions = data["transactions"][0]
    nonce = data["nonce"]
    miner_address = data["miner_address"]
    block_hash = data["block_hash"]

    # Debugging: Print transaction data to inspect the format
    # print("Transactions data:", transactions)  # Debugging print for transaction data

    # Reconstruct the block for validation
    try:
        new_block = Block(prev_hash, transactions)  # Single transaction
    except Exception as e:
        return jsonify({"error": f"Invalid transaction data: {str(e)}"}), 400

    new_block.nonce = nonce
    print("rebult block data:", new_block)
    # Debugging: print block data and recalculated hash
    recalculated_hash = new_block.compute_hash()
    print("Recalculated hash:", recalculated_hash)  # Debugging line to check hash
    print("Block hash being submitted:", block_hash)  # Debugging line to check submitted hash

    # # Ensure consistency in the way data is serialized for hash calculation
    # serialized_data = json.dumps({
    #     "prev_hash": new_block.prev_hash,
    #     "transactions": new_block.transactions,
    #     "nonce": new_block.nonce
    # }).encode()
    # print("rebult block data:", serialized_data)
    # # Ensure that the recalculated hash is consistent
    # recalculated_hash = hashlib.md5(serialized_data).hexdigest()
    # print("Recalculated hash (after serialization fix):", recalculated_hash)

    if recalculated_hash != block_hash:
        return jsonify({"error": "Block hash does not match the recalculated hash"}), 400

    # Check proof of work and chain validity
    if not recalculated_hash.startswith("0" * blockchain.difficulty):
        return jsonify({"error": "Invalid proof of work"}), 400
    if prev_hash != blockchain.chain[-1].compute_hash():
        return jsonify({"error": "Previous hash does not match the last block in the chain"}), 400

    # Add the block to the blockchain
    blockchain.chain.append(new_block)
    print("mining sucessful")

    # Reward the miner
    # blockchain.add_transaction(Transaction(1, "network", miner_address))
    blockchain.pop_transaction()
    # Reward the miner
    return jsonify({"message": "Block added successfully!", "miner_rewarded": miner_address}), 200



if __name__ == '__main__':
    app.run(debug=True)
