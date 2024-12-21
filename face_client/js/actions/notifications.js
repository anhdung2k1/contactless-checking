const getNotifications = async () => {
    try {
        const response = await fetch(`${HOST_IP}/api/notifications`, {
            method: 'GET',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${TOKEN}`
            }
        });

        if (!response.ok) {
            throw new Error('Cannot fetch notifications');
        }

        const data = await response.json();
        renderNotifications(data);
    } catch (error) {
        console.error('Fetch Notifications failed: ', error);
    }
};

const renderNotifications = (notifications) => {
    const notificationList = document.getElementById('notification-list');
    const notificationCount = document.getElementById('notification-count');
    notificationList.innerHTML = '';

    notifications.forEach((notification) => {
        const { notificationMessage, createdAt } = notification;

        const timeAgo = getTimeAgo(createdAt);

        const notificationItem = `
            <a href="#" class="list-group-item">
                <div class="row g-0 align-items-center">
                    <div class="col-2">
                        <i class="text-primary" data-feather="bell"></i>
                    </div>
                    <div class="col-10">
                        <div class="text-dark">${notificationMessage.replace(/"/g, "")}</div>
                        <div class="text-muted small mt-1">${timeAgo}</div>
                    </div>
                </div>
            </a>
        `;

        notificationList.innerHTML += notificationItem;
    });

    notificationCount.textContent = notifications.length;
    feather.replace(); // Replace Feather icons after the notifications are loaded
};

const getTimeAgo = (dateString) => {
    const date = new Date(dateString);
    const now = new Date();
    const diffInSeconds = Math.floor((now - date) / 1000);

    const units = [
        { unit: 'year', seconds: 31536000 },
        { unit: 'month', seconds: 2592000 },
        { unit: 'week', seconds: 604800 },
        { unit: 'day', seconds: 86400 },
        { unit: 'hour', seconds: 3600 },
        { unit: 'minute', seconds: 60 },
        { unit: 'second', seconds: 1 }
    ];

    for (const { unit, seconds } of units) {
        const interval = Math.floor(diffInSeconds / seconds);
        if (interval >= 1) {
            return `${interval} ${unit}${interval !== 1 ? 's' : ''} ago`;
        }
    }

    return 'just now';
};

document.addEventListener("DOMContentLoaded", getNotifications);