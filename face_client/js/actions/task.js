const MODEL_URL = window.config.MODEL_URL;

let tasks = [];
let currentTaskIndex = -1;

function renderTaskTable(tasks)
{
    const tbody = document.querySelector('#taskTable tbody');
    tbody.innerHTML = '';

    tasks.forEach((task, index) => {
        const row = document.createElement('tr');
        console.log("renderTaskTable: (), task: " + JSON.stringify(task));

        row.innerHTML = `
    <td>${task.taskName}</td>
    <td class="d-none d-xl-table-cell">${task.taskDesc}</td>
    <td class="d-none d-xl-table-cell">${task.taskStatus}</td>
    <td class="d-none d-xl-table-cell">${task.customerName != '' ? task.customerName : 'N/A'}</td>
    <td>
        <div style="display: flex; justify-content: space-between; align-items: center;">
            <div style="display: flex; flex-direction: column;">
                <button class="btn btn-danger btn-sm" style="margin-bottom: 10px;" onclick="deleteTask(${index})">Delete</button>
                <button class="btn btn-warning btn-sm" onclick="showUpdateTaskModal(${index})">Update</button>
            </div>
        </div>
    </td>
`;

        tbody.appendChild(row);
    });
}

function loadCustomers() {
    fetch(`${HOST_IP}/api/customers`, {
        method: 'GET',
        headers: {
            'Authorization': `Bearer ${TOKEN}`, // Thay thế TOKEN bằng giá trị token hợp lệ
            'Content-Type': 'application/json'
        }
    })
    .then(response => {
        if (!response.ok) {
            throw new Error(`Failed to fetch customers: ${response.status}`);
        }
        return response.json();
    })
    .then(data => {
        const customerSelect = document.getElementById('customerSelect');
        customerSelect.innerHTML = '<option value="">Select a customer</option>'; 
        data.forEach(customer => {
            const option = document.createElement('option');
            option.value = customer.customerID;  
            option.textContent = customer.customerName; 
            customerSelect.appendChild(option);
        });
    })
    .catch(error => console.error('Error loading customers:', error));
}

function showAddTaskModal() {
    currentTaskIndex = -1;
    document.getElementById('taskModalLabel').innerText = 'Add Task';
    document.getElementById('taskForm').reset();
    $('#taskModal').modal('show');
}

function showUpdateTaskModal(index) {
    currentTaskIndex = index;
    const task = tasks[index];

    document.getElementById('taskStatusInput').value = task.taskStatus;
    document.getElementById('taskDescInput').value = task.taskDesc;
    document.getElementById('taskNameInput').value = task.taskName;

    if (task.customer) {
        document.getElementById('customerSelect').value = task.customer.customerId; // ID của Customer
    } else {
        document.getElementById('customerSelect').value = ''; // Không có Customer nào liên kết
    }

    $('#taskModal').modal('show');
}


async function deleteTask(index) {
    const task = tasks[index];
    try {
        const response = await fetch(`${HOST_IP}/api/tasks/${task.taskId}`, {
            method: 'DELETE',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${TOKEN}`
            }
        });

        if (!response.ok) {
            throw new Error('Failed to delete task');
        }

        tasks.splice(index, 1);
        renderTaskTable(tasks);
    } catch (error) {
        console.error('Delete task failed: ', error);
        alert('Failed to delete task: ' + error.message);
    }
}

document.getElementById('taskForm').addEventListener('submit', async function(event) {
    event.preventDefault();

    const task = {
        taskStatus: document.getElementById('taskStatusInput').value,
        taskDesc: document.getElementById('taskDescInput').value,
        taskName: document.getElementById('taskNameInput').value,
    };

    if (currentTaskIndex === -1) {
        await addTask(task);
    } else {
        task.taskId = tasks[currentTaskIndex].taskId;
        await updateTask(task);
    }

    $('#taskModal').modal('hide');
    searchTask();
});

const addTask = async (formData) => {
    try {
        // Thêm customerId vào formData
        const customerID = document.getElementById('customerSelect').value;
        formData.customer = { customerID }; // Cấu trúc JSON phải khớp với backend

        const response = await fetch(`${HOST_IP}/api/tasks`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${TOKEN}`
            },
            body: JSON.stringify(formData)
        });

        if (!response.ok) {
            throw new Error('Failed to add task');
        }

        const data = await response.json();
        tasks.push(data);
        alert("Add Task Successfully");
        searchTask(); // Reload danh sách sau khi thêm
    } catch (error) {
        console.error('Add Task failed: ', error);
        alert('Failed to add task: ' + error.message);
    }
};

const updateTask = async (formData) => {
    try {
        // Thêm customerId vào formData
        const customerId = document.getElementById('customerSelect').value;
        formData.customer = { customerId };

        const response = await fetch(`${HOST_IP}/api/tasks/${formData.taskId}`, {
            method: 'PATCH',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${TOKEN}`
            },
            body: JSON.stringify(formData)
        });

        if (!response.ok) {
            throw new Error('Failed to update task');
        }

        const data = await response.json();
        tasks[currentTaskIndex] = data;
        alert("Update Task Successfully");
        searchTask(); // Reload danh sách sau khi cập nhật
    } catch (error) {
        console.error('Update Task failed: ', error);
        alert('Failed to update task: ' + error.message);
    }
};

function delay(ms) {
    return new Promise(resolve => setTimeout(resolve, ms));
}

const searchCusTask = async () => {
    const cusName = document.getElementById('searchCusInput').value;
    const query = cusName ? `${encodeURIComponent(cusName)}` : '';
    try {
        const response = await fetch(`${HOST_IP}/api/tasks/query?query=${query}`, {
            method: 'GET',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${TOKEN}`
            }
        });

        if (!response.ok) {
            throw new Error('Cannot retrieve tasks');
        }   

        const data = await response.json();
        tasks = data;
        renderTaskTable(data);
    } catch (error) {
        console.error('Get Tasks failed: ', error);
        alert('Failed to get tasks: ' + error.message);
    }
};

const searchTask = async () => {
    const taskName = document.getElementById('searchInput').value;
    const query = taskName ? `${encodeURIComponent(taskName)}` : '';
    try {
        const response = await fetch(`${HOST_IP}/api/tasks/query?query=${query}`, {
            method: 'GET',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${TOKEN}`
            }
        });

        if (!response.ok) {
            throw new Error('Cannot retrieve tasks');
        }   

        const data = await response.json();
        tasks = data;
        renderTaskTable(data);
    } catch (error) {
        console.error('Get Tasks failed: ', error);
        alert('Failed to get tasks: ' + error.message);
    }
};

document.addEventListener('DOMContentLoaded', () => {
    searchTask(); // Fetch all customers when the page loads
    loadCustomers();
});