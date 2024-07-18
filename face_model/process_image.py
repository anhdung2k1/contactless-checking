import numpy as np
import os
import csv
from PIL import Image
from ultralytics import YOLO
from argface_model.argface_classifier import ArcFaceClassifier
import uuid
import torch
from torchvision import transforms
from facenet_pytorch import InceptionResnetV1
from facenet_main import FaceNetModel
from s3_config.s3Config import S3Config
import logging
import matplotlib.pyplot as plt

# Configure logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

file_location = os.path.abspath(__file__)  # Get current file abspath
root_directory = os.path.dirname(file_location)  # Get root dir

build_dir = os.path.join(root_directory, '..', 'build')
arcface_dataset = os.path.join(build_dir, 'arcface_train_dataset')
arcface_model_dir = os.path.join(build_dir, '.insightface')
model_save_path = os.path.join(build_dir, '.insightface/arcface_model.pth')
ground_truth_csv = os.path.join(build_dir, 'ground_truth_labels.csv')  # Path to ground truth CSV
# Face Net
facenet_model_dir = os.path.join(build_dir, 'face_net_train')
facenet_model_file_path = os.path.join(facenet_model_dir, 'facenet_model.pth')

class ImageProcessor:
    def __init__(self, yolo_model_path, person_name="UNKNOWN"):
        self.yolo_model = YOLO(yolo_model_path)
        self.argface_model = ArcFaceClassifier(arcface_dataset)
        self.person_name = person_name
        self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        self.s3Config = S3Config()
        self.distances = []
        
        if os.path.exists(facenet_model_file_path):
            self.facenet_trainer = FaceNetModel(device=self.device, save_path=facenet_model_file_path)
            self.facenet_trainer.load_model(facenet_model_file_path)
            self.facenet_model = self.facenet_trainer.model
            logging.info(f"Loaded FaceNet model from {facenet_model_file_path}")
        else:
            self.facenet_model = InceptionResnetV1(pretrained='vggface2').eval().to(self.device)
            logging.info("Using pretrained InceptionResnetV1 model")

    def verify_images(self, image2):
        try:
            logging.info("Starting verification process")

            customer_dir = os.path.join(arcface_dataset, self.person_name)
            if not os.path.exists(customer_dir):
                logging.error(f"Customer directory not found: {customer_dir}")
                return {'status': 'error', 'message': 'Customer not found'}

            customer_images = [f for f in os.listdir(customer_dir) if os.path.isfile(os.path.join(customer_dir, f))]
            if not customer_images:
                logging.error(f"No images found for the customer: {self.person_name}")
                return {'status': 'error', 'message': 'No images found for the customer'}

            first_image_path = os.path.join(customer_dir, customer_images[0])
            logging.info(f"Using first image for verification: {first_image_path}")

            preprocess = transforms.Compose([
                transforms.Resize((112, 112)),
                transforms.ToTensor(),
                transforms.Normalize([0.5, 0.5, 0.5], [0.5, 0.5, 0.5])
            ])

            image1 = Image.open(first_image_path).convert('RGB')
            if image2.mode != 'RGB':
                image2 = image2.convert('RGB')

            image1_tensor = preprocess(image1).unsqueeze(0).to(self.device)
            image2_tensor = preprocess(image2).unsqueeze(0).to(self.device)

            with torch.no_grad():
                embedding1 = self.facenet_model(image1_tensor).cpu().numpy()
                embedding2 = self.facenet_model(image2_tensor).cpu().numpy()
                
            logging.info(f"Embeddings shapes: {embedding1.shape}, {embedding2.shape}")

            if embedding1.shape != embedding2.shape:
                logging.error(f"Embedding shapes do not match: {embedding1.shape} vs {embedding2.shape}")
                return {'status': 'error', 'message': 'Embedding shapes do not match'}

            logging.info("Embeddings calculated for both images")

            distance = np.linalg.norm(embedding1 - embedding2).item()
            logging.info(f"Distance between embeddings: {distance}")

            threshold = 1.0

            is_same_person = distance < threshold
            logging.info("Images are of the same person" if is_same_person else "Images are of different persons")
            
            self.distances.append(distance)

            return {
                'status': 'success',
                'is_same_person': is_same_person,
                'person_name': self.person_name,
                'distance': distance
            }
        except Exception as e:
            logging.error(f"Error in verify_images: {str(e)}")
            return {
                'status': 'error',
                'message': str(e)
            }

    def process_image(self, image):
        logging.info("Starting image processing")

        if image.mode != 'RGB':
            image = image.convert('RGB')
        image_np = np.array(image)

        results = self.yolo_model(image_np)
        detections = []
        for result in results:
            for box in result.boxes:
                x1, y1, x2, y2 = map(int, box.xyxy[0])
                if box.cls == 0:
                    detections.append({
                        'bbox': (x1, y1, x2, y2),
                        'confidence': box.conf.item()
                    })

        for detection in detections:
            if os.path.isfile(model_save_path):
                self.argface_model.load_model()
            else:
                self.s3Config.download_all_objects('.insightface/', build_dir)
                self.argface_model.initialize_model()
                self.argface_model.extract_features()
                self.argface_model.train()
                self.argface_model.load_model()

            x1, y1, x2, y2 = detection['bbox']

            padding = 100
            x1 = max(0, x1 - padding)
            y1 = max(0, y1 - padding)
            x2 = min(image_np.shape[1], x2 + padding)
            y2 = min(image_np.shape[0], y2 + padding)

            face_roi = image_np[y1:y2, x1:x2]
            face_pil = Image.fromarray(face_roi)

            temp_face_path = f"/tmp/{uuid.uuid4()}.png"
            face_pil.save(temp_face_path)

            try:
                self.person_name = self.argface_model.identify_person(temp_face_path)
                detection['person_name'] = self.person_name
                logging.info(f"Person identified: {self.person_name}")
            except Exception as e:
                detection['person_name'] = "Unknown"
                logging.error(f"Error identifying person: {e}")

            os.remove(temp_face_path)

        logging.info(f"Image processing complete with {len(detections)} detections")
        return {
            'status': 'success',
            'message': 'Image processed',
            'detections': detections,
            'embeddings': len(detections)
        }

    def retrieve_image(self, image):
        logging.info("Starting image retrieval")

        result_dir = arcface_dataset
        if not os.path.exists(result_dir):
            os.makedirs(result_dir)
            logging.info(f"Directory {result_dir} created.")
        else:
            logging.info(f"Directory {result_dir} already exists.")

        label_dir = os.path.join(result_dir, self.person_name)
        if not os.path.exists(label_dir):
            os.makedirs(label_dir)
            logging.info(f"Directory {label_dir} created.")
        else:
            logging.info(f"Directory {label_dir} already exists.")

        if image.mode != 'RGB':
            image = image.convert('RGB')

        face_img = f"{self.person_name}_{uuid.uuid4()}.png"
        face_save_path = os.path.join(label_dir, face_img)
        image.save(face_save_path)
        logging.info(f"Saved processed face image to {face_save_path}")

        return {
            'status': 'success',
            'message': 'Image downloaded'
        }
    
    def plot_and_save_distances(self, save_path):
        # Create directory if it does not exist
        save_dir = os.path.dirname(save_path)
        if not os.path.exists(save_dir):
            os.makedirs(save_dir)
            logging.info(f"Directory {save_dir} created.")
        else:
            logging.info(f"Directory {save_dir} already exists.")
        
        plt.figure(figsize=(10, 5))
        plt.plot(self.distances, marker='o', linestyle='-')
        plt.title('Distances Between Image Embeddings')
        plt.xlabel('Image Pair Index')
        plt.ylabel('Distance')
        plt.grid(True)
        plt.savefig(save_path)
        logging.info(f"Plot saved to {save_path}")