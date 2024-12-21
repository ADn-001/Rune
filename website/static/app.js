function showWalletSection() {
    document.getElementById('welcome-section').style.display = 'none';
    document.getElementById('wallet-section').style.display = 'block';
}

function checkWallet() {
    const walletAddress = document.getElementById('wallet-input').value;

    fetch('/check_wallet', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ wallet: walletAddress })
    })
    .then(response => response.json())
    .then(data => {
        if (data.valid) {
            document.getElementById('wallet-info').innerHTML = `Wallet Balance: ${data.balance}`;
        } else {
            document.getElementById('wallet-info').innerHTML = 'Invalid wallet address!';
        }
    });
}
