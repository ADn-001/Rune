// Wallet Section Functions
function showWalletSection() {
    document.getElementById('welcome-section').style.display = 'none';
    document.getElementById('wallet-section').style.display = 'block';
    document.getElementById('transaction-section').style.display = 'block'; // Show the transaction section
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

async function createWallet() {
    const response = await fetch("/wallet", { method: "POST" });
    const data = await response.json();

    if (response.ok) {
        alert(`Wallet created successfully! Address: ${data.address}`);
        document.getElementById("wallet-input").value = data.address;
        showWalletSection();
    } else {
        alert(data.error || "Failed to create wallet");
    }
}

async function getWalletBalance() {
    const walletAddress = document.getElementById('wallet-input').value;

    if (!walletAddress) {
        alert("Please enter a valid wallet address!");
        return;
    }

    const response = await fetch(`/wallet/${walletAddress}`);
    const data = await response.json();

    if (response.ok) {
        document.getElementById('wallet-info').innerHTML = `Wallet Balance: ${data.balance}`;
    } else {
        document.getElementById('wallet-info').innerHTML = 'Invalid wallet address!';
    }
}

async function sendCoins() {
    const payerAddress = document.getElementById('payer-wallet-input').value;
    const payeeAddress = document.getElementById('payee-wallet-input').value;
    const amount = parseFloat(document.getElementById('amount-input').value);

    if (!payerAddress || !payeeAddress || isNaN(amount) || amount <= 0) {
        alert("Please fill in valid payer, payee, and amount fields.");
        return;
    }

    try {
        const response = await fetch('/transaction', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ payer: payerAddress, payee: payeeAddress, amount: amount })
        });

        const data = await response.json();

        if (response.ok) {
            alert("Transaction successful: " + data.message);
            getWalletBalance();
        } else {
            alert("Transaction failed: " + (data.error || "Unknown error"));
        }
    } catch (error) {
        alert("An error occurred: " + error.message);
    }
}

// ALEX WORK: Scroll and Navigation
window.addEventListener('scroll', () => {
    const sections = document.querySelectorAll('section');
    const navLinks = document.querySelectorAll('.navbar a');

    sections.forEach(section => {
        const rect = section.getBoundingClientRect();
        if (rect.top >= 0 && rect.top < window.innerHeight / 2) {
            navLinks.forEach(link => link.classList.remove('active'));
            document.querySelector(`.navbar a[href="#${section.id}"]`).classList.add('active');
        }
    });
});

function scrollToSection(sectionId) {
    const section = document.getElementById(sectionId);

    if (section) {
        section.style.display = 'block';
        section.scrollIntoView({ behavior: 'smooth' });
    }
}

document.querySelectorAll('nav a').forEach(link => {
    link.addEventListener('click', (event) => {
        event.preventDefault();
        const targetId = link.getAttribute('href').substring(1);
        scrollToSection(targetId);
    });
});

// Event listeners for wallet actions
document.getElementById("sendCoinsBtn").addEventListener("click", sendCoins);
document.getElementById("createWalletBtn").addEventListener("click", createWallet);
document.getElementById("checkWalletBtn").addEventListener("click", getWalletBalance);
