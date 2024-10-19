import os
from PIL import Image
import numpy as np
import torch
from torchvision import transforms
from facenet_pytorch import InceptionResnetV1

class FeatureExtractor:
    def __init__(self, data_path):
        self.data_path = data_path
        self.resnet = InceptionResnetV1(pretrained='vggface2').eval()
        self.transform = transforms.Compose([
            transforms.Resize((112, 112)),
            transforms.ToTensor(),
            transforms.Normalize([0.5, 0.5, 0.5], [0.5, 0.5, 0.5])
        ])
        self.features = []
        self.labels = []
        self.label_map = {}

    def extract_labels(self):
        """Extract labels from the dataset directory."""
        try:
            for label, person in enumerate(os.listdir(self.data_path)):
                person_path = os.path.join(self.data_path, person)
                if os.path.isdir(person_path):
                    self.label_map[label] = person
            if not self.label_map:
                raise ValueError("No labels found. The dataset directory might be empty.")
        except Exception as e:
            raise ValueError(f"Error extracting labels: {e}") from e

    def extract_features(self, model):
        """Extract features from the images using the given model."""
        if not self.label_map:
            raise ValueError("Label map is empty. Please call extract_labels() first.")

        for label, person in self.label_map.items():
            person_path = os.path.join(self.data_path, person)
            if not os.path.isdir(person_path):
                continue
            for image_name in os.listdir(person_path):
                image_path = os.path.join(person_path, image_name)
                if not image_path.lower().endswith(('.png', '.jpg', '.jpeg', '.bmp')):
                    continue
                try:
                    image = Image.open(image_path).convert("RGB")
                except Exception as e:
                    continue

                image_tensor = self.transform(image).unsqueeze(0)
                try:
                    with torch.no_grad():
                        embedding = model.get_embedding(image_tensor)
                except Exception:
                    continue

                self.features.append(embedding.squeeze().numpy())
                self.labels.append(label)

        if not self.features or not self.labels:
            raise ValueError("Feature extraction failed. No valid images found.")

        self.features = np.array(self.features)
        self.labels = np.array(self.labels)

    def get_features_and_labels(self):
        """Return the extracted features and labels."""
        if not self.features or not self.labels:
            raise ValueError("No features or labels available. Please run extract_features() first.")
        return self.features, self.labels