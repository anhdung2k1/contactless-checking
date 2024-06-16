import os
import torch
from PIL import Image, ImageDraw
from torchvision import transforms

from .argface_extract_features import FeatureExtractor
from .argface_model import ArcFaceModel
from .argface_train import ArcFaceTrainer

file_location = os.path.abspath(__file__)  # Get current file abspath
root_directory = os.path.dirname(file_location)  # Get root dir

build_dir = os.path.join(root_directory, '..', '../build')
arcface_model_dir = os.path.join(build_dir, '.insightface')
model_save_path = os.path.join(build_dir, '.insightface/arcface_model.pth')

class ArcFaceClassifier:
    _model_loaded = False
    def __init__(self, data_path):
        self.data_path = data_path
        self.feature_extractor = FeatureExtractor(data_path)
        self.features, self.labels, self.label_map = None, None, None
        self.model = None

    def initialize_model(self, num_classes=None):
        self.extract_labels()
        if num_classes is None:
            num_classes = len(self.label_map) if self.label_map else 0
        if num_classes == 0:
            raise ValueError("Label map is not initialized. Call extract_labels() first.")
        feature_dim = 512
        self.model = ArcFaceModel(feature_dim=feature_dim, num_classes=num_classes, model_dir=arcface_model_dir)

    def extract_labels(self):
        self.feature_extractor.extract_labels()
        self.label_map = self.feature_extractor.label_map

    def extract_features(self):
        if self.model is None:
            raise ValueError("Model is not initialized. Call initialize_model() first.")
        self.feature_extractor.extract_features(self.model)
        self.features, self.labels = self.feature_extractor.get_features_and_labels()
        
        # Debugging logs
        print(f'Extracted features: {self.features}')
        print(f'Extracted labels: {self.labels}')
        if self.features is None or self.labels is None:
            raise ValueError("Features or labels not extracted correctly.")
        if len(self.features) == 0 or len(self.labels) == 0:
            raise ValueError("Extracted features or labels are empty.")

    def train(self, num_epochs=100, lr=0.001, momentum=0.9):
        if self.features is None or self.labels is None:
            raise ValueError("Features or labels are None. Ensure they are extracted correctly.")
        trainer = ArcFaceTrainer(self.model, self.features, self.labels, lr, momentum)
        trainer.train(num_epochs)
        torch.save(self.model.state_dict(), model_save_path)

    def load_model(self):
        if not ArcFaceClassifier._model_loaded:
            self.initialize_model()
            self.model.load_state_dict(torch.load(model_save_path))
            ArcFaceClassifier._model_loaded = True
            print(f"Model loaded: {model_save_path}")
        else:
            print("Model already loaded, skipping reload.")

    def model_exists(self):
        return os.path.exists(model_save_path)


    def identify_person(self, image_file, save_image_path=None):
        if not os.path.exists(image_file):
            raise FileNotFoundError(f"Image file not found: {image_file}")

        transform = transforms.Compose([
            transforms.Resize((112, 112)),
            transforms.ToTensor(),
            transforms.Normalize([0.5, 0.5, 0.5], [0.5, 0.5, 0.5])
        ])
        image = Image.open(image_file).convert("RGB")  # Ensure image is in RGB format
        image_tensor = transform(image).unsqueeze(0)
        with torch.no_grad():
            embedding = self.model.get_embedding(image_tensor)
        predicted = self.model.predict(embedding)
        person_name = self.label_map[predicted.item()]

        if save_image_path:
            draw = ImageDraw.Draw(image)
            draw.text((10, 10), person_name, fill=(255, 0, 0))
            image.save(save_image_path)

        return person_name
    
    def identify_person_from_embedding(self, embedding):
        embedding_tensor = torch.tensor(embedding, dtype=torch.float32).unsqueeze(0).to(self.model.device)
        predicted = self.model.predict(embedding_tensor)
        person_name = self.label_map[predicted.item()]
        return person_name