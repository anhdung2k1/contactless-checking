import numpy as np
import os
from PIL import Image
from facenet_pytorch import MTCNN
from ultralytics import YOLO
from argface_model.argface_classifier import ArcFaceClassifier
from s3_config.s3Config import S3Config 
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
        self.s3Config = S3Config()
        self.person_name = "UNKNOWN"

    def process_image(self, image):
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
                self.person_name = self.argface_model.identify_person(temp_face_path)
                detection['person_name'] = self.person_name
                   
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
        
    def retrieve_image(self, image):
        result_dir = arcface_dataset
        if not os.path.exists(result_dir):
            os.makedirs(result_dir)
            print(f"Directory {result_dir} created.")
        else:
            print(f"Directory {result_dir} already exists.")
        
        label_dir = os.path.join(result_dir, self.person_name)
        if not os.path.exists(label_dir):
            os.makedirs(label_dir)
            print(f"Directory {label_dir} created.")
        else:
            print(f"Directory {label_dir} already exists.")

        # Convert the image to RGB if it's not already
        if image.mode != 'RGB':
            image = image.convert('RGB')

        # Save the detected image in local
        face_img = f"{self.person_name}_{uuid.uuid4()}.png"
        face_save_path = os.path.join(label_dir, face_img)
        image.save(face_save_path)
        print(f"Saved processed face image to {face_save_path}")

        # Save the detected image in S3 Bucket
        s3_object_name = f"arcface_train_dataset/{self.person_name}/{face_img}"
        self.s3Config.upload_file(s3_object_name, face_save_path)
        print(f"Uploaded {face_save_path} to S3 bucket at {s3_object_name}")
        
        return {
            'status': 'success',
            'message': 'Image downloaded'
        }
