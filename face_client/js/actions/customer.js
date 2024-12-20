const MODEL_URL = window.config.MODEL_URL;

let customers = [];
let currentCustomerIndex = -1;

let currentPage = 0;
const pageSize = 5;

const imageList = document.getElementById('imageList'); 
let images = [];

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
                <div style="display: flex; justify-content: space-between; align-items: center;">
                    <div style="display: flex; flex-direction: column;">
                        <button class="btn btn-danger btn-sm" style="margin-bottom: 10px;" onclick="deleteCustomer(${index})">Delete</button>
                        <button class="btn btn-warning btn-sm" onclick="showUpdateCustomerModal(${index})">Update</button>
                    </div>
                    <button class="btn btn-primary btn-sm" style="margin-left: 10px;" onclick="getCheckInTime(${index})">CheckInTime</button>
                    <button class="btn btn-primary btn-sm" style="margin-left: 20px;" onclick="openCamera(${index})">Camera</button>
                </div>
            </td>
        `;

        tbody.appendChild(row);
    });
}

function renderCustomerCheckInTimeModal(customer) {
    const tbody = document.querySelector('#customerCheckInTable tbody');
    tbody.innerHTML = '';
    document.getElementById('customerCheckInTimeModalLabel').innerText = `Customer ${customer.customerName} Check In Time`
    customer.checkInTime.forEach(checkIn => {
        const row = document.createElement('tr');

        row.innerHTML = `
            <td>${customer.customerName}</td>
            <td class="d-none d-xl-table-cell">${checkIn}</td>
        `;
        tbody.appendChild(row);
    });
}

function showCustomerCheckInModal() {
    $('#customerCheckInTimeModal').modal('show')
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

// Delete Customer
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

// Show Check In time of Customer
async function getCheckInTime(index) {
    const customer = customers[index]
    try {
        const response = await fetch(`${HOST_IP}/api/customers/getCheckIn/${customer.customerID}`, {
            method: 'GET',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${TOKEN}`
            }
        });

        if (!response.ok) {
            throw new Error('Failed to get checkInTime of customer');
        }
        
        const data = await response.json();
        console.log(data);
        showCustomerCheckInModal();
        renderCustomerCheckInTimeModal(data);

    } catch (error) {
        console.error('Failed to fetch checkInTime ', error);
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

const addCustomer = async (formData) => {
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
};

const updateCustomer = async (formData) => {
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
};

function delay(ms) {
    return new Promise(resolve => setTimeout(resolve, ms));
}

const addCustomerImage = async (customerID, base64Image) => {
    try {
        const formData = { photoUrl: base64Image };

        const response = await fetch(`${HOST_IP}/api/customers/${customerID}`, {
            method: 'PATCH',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${TOKEN}`
            },
            body: JSON.stringify(formData)
        });

        if (!response.ok) {
            throw new Error('Failed to add customer Image');
        }

        const dataBool = await response.json();
        if (dataBool) {
            console.log("Add customer image successfully");
        }

        await delay(2000); // 2s delay for stable
    } catch (error) {
        console.error('Update Customer Image failed:', error);
        alert('Add Customer Image Failed: ' + error.message);
    }
};

const searchCustomer = async () => {
    const customerName = document.getElementById('searchInput').value;
    const query = customerName ? `${encodeURIComponent(customerName)}` : '';
    try {
        const response = await fetch(`${HOST_IP}/api/customers/query?query=${query}&page=${currentPage}&size=${pageSize}`, {
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
        customers = data.content; 
        renderCustomerTable(customers);

        renderPagination(data.totalPages, currentPage);

    } catch (error) {
        console.error('Get Customers failed: ', error);
        alert('Failed to get customers: ' + error.message);
    }
};

document.addEventListener('DOMContentLoaded', () => {
    searchCustomer(); // Fetch all customers when the page loads
});

// Open camera modal
function openCamera(index) {
    currentCustomerIndex = index; // Store the current customer index
    $('#cameraModal').modal('show');
    startVideo();
}

// Start video stream
async function startVideo() {
    const video = document.getElementById('video');
    const stream = await navigator.mediaDevices.getUserMedia({ video: true });
    video.srcObject = stream;
}

document.getElementById('captureButton').addEventListener('click', () => {
    const canvas = document.getElementById('canvas');
    const video = document.getElementById('video');
    const ctx = canvas.getContext('2d');

    // Resize canvas to match video size
    const maxWidth = 130;
    const scale = maxWidth / video.videoWidth;
    canvas.width = maxWidth;
    canvas.height = video.videoHeight * scale;

    ctx.drawImage(video, 0, 0, canvas.width, canvas.height);

    // Convert canvas to data URL (base64 format)
    const imageData = canvas.toDataURL('image/png');

    images.push(imageData);

    const imageContainer = createImageContainer(imageData);
    imageList.appendChild(imageContainer);

    canvas.classList.add('d-none');
    document.getElementById('downloadButton').classList.remove('d-none');
});



// Handle download captured image
document.getElementById('downloadButton').addEventListener('click', async () => {
    const canvas = document.getElementById('canvas');
    const customerName = customers[currentCustomerIndex].customerName;
    canvas.toBlob(async (blob) => {
        const formData = new FormData();
        formData.append('image', blob, 'captured_image.png');
        formData.append('customerName', customerName); // Append the customer's name
        await sendImageDataToModelHost(formData);

        // Send to API host base64 image
        const reader = new FileReader();
        reader.onload = function (e) {
            const base64Image = e.target.result;
            addCustomerImage(customers[currentCustomerIndex].customerID, base64Image);
        };
        reader.readAsDataURL(blob);
    }, 'image/png');
});

async function sendImageDataToModelHost(formData) {
    try {
        // This send to face_model host MODEL_URL to save in localhost for generating data for training
        const response = await fetch(`${MODEL_URL}/retrieve`, {
            method: 'POST',
            body: formData
        });

        const data = await response.json();
        if (data.status === 'success') {
            console.log('Download Image success');
        } else {
            alert(`Error: ${data.error}`);
        }
    } catch (error) {
        alert(`Error: ${error.message}`);
    }
}

document.addEventListener('DOMContentLoaded', () => {
    // Initial placeholder for adding images
    addPlaceholder();
});

function addPlaceholder() {
    const imageList = document.getElementById('imageList');

    const imageContainer = document.createElement('div');
    imageContainer.className = 'image-container mb-3';
    imageContainer.style.position = 'relative';
    imageContainer.style.display = 'flex';
    imageContainer.style.alignItems = 'center';
    imageContainer.style.justifyContent = 'center';
    imageContainer.style.marginRight = '10px';

    const imageInput = document.createElement('input');
    imageInput.type = 'file';
    imageInput.accept = 'image/*';
    imageInput.className = 'form-control';
    imageInput.multiple = false; // To handle one image at a time per input
    imageInput.style.display = 'none';
    imageContainer.appendChild(imageInput);

    const placeholder = document.createElement('div');
    placeholder.className = 'image-placeholder';
    placeholder.style.width = '100px';
    placeholder.style.height = '100px';
    placeholder.style.border = '2px dashed #ccc';
    placeholder.style.display = 'flex';
    placeholder.style.alignItems = 'center';
    placeholder.style.justifyContent = 'center';
    placeholder.style.cursor = 'pointer';
    placeholder.innerText = '+';
    imageContainer.appendChild(placeholder);

    imageList.appendChild(imageContainer);

    placeholder.addEventListener('click', () => {
        imageInput.click();
    });

    imageInput.addEventListener('change', (event) => {
        const file = event.target.files[0];
        if (file) {
            const reader = new FileReader();
            reader.onload = (e) => {
                placeholder.innerText = '';
                const img = document.createElement('img');
                img.src = e.target.result;
                img.style.width = '100px';
                img.style.height = '100px';
                img.style.objectFit = 'cover'; // Ensure image fits within the placeholder
                imageContainer.appendChild(img);
                imageContainer.removeChild(placeholder); // Remove placeholder after image is loaded

                // Add delete button
                const deleteButton = document.createElement('button');
                deleteButton.className = 'btn btn-danger btn-sm';
                deleteButton.style.position = 'absolute';
                deleteButton.style.top = '5px';
                deleteButton.style.right = '5px';
                deleteButton.innerText = 'X';
                imageContainer.appendChild(deleteButton);

                deleteButton.addEventListener('click', () => {
                    imageContainer.remove();
                    if (document.querySelectorAll('.image-placeholder').length === 0) {
                        addPlaceholder();
                    }
                });

                // Add a new placeholder for the next image
                addPlaceholder();
            };
            reader.readAsDataURL(file);
        }
    });
}

document.getElementById('uploadImagesButton').addEventListener('click', async () => {
    const customerName = customers[currentCustomerIndex].customerName;

    const fileInput = document.getElementById('imageUpload');
    const files = fileInput.files;

    for (const file of files) {
        const reader = new FileReader();
        reader.onload = function (e) {
            const base64Image = e.target.result;
            images.push(base64Image);

            const imageContainer = createImageContainer(base64Image);
            imageList.appendChild(imageContainer);
        };
        reader.readAsDataURL(file);
    }

    for (const imageData of images) {
        const formData = new FormData();
        formData.append('image', imageData);
        formData.append('customerName', customerName);

        await sendImageDataToModelHost(formData);
    }

    alert('All images uploaded successfully');
});


function renderPagination(totalPages, currentPage) {
    const paginationContainer = document.getElementById('pagination');
    paginationContainer.innerHTML = ''; 

    const prevButton = document.createElement('li');
    prevButton.classList.add('page-item');
    const prevLink = document.createElement('a');
    prevLink.classList.add('page-link');
    prevLink.innerText = 'Previous Page';
    prevLink.href = '#';
    prevLink.disabled = currentPage === 0;
    prevLink.addEventListener('click', (e) => {
        e.preventDefault();
        changePage(currentPage - 1);
    });
    prevButton.appendChild(prevLink);
    paginationContainer.appendChild(prevButton);

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

    const nextButton = document.createElement('li');
    nextButton.classList.add('page-item');
    const nextLink = document.createElement('a');
    nextLink.classList.add('page-link');
    nextLink.innerText = 'Next Page';
    nextLink.href = '#';
    nextLink.disabled = currentPage === totalPages - 1;
    nextLink.addEventListener('click', (e) => {
        e.preventDefault();
        changePage(currentPage + 1);
    });
    nextButton.appendChild(nextLink);
    paginationContainer.appendChild(nextButton);
}


function changePage(page) {
    currentPage = page;
    searchCustomer(); 
}

document.getElementById('searchInput').addEventListener('input', () => {
    currentPage = 0;
    searchCustomer();
});


function createImageContainer(base64Image) {
    const imageContainer = document.createElement('div');
    imageContainer.classList.add('image-container');
    imageContainer.style.position = 'relative';

    const img = document.createElement('img');
    img.src = base64Image;
    img.style.width = '100px';
    img.style.height = '100px';
    img.style.objectFit = 'cover';
    imageContainer.appendChild(img);

    const deleteButton = document.createElement('button');
    deleteButton.className = 'btn btn-danger btn-sm';
    deleteButton.style.position = 'absolute';
    deleteButton.style.top = '5px';
    deleteButton.style.right = '5px';
    deleteButton.innerText = 'X';
    imageContainer.appendChild(deleteButton);

    deleteButton.addEventListener('click', () => {
        const index = images.indexOf(base64Image);
        if (index > -1) images.splice(index, 1); 
        imageContainer.remove();
    });

    return imageContainer;
}