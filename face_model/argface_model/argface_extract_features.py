import os
from PIL import Image
import numpy as np
import torch
from torchvision import transforms
from facenet_pytorch import InceptionResnetV1
from ..logger import info, debug, error

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
        info(f"Initialized FeatureExtractor with data path: {data_path}")

    def extract_labels(self):
        """Extract labels from the dataset directory."""
        try:
            info("Extracting labels from the dataset.")
            for label, person in enumerate(os.listdir(self.data_path)):
                person_path = os.path.join(self.data_path, person)
                if os.path.isdir(person_path):
                    self.label_map[label] = person
                    info(f"Label {label}: {person}")
            if not self.label_map:
                error("No labels found. Please check the dataset directory.")
                raise ValueError("No labels found. The dataset directory might be empty.")
        except Exception as e:
            error(f"Error extracting labels: {e}")
            raise ValueError(f"Error extracting labels: {e}") from e

    def extract_features(self, model):
        """Extract features from the images using the given model."""
        if not self.label_map:
            error("Label map is empty. Please call extract_labels() first.")
            raise ValueError("Label map is empty. Please call extract_labels() first.")

        info("Starting feature extraction.")
        for label, person in self.label_map.items():
            person_path = os.path.join(self.data_path, person)
            if not os.path.isdir(person_path):
                error(f"Expected directory for {person}, but found something else.")
                continue
            for image_name in os.listdir(person_path):
                image_path = os.path.join(person_path, image_name)
                if not image_path.lower().endswith(('.png', '.jpg', '.jpeg', '.bmp')):
                    debug(f"Skipped non-image file: {image_path}")
                    continue
                try:
                    image = Image.open(image_path).convert("RGB")
                    info(f"Processing image: {image_path}")
                except Exception as e:
                    error(f"Failed to open image {image_path}: {e}")
                    continue

                image_tensor = self.transform(image).unsqueeze(0)
                try:
                    with torch.no_grad():
                        embedding = model.get_embedding(image_tensor)
                    info(f"Extracted embedding for image: {image_path}")
                except Exception as e:
                    error(f"Failed to get embedding for {image_path}: {e}")
                    continue

                self.features.append(embedding.squeeze().numpy())
                self.labels.append(label)

        if not self.features or not self.labels:
            error("No features or labels were extracted.")
            raise ValueError("Feature extraction failed. No valid images found.")

        self.features = np.array(self.features)
        self.labels = np.array(self.labels)
        info(f"Feature extraction completed. Total samples: {len(self.features)}")

    def get_features_and_labels(self):
        """Return the extracted features and labels."""
        if not self.features or not self.labels:
            error("No features or labels available. Please run extract_features() first.")
            raise ValueError("No features or labels available. Please run extract_features() first.")
        info("Returning features and labels.")
        return self.features, self.labels