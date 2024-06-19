import numpy as np
import os
from PIL import Image
from facenet_pytorch import MTCNN
from ultralytics import YOLO
from argface_model.argface_classifier import ArcFaceClassifier
import uuid

file_location = os.path.abspath(__file__)  # Get current file abspath
root_directory = os.path.dirname(file_location)  # Get root dir

build_dir = os.path.join(root_directory, '..', 'build')
arcface_dataset = os.path.join(build_dir, 'arcface_train_dataset')
arcface_model_dir = os.path.join(build_dir, '.insightface')
model_save_path = os.path.join(build_dir, '.insightface/arcface_model.pth')

class ImageProcessor:
    def __init__(self, yolo_model_path):
        self.yolo_model = YOLO(yolo_model_path)
        self.mtcnn = MTCNN(keep_all=True)
        self.argface_model = ArcFaceClassifier(arcface_dataset)

    def process_image(self, image, save_image_path=None):
        # Convert PIL image to RGB and then to numpy array
        if image.mode != 'RGB':
            image = image.convert('RGB')
        image_np = np.array(image)

        # Detect objects with YOLOv8
        results = self.yolo_model(image_np)
        detections = []
        for result in results:
            for box in result.boxes:
                x1, y1, x2, y2 = map(int, box.xyxy[0])
                if box.cls == 0:  # Assuming class 0 is 'person'
                    detections.append({
                        'bbox': (x1, y1, x2, y2),
                        'confidence': box.conf.item()
                    })

        # embeddings = []
        for detection in detections:
            if os.path.isfile(model_save_path):
                self.argface_model.load_model()
            else:
                self.argface_model.initialize_model()
                self.argface_model.extract_features()
                self.argface_model.train()
                self.argface_model.load_model()
                
            x1, y1, x2, y2 = detection['bbox']
            
            # Add padding to the bounding box
            padding = 100
            x1 = max(0, x1 - padding)
            y1 = max(0, y1 - padding)
            x2 = min(image_np.shape[1], x2 + padding)
            y2 = min(image_np.shape[0], y2 + padding)
            
            face_roi = image_np[y1:y2, x1:x2]
            face_pil = Image.fromarray(face_roi)

            # Save face region as an image file
            temp_face_path = f"/tmp/{uuid.uuid4()}.png"
            face_pil.save(temp_face_path)

            # Use the identify_person function
            try:
                person_name = self.argface_model.identify_person(temp_face_path, save_image_path)
                detection['person_name'] = person_name
            except Exception as e:
                detection['person_name'] = "Unknown"
                print(f"Error identifying person: {e}")

            # Clean up temporary image file
            os.remove(temp_face_path)

        return {
            'status': 'success',
            'message': 'Image processed',
            'detections': detections,
            'embeddings': len(detections)
        }