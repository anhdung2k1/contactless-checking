document.addEventListener('DOMContentLoaded', () => {
    const MODEL_URL = window.config.MODEL_URL;  // Define the base URL
    const HOST_IP = window.config.HOST_IP;
    const TOKEN = window.config.TOKEN;
    const uploadForm = document.getElementById('uploadForm');
    const imageInput = document.getElementById('imageInput');
    const video = document.getElementById('video');
    // const captureButton = document.getElementById('captureButton');
    const canvas = document.getElementById('canvas');
    const ctx = canvas.getContext('2d');
    // const submitCaptureButton = document.getElementById('submitCaptureButton');
    const captureAndSubmitButton = document.getElementById('captureAndSubmitButton');
    const resultCanvas = document.getElementById('resultCanvas');
    const resultCtx = resultCanvas.getContext('2d');

    // Start high-quality video stream for camera
    if (navigator.mediaDevices && navigator.mediaDevices.getUserMedia) {
        const constraints = {
            video: {
                facingMode: 'environment', // Use the rear camera (if available)
                width: { ideal: 1920 },  // Ideal width (Full HD)
                height: { ideal: 1080 }, // Ideal height (Full HD)
                frameRate: { ideal: 60 } // Ideal frame rate (60 fps)
            }
        };

        navigator.mediaDevices.getUserMedia(constraints)
            .then((stream) => {
                video.srcObject = stream;
                video.play();
            })
            .catch((error) => {
                console.error('Error accessing the camera: ', error);
            });
    }

    // Handle image upload form submission
    uploadForm.addEventListener('submit', async (event) => {
        event.preventDefault();
        const formData = new FormData();
        const file = imageInput.files[0];
        if (!file) {
            console.log('Please select an image file.');
            return;
        }
        formData.append('image', file);
        await sendImage(formData, file);
    });

    captureAndSubmitButton.addEventListener('click', async () => {
        canvas.width = video.videoWidth;
        canvas.height = video.videoHeight;
        ctx.drawImage(video, 0, 0, video.videoWidth, video.videoHeight);
        canvas.toBlob(async (blob) => {
            const formData = new FormData();
            formData.append('image', blob, 'captured_image.png');
            await sendImage(formData, blob);
        }, 'image/png');
    });

    async function sendImage(formData, imageSource) {
        try {
            const response = await fetch(`${MODEL_URL}/upload`, {  // Use the base URL
                method: 'POST',
                body: formData,
            });

            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }

            const data = await response.json();
            console.log('Upload response data:', data); // Log the response data
            customerNameList = [];

            if (data.status === 'success') {
                displayResults(data, imageSource);
                data.detections.forEach(detection => {
                    console.log("sendImage detection: ", detection);
                    const personDetected = verifyPerson(detection);
                    console.log("personDetected: ", personDetected);
                    if (personDetected) {
                        console.log(`Add person_name: ${detection.person_name} to customerNameList`);
                        customerNameList.push(detection.person_name);
                    }
                });
                if (customerNameList.length > 0) {
                    // Get All Tasks with List of Customer Name
                    getAllTasksByListCustomerName(customerNameList);
                }
            } else {
                console.error(`Error: ${data.message}`);
            }
        } catch (error) {
            console.error('Error in sendImage:', error); // Log the error
        }
    }

    function renderCustomerTaskModal(tasks) {
        const tbody = document.querySelector('#customerTaskTable tbody');
        tbody.innerHTML = '';

        if (tasks.length === 0) {
            tbody.innerHTML = `
                <tr>
                    <td colspan="5" style="text-align: center;">No tasks found</td>
                </tr>
            `;
            return;
        }

        document.getElementById('customerTaskModalLabel').innerText = 'Customer Task';
        tasks.forEach((task) => {
            const row = document.createElement('tr');
            row.innerHTML = `
                <td>${task.taskName}</td>
                <td class="d-none d-xl-table-cell">${task.taskDesc}</td>
                <td class="d-none d-xl-table-cell">${task.taskStatus}</td>
                <td class="d-none d-xl-table-cell">${task.customer ? task.customer.customerName : 'N/A'}</td>
                <td class="d-none d-xl-table-cell">${task.estimateHours ? task.estimateHours : 'N/A'}</td>
                <td class="d-none d-xl-table-cell">${task.logHours ? task.logHours : 'N/A'}</td>
            `;
            tbody.appendChild(row);
        });
    }

    function showCustomerTaskModal() {
        $('#customerTaskModal').modal('show');
    }

    function verifyPerson(data) {
        if (typeof data !== 'object' || data === null) {
            throw new Error('Invalid input: data must be a non-null object');
        }
    
        const { is_same_person = false, similarity = 0, person_name = 'Unknown' } = data;
    
        let recordData = "";
        let recordStatus = "";
    
        console.log(`is_same_person: ${is_same_person}, similarity: ${similarity}, person_name: ${person_name}`);
        if (is_same_person) {
            console.log(`Valid Person! Similarity: ${similarity}`);
            recordData = `${person_name} has checked in at ${getCurrentDate()}`;
            recordStatus = 'success';
        } else {
            console.log(`Invalid Person! Similarity: ${similarity}`);
            recordData = `${person_name} has failed to check in at ${getCurrentDate()}`;
            recordStatus = 'failed';
        }
    
        try {
            record(recordData, recordStatus);
            sendNotification(recordData);
        } catch (error) {
            console.error('Error during record or notification process:', error);
        }
    
        return is_same_person;
    }    

    async function getAllTasksByListCustomerName(customerNameList) {
        try {
            // Need to add new API from customerName list
            const query = encodeURIComponent(customerNameList.join(','));
            const response = await fetch(`${HOST_IP}/api/tasks/getTask?customerList=${query}`, {
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
            console.log(`getAllTasksByListCustomerName: ${data}`);
            showCustomerTaskModal();
            renderCustomerTaskModal(data);
        } catch (error) {
            console.error('Error in getTaskByCustomerName: ', error);
        }
    }

    async function record(recordData, status) {
        try {
            const response = await fetch(`${HOST_IP}/api/records`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${TOKEN}`
                },
                body: JSON.stringify({ recordData, status })
            });
            
            if (!response.ok) {
                console.log(`Error in response: ${response.status}, message: ${response.error}`)
                throw new Error(`HTTP error! status: ${response.status}`);
            }

            const data = await response.json();
            if (data) {
                console.log('Successfully recorded');
            }
        } catch (error) {
            console.error('Error in record:', error);
        }
    }

    async function sendNotification(message) {
        try {
            const response = await fetch(`${HOST_IP}/api/notifications`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${TOKEN}`
                },
                body: JSON.stringify(message)
            });
            
            if (!response.ok) {
                console.log(`Error in response: ${response.status}, message: ${response.error}`)
                throw new Error(`HTTP error! status: ${response.status}`);
            }

            const data = await response.json();
            if (data) {
                console.log('Successfully sent notification');
            }
        } catch (error) {
            console.error('Error in sendNotification:', error);
        }
    }

    function getCurrentDate() {
        const currentDate = new Date();

        const year = currentDate.getFullYear();
        const month = (currentDate.getMonth() + 1).toString().padStart(2, '0'); // Months are zero-based
        const day = currentDate.getDate().toString().padStart(2, '0');

        return `${year}-${month}-${day}`;
    }

    function displayResults(data, imageSource) {
        const image = new Image();

        image.onload = () => {
            resultCanvas.width = image.width;
            resultCanvas.height = image.height;
            resultCtx.drawImage(image, 0, 0);
            data.detections.forEach(detection => {
                const { bbox, confidence } = detection;
                const personName = detection.person_name;
                const validPerson = detection.is_same_person
                const [x1, y1, x2, y2] = bbox;
                resultCtx.strokeStyle = 'red';
                resultCtx.lineWidth = 2;
                resultCtx.strokeRect(x1, y1, x2 - x1, y2 - y1);
                resultCtx.fillStyle = 'red';
                resultCtx.font = '16px Arial';
                resultCtx.fillText(`confidence: (${confidence.toFixed(2)})`, x1, y1 - 10);
                resultCtx.fillText(`person_name: ${personName}`, x1, y1 - 30);
                resultCtx.fillText(`valid_person: ${validPerson}`, x1, y1 - 50);
            });
        };
        if (imageSource instanceof Blob) {
            image.src = URL.createObjectURL(imageSource);
        } else {
            const reader = new FileReader();
            reader.onload = () => {
                image.src = reader.result;
            };
            reader.readAsDataURL(imageSource);
        }
    }
});
