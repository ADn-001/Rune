from flask import Flask, render_template, request, jsonify
from crypto import Blockchain, Transaction, create_wallet_with_address, get_wallet_info, get_wallet_balance, update_wallet_balance, get_wallet_balance_internal, update_wallet_balance_internal
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


@app.route("/mine", methods=["GET"])
def mine():
    miner_address = request.args.get("miner")
    blockchain.mine_pending_transactions(miner_address)
    return jsonify({"message": "Block mined successfully!", "miner": miner_address})

if __name__ == '__main__':
    app.run(debug=True)
