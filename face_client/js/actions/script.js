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
                frameRate: { ideal: 144 } // Ideal frame rate (30 fps)
            }
        };

        navigator.mediaDevices.getUserMedia(constraints)
            .then((stream) => {
                video.srcObject = stream;
                video.play();
            })
            .catch((error) => {
                console.error('Error accessing the camera: ', error);
                alert('Could not access the camera. Please check permissions.');
            });
    }

    // Handle image upload form submission
    uploadForm.addEventListener('submit', async (event) => {
        event.preventDefault();
        const formData = new FormData();
        const file = imageInput.files[0];
        if (!file) {
            alert('Please select an image file.');
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

            if (data.status === 'success') {
                displayResults(data, imageSource);
                data.detections.forEach(detection => {
                    console.log("sendImage detection: ", detection);
                    verifyPerson(detection);
                });
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
         // Use fallback values if data fields are undefined
        const isSamePerson = data.is_same_person !== undefined ? data.is_same_person : false;
        const similarity = data.similarity !== undefined ? data.similarity : 0;
        const personName = data.person_name || 'Unknown';

        console.log(`is_same_person: ${isSamePerson}, similarity: ${similarity}, person_name: ${personName}`);
        if (isSamePerson) {
            console.log(`Valid Person! Similarity: ${similarity}`);
            const recordData = `${personName} has checked in at ${getCurrentDate()}`;
            record(recordData, 'success');
            sendNotification(recordData);
            //TO DO: Show the Task Modal according to customer name if the customer is valid detected
            if (isSamePerson) {
                getTaskByCustomerName(personName);
            }
        } else {
            console.log(`Invalid Person! Similarity: ${similarity}`);
            const recordData = `${personName} has failed to check in at ${getCurrentDate()}`;
            record(recordData, 'failed');
            sendNotification(recordData);
        }
    }

    async function getTaskByCustomerName(customerName) {
        try {
            const query = encodeURIComponent(customerName);
            const response = await fetch(`${HOST_IP}/api/tasks/getTask/${query}`, {
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
            console.log(`getTaskByCustomerName ${customerName}: ${data}`);
            showCustomerTaskModal();
            renderCustomerTaskModal(data);
        } catch (error) {
            console.log('Error in getTaskByCustomerName: ' + customerName, error);
            alert(`Error in getTaskByCustomerName: ${customerName} ${error.message}`);
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
            alert(`Error: ${error.message}`);
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
            alert(`Error: ${error.message}`);
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
