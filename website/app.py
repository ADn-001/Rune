from flask import Flask, render_template, request, jsonify

app = Flask(__name__)

# Placeholder wallet and blockchain data
wallets = {"sample_wallet": 100}
transactions = []

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/check_wallet', methods=['POST'])
def check_wallet():
    wallet = request.json.get('wallet')
    if wallet in wallets:
        return jsonify({"valid": True, "balance": wallets[wallet]})
    return jsonify({"valid": False})

@app.route('/send_money', methods=['POST'])
def send_money():
    sender = request.json.get('sender')
    recipient = request.json.get('recipient')
    amount = request.json.get('amount')

    if sender not in wallets or recipient not in wallets:
        return jsonify({"success": False, "error": "Invalid wallet address"})
    if wallets[sender] < amount:
        return jsonify({"success": False, "error": "Insufficient balance"})

    wallets[sender] -= amount
    wallets[recipient] += amount
    transactions.append({"sender": sender, "recipient": recipient, "amount": amount})
    return jsonify({"success": True, "message": "Transaction successful!"})

if __name__ == '__main__':
    app.run(debug=True)
