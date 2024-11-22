// In-memory storage for users
let registeredUsers = [];

// Toggle between login and signup forms
document.getElementById('login-toggle').addEventListener('click', () => {
    document.getElementById('login-form').classList.add('active');
    document.getElementById('signup-form').classList.remove('active');
    document.getElementById('login-toggle').classList.add('active');
    document.getElementById('signup-toggle').classList.remove('active');
});

document.getElementById('signup-toggle').addEventListener('click', () => {
    document.getElementById('signup-form').classList.add('active');
    document.getElementById('login-form').classList.remove('active');
    document.getElementById('signup-toggle').classList.add('active');
    document.getElementById('login-toggle').classList.remove('active');
});

// Switch to signup form when clicking the bottom "Sign Up" link
document.getElementById('bottom-switch-to-signup').addEventListener('click', () => {
    document.getElementById('signup-form').classList.add('active');
    document.getElementById('login-form').classList.remove('active');
    document.getElementById('signup-toggle').classList.add('active');
    document.getElementById('login-toggle').classList.remove('active');
});

// Switch to login form when clicking "Log In" link
document.getElementById('switch-to-login').addEventListener('click', () => {
    document.getElementById('login-form').classList.add('active');
    document.getElementById('signup-form').classList.remove('active');
    document.getElementById('login-toggle').classList.add('active');
    document.getElementById('signup-toggle').classList.remove('active');
});

// Validate signup form
function validateSignup() {
    const name = document.getElementById('signup-name').value;
    const email = document.getElementById('signup-email').value;
    const password = document.getElementById('signup-password').value;
    const confirmPassword = document.getElementById('signup-confirm-password').value;

    // Check if the name contains any numbers
    if (/\d/.test(name)) {
        alert("Name cannot contain numbers.");
        return false;
    }

    // Validate password length and match
    if (password.length < 6) {
        alert("Password must be at least 6 characters long.");
        return false;
    }

    if (password !== confirmPassword) {
        alert("Passwords do not match.");
        return false;
    }

    // Check if the user is already registered
    const userExists = registeredUsers.some(user => user.email === email);
    if (userExists) {
        alert("Email is already registered. Please use a different email.");
        return false;
    }

    // Store the registered user in-memory (username and password)
    registeredUsers.push({ name, email, password });
    alert("Signup successful!");

    // Switch to login form after successful signup
    document.getElementById('login-form').classList.add('active');
    document.getElementById('signup-form').classList.remove('active');
    document.getElementById('login-toggle').classList.add('active');
    document.getElementById('signup-toggle').classList.remove('active');

    return false;  // Prevent form submission for now
}

// Validate login form
function validateLogin() {
    const loginEmail = document.getElementById('login-email').value;
    const loginPassword = document.getElementById('login-password').value;

    // Check if the user exists in the registered users array
    const user = registeredUsers.find(user => user.email === loginEmail && user.password === loginPassword);

    if (user) {
        alert(`Welcome back, ${user.name}! Login successful.`);
    } else {
        alert("Invalid email or password. Please try again.");
        return false;
    }

    return true;  // Allow form submission
}

// Attach event listeners for form submissions
document.getElementById('signup-form').onsubmit = validateSignup;
document.getElementById('login-form').onsubmit = validateLogin;
