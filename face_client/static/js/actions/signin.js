const HOST_IP=window.config.HOST_IP
// Function to handle signin
const signin = async (formData) => {
    try {
        const response = await fetch(`http://${HOST_IP}/api/accounts/signin`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(formData)
        });

        if (!response.ok) {
            throw new Error('Signin failed');
        }

        const data = await response.json();

        localStorage.setItem('profile', JSON.stringify(data));
        
        if (data.token) {
            window.location.href = 'index.html'; // Redirect on successful signin
        }
    } catch (error) {
        console.error('Signin failed:', error);
        alert('Login failed: ' + error.message);
    }
};

document.addEventListener('DOMContentLoaded', () => {
    const signinForm = document.getElementById('signin-form');
    if (signinForm) {
        signinForm.addEventListener('submit', async function(event) {
            event.preventDefault(); // Prevent default form submission

            const userName = document.getElementById('userName').value;
            const password = document.getElementById('password').value;

            const formData = { userName, password };
            await signin(formData);
        });
    } else {
        console.error('Element with id "signin-form" not found.');
    }
});
