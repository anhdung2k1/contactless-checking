const MODEL_URL = window.config.BASE_URL;  // Define the base URL

document.addEventListener('DOMContentLoaded', () => {
    const uploadForm = document.getElementById('uploadForm');
    const imageInput = document.getElementById('imageInput');
    const video = document.getElementById('video');
    const captureButton = document.getElementById('captureButton');
    const canvas = document.getElementById('canvas');
    const ctx = canvas.getContext('2d');
    const submitCaptureButton = document.getElementById('submitCaptureButton');
    const downloadButton = document.getElementById('downloadButton');
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
        downloadButton.classList.remove('d-none');
    });

    // Handle captured image submission
    submitCaptureButton.addEventListener('click', async () => {
        canvas.toBlob(async (blob) => {
            const formData = new FormData();
            formData.append('image', blob, 'captured_image.png');
            await sendImage(formData, blob);
        }, 'image/png');
    });

    // Handle download captured image
    downloadButton.addEventListener('click', async () => {
        canvas.toBlob(async (blob) => {
            const formData = new FormData();
            formData.append('image', blob, 'captured_image.png');
            await downloadImage(formData);
        }, 'image/png');
    });

    async function sendImage(formData, imageSource) {
        try {
            const response = await fetch(`${MODEL_URL}/upload`, {  // Use the base URL
                method: 'POST',
                body: formData,
            });

            const data = await response.json();
            if (data.status === 'success') {
                displayResults(data, imageSource);
            } else {
                alert(`Error: ${data.error}`);
            }
        } catch (error) {
            alert(`Error: ${error.message}`);
        }
    }
    
    async function downloadImage(formData) {
        try {
            const response = await fetch(`${MODEL_URL}/retrieve`, {
                method: 'POST',
                body: formData
            });

            const data = await response.json();
            if (data.status === 'success') {
                alert('Download Image success');
            } else {
                alert(`Error: ${data.error}`);
            }
        } catch (error) {
            alert(`Error: ${error.message}`);
        }
    }

    function displayResults(data, imageSource) {
        const image = new Image();
        image.onload = () => {
            resultCanvas.width = image.width;
            resultCanvas.height = image.height;
            resultCtx.drawImage(image, 0, 0);
            data.detections.forEach(detection => {
                const { bbox, confidence, person_name } = detection;
                const [x1, y1, x2, y2] = bbox;
                resultCtx.strokeStyle = 'red';
                resultCtx.lineWidth = 2;
                resultCtx.strokeRect(x1, y1, x2 - x1, y2 - y1);
                resultCtx.fillStyle = 'red';
                resultCtx.font = '16px Arial';
                resultCtx.fillText(`confidence: (${confidence.toFixed(2)})`, x1, y1 - 10);
                resultCtx.fillText(`person_name: ${person_name}`, x1, y1 - 30);
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