import os
import uuid
import numpy as np
import torch
from PIL import Image
from torchvision import transforms
from ultralytics import YOLO
from facenet_pytorch import InceptionResnetV1
from argface_model.argface_classifier import ArcFaceClassifier
from facenet_model.facenet_model import FaceNetModel
from logger import info, error
import matplotlib.pyplot as plt

# File and directory configurations
file_location = os.path.abspath(__file__)
root_directory = os.path.dirname(file_location)
build_dir = os.path.join(root_directory, '..', 'build')
arcface_dataset = os.path.join(build_dir, 'arcface_train_dataset')
arcface_model_dir = os.path.join(build_dir, '.insightface')
model_save_path = os.path.join(arcface_model_dir, 'arcface_model.pth')
facenet_model_dir = os.path.join(build_dir, 'face_net_train')
facenet_model_file_path = os.path.join(facenet_model_dir, 'facenet_model.pth')

class ImageProcessor:
    def __init__(self, yolo_model_path, person_name="UNKNOWN"):
        self.yolo_model = YOLO(yolo_model_path)
        self.argface_model = ArcFaceClassifier(arcface_dataset)
        self.person_name = person_name
        self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        self.distances = []
        self._initialize_facenet_model()

    def _initialize_facenet_model(self):
        """Initialize the FaceNet model."""
        if os.path.exists(facenet_model_file_path):
            self.facenet_trainer = FaceNetModel(device=self.device, save_path=facenet_model_file_path)
            self.facenet_model = self.facenet_trainer.model
            info(f"Loaded FaceNet model from {facenet_model_file_path}")
        else:
            self.facenet_model = InceptionResnetV1(pretrained='vggface2').eval().to(self.device)
            info("Using pretrained InceptionResnetV1 model")

    def _preprocess_image(self, image):
        """Preprocess the image for model input."""
        if image.mode != 'RGB':
            image = image.convert('RGB')
        preprocess = transforms.Compose([
            transforms.Resize((112, 112)),
            transforms.ToTensor(),
            transforms.Normalize([0.5, 0.5, 0.5], [0.5, 0.5, 0.5])
        ])
        return preprocess(image).unsqueeze(0).to(self.device)

    def verify_images(self, image2):
        """Verify if the input image matches the customer's saved images."""
        try:
            info("Starting verification process")

            # Check customer directory and images
            customer_dir = os.path.join(arcface_dataset, self.person_name)
            if not os.path.exists(customer_dir):
                error(f"Customer directory not found: {customer_dir}")
                return {'status': 'error', 'message': 'Customer not found'}

            customer_images = [f for f in os.listdir(customer_dir) if os.path.isfile(os.path.join(customer_dir, f))]
            if not customer_images:
                error(f"No images found for the customer: {self.person_name}")
                return {'status': 'error', 'message': 'No images found for the customer'}

            # Preprocess images
            first_image_path = os.path.join(customer_dir, customer_images[0])
            info(f"Using first image for verification: {first_image_path}")
            image1_tensor = self._preprocess_image(Image.open(first_image_path))
            image2_tensor = self._preprocess_image(image2)

            # Calculate embeddings
            with torch.no_grad():
                embedding1 = self.facenet_model(image1_tensor).cpu().numpy()
                embedding2 = self.facenet_model(image2_tensor).cpu().numpy()
                
            if embedding1.shape != embedding2.shape:
                error(f"Embedding shapes do not match: {embedding1.shape} vs {embedding2.shape}")
                return {'status': 'error', 'message': 'Embedding shapes do not match'}

            distance = np.linalg.norm(embedding1 - embedding2).item()
            info(f"Distance between embeddings: {distance}")

            # Determine if the images belong to the same person
            threshold = 0.5
            is_same_person = distance < threshold
            info("Images are of the same person" if is_same_person else "Images are of different persons")
            
            self.distances.append(distance)

            return {
                'status': 'success',
                'is_same_person': is_same_person,
                'person_name': self.person_name,
                'distance': distance
            }
        except Exception as e:
            error(f"Error in verify_images: {str(e)}")
            return {'status': 'error', 'message': str(e)}

    def process_image(self, image):
        """Detect faces in the image and identify the person."""
        try:
            info("Starting image processing")
            image_np = np.array(image.convert('RGB'))
            total_crops, total_boxes, total_scores, total_cls = self._detect_faces(image_np)

            # Check if any faces were detected
            if not total_boxes or len(total_boxes[0]) == 0:
                info("No faces detected in the image.")
                return {
                    'status': 'success',
                    'message': 'No faces detected',
                    'detections': [],
                    'embeddings': 0
                }

            for crop, box, score, cls in zip(total_crops[0], total_boxes[0], total_scores[0], total_cls[0]):
                detection_data = {'bbox': box, 'score': score, 'class': cls}
                self._identify_person(detection_data, image_np)

            info(f"Image processing complete with {len(total_boxes[0])} detections")
            return {
                'status': 'success',
                'message': 'Image processed',
                'detections': total_boxes[0],
                'embeddings': len(total_boxes[0])
            }
        except Exception as e:
            error(f"Error in process_image: {str(e)}")
            return {'status': 'error', 'message': str(e)}

    def _detect_faces(self, image_np, box_format='xyxy', th=0.5):
        """Run YOLO model to detect faces in the image."""
        try:
            total_crops = []
            total_boxes = []
            total_scores = []
            total_cls = []

            # Run YOLO model to get predictions
            results = self.yolo_model.predict(image_np, stream=False, verbose=False)

            for i, image_result in enumerate(results):
                filtered_crops = []
                filtered_boxes = []
                filtered_scores = []
                filtered_cls = []

                # Get the corresponding image
                img = image_np if isinstance(image_np, list) else [image_np]
                img = img[i]
                img_h, img_w = img.shape[:2]

                # Extract bounding boxes, scores, and classes
                if box_format == 'xyxy':
                    image_boxes = image_result.boxes.xyxy.cpu().numpy()
                elif box_format == 'xywh':
                    image_boxes = image_result.boxes.xyxy.cpu().numpy()
                    image_boxes = [[round(x1), round(y1), round(np.abs(x1-x2)), round(np.abs(y1-y2))] for x1, y1, x2, y2 in image_boxes]
                elif box_format == 'xyxyn':
                    image_boxes = image_result.boxes.xyxyn.cpu().numpy()
                elif box_format == 'xywhn':
                    image_boxes = image_result.boxes.xyxyn.cpu().numpy()
                    image_boxes = [[float(x1), float(y1), float(np.abs(x1-x2)), float(np.abs(y1-y2))] for x1, y1, x2, y2 in image_boxes]

                image_scores = image_result.boxes.conf.cpu().numpy()
                image_cls = image_result.boxes.cls.cpu().numpy()

                # Filter the results based on the threshold
                for j in range(len(image_boxes)):
                    (x1, y1, x2, y2), score, c = image_boxes[j], image_scores[j], image_cls[j]
                    if score >= th:
                        filtered_scores.append(score)
                        filtered_cls.append(c)
                        if box_format == 'xyxy':
                            filtered_crops.append(Image.fromarray(img[int(y1):int(y2), int(x1):int(x2)]))
                            filtered_boxes.append([int(x1), int(y1), int(x2), int(y2)])
                        elif box_format == 'xyxyn':
                            filtered_crops.append(Image.fromarray(img[int(y1 * img_h):int(y2 * img_h), int(x1 * img_w):int(x2 * img_w)]))
                            filtered_boxes.append([float(x1), float(y1), float(x2), float(y2)])
                        elif box_format == 'xywh':
                            filtered_crops.append(Image.fromarray(img[int(y1):int(y1 + y2), int(x1):int(x1 + x2)]))
                            filtered_boxes.append([int(x1), int(y1), int(x2), int(y2)])
                        elif box_format == 'xywhn':
                            filtered_crops.append(Image.fromarray(img[int(y1 * img_h):int((y1 + y2) * img_h), int(x1 * img_w):int((x1 + x2) * img_w)]))
                            filtered_boxes.append([float(x1), float(y1), float(x2), float(y2)])

                total_crops.append(filtered_crops)
                total_boxes.append(filtered_boxes)
                total_scores.append(filtered_scores)
                total_cls.append(filtered_cls)

            return total_crops, total_boxes, total_scores, total_cls
        except Exception as e:
            error(f"Error in _detect_faces: {str(e)}")
            return [], [], [], []

    def _identify_person(self, detection, image_np):
        """Identify the person in the detected face."""
        x1, y1, x2, y2 = detection['bbox']
        face_roi = self._extract_face(image_np, x1, y1, x2, y2)
        temp_face_path = f"/tmp/{uuid.uuid4()}.png"
        face_roi.save(temp_face_path)

        try:
            self.person_name = self.argface_model.identify_person(temp_face_path)
            detection['person_name'] = self.person_name
            info(f"Person identified: {self.person_name}")
        except Exception as e:
            detection['person_name'] = "Unknown"
            error(f"Error identifying person: {str(e)}")
            info("Set person name to 'Unknown' due to identification error.")
        finally:
            try: 
                os.remove(temp_face_path) 
            except Exception as e: 
                error(f"Error deleting temp file: {str(e)}")

    def _extract_face(self, image_np, x1, y1, x2, y2, padding=100):
        """Extract and return a face region from the image with padding."""
        h, w = image_np.shape[:2]
        x1 = max(0, x1 - padding)
        y1 = max(0, y1 - padding)
        x2 = min(w, x2 + padding)
        y2 = min(h, y2 + padding)
        face_roi = Image.fromarray(image_np[y1:y2, x1:x2])
        return face_roi

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

    def plot_and_save_distances(self, save_path):
        """Plot and save the distances between image embeddings."""
        os.makedirs(os.path.dirname(save_path), exist_ok=True)
        plt.figure(figsize=(10, 5))
        plt.plot(self.distances, marker='o', linestyle='-')
        plt.title('Distances Between Image Embeddings')
        plt.xlabel('Image Pair Index')
        plt.ylabel('Distance')
        plt.grid(True)
        plt.savefig(save_path)
        info(f"Plot saved to {save_path}")