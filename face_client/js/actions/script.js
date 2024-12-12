document.addEventListener('DOMContentLoaded', () => {
    const MODEL_URL = window.config.MODEL_URL;  // Define the base URL
    const HOST_IP = window.config.HOST_IP;
    const TOKEN = window.config.TOKEN;
    const uploadForm = document.getElementById('uploadForm');
    const imageInput = document.getElementById('imageInput');
    const video = document.getElementById('video');
    const captureButton = document.getElementById('captureButton');
    const canvas = document.getElementById('canvas');
    const ctx = canvas.getContext('2d');
    const submitCaptureButton = document.getElementById('submitCaptureButton');
    const resultCanvas = document.getElementById('resultCanvas');
    const resultCtx = resultCanvas.getContext('2d');

    // Start video stream for camera
    if (navigator.mediaDevices && navigator.mediaDevices.getUserMedia) {
        navigator.mediaDevices.getUserMedia({ video: true }).then((stream) => {
            video.srcObject = stream;
            video.play();
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

    // Capture image from video stream
    captureButton.addEventListener('click', () => {
        canvas.width = video.videoWidth;
        canvas.height = video.videoHeight;
        ctx.drawImage(video, 0, 0, video.videoWidth, video.videoHeight);
        canvas.classList.remove('d-none');
        submitCaptureButton.classList.remove('d-none');
    });

    // Handle captured image submission
    submitCaptureButton.addEventListener('click', async () => {
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
                verifyPerson(data);
            } else {
                console.error(`Error: ${data.message}`);
            }
        } catch (error) {
            console.error('Error in sendImage:', error); // Log the error
        }
    }

    function verifyPerson(data) {
         // Use fallback values if data fields are undefined
        const isSamePerson = data.is_same_person !== undefined ? data.is_same_person : false;
        const similarity = data.similarity !== undefined ? data.similarity : 0;
        const personName = data.person_name || 'Unknown';

        console.log(`is_same_person: ${isSamePerson}, similarity: ${similarity}, person_name: ${personName}`);
        if (isSamePerson) {
            alert(`Valid Person! Similarity: ${similarity}`);
            const recordData = `${personName} has checked in at ${getCurrentDate()}`;
            record(recordData, 'success');
            sendNotification(recordData);
            //TO DO: 
            
        } else {
            alert(`Invalid Person! Similarity: ${similarity}`);
            const recordData = `${personName} has failed to check in at ${getCurrentDate()}`;
            record(recordData, 'failed');
            sendNotification(recordData);
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
        const personName = data.person_name || 'Unknown';

        image.onload = () => {
            resultCanvas.width = image.width;
            resultCanvas.height = image.height;
            resultCtx.drawImage(image, 0, 0);
            data.detections.forEach(detection => {
                const { bbox, confidence } = detection;
                const [x1, y1, x2, y2] = bbox;
                resultCtx.strokeStyle = 'red';
                resultCtx.lineWidth = 2;
                resultCtx.strokeRect(x1, y1, x2 - x1, y2 - y1);
                resultCtx.fillStyle = 'red';
                resultCtx.font = '16px Arial';
                resultCtx.fillText(`confidence: (${confidence.toFixed(2)})`, x1, y1 - 10);
                resultCtx.fillText(`person_name: ${personName}`, x1, y1 - 30);
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
