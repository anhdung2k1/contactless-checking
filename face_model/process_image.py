import os
import tempfile
import numpy as np
import uuid
import torch
from PIL import Image
from ultralytics import YOLO
from argface_model.argface_classifier import ArcFaceClassifier
from facenet_model.facenet_model import FaceNetModel
from logger import info, error

file_location = os.path.abspath(__file__)  # Get current file abspath
root_directory = os.path.dirname(file_location)  # Get root dir

build_dir = os.path.join(root_directory, '..', 'build')
arcface_dataset = os.path.join(build_dir, 'arcface_train_dataset')
arcface_model_dir = os.path.join(build_dir, '.insightface')
model_save_path = os.path.join(arcface_model_dir, 'arcface_model.pth')
# Face Net
facenet_model_dir = os.path.join(build_dir, 'face_net_train')
facenet_model_file_path = os.path.join(facenet_model_dir, 'facenet_model.pth')

class ImageProcessor:
    def __init__(self, yolo_model_path, person_name="UNKNOWN"):
        self.argface_model = ArcFaceClassifier(arcface_dataset, arcface_model_dir, model_save_path)
        self.person_name = person_name
        self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        self.yolo_model = YOLO(yolo_model_path).to(self.device)
        self.distances = []
        self.facenet_model = FaceNetModel(image_path=arcface_dataset, model_file_path=facenet_model_file_path, save_path=facenet_model_dir)

    def verify_images(self, image_path):
        try:
            info("Starting verification process")
            
            customer_dir = os.path.join(arcface_dataset, self.person_name)
            if not os.path.exists(customer_dir):
                error(f"Customer directory not found: {customer_dir}")
                return {'status': 'error', 'message': 'Customer not found'}

            customer_images = [f for f in os.listdir(customer_dir) if os.path.isfile(os.path.join(customer_dir, f))]
            if not customer_images:
                error(f"No images found for the customer: {self.person_name}")
                return {'status': 'error', 'message': 'No images found for the customer'}

            first_image_path = os.path.join(customer_dir, customer_images[0])
            info(f"Using first image for verification: {first_image_path}")

            # Get embeddings for the first customer image and the provided image
            embeddings = self.facenet_model.get_embeddings([first_image_path, image_path])

            if embeddings.shape[0] != 2:
                error("Failed to calculate embeddings for both images.")
                return {'status': 'error', 'message': 'Failed to calculate embeddings for both images'}

            embedding1, embedding2 = embeddings[0], embeddings[1]
            info("Embeddings calculated for both images")

            # Calculate Euclidean distance (lower indicates more similarity)
            similarity = np.linalg.norm(embedding1 - embedding2)
            info(f"Euclidean distance between embeddings: {similarity}")

            # Decide based on a threshold
            threshold = 1.5
            is_same_person = similarity < threshold
            info("Images are of the same person" if is_same_person else "Images are of different persons")

            self.distances.append(similarity)

            return {
                'is_same_person': bool(is_same_person),
                'similarity': float(similarity)
            }
        except Exception as e:
            raise ValueError(f"Error in verify_images: {str(e)}")

    def process_image(self, image):
        info("Starting image processing")

        if image.mode != 'RGB':
            image = image.convert('RGB')
        image_np = np.array(image)

        results = self.yolo_model(image_np)
        detections = []
        is_same_person = False
        similarity = 0.0
        embedding_count = 0
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

            with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as temp_face_file:
                face_pil.save(temp_face_file.name)
                temp_face_path = temp_face_file.name

            try:
                info(f"Processing face at path: {temp_face_path}")
                self.person_name = self.argface_model.identify_person(temp_face_path)            
            except Exception as e:
                error_msg = str(e)
                error("Debug: Model device: {}".format(self.argface_model.model.device))
                error("Debug: Tensor device in identify_person method was likely incorrect.")
                self.person_name = "Unknown"
                error(f"Error identifying person: {error_msg}")

            if self.person_name != 'Unknown':
                info('Validating person...')
                validate_person = self.verify_images(temp_face_path)
                is_same_person = validate_person['is_same_person']
                similarity = validate_person['similarity']
                embedding_count += 1
                info(f"is_same_person: {is_same_person}")
                info(f"similarity: {similarity}")
                detection['is_same_person'] = is_same_person
                detection['similarity'] = similarity
                detection['person_name'] = self.person_name

            os.remove(temp_face_path)
            info(f"Person identified: {self.person_name}")

        info(f"Image processing complete with {len(detections)} detections")

        return {
            'status': 'success',
            'message': 'Image processed',
            'detections': detections,
            'embeddings': embedding_count
        }
    
    def retrieve_image(self, image):
        """Save the processed image to the local directory."""
        info("Starting image retrieval")
        label_dir = os.path.join(arcface_dataset, self.person_name)
        os.makedirs(label_dir, exist_ok=True)
        face_img = f"{self.person_name}_{uuid.uuid4()}.png"
        face_save_path = os.path.join(label_dir, face_img)
        image.convert('RGB').save(face_save_path)
        info(f"Saved processed face image to {face_save_path}")
        return {'status': 'success', 'message': 'Image downloaded'}
