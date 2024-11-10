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

        document.getElementById('userName').innerText = userData.userName;
        document.getElementById('profilePicture').src = userData.imageUrl || 'img/avatars/avatar-4.jpg';
        document.getElementById('userNameInput').value = userData.userName;
        document.getElementById('birthDayInput').value = userData.birthDay;
        document.getElementById('addressInput').value = userData.address;
        document.getElementById('genderSelect').value = userData.gender;

        console.log("User Data: ", userData);
        return userData;
    } catch (error) {
        console.error('Fetch User failed:', error);
        console.error('Fetch User Failed: ' + error.message);
    }
};

const updateUser = async (formData) => {
    try {
        const userIDData = await getUserID();
        const userID = userIDData.id;
        console.log(userID);
        const response = await fetch(`${HOST_IP}/api/users/${userID}`, {
            method: 'PATCH',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${TOKEN}`
            },
            body: JSON.stringify(formData)
        });

        if (!response.ok) {
            throw new Error('Failed to update user');
        }
    } catch (error) {
        console.error('Update User failed:', error);
        console.error('Update User Failed: ' + error.message);
    }
};

const updateProfilePicture = async (base64Image) => {
    try {
        const userIDData = await getUserID();
        const userID = userIDData.id;

        const formData = { imageUrl: base64Image };

        const response = await fetch(`${HOST_IP}/api/users/${userID}`, {
            method: 'PATCH',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${TOKEN}`
            },
            body: JSON.stringify(formData)
        });

        if (!response.ok) {
            throw new Error('Failed to upload profile picture');
        }

        const data = await response.json();
        document.getElementById('profilePicture').src = data.imageUrl;
        console.log('Profile picture updated:', data);
    } catch (error) {
        console.error('Update Profile Picture failed:', error.message);
    }
};

document.addEventListener('DOMContentLoaded', () => {
    getUser();
});

document.getElementById('editProfileForm').addEventListener('submit', async function (event) {
    event.preventDefault();

    const userName = document.getElementById('userNameInput').value;
    const birthDay = document.getElementById('birthDayInput').value;
    const address = document.getElementById('addressInput').value;
    const gender = document.getElementById('genderSelect').value;

    document.getElementById('userName').innerText = userName;
    const formData = { birthDay, address, gender };
    console.log(formData);
    await updateUser(formData);
});


document.getElementById('profilePictureInput').addEventListener('change', async function (event) {
    const file = event.target.files[0];
    if (file) {
        const reader = new FileReader();
        reader.onload = function (e) {
            const base64Image = e.target.result;
            document.getElementById('profilePicture').src = base64Image;
            console.log("base64: ", base64Image);
            updateProfilePicture(base64Image);
        };
        reader.readAsDataURL(file);
    }
});