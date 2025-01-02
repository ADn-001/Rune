
async function fetchAboutUs(){
    try {
        const response = await fetch('/about', {
            method: 'GET',
            headers: {
                'Content-Type': 'application/json'
            }
        });

        if (response.ok) {
            const data = await response.text();
            document.getElementById('content').innerHTML = data;
        } else {
            console.error('Failed to fetch the About Us page:', response.status, response.statusText);
        }
    } catch (error) {
        console.error('Error fetching the About Us page:', error);
    }
}

function aboutUs(event) {
    event.preventDefault(); // Prevent the default link behavior
    fetchAboutUs(); // Call the function to fetch the "About Us" page
}

async function home(){
    try {
        const response = await fetch('/', {
            method: 'GET',
            headers: {
                'Content-Type': 'application/json'
            }
        });

        if (response.ok) {
            const data = await response.text();
            document.getElementById('content').innerHTML = data;
        } else {
            console.error('Failed to fetch the About Us page:', response.status, response.statusText);
        }
    } catch (error) {
        console.error('Error fetching the About Us page:', error);
    }
}

// Original function: Show wallet section
function showWalletSection() {
    document.getElementById('wallet-section').classList.remove('hidden');
    document.getElementById('wallet-section').classList.add('visible');
    document.getElementById('transaction-section').classList.remove('hidden');
    document.getElementById('transaction-section').classList.add('visible');
    document.getElementById('mining-section').classList.remove('hidden');
    document.getElementById('mining-section').classList.add('visible');
    const targetSection = document.getElementById('wallet-section')
        const offset = 200; // Adjust this value to set how much higher the scroll should stop
        const topPosition = targetSection.getBoundingClientRect().top + window.scrollY - offset;

        window.scrollTo({ 
            top: topPosition, 
            behavior: 'smooth' 
        });
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
        showWalletCreatedSuccess();
        showCheckWalletForm();
        //const walletOutput = document.getElementById("created-wallet-output");
        // walletOutput.innerHTML = `Wallet created successfully! Address: ${data.address}`;
        document.getElementById("wallet-input").value = data.address;
        document.getElementById("wallet-password-input-check").value = password;
        const wallet_title = document.getElementById("wallet-title");
        wallet_title.style.display = 'block';
        document.getElementById('wallet-info').classList.remove('hidden');
        document.getElementById('wallet-Address').innerHTML = `Address: ${data.address}`;
        document.getElementById('wallet-info').innerHTML = `${10}`;
        toggleForm('none', 'wallet-input-form')
        
    } else {
        alert(data.error || "Failed to create wallet");
    }
}

function showCreateWalletForm() {
    toggleForm('none', 'wallet-input-form');
    toggleForm('block', 'wallet-create-form');
} 

function showCheckWalletForm() {
    toggleForm('none', 'wallet-create-form');
    toggleForm('block', 'wallet-input-form');
} 

// Original function: Check wallet balance
// Modified function: Check wallet balance
async function getWalletBalance() {
    showCheckWalletForm();
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
        const wallet_title = document.getElementById("wallet-title");
        wallet_title.style.display = 'block';
        //document.getElementById('wallet-info').classList.remove('hidden');
        document.getElementById('wallet-Address').innerHTML = `Address: ${walletAddress}`;
        document.getElementById('wallet-info').innerHTML = `${data.balance} R`;
        toggleForm('none', 'wallet-input-form')
    } else {
        document.getElementById('wallet-error').innerHTML = `Something went wrong :(`;
        alert(data.error || "Failed to retrieve wallet balance.");
    }
}

async function donthavewallet() {
    toggleForm('block', 'wallet-create-form')
}

async function toggleForm(toggle='', form='') {
    const targetform = document.getElementById(form);
        targetform.style.display = toggle;
}
async function sendCoins() {
    const payerAddress = document.getElementById('wallet-input').value;
    const payeeAddress = document.getElementById('payee-wallet-input').value;
    const amount = parseFloat(document.getElementById('amount-input').value);
    const password = document.getElementById('wallet-password-input-check').value;

    if (!payeeAddress || isNaN(amount) || amount <= 0) {
        alert("Please fill in valid payee, amount fields, and password.");
        return;
    }

    if (!payerAddress || !password) {
        alert("Please fill in your wallet address and password.");
        document.getElementById('wallet-section').scrollIntoView({ behavior: 'smooth' });
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
            const wallet_response = await fetch(`/wallet/balance`, {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ address: payerAddress, password: password })
            });
            const wallet_data = await wallet_response.json();
        
            if (wallet_response.ok) {
                 const wallet_title = document.getElementById("wallet-title");
                 wallet_title.style.display = 'block';
                // //document.getElementById('wallet-info').classList.remove('hidden');
                document.getElementById('wallet-Address').innerHTML = `Address: ${payerAddress}`;
                document.getElementById('wallet-info').innerHTML = `${wallet_data.balance-amount}`;
                toggleForm('none', 'wallet-input-form')
            } else {
                document.getElementById('wallet-error').innerHTML = `Something went wrong :(`;
                alert(data.error || "Failed to retrieve wallet balance.");
            }
            
        } else {
            document.getElementById("transaction-info").innerHTML =
                `Transaction failed: ${data.error || "Unknown error"}`;
        }
        // const wallet_response = await fetch(`/wallet/balance`, {
        //     method: "POST",
        //     headers: { "Content-Type": "application/json" },
        //     body: JSON.stringify({ address: payerAddress, password: password })
        // });
        // const wallet_data = await wallet_response.json();
    
        // if (wallet_response.ok) {
        //      const wallet_title = document.getElementById("wallet-title");
        //      wallet_title.style.display = 'block';
        //     // //document.getElementById('wallet-info').classList.remove('hidden');
        //     document.getElementById('wallet-Address').innerHTML = `Address: ${payerAddress}`;
        //     document.getElementById('wallet-info').innerHTML = `${wallet_data.balance}`;
        //     toggleForm('none', 'wallet-input-form')
        // } else {
        //     document.getElementById('wallet-error').innerHTML = `Something went wrong :(`;
        //     alert(data.error || "Failed to retrieve wallet balance.");
        // }
    } catch (error) {
        document.getElementById("transaction-info").innerHTML =
            `An error occurred: ${error.message}`;
    }

}

// Function to show wallet creation success message with animation
function showWalletCreatedSuccess() {
    showSuccessMessage("Wallet Created Successfully!", 'wallet-section', "wallet-section", true, "10 Runes added to your wallet as opening bonus!!!");
}

// Function to show transaction success message with animation
function showTransactionSuccess() {
    showSuccessMessage("Validating transaction...", 'transaction-section', "wallet-section", true, "transaction sucessful");
}

// Utility function to show any success message
function showSuccessMessage(message, parentElementId, destination='wallet-section', addition_popup=false, additional_message='') {
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
        document.getElementById(destination).scrollIntoView({ behavior: 'smooth' });
        if(addition_popup) {
            showSuccessMessage(additional_message, destination)
        }
    }, 3000);
}

// Event listeners for buttons
document.getElementById("sendCoinsBtn").addEventListener("click", sendCoins);
document.getElementById("createWalletBtn").addEventListener("click", createWallet);
document.getElementById("checkWalletBtn").addEventListener("click", getWalletBalance);
// document.getElementById("text-button").addEventListener("click", showCreateWalletForm);
document.getElementById("downloadBtn").addEventListener("click", function() {
    window.location.href = "https://drive.google.com/file/d/17rX0M8e61ckTHMpIQF-e0tQI0EdC_c6s/view?usp=sharing"; // Replace with actual file path
});
document.querySelectorAll('.navbar a').forEach(anchor => {
    anchor.addEventListener('click', function (e) {
        e.preventDefault();
        const targetSection = document.querySelector(this.getAttribute('href'));
        const offset = 50; // Adjust this value to set how much higher the scroll should stop
        const topPosition = targetSection.getBoundingClientRect().top + window.scrollY - offset;

        window.scrollTo({ 
            top: topPosition, 
            behavior: 'smooth' 
        });
    });
});

const navbar = document.getElementById('navbar');
const walletSection = document.getElementById("wallet-section");

window.addEventListener('scroll', () => {
    const walletSectionTop = walletSection.offsetTop;

    if (window.scrollY >= walletSectionTop + 200) {
        navbar.style.display = 'flex'; // Show the navbar
    } else {
        navbar.style.display = 'none'; // Hide the navbar
    }
});

// Hide the navbar initially
navbar.style.display = 'none';

//drop down menu when crossing max width 
let menuList = document.getElementById("menuList")
menuList.style.maxHeight="0px";

function toggleMenu(){
    if(menuList.style.maxHeight=="0px"){
        menuList.style.maxHeight="300px"
    }
    else{
        menuList.style.maxHeight="0px"
    }
}

// Function to toggle the menu
function toggleMenu() {
    var menu = document.querySelector('.navbar ul');
    menu.classList.toggle('active');
}


document.addEventListener("scroll", () => {
    const scrollY = window.scrollY; // Get the vertical scroll position
    const parallaxBg = document.getElementById("parallax-bg");
    parallaxBg.style.transform = `translateY(${scrollY * 0.5}px)`; // Adjust the multiplier (0.5) for parallax intensity
});
