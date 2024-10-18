from flask import Flask, request, jsonify
from flask_cors import CORS
from PIL import Image
import io
import os
from process_image import ImageProcessor
from s3_config.s3Config import S3Config
from logger import info, debug, error
from argface_model.argface_classifier import ArcFaceClassifier
from facenet_model.facenet_model import FaceNetModel


app = Flask(__name__)
CORS(app)

file_location = os.path.abspath(__file__)  # Get current file abspath
root_directory = os.path.dirname(file_location)  # Get root dir
build_dir = os.path.join(root_directory, '..', 'build')
arcface_dataset = os.path.join(build_dir, 'arcface_train_dataset')
arcface_model_dir = os.path.join(build_dir, '.insightface')

yolo_root_dir = os.path.join(build_dir, 'yolo_model')
yolo_dir = "yolo_model/runs/detect/train/weights/best.pt"
yolo_path = os.path.join(root_directory, '..', 'build', yolo_dir)

# Export AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY, AWS_DEFAULT_REGION in your env
s3Config = S3Config()

if not os.path.exists(build_dir):
    # Create build_dir if is not exist
    info(f"Create {build_dir}")
    os.makedirs(build_dir)

if not os.path.exists(yolo_root_dir):
    info(f"Create {yolo_root_dir} folder")
    os.makedirs(yolo_root_dir)

if not os.path.exists(yolo_path):
    info(f"Create {yolo_path} folder")
    s3Config.download_all_objects('yolo_model/', build_dir)
    
if not os.path.exists(arcface_dataset):
    info(f"{arcface_dataset} not found. Downloading from S3...")
    s3Config.download_all_objects('arcface_train_dataset/', build_dir)

# Initialize the ImageProcessor
image_processor = ImageProcessor(yolo_path)

@app.route('/upload', methods=['POST'])
def upload_image():
    if 'image' not in request.files:
        return jsonify({'error': 'No image provided'}), 400

    file = request.files['image']
    debug(f"file: {file}")
    try:
        image = Image.open(io.BytesIO(file.read()))
        result = image_processor.process_image(image)
        debug("/upload: {result}")
        return jsonify(result), 200
    except Exception as e:
        error(f"Error in /process: {str(e)}", exc_info=True)
        return jsonify({'error': f'Failed to process image: {str(e)}'}), 500

@app.route('/retrieve', methods=['POST'])
def retrieve_image():
    if 'image' not in request.files or 'customerName' not in request.form:
        return jsonify({'error': 'No image or customerName provided'}), 400
    
    file = request.files['image']
    customer_name = request.form['customerName']
    debug(f"File: {file} \ncustomer_name: {customer_name}")
    
    try:
        image = Image.open(io.BytesIO(file.read()))
        # Initialize new Image Processor instance with customer name
        image_processor_with_name = ImageProcessor(yolo_path, customer_name)
        result = image_processor_with_name.retrieve_image(image)
        debug(f"/retrieve: {result}")
        return jsonify(result), 200
    except Exception as e:
        error(f"Error in /retrieve: {str(e)}", exc_info=True)
        return jsonify({'error': f'Failed to retrieve image: {str(e)}'}), 500
    
@app.route('/verify', methods=['POST'])
def verify_images():
    if 'image' not in request.files:
        return jsonify({'error': 'No image provided'}), 400

    file = request.files['image']
    debug(f"file: {file}")
    try:
        image_verify = Image.open(io.BytesIO(file.read()))
        result = image_processor.verify_images(image_verify)
        image_processor.plot_and_save_distances(os.path.join(build_dir, 'facenet_distance'))
        debug(f"Result: {result}")
        return jsonify(result), 200
    except Exception as e:
        error(f"Error in /verify: {str(e)}", exc_info=True)
        return jsonify({'error': f'Failed to verify images: {str(e)}'}), 500

@app.route('/train', methods=['POST'])
def train_images():
    data = request.get_json()
    variable_key = data.get('variableKey')
    variable_value = data.get('variableValue')

    config = dict(zip(variable_key, variable_value))
    num_epochs = int(config.get("NUM_EPOCHS"))
    learning_rate = float(config.get("LEARNING_RATE"))
    momentum = float(config.get("MOMENTUM"))
    debug(f"config: {config}")
    
    if not os.path.exists(arcface_dataset):
        error(f"{arcface_dataset} not found. Downloading from S3...")
        s3Config.download_all_objects('arcface_train_dataset/', build_dir)

    # Import ArcFace Model
    classifier = ArcFaceClassifier(arcface_dataset)
    if classifier.model_exists():
        info("Loading existing model and continuing training.")
        classifier.load_model()
        classifier.extract_features()
    else:
        info("Initializing and training the model.")
        classifier.initialize_model()
        classifier.extract_features()
    classifier.train(num_epochs=num_epochs, lr=learning_rate, momentum=momentum)
    classifier.plot_training_metrics(os.path.join(arcface_model_dir, 'arcface_train_loss'))

    #Import FaceNet Model
    faceNetModel = FaceNetModel(arcface_dataset)
    faceNetModel.train()
    return jsonify({'status': 'success', 'message': 'Model trained success'}), 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
