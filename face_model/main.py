from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from PIL import Image
import io
import os
from process_image import ImageProcessor

app = Flask(__name__)
CORS(app)

file_location = os.path.abspath(__file__)  # Get current file abspath
root_directory = os.path.dirname(file_location)  # Get root dir

yolo_path = os.path.join(root_directory, '..', 'build/yolo_model/runs/detect/train/weights/best.pt')

# Initialize the ImageProcessor
image_processor = ImageProcessor(yolo_path)

@app.route('/upload', methods=['POST'])
def upload_image():
    if 'image' not in request.files:
        return jsonify({'error': 'No image provided'}), 400

    file = request.files['image']
    try:
        image = Image.open(io.BytesIO(file.read()))
        result = image_processor.process_image(image)
        return jsonify(result), 200
    except Exception as e:
        return jsonify({'error': f'Failed to process image: {str(e)}'}), 500

@app.route('/')
def serve_static_index():
    return send_from_directory(app.static_folder, 'index.html')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
