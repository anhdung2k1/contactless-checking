let customers = [];

let currentCustomerIndex = -1;

function renderCustomerTable(customers) {
    const tbody = document.querySelector('#customerTable tbody');
    tbody.innerHTML = '';

    customers.forEach((customer, index) => {
        const row = document.createElement('tr');

        row.innerHTML = `
            <td>${customer.customerName}</td>
            <td class="d-none d-xl-table-cell">${customer.customerEmail}</td>
            <td class="d-none d-xl-table-cell">${customer.customerAddress}</td>
            <td>${customer.customerGender}</td>
            <td class="d-none d-xl-table-cell">${customer.customerBirthDay}</td>
            <td>
                <button class="btn btn-danger btn-sm" style="margin-bottom: 10px;" onclick="deleteCustomer(${index})">Delete</button>
                <button class="btn btn-warning btn-sm" onclick="showUpdateCustomerModal(${index})">Update</button>
            </td>
        `;

        tbody.appendChild(row);
    });
}

function showAddCustomerModal() {
    currentCustomerIndex = -1;
    document.getElementById('customerModalLabel').innerText = 'Add Customer';
    document.getElementById('customerForm').reset();
    $('#customerModal').modal('show');
}

function showUpdateCustomerModal(index) {
    currentCustomerIndex = index;
    const customer = customers[index];
    document.getElementById('customerModalLabel').innerText = 'Update Customer';
    document.getElementById('customerNameInput').value = customer.customerName;
    document.getElementById('customerEmailInput').value = customer.customerEmail;
    document.getElementById('customerAddressInput').value = customer.customerAddress;
    document.getElementById('customerGenderSelect').value = customer.customerGender;
    document.getElementById('customerBirthDayInput').value = customer.customerBirthDay;
    $('#customerModal').modal('show');
}

async function deleteCustomer(index) {
    const customer = customers[index];
    try {
        const response = await fetch(`${HOST_IP}/api/customers/${customer.customerID}`, {
            method: 'DELETE',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${TOKEN}`
            }
        });

        if (!response.ok) {
            throw new Error('Failed to delete customer');
        }

        customers.splice(index, 1);
        renderCustomerTable(customers);
    } catch (error) {
        console.error('Delete Customer failed: ', error);
        alert('Failed to delete customer: ' + error.message);
    }
}

document.getElementById('customerForm').addEventListener('submit', async function(event) {
    event.preventDefault();

    const customer = {
        customerName: document.getElementById('customerNameInput').value,
        customerEmail: document.getElementById('customerEmailInput').value,
        customerAddress: document.getElementById('customerAddressInput').value,
        customerGender: document.getElementById('customerGenderSelect').value,
        customerBirthDay: document.getElementById('customerBirthDayInput').value
    };

    if (currentCustomerIndex === -1) {
        await addCustomer(customer);
    } else {
        customer.customerID = customers[currentCustomerIndex].customerID;
        await updateCustomer(customer);
    }

    $('#customerModal').modal('hide');
    searchCustomer();
});

const addCustomer = async(formData) => {
    try {
        const response = await fetch(`${HOST_IP}/api/customers`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${TOKEN}`
            },
            body: JSON.stringify(formData)
        });

        if (!response.ok) {
            throw new Error('Failed to add customer');
        }

        const data = await response.json();
        customers.push(data);
        alert("Add Customer Successfully");
    } catch (error) {
        console.error('Add Customer failed: ', error);
        alert('Failed to add customer: ' + error.message);
    }
}

const updateCustomer = async(formData) => {
    try {
        const response = await fetch(`${HOST_IP}/api/customers/${formData.customerID}`, {
            method: 'PATCH',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${TOKEN}`
            },
            body: JSON.stringify(formData)
        });

        if (!response.ok) {
            throw new Error('Failed to update customer');
        }

        const data = await response.json();
        customers[currentCustomerIndex] = data;
        alert("Update Customer Successfully");
    } catch (error) {
        console.error('Update Customer failed: ', error);
        alert('Failed to update customer: ' + error.message);
    }
}

const searchCustomer = async() => {
    const customerName = document.getElementById('searchInput').value;
    const query = customerName ? `${encodeURIComponent(customerName)}` : '';
    try {
        const response = await fetch(`${HOST_IP}/api/customers/query?query=${query}`, {
            method: 'GET',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${TOKEN}`
            }
        });

        if (!response.ok) {
            throw new Error('Cannot retrieve customers');
        }

        const data = await response.json();
        customers = data;
        renderCustomerTable(data);
    } catch (error) {
        console.error('Get Customers failed: ', error);
        alert('Failed to get customers: ' + error.message);
    }
}

document.addEventListener('DOMContentLoaded', () => {
    searchCustomer(); // Fetch all customers when the page loads
});