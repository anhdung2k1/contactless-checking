const logout = () => {
    try {
        localStorage.removeItem('profile');
        window.location.href = 'pages-sign-in.html';
    }  catch (error) {
        console.error('Logout failed: ', error)
    }
}

document.addEventListener('DOMContentLoaded', () => {
    const logoutLink = document.getElementById('logout-link')
    if (logoutLink) {
        logoutLink.addEventListener('click', (e) => {
            e.preventDefault();
            logout();
        });
    } else {
        console.error('Element with id "logout-link" not found.');
    }
})