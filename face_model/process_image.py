import numpy as np
import os
from PIL import Image, ImageDraw
from facenet_pytorch import InceptionResnetV1, MTCNN
from ultralytics import YOLO
from argface_model.argface_classifier import ArcFaceClassifier

file_location = os.path.abspath(__file__)  # Get current file abspath
root_directory = os.path.dirname(file_location)  # Get root dir

build_dir = os.path.join(root_directory, '..', 'build')
arcface_dataset = os.path.join(build_dir, 'arcface_train_dataset')
arcface_model_dir = os.path.join(build_dir, '.insightface')
model_save_path = os.path.join(build_dir, '.insightface/arcface_model.pth')

class ImageProcessor:
    def __init__(self, yolo_model_path):
        self.yolo_model = YOLO(yolo_model_path)
        self.facenet_model = InceptionResnetV1(pretrained='vggface2').eval()
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

        embeddings = []
        for detection in detections:
            x1, y1, x2, y2 = detection['bbox']
            face_roi = image_np[y1:y2, x1:x2]
            face_pil = Image.fromarray(face_roi)
            
            face_tensor = self.mtcnn(face_pil)
            if face_tensor is not None and face_tensor.shape[0] > 0:
                face_tensor = face_tensor.unsqueeze(0) if len(face_tensor.shape) == 3 else face_tensor
                if len(face_tensor.shape) == 4 and face_tensor.shape[1] == 3:
                    embedding = self.facenet_model(face_tensor).detach().numpy()
                    
                    if len(embedding.shape) == 2:
                        embedding = embedding[0]
                    
                    embeddings.append(embedding)
                    detection['embedding'] = embedding.tolist()  # Add embedding to detection result
                    if os.path.isfile(model_save_path):
                        self.argface_model.load_model()
                    else:
                        self.argface_model.initialize_model()
                        self.argface_model.extract_features()
                        self.argface_model.train()

                        person_name = self.argface_model.identify_person_from_embedding(detection['embedding'])
                        detection['person_name'] = person_name
                else:
                    print(f"Unexpected face_tensor shape: {face_tensor.shape}")

        return {
            'status': 'success',
            'message': 'Image processed',
            'detections': detections,
            'embeddings': len(embeddings)
        }
