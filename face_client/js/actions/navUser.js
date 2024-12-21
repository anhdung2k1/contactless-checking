const HOST_IP = window.config.HOST_IP;
const TOKEN = window.config.TOKEN;

const getUserID = async () => {
    try {
        const profile = JSON.parse(localStorage.getItem('profile'));
        const userName = profile.userName;

        const response = await fetch(`${HOST_IP}/api/users/find?user_name=${encodeURIComponent(userName)}`, {
            method: 'GET',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${TOKEN}`
            }
        });

        if (!response.ok) {
            throw new Error('Cannot get user ID');
        }

        const data = await response.json();
        return data;
    } catch (error) {
        console.error('Get User ID failed: ', error);
        console.error('Failed to get user ID: ' + error.message);
    }
};

const getUser = async () => {
    try {
        const userIDData = await getUserID();
        const userID = userIDData.id;
        console.log(userID);
        const response = await fetch(`${HOST_IP}/api/users/${userID}`, {
            method: 'GET',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${TOKEN}`
            }
        });

        if (!response.ok) {
            throw new Error('Failed to fetch user');
        }
        const userData = await response.json();

        // Update the profile picture and username in the navbar
        document.getElementById('navbarProfilePicture').src = userData.imageUrl || 'img/avatars/avatar.jpg';
        document.getElementById('navbarUserName').innerText = userData.userName;

        console.log("User Data: ", userData);
        return userData;
    } catch (error) {
        console.error('Fetch User failed:', error);
    }
};

document.addEventListener('DOMContentLoaded', () => {
    getUser();
});