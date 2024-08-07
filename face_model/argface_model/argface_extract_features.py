import os
from PIL import Image
import numpy as np
import torch
from torchvision import transforms
from facenet_pytorch import InceptionResnetV1
import logging

# Configure logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
handler = logging.StreamHandler()
handler.setLevel(logging.INFO)
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)

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
        logger.info("FeatureExtractor initialized with data path: %s", self.data_path)

    def extract_labels(self):
        try:
            for label, person in enumerate(os.listdir(self.data_path)):
                self.label_map[label] = person
            logger.info(f"Labels extracted: {self.label_map}")
        except Exception as e:
            logger.error("Error extracting labels: %s", e)
            raise

    def extract_features(self, model):
        if not self.label_map:
            logger.error("Label map is empty. Please call extract_labels() first.")
            raise ValueError("Label map is empty. Please call extract_labels() first.")
        
        for label, person in enumerate(os.listdir(self.data_path)):
            person_path = os.path.join(self.data_path, person)
            if not os.path.isdir(person_path):
                logger.warning(f"Skipping {person_path} as it is not a directory")
                continue
            for image_name in os.listdir(person_path):
                image_path = os.path.join(person_path, image_name)
                if not image_path.lower().endswith(('.png', '.jpg', '.jpeg', '.bmp')):
                    logger.warning(f"Skipping {image_path} as it is not an image file")
                    continue
                logger.info(f"Opening image: {image_path}")
                try:
                    image = Image.open(image_path).convert("RGB")
                except Exception as e:
                    logger.warning(f"Failed to open image {image_path}: {e}")
                    continue
                
                image = self.transform(image).unsqueeze(0)
                try:
                    with torch.no_grad():
                        embedding = model.get_embedding(image)
                except Exception as e:
                    logger.warning(f"Failed to get embedding for {image_path}: {e}")
                    continue
                
                self.features.append(embedding.squeeze().numpy())
                self.labels.append(label)
                logger.debug(f"Extracted features for {image_path}")
        
        self.features = np.array(self.features)
        self.labels = np.array(self.labels)
        logger.info(f"Features and labels extracted: {len(self.features)} features, {len(self.labels)} labels")

    def get_features_and_labels(self):
        logger.info("Returning features and labels")
        return self.features, self.labels

# Example usage:
# extractor = FeatureExtractor(data_path='path_to_data')
# extractor.extract_labels()
# extractor.extract_features(extractor.resnet)
# features, labels = extractor.get_features_and_labels()