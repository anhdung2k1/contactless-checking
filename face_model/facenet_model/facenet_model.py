import os
import torch
import numpy as np
from PIL import Image, UnidentifiedImageError
from torchvision import transforms
from facenet_pytorch import InceptionResnetV1
import torch.nn as nn
import torch.optim as optim
from concurrent.futures import ThreadPoolExecutor
from sklearn.metrics import accuracy_score
from scipy.spatial.distance import euclidean
from logger import info, debug, error  # Assuming logger.py contains the functions for logging

class FaceNetModel:
    def __init__(self, image_paths=[], batch_size=32, lr=0.001, num_epochs=20, num_classes=2, device='cuda', 
                 save_path=None, model_file_path=None):
        self.image_paths = image_paths
        self.batch_size = batch_size
        self.lr = lr
        self.num_epochs = num_epochs
        self.num_classes = num_classes
        self.device = device
        self.save_path = save_path
        self.model_file_path = model_file_path
        self.image_cache = {}

        self._initialize_model()

    def _initialize_model(self):
        """Initialize the model, optimizer, and criterion."""
        self.model = InceptionResnetV1(pretrained='vggface2', classify=False).to(self.device)
        self.model.logits = nn.Linear(self.model.last_linear.in_features, self.num_classes).to(self.device)
        self.criterion = nn.CrossEntropyLoss()
        self.optimizer = optim.Adam(self.model.parameters(), lr=self.lr)

        if self.model_file_path and os.path.exists(self.model_file_path):
            self._load_model(self.model_file_path)

    def _load_model(self, model_file_path):
        """Load a pre-trained model if the model file exists."""
        checkpoint = torch.load(model_file_path)
        self.model.load_state_dict(checkpoint, strict=False)
        info(f"Model loaded from {model_file_path}")

    def _transform(self):
        """Return image transformation pipeline."""
        return transforms.Compose([
            transforms.Resize((160, 160)),
            transforms.ToTensor(),
            transforms.Normalize([0.5, 0.5, 0.5], [0.5, 0.5, 0.5])
        ])

    def _load_images(self):
        """Load images and labels from the given paths."""
        image_paths, labels = [], []
        valid_extensions = ('.jpg', '.jpeg', '.png', '.bmp')
        for folder in self.image_paths:
            for label in os.listdir(folder):
                label_path = os.path.join(folder, label)
                if os.path.isdir(label_path):
                    for image_name in os.listdir(label_path):
                        image_path = os.path.join(label_path, image_name)
                        if image_path.lower().endswith(valid_extensions):
                            image_paths.append(image_path)
                            labels.append(label)
                        else:
                            debug(f"Skipped non-image file: {image_path}")
        return image_paths, labels

    def _preprocess_image(self, image_path):
        """Preprocess an image for input to the model."""
        if image_path in self.image_cache:
            return self.image_cache[image_path]
        try:
            image = Image.open(image_path).convert("RGB")
            transformed_image = self._transform()(image)
            self.image_cache[image_path] = transformed_image
            return transformed_image
        except UnidentifiedImageError:
            error(f"Skipped non-image file: {image_path}")
            return None

    def _load_batch(self, batch_paths, batch_labels):
        """Load a batch of images and their corresponding labels."""
        batch_images, batch_targets = [], []
        label_map = {label: idx for idx, label in enumerate(set(batch_labels))}
        with ThreadPoolExecutor() as executor:
            results = list(executor.map(self._preprocess_image, batch_paths))
        for result, label in zip(results, batch_labels):
            if result is not None:
                batch_images.append(result)
                batch_targets.append(label_map[label])
        return batch_images, batch_targets

    def _split_dataset(self, image_paths, labels, split_ratio=0.8):
        """Split dataset into training and validation sets."""
        data = list(zip(image_paths, labels))
        np.random.shuffle(data)
        split_index = int(len(data) * split_ratio)
        train_data, val_data = data[:split_index], data[split_index:]
        train_paths, train_labels = zip(*train_data)
        val_paths, val_labels = zip(*val_data)
        return train_paths, train_labels, val_paths, val_labels

    def train(self):
        """Train the FaceNet model."""
        info("Starting training process")
        image_paths, labels = self._load_images()
        train_image_paths, train_labels, val_image_paths, val_labels = self._split_dataset(image_paths, labels)

        for epoch in range(self.num_epochs):
            info(f"Epoch {epoch+1}/{self.num_epochs}")
            train_loss, train_acc = self._run_epoch(train_image_paths, train_labels)
            val_loss, val_acc = self._run_epoch(val_image_paths, val_labels, train=False)
            info(f"Train Loss: {train_loss:.4f}, Train Acc: {train_acc:.4f}, "
                 f"Val Loss: {val_loss:.4f}, Val Acc: {val_acc:.4f}")

    def _run_epoch(self, image_paths, labels, train=True):
        """Run a single epoch for training or validation."""
        self.model.train() if train else self.model.eval()
        epoch_loss, all_labels, all_preds = 0.0, [], []

        for i in range(0, len(image_paths), self.batch_size):
            batch_paths = image_paths[i:i + self.batch_size]
            batch_labels = labels[i:i + self.batch_size]
            batch_images, batch_targets = self._load_batch(batch_paths, batch_labels)
            
            if not batch_images:
                continue

            images = torch.stack(batch_images).to(self.device)
            targets = torch.tensor(batch_targets, dtype=torch.long).to(self.device)

            self.optimizer.zero_grad()
            with torch.set_grad_enabled(train):
                outputs = self.model(images)
                loss = self.criterion(outputs, targets)
                if train:
                    loss.backward()
                    self.optimizer.step()

            epoch_loss += loss.item()
            _, preds = torch.max(outputs, 1)
            all_labels.extend(targets.cpu().numpy())
            all_preds.extend(preds.cpu().numpy())

        accuracy = accuracy_score(all_labels, all_preds)
        return epoch_loss / len(image_paths), accuracy

    def verify_images(self, threshold=0.5):
        """Verify images by comparing embeddings."""
        distances, labels = [], []
        for label_folder in os.listdir(self.image_paths[0]):
            folder_path = os.path.join(self.image_paths[0], label_folder)
            if not os.path.isdir(folder_path):
                continue

            images = [os.path.join(folder_path, img) for img in os.listdir(folder_path)
                      if img.lower().endswith(('.jpg', '.jpeg', '.png', '.bmp'))]

            if len(images) < 2:
                continue

            reference_image = self._preprocess_image(images[0]).unsqueeze(0).to(self.device)
            reference_embedding = self.model(reference_image).cpu().numpy().flatten()

            for image_path in images[1:]:
                test_image = self._preprocess_image(image_path).unsqueeze(0).to(self.device)
                test_embedding = self.model(test_image).cpu().numpy().flatten()
                distance = euclidean(reference_embedding, test_embedding)
                is_same = distance < threshold
                distances.append(distance)
                labels.append(1 if is_same else 0)
        return distances, labels

def main():
    build_dir = os.path.join(os.path.dirname(__file__), '..', 'build')
    data_path = os.path.join(build_dir, 'arcface_train_dataset')
    save_path = os.path.join(build_dir, 'face_net_train')
    model_file_path = os.path.join(save_path, 'facenet_model.pth')

    os.makedirs(save_path, exist_ok=True)
    device = 'cuda' if torch.cuda.is_available() else 'cpu'

    facenet_model = FaceNetModel(image_paths=[data_path], batch_size=32, lr=0.001, 
                                 num_epochs=20, device=device, save_path=save_path, 
                                 model_file_path=model_file_path)
    facenet_model.train()
    distances, labels = facenet_model.verify_images(threshold=0.05)
    info(f"Verification Results: {len(distances)} comparisons made.")
    debug(f"Distances: {distances}")
    debug(f"Labels: {labels}")

if __name__ == "__main__":
    main()
