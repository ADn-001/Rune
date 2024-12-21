// Wallet Section Functions
function showWalletSection() {
    const walletSection = document.getElementById('wallet-section');
    const transactionSection = document.getElementById('transaction-section');
    const miningSection = document.getElementById('mining-section');

    walletSection.classList.remove('hidden');
    walletSection.classList.add('visible');
    transactionSection.classList.remove('hidden');
    transactionSection.classList.add('visible');
    miningSection.classList.remove('hidden');
    miningSection.classList.add('visible');
    walletSection.scrollIntoView({ behavior: 'smooth' });
}

// Function to create a wallet
async function createWallet() {
    const response = await fetch("/wallet", { method: "POST" });
    const data = await response.json();

    if (response.ok) {
        const walletOutput = document.getElementById("created-wallet-output");
        walletOutput.innerHTML = `Wallet created successfully! Address: ${data.address}`;
        document.getElementById("wallet-input").value = data.address;

        // Show success animation for wallet creation
        showWalletCreatedSuccess();
        showWalletSection();
    } else {
        alert(data.error || "Failed to create wallet");
    }
}

// Function to check wallet balance
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

// Function to send coins
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
            // Show transaction success animation
            showTransactionSuccess();

            // Update wallet balance
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
    const successMessage = document.createElement('div');
    successMessage.classList.add('success-message');
    successMessage.innerHTML = "Wallet Created Successfully!";
    
    const walletSection = document.getElementById('wallet-section');
    walletSection.appendChild(successMessage);

    // Add animation for success message
    setTimeout(() => {
        successMessage.classList.add('success-message-visible');
    }, 100);

    // Remove message after animation
    setTimeout(() => {
        successMessage.classList.remove('success-message-visible');
        setTimeout(() => {
            successMessage.remove();
        }, 300); // Wait for animation to finish before removing
    }, 3000);
}

// Function to show transaction success message with animation
function showTransactionSuccess() {
    const successMessage = document.createElement('div');
    successMessage.classList.add('success-message');
    successMessage.innerHTML = "Transaction Successful!";
    
    const transactionSection = document.getElementById('transaction-section');
    transactionSection.appendChild(successMessage);

    // Add animation for success message
    setTimeout(() => {
        successMessage.classList.add('success-message-visible');
    }, 100);

    // Remove message after animation
    setTimeout(() => {
        successMessage.classList.remove('success-message-visible');
        setTimeout(() => {
            successMessage.remove();
        }, 300); // Wait for animation to finish before removing
    }, 3000);
}

// Scroll and navigation for sections
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
