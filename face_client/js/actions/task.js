const MODEL_URL = window.config.MODEL_URL;

let tasks = [];
let currentTaskIndex = -1;

function renderTaskTable(tasks)
{
    const tbody = document.querySelector('#taskTable tbody');
    tbody.innerHTML = '';

    tasks.forEach((task, index) => {
        const row = document.createElement('tr');

        row.innerHTML = `
            <td>${task.taskStatus}</td>
            <td class="d-none d-xl-table-cell">${task.taskDesc}</td>
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
    };

    if (currentTaskIndex === -1) {
        await addTask(task);
    } else {
        task.taskID = tasks[currentTaskIndex].taskID;
        await updateTask(task);
    }

    $('#taskModal').modal('hide');
    searchTask();
});

const addTask = async (formData) => {
    try {
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
    } catch (error) {
        console.error('Add Task failed: ', error);
        alert('Failed to add task: ' + error.message);
    }
};

const updateTask = async (formData) => {
    try {
        const task = {
            taskId: formData.taskId,  // Đảm bảo rằng taskId được truyền lên API
            taskStatus: formData.taskStatus,
            taskDesc: formData.taskDesc
        };

        const response = await fetch(`${HOST_IP}/api/tasks/${formData.taskId}`, {
            method: 'PATCH',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${TOKEN}`
            },
            body: JSON.stringify(task)  // Gửi task object lên server
        });

        if (!response.ok) {
            throw new Error('Failed to update Task');
        }

        const data = await response.json();
        tasks[currentTaskIndex] = data;  // Cập nhật task trong mảng tasks
        alert("Update Task Successfully");
    } catch (error) {
        console.error('Update Task failed: ', error);
        alert('Failed to update Task: ' + error.message);
    }
};




// const updateTask = async (formData) => {
//     try {
//         const response = await fetch(`${HOST_IP}/api/tasks/${formData.taskID}`, {
//             method: 'PATCH',
//             headers: {
//                 'Content-Type': 'application/json',
//                 'Authorization': `Bearer ${TOKEN}`
//             },
//             body: JSON.stringify(formData)
//         });

//         if (!response.ok) {
//             throw new Error('Failed to update task');
//         }

//         const data = await response.json();
//         tasks[currentTaskIndex] = data;
//         alert("Update Task Successfully");
//     } catch (error) {
//         console.error('Update Task failed: ', error);
//         alert('Failed to update task: ' + error.message);
//     }
// };

function delay(ms) {
    return new Promise(resolve => setTimeout(resolve, ms));
}

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