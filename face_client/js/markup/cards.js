let customerSize = 0;
let recordSize = 0;

const countCustomer = async () => {
    try {
        const response = await fetch(`${HOST_IP}/api/customers/count`, {
            method: 'GET',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${TOKEN}`
            }
        });

        if (!response.ok) {
            throw new Error('Cannot count customers');
        }

        const data = await response.json();
        customerSize = data;
    } catch (error) {
        console.error('Count Customers failed: ', error);
        alert('Failed to count customers: ' + error.message);
    }
};

const countRecords = async () => {
    try {
        const response = await fetch(`${HOST_IP}/api/records/count`, {
            method: 'GET',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${TOKEN}`
            }
        });

        if (!response.ok) {
            throw new Error('Cannot count records');
        }

        const data = await response.json();
        recordSize = data;
    } catch (error) {
        console.error('Count Records failed: ', error);
        alert('Failed to count records: ' + error.message);
    }
};

async function fetchCountsAndLoadCards() {
    await Promise.all([countCustomer(), countRecords()]);
    loadCards();
}

function createCard(title, statIcon, statValue) {
    return `
        <div class="card">
            <div class="card-body">
                <div class="row">
                    <div class="col mt-0">
                        <h5 class="card-title">${title}</h5>
                    </div>
                    <div class="col-auto">
                        <div class="stat text-primary">
                            <i class="align-middle" data-feather="${statIcon}"></i>
                        </div>
                    </div>
                </div>
                <h1 class="mt-1 mb-3">${statValue}</h1>
            </div>
        </div>
    `;
}

function loadCards() {
    const container = document.getElementById('cards-container');
    const cards = [
        {
            title: "Customer Checking Records",
            statIcon: "truck",
            statValue: `${recordSize}`
        },
        {
            title: "Customer Registered",
            statIcon: "users",
            statValue: `${customerSize}`,
        }
    ];

    let htmlContent = '';
    cards.forEach(card => {
        htmlContent += `<div class="col-sm-6">${createCard(card.title, card.statIcon, card.statValue)}</div>`;
    });
    container.innerHTML = htmlContent;
    feather.replace();
}

document.addEventListener("DOMContentLoaded", fetchCountsAndLoadCards);
