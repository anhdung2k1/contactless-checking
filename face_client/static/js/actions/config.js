let profile = JSON.parse(localStorage.getItem('profile'));

window.config = {
    MODEL_URL: 'http://localhost:5000',
    HOST_IP: 'http://localhost:8443',
    TOKEN: profile !== null ? profile.token : null
};