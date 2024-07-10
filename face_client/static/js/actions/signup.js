const HOST_IP=window.config.HOST_IP
// Function to handle signup
const signup = async (formData) => {
    try {
        const response = await fetch(`http://${HOST_IP}/api/accounts/signup`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(formData)
        });

        if (!response.ok) {
            throw new Error('Signup failed');
        }

        const data = await response.json();

        localStorage.setItem('profile', JSON.stringify(data));
        
        if (data.token) {
            window.location.href = 'index.html'; // Redirect on successful signup
        }
    } catch (error) {
        console.error('Signup failed:', error);
        alert('Register Failed: ' + error.message);
    }
};

document.addEventListener('DOMContentLoaded', () => {
    const signupForm = document.getElementById('signup-form');
    if (signupForm) {
        signupForm.addEventListener('submit', async function(event) {
            event.preventDefault(); // Prevent default form submission

            const userName = document.getElementById('userName').value;
            const password = document.getElementById('password').value;

            const formData = { userName, password };
            await signup(formData);
        });
    } else {
        console.error('Element with id "signup-form" not found.');
    }
});
