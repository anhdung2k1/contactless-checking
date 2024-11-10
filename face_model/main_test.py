from process_image import ImageProcessor
from argface_model.argface_classifier import ArcFaceClassifier
from facenet_model.facenet_model import FaceNetModel
import os
from PIL import Image, ImageDraw, ImageFont
from s3_config.s3Config import S3Config
from logger import info, error

file_location = os.path.abspath(__file__)  # Get current file abspath
root_directory = os.path.dirname(file_location)  # Get root dir
build_dir = os.path.join(root_directory, '..', 'build')

# ArcFace
arcface_dataset = os.path.join(build_dir, 'arcface_train_dataset')
arcface_model = os.path.join(build_dir, '.insightface')
arcface_model_save = os.path.join(arcface_model, 'arcface_model.pth')

# Yolo
yolo_dir = "yolo_model/train/weights/best.pt"
yolo_path = os.path.join(build_dir, yolo_dir)

# FaceNet
faceNet_model_save = os.path.join(build_dir, 'face_net_train')
faceNet_model = os.path.join(faceNet_model_save, 'facenet_model.pth')

def save_detected_image(image, result, output_path):
    # Ensure the image is in RGB mode
    if image.mode == 'RGBA':
        image = image.convert('RGB')

    draw = ImageDraw.Draw(image)
    
    # Use the default font with the default size
    font = ImageFont.load_default()
    text_color = (0, 255, 0)  # Green color in RGB

    for detection in result['detections']:
        bbox = detection['bbox']
        person_name = result['person_name']
        confidence = detection.get('confidence', 0)

        # Draw the bounding box and text
        draw.rectangle(bbox, outline='red', width=2)
        draw.text((bbox[0], bbox[1] - 10), f"{person_name} ({confidence:.2f})", fill=text_color, font=font)
    
    # Ensure the output directory exists
    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    try:
        image.save(output_path)
        info(f"Saved detected image to {output_path}")
    except Exception as e:
        error(f"Error saving image {output_path}: {e}")

def main():
    if not os.path.exists(arcface_dataset):
        # Export AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY, AWS_DEFAULT_REGION in your env
        s3Config = S3Config()
        error(f"{arcface_dataset} not found. Downloading from S3...")
        s3Config.download_all_objects('arcface_train_dataset/', build_dir)
    classifier = ArcFaceClassifier(arcface_dataset, arcface_model_dir=arcface_model, model_save_path=arcface_model_save)
    if classifier.model_exists():
            info("Loading existing model and continuing training.")
            classifier.load_model()
            classifier.extract_features()
    else:
        info("Initializing and training the model.")
        classifier.initialize_model()
        classifier.extract_features()
    classifier.train(num_epochs=50, lr=0.001, momentum=0.9)
    info("Training completed.")
    classifier.plot_training_metrics(os.path.join(arcface_model, 'arcface_train_loss'))
    
    facenet_model = FaceNetModel(image_path=arcface_dataset, batch_size=32, lr=0.001, 
                                 num_epochs=20, save_path=faceNet_model_save, 
                                 model_file_path=faceNet_model)
    facenet_model.train()
    
    distances, labels = facenet_model.verify_images(threshold=0.5)
    info(f"Verification Results: {len(distances)} comparisons made.")
    info(f"Distances: {distances}")
    info(f"Labels: {labels}")

    image_processor = ImageProcessor(yolo_path)

    valid_extensions = ('.jpg', '.jpeg', '.png', '.bmp')  # Add more extensions if needed
    for label_name in os.listdir(arcface_dataset):
        label_path = os.path.join(arcface_dataset, label_name)
        if os.path.isdir(label_path):
            for image_name in os.listdir(label_path):
                image_path = os.path.join(label_path, image_name)
                if os.path.isfile(image_path) and image_path.lower().endswith(valid_extensions):
                    try:
                        image = Image.open(image_path)
                        result = image_processor.process_image(image)
                        info(f"Result: {result}")
                        
                        # Save the detected image with bounding boxes
                        save_detected_image(image, result, os.path.join(build_dir, 'output', image_name))
                    except Exception as e:
                        error(f"Error processing image {image_name}: {e}")

if __name__ == '__main__':
    main()