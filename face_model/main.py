from flask import Flask, request, jsonify
from flask_cors import CORS
from PIL import Image
import io
import os
from process_image import ImageProcessor
from s3_config.s3Config import S3Config
import logging

# Configure logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

app = Flask(__name__)
CORS(app)

file_location = os.path.abspath(__file__)  # Get current file abspath
root_directory = os.path.dirname(file_location)  # Get root dir
build_dir = os.path.join(root_directory, '..', 'build')

yolo_dir = "yolo_model/runs/detect/train/weights/best.pt"
yolo_path = os.path.join(root_directory, '..', 'build', yolo_dir)

s3Config = S3Config()

if not os.path.exists(yolo_path):
    s3Config.download_all_objects('yolo_model/', build_dir)

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
        logging.error(f"Error in /process: {str(e)}", exc_info=True)
        return jsonify({'error': f'Failed to process image: {str(e)}'}), 500

@app.route('/retrieve', methods=['POST'])
def retrieve_image():
    if 'image' not in request.files or 'customerName' not in request.form:
        return jsonify({'error': 'No image or customerName provided'}), 400
    
    file = request.files['image']
    customer_name = request.form['customerName']
    
    try:
        image = Image.open(io.BytesIO(file.read()))
        # Initialize new Image Processor instance with customer name
        image_processor_with_name = ImageProcessor(yolo_path, customer_name)
        result = image_processor_with_name.retrieve_image(image)
        return jsonify(result), 200
    except Exception as e:
        logging.error(f"Error in /retrieve: {str(e)}", exc_info=True)
        return jsonify({'error': f'Failed to retrieve image: {str(e)}'}), 500
    
@app.route('/verify', methods=['POST'])
def verify_images():
    if 'image' not in request.files:
        return jsonify({'error': 'No image provided'}), 400

    file = request.files['image']
    
    try:
        image_verify = Image.open(io.BytesIO(file.read()))
        result = image_processor.verify_images(image_verify)
        image_processor.plot_and_save_distances(os.path.join(build_dir, 'facenet_distance'))
        return jsonify(result), 200
    except Exception as e:
        logging.error(f"Error in /verify: {str(e)}", exc_info=True)
        return jsonify({'error': f'Failed to verify images: {str(e)}'}), 500

if __name__ == '__main__':
    cert_path = os.path.join(root_directory, 'ssl', 'tls.crt')
    key_path = os.path.join(root_directory, 'ssl', 'tls.key')
    app.run(host='0.0.0.0', port=5000, ssl_context=(cert_path, key_path))
