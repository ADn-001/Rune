from flask import Flask, render_template, request, jsonify
from crypto import Blockchain, Transaction, create_wallet_with_address, get_wallet_info, get_wallet_balance, update_wallet_balance
app = Flask(__name__)


# Instantiate Blockchain
blockchain = Blockchain()

@app.route("/")
def home():
    return render_template("index.html")


@app.route("/wallet", methods=["POST"])
def create_wallet_route():
    """API route to create a new wallet."""
    address = create_wallet_with_address()
    if address:
        return jsonify({"message": "Wallet created successfully!", "address": address}), 201
    else:
        return jsonify({"error": "Failed to create wallet"}), 500

@app.route("/wallet/<address>", methods=["GET"])
def get_wallet_info_route(address):
    """API route to retrieve wallet information."""
    wallet = get_wallet_info(address)
    if wallet:
        return jsonify({"address": address, "balance": wallet["balance"]})
    else:
        return jsonify({"error": "Wallet not found"}), 404


@app.route("/wallet/balance", methods=["GET"])
def get_balance():
    address = request.args.get("address")
    balance = get_wallet_balance(address)
    if balance is not None:
        return jsonify({"address": address, "balance": balance})
    else:
        return jsonify({"error": "Wallet not found"}), 404


@app.route("/transaction", methods=["POST"])
def create_transaction():
    payer = request.json.get("payer")
    payee = request.json.get("payee")
    amount = float(request.json.get("amount"))

    payer_balance = get_wallet_balance(payer)
    if payer_balance is None or payer_balance < amount:
        return jsonify({"error": "Insufficient balance"}), 400

    if get_wallet_balance(payee) is None:
        return jsonify({"error": "Payee wallet not found"}), 404

    # Update wallet balances
    update_wallet_balance(payer, payer_balance - amount)
    update_wallet_balance(payee, get_wallet_balance(payee) + amount)

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
