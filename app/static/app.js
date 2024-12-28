// Original function: Show wallet section
function showWalletSection() {
    document.getElementById('wallet-section').classList.remove('hidden');
    document.getElementById('wallet-section').classList.add('visible');
    document.getElementById('transaction-section').classList.remove('hidden');
    document.getElementById('transaction-section').classList.add('visible');
    document.getElementById('mining-section').classList.remove('hidden');
    document.getElementById('mining-section').classList.add('visible');
    document.getElementById('wallet-section').scrollIntoView({ behavior: 'smooth' });
    const navbar = document.getElementById('navbar');
    navbar.style.display = 'flex';
}

// Original function: Create a wallet
// Modified function: Create a wallet
async function createWallet() {
    const password = document.getElementById("wallet-password-input-create").value;


    if (!password) {
        alert("Password is required to create a wallet.");
        return;
    }

    const response = await fetch("/wallet", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ password })
    });
    const data = await response.json();

    if (response.ok) {
        const walletOutput = document.getElementById("created-wallet-output");
        walletOutput.innerHTML = `Wallet created successfully! Address: ${data.address}`;
        document.getElementById("wallet-input").value = data.address;

        showWalletCreatedSuccess();
        showWalletSection();
    } else {
        alert(data.error || "Failed to create wallet");
    }
}


// Original function: Check wallet balance
// Modified function: Check wallet balance
async function getWalletBalance() {
    const walletAddress = document.getElementById('wallet-input').value;

    if (!walletAddress) {
        alert("Please enter a valid wallet address!");
        return;
    }

    const password = document.getElementById("wallet-password-input-check").value;
    if (!password) {
        alert("Password is required to check wallet balance.");
        return;
    }

    const response = await fetch(`/wallet/balance`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ address: walletAddress, password: password })
    });
    const data = await response.json();

    if (response.ok) {
        document.getElementById('wallet-info').innerHTML = `Wallet Balance: ${data.balance}`;
    } else {
        alert(data.error || "Failed to retrieve wallet balance.");
    }
}


async function sendCoins() {
    const payerAddress = document.getElementById('payer-wallet-input').value;
    const payeeAddress = document.getElementById('payee-wallet-input').value;
    const amount = parseFloat(document.getElementById('amount-input').value);
    const password = document.getElementById('wallet-password-input-send').value;

    if (!payerAddress || !payeeAddress || isNaN(amount) || amount <= 0 || !password) {
        alert("Please fill in valid payer, payee, amount fields, and password.");
        return;
    }

    try {
        const response = await fetch('/transaction', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ payer: payerAddress, payee: payeeAddress, amount, password })
        });

        const data = await response.json();

        if (response.ok) {
            // Show transaction success animation
            showTransactionSuccess();
            // Optionally update the wallet balance after sending coins
            getWalletBalance();
        } else {
            document.getElementById("transaction-info").innerHTML =
                `Transaction failed: ${data.error || "Unknown error"}`;
        }
    } catch (error) {
        document.getElementById("transaction-info").innerHTML =
            `An error occurred: ${error.message}`;
    }
}

// Function to show wallet creation success message with animation
function showWalletCreatedSuccess() {
    showSuccessMessage("Wallet Created Successfully!", 'wallet-section');
}

// Function to show transaction success message with animation
function showTransactionSuccess() {
    showSuccessMessage("Transaction Successful!", 'transaction-section');
}

// Utility function to show any success message
function showSuccessMessage(message, parentElementId) {
    const parentElement = document.getElementById(parentElementId);

    // Prevent duplicate messages
    const existingMessage = parentElement.querySelector('.success-message');
    if (existingMessage) existingMessage.remove();

    const successMessage = document.createElement('div');
    successMessage.classList.add('success-message');
    successMessage.innerHTML = message;

    parentElement.appendChild(successMessage);

    // Display and animate success message
    setTimeout(() => {
        successMessage.style.display = 'flex';
        successMessage.classList.add('success-message-visible');
    }, 100);

    // Remove the message after 3 seconds
    setTimeout(() => {
        successMessage.classList.remove('success-message-visible');
        setTimeout(() => successMessage.remove(), 300); // Wait for animation
    }, 3000);
}

// Event listeners for buttons
document.getElementById("sendCoinsBtn").addEventListener("click", sendCoins);
document.getElementById("createWalletBtn").addEventListener("click", createWallet);
document.getElementById("checkWalletBtn").addEventListener("click", getWalletBalance);
document.querySelectorAll('.navbar a').forEach(anchor => {
    anchor.addEventListener('click', function (e) {
        e.preventDefault();
        const targetSection = document.querySelector(this.getAttribute('href'));
        targetSection.scrollIntoView({ behavior: 'smooth', block: 'start' });
    });
});

const navbar = document.getElementById('navbar');
const walletSection = document.getElementById("wallet-section");

window.addEventListener('scroll', () => {
    const walletSectionTop = walletSection.offsetTop;

    if (window.scrollY >= walletSectionTop + 100) {
        navbar.style.display = 'flex'; // Show the navbar
    } else {
        navbar.style.display = 'none'; // Hide the navbar
    }
});

// Hide the navbar initially
navbar.style.display = 'none';

