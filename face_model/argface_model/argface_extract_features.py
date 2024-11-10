import os
from PIL import Image
import numpy as np
import torch
from torchvision import transforms
from logger import info, error

class FeatureExtractor:
    def __init__(self, data_path):
        self.data_path = data_path
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
            info(f"Extracting labels from {self.data_path}")
            for label, person in enumerate(os.listdir(self.data_path)):
                person_path = os.path.join(self.data_path, person)
                if os.path.isdir(person_path):
                    self.label_map[label] = person
            if not self.label_map:
                raise ValueError("No labels found. The dataset directory might be empty.")
            info(f"Labels extracted: {self.label_map}")
        except Exception as e:
            error(f"Error extracting labels: {e}")
            raise ValueError(f"Error extracting labels: {e}") from e

    def extract_features(self, model):
        """Extract features from the images using the given model."""
        if not self.label_map:
            error("Label map is empty. Please call extract_labels() first.")
            raise ValueError("Label map is empty. Please call extract_labels() first.")

        info("Starting feature extraction...")
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
                    info(f"Processing image: {image_path}")
                except Exception as e:
                    error(f"Error opening image {image_path}: {e}")
                    continue

                image_tensor = self.transform(image).unsqueeze(0)
                try:
                    with torch.no_grad():
                        embedding = model.get_embedding(image_tensor)
                    # Ensure the tensor is moved to the CPU before converting to a NumPy array
                    self.features.append(embedding.squeeze().cpu().numpy())
                    self.labels.append(label)
                    info(f"Feature extracted for image: {image_path}")
                except Exception as e:
                    error(f"Error extracting embedding for {image_path}: {e}")
                    continue

        # Convert to NumPy arrays and check size
        self.features = np.array(self.features)
        self.labels = np.array(self.labels)

        if self.features.size == 0 or self.labels.size == 0:
            error("Feature extraction failed. No valid images found.")
            raise ValueError("Feature extraction failed. No valid images found.")

        info("Feature extraction completed successfully.")

    def get_features_and_labels(self):
        """Return the extracted features and labels."""
        if self.features.size == 0 or self.labels.size == 0:
            error("No features or labels available. Please run extract_features() first.")
            raise ValueError("No features or labels available. Please run extract_features() first.")
        info("Returning extracted features and labels.")
        return self.features, self.labels
