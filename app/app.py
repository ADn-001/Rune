from flask import Flask, render_template, request, jsonify
from crypto import Blockchain, Transaction, create_wallet_with_address, get_wallet_info, get_wallet_balance, update_wallet_balance, get_wallet_balance_internal, update_wallet_balance_internal, Block
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

    address = create_wallet_with_address(password)
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
    balance = get_wallet_balance(address, password)
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

    payer_balance = get_wallet_balance(payer, password)
    if payer_balance is None or payer_balance < amount:
        return jsonify({"error": "Insufficient balance or invalid password"}), 400

    if get_wallet_balance_internal(payee) is None:  # Password not required for payee check
        return jsonify({"error": "Payee wallet not found"}), 404

    # Update wallet balances
    update_wallet_balance(payer, payer_balance - amount, password)
    update_wallet_balance_internal(payee, get_wallet_balance_internal(payee) + amount)

    # Add transaction to blockchain
    transaction = Transaction(amount, payer, payee)
    blockchain.add_transaction(transaction)

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
        "transactions": [t.to_dict() for t in blockchain.pending_transactions],
        "difficulty": blockchain.difficulty
    }
    return jsonify(mining_data), 200


@app.route("/submit-mined-block", methods=["POST"])
def submit_mined_block():
    """API route to accept a mined block, validate it, and add it to the blockchain."""
    data = request.json

    # Validate incoming data structure
    required_fields = ["prev_hash", "transactions", "nonce", "miner_address", "block_hash"]
    if not all(field in data for field in required_fields):
        return jsonify({"error": "Incomplete block data"}), 400

    prev_hash = data["prev_hash"]
    transactions = data["transactions"]
    nonce = data["nonce"]
    miner_address = data["miner_address"]
    block_hash = data["block_hash"]

    # Reconstruct the block for validation
    try:
        new_block = Block(prev_hash, [Transaction(**tx) for tx in transactions])
    except Exception as e:
        return jsonify({"error": f"Invalid transaction data: {str(e)}"}), 400

    new_block.nonce = nonce

    # Recalculate hash for validation
    recalculated_hash = new_block.compute_hash()
    if recalculated_hash != block_hash:
        return jsonify({"error": "Block hash does not match the recalculated hash"}), 400

    # Check proof of work and chain validity
    if not recalculated_hash.startswith("0" * blockchain.difficulty):
        return jsonify({"error": "Invalid proof of work"}), 400
    if prev_hash != blockchain.chain[-1].compute_hash():
        return jsonify({"error": "Previous hash does not match the last block in the chain"}), 400

    # Add the block to the blockchain
    blockchain.chain.append(new_block)

    # Reward the miner
    blockchain.add_transaction(Transaction(1, "network", miner_address))

    return jsonify({"message": "Block added successfully!", "miner_rewarded": miner_address}), 200

if __name__ == '__main__':
    app.run(debug=True)
