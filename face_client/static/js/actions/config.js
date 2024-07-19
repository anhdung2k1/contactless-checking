let profile = JSON.parse(localStorage.getItem('profile'));

window.config = {
    MODEL_URL: 'https://localhost:5000',
    HOST_IP: 'https://localhost:8443',
    TOKEN: profile !== null ? profile.token : null
};