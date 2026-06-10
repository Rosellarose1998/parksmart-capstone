const API_URL = "http://127.0.0.1:8000";

// Reserve parking spot
function reserveSpot(spot) {
    const token = localStorage.getItem("token");

    if (!token) {
        alert("Please log in before reserving a parking spot.");
        window.location.href = "login.html";
        return;
    }

    const dateInput = document.getElementById("date-" + spot);
    const date = dateInput ? dateInput.value : "";

    if (!date) {
        alert("Please choose a reservation date.");
        return;
    }

    const reservations = JSON.parse(localStorage.getItem("reservations")) || [];

    reservations.push({
        spot: spot,
        date: date,
        status: "Active"
    });

    localStorage.setItem("reservations", JSON.stringify(reservations));

    updateParkingPage();
    alert("Reserved spot " + spot + " for " + date);
}

// Update parking page
function updateParkingPage() {
    const reservations = JSON.parse(localStorage.getItem("reservations")) || [];

    reservations.forEach(function (reservation) {
        const status = document.getElementById("status-" + reservation.spot);
        const button = document.getElementById("button-" + reservation.spot);
        const dateInput = document.getElementById("date-" + reservation.spot);

        if (status && button) {
            status.textContent = "Reserved";
            button.textContent = "Reserved";
            button.className = "btn btn-secondary";
            button.disabled = true;
        }

        if (dateInput) {
            dateInput.value = reservation.date;
            dateInput.disabled = true;
        }
    });
}

// Update reservations page
function updateReservationsPage() {
    const reservations = JSON.parse(localStorage.getItem("reservations")) || [];
    const reservationTable = document.getElementById("reservationTable");

    if (reservationTable) {
        reservationTable.innerHTML = "";

        reservations.forEach(function (reservation) {
            reservationTable.innerHTML += `
                <tr>
                    <td>${reservation.spot}</td>
                    <td>${reservation.date}</td>
                    <td>${reservation.status}</td>
                </tr>
            `;
        });
    }
}

// Register user for frontend demo
function registerUser(event) {
    event.preventDefault();

    const fullName = document.getElementById("fullName").value;
    const email = document.getElementById("registerEmail").value;
    const password = document.getElementById("registerPassword").value;

    localStorage.setItem("accountName", fullName);
    localStorage.setItem("accountEmail", email);
    localStorage.setItem("accountPassword", password);

    localStorage.setItem("token", "demo-token");
    localStorage.setItem("userEmail", email);

    alert("Account created. You are now logged in.");
    window.location.href = "parking.html";
}

// Login user for frontend demo
function loginUser(event) {
    event.preventDefault();

    const email = document.getElementById("loginEmail").value;
    const password = document.getElementById("loginPassword").value;

    const savedEmail = localStorage.getItem("accountEmail");
    const savedPassword = localStorage.getItem("accountPassword");

    if (email === savedEmail && password === savedPassword) {
        localStorage.setItem("token", "demo-token");
        localStorage.setItem("userEmail", email);

        window.location.href = "parking.html";
    } else {
        alert("No account found or wrong password. Please register first.");
    }
}

// Show logged-in user
function showLoggedInUser() {
    const name = localStorage.getItem("accountName");
    const display = document.getElementById("userDisplay");

    if (display && name) {
        display.textContent = "Welcome, " + name;
    }
}

// Logout user
function logoutUser() {
    localStorage.removeItem("token");
    localStorage.removeItem("userEmail");

    window.location.href = "login.html";
}

// Run when page loads
window.onload = function () {
    updateParkingPage();
    updateReservationsPage();
    showLoggedInUser();
};