const MODEL_URL = window.config.MODEL_URL;

let tasks = [];
let currentTaskIndex = -1;

let currentPage = 0;
const pageSize = 5;

function renderTaskTable(tasks, includeCustomerName = true) {
    const tbody = document.querySelector('#taskTable tbody');
    tbody.innerHTML = '';

    if (tasks.length === 0) {
        tbody.innerHTML = `
            <tr>
                <td colspan="5" style="text-align: center;">No tasks found</td>
            </tr>
        `;
        return;
    }

    tasks.forEach((task, index) => {
        const row = document.createElement('tr');
        row.innerHTML = `
            <td>${task.taskName}</td>
            <td class="d-none d-xl-table-cell">${task.taskDesc}</td>
            <td class="d-none d-xl-table-cell">${task.taskStatus}</td>
            ${includeCustomerName ? `<td class="d-none d-xl-table-cell">${task.customer != null ? task.customer.customerName : 'N/A'}</td>` : ''}
            <td class="d-none d-xl-table-cell">${task.estimateHours ? task.estimateHours : 'N/A'}</td>
            <td class="d-none d-xl-table-cell">${task.logHours ? task.logHours : 'N/A'}</td>
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
    const pageSize = 100;  // Số lượng khách hàng mỗi trang
    let allCustomers = [];
    let currentPage = 0;

    function fetchPage(page) {
        return fetch(`${HOST_IP}/api/customers?page=${page}&size=${pageSize}`, {
            method: 'GET',
            headers: {
                'Authorization': `Bearer ${TOKEN}`,
                'Content-Type': 'application/json'
            }
        })
        .then(response => {
            if (!response.ok) {
                throw new Error(`Failed to fetch customers: ${response.status}`);
            }
            return response.json();
        });
    }

    function loadAllPages() {
        fetchPage(currentPage)
            .then(data => {
                if (Array.isArray(data.content)) {
                    allCustomers = [...allCustomers, ...data.content];  // Gộp các khách hàng từ nhiều trang
                    if (data.content.length === pageSize) {
                        currentPage++;  // Nếu có nhiều khách hàng, tiếp tục lấy trang tiếp theo
                        loadAllPages();  // Đệ quy tiếp tục lấy trang tiếp theo
                    } else {
                        populateCustomerSelect(allCustomers);  // Khi lấy hết tất cả khách hàng
                    }
                } else {
                    console.error('Unexpected data structure for customers:', data);
                }
            })
            .catch(error => console.error('Error loading customers:', error));
    }

    function populateCustomerSelect(customers) {
        const customerSelect = document.getElementById('customerSelect');
        customerSelect.innerHTML = '<option value="">Select a customer</option>';
        customers.forEach(customer => {
            const option = document.createElement('option');
            option.value = customer.customerID;
            option.textContent = customer.customerName;
            customerSelect.appendChild(option);
        });
    }

    loadAllPages();  // Bắt đầu quá trình tải dữ liệu từ trang đầu tiên
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

    document.getElementById('taskModalLabel').innerText = 'Update Task';
    document.getElementById('taskStatusInput').value = task.taskStatus;
    document.getElementById('taskDescInput').value = task.taskDesc;
    document.getElementById('taskNameInput').value = task.taskName;
    document.getElementById('estimateHoursInput').value = task.estimateHours;
    document.getElementById('logHoursInput').value = task.logHours;

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
        search();
    } catch (error) {
        console.error('Delete task failed: ', error);
    }
}


document.getElementById('taskForm').addEventListener('submit', async function(event) {
    event.preventDefault();

    const task = {
        taskStatus: document.getElementById('taskStatusInput').value,
        taskDesc: document.getElementById('taskDescInput').value,
        taskName: document.getElementById('taskNameInput').value,
        estimateHours: parseInt(document.getElementById('estimateHoursInput').value, 10),
        logHours: parseInt(document.getElementById('logHoursInput').value, 10),  
    };

    if (isNaN(task.estimateHours)) {
        task.estimateHours = 0;
    }
    if (isNaN(task.logHours)) {
        task.logHours = 0;
    }

    if (currentTaskIndex === -1) {
        await addTask(task);
    } else {
        task.taskId = tasks[currentTaskIndex].taskId;
        await updateTask(task);
    }

    $('#taskModal').modal('hide');
    search();
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
        console.log("addTask body: ", JSON.stringify(formData));

        if (!response.ok) {
            throw new Error('Failed to add task');
        }

        const data = await response.json();
        tasks.push(data);
        alert("Add Task Successfully");
        search(); // Reload danh sách sau khi thêm
    } catch (error) {
        console.error('Add Task failed: ', error);
    }
};


const updateTask = async (formData) => {
    try {
        // Thêm customerId vào formData
        const customerID = document.getElementById('customerSelect').value;
        formData.customer = { customerID };

        const response = await fetch(`${HOST_IP}/api/tasks/${formData.taskId}`, {
            method: 'PATCH',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${TOKEN}`
            },
            body: JSON.stringify(formData)
        });
        console.log("updateTask, body: ", JSON.stringify(formData));

        if (!response.ok) {
            throw new Error('Failed to update task');
        }

        const data = await response.json();
        tasks[currentTaskIndex] = data;
        console.log("Update Task Successfully");
        search(); // Reload danh sách sau khi cập nhật
    } catch (error) {
        console.error('Update Task failed: ', error);
    }
};

function delay(ms) {
    return new Promise(resolve => setTimeout(resolve, ms));
}

const search = async () => {
    const searchType = document.getElementById('searchType').value; // Kiểu tìm kiếm: taskName hoặc customerName
    const searchInput = document.getElementById('searchInput').value.trim(); // Từ khóa tìm kiếm
    const query = searchInput ? encodeURIComponent(searchInput) : '';

    let url = '';
    
    if (searchType === 'taskName') {
        if (query) {
            url = `${HOST_IP}/api/tasks/query?query=${query}&page=${currentPage}&size=${pageSize}`;
        } else {
            url = `${HOST_IP}/api/tasks?page=${currentPage}&size=${pageSize}`;
        }
    } else if (searchType === 'customerName') {
        if (query) {
            url = `${HOST_IP}/api/tasks/getTask/customer/query?query=${query}&page=${currentPage}&size=${pageSize}`;
        } else {
            url = `${HOST_IP}/api/tasks?page=${currentPage}&size=${pageSize}`;
        }
    }

    try {
        const response = await fetch(url, {
            method: 'GET',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${TOKEN}`
            }
        });

        if (!response.ok) {
            throw new Error(`Cannot retrieve tasks. Status: ${response.status}`);
        }

        const data = await response.json();
        console.log(data); 

        if (Array.isArray(data)) {
            tasks = data;
        } else {
            tasks = data.content || [];
        }

        renderTaskTable(tasks);
        renderPagination(data.totalPages || 1, currentPage); // Render phân trang

    } catch (error) {
        console.error('Get Tasks failed: ', error);
    }
};


document.addEventListener('DOMContentLoaded', () => {
    search();
    loadCustomers();
});

function renderPagination(totalPages, currentPage) {
    const paginationContainer = document.getElementById('pagination');
    paginationContainer.innerHTML = ''; // Xóa các nút cũ

    // Nút "Trang trước"
    const prevButton = document.createElement('li');
    prevButton.classList.add('page-item');
    const prevLink = document.createElement('a');
    prevLink.classList.add('page-link');
    prevLink.innerText = 'Previous';
    prevLink.href = '#';
    prevLink.disabled = currentPage === 0;
    prevLink.addEventListener('click', (e) => {
        e.preventDefault();
        changePage(currentPage - 1);
    });
    prevButton.appendChild(prevLink);
    paginationContainer.appendChild(prevButton);

    // Nút các trang
    for (let i = 0; i < totalPages; i++) {
        const pageButton = document.createElement('li');
        pageButton.classList.add('page-item');
        if (i === currentPage) {
            pageButton.classList.add('active');
        }

        const pageLink = document.createElement('a');
        pageLink.classList.add('page-link');
        pageLink.innerText = i + 1;
        pageLink.href = '#';
        pageLink.addEventListener('click', (e) => {
            e.preventDefault();
            changePage(i);
        });

        pageButton.appendChild(pageLink);
        paginationContainer.appendChild(pageButton);
    }

    // Nút "Trang sau"
    const nextButton = document.createElement('li');
    nextButton.classList.add('page-item');
    const nextLink = document.createElement('a');
    nextLink.classList.add('page-link');
    nextLink.innerText = 'Next';
    nextLink.href = '#';
    nextLink.disabled = currentPage === totalPages - 1;
    nextLink.addEventListener('click', (e) => {
        e.preventDefault();
        changePage(currentPage + 1);
    });
    nextButton.appendChild(nextLink);
    paginationContainer.appendChild(nextButton);
}


// Hàm thay đổi trang
function changePage(page) {
    currentPage = page;
    search(); // Gọi lại hàm search để tải dữ liệu của trang mới
}


document.getElementById('searchInput').addEventListener('input', () => {
    currentPage = 0; // Quay về trang đầu tiên khi người dùng thay đổi từ khóa tìm kiếm
    search();
});
