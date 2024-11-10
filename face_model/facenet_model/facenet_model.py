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
from scipy.spatial.distance import cosine
from threading import Lock  # For thread-safe access to the cache
from tqdm import tqdm
from logger import info, error

class FaceNetModel:
    def __init__(self, image_path='', batch_size=32, lr=0.001, num_epochs=20, num_classes=2, 
                 save_path=None, model_file_path=None):
        self.image_path = image_path if image_path else ''
        self.batch_size = batch_size
        self.lr = lr
        self.num_epochs = num_epochs
        self.num_classes = num_classes
        self.device = 'cuda' if torch.cuda.is_available() else 'cpu'
        self.save_path = save_path if save_path else './checkpoints'
        self.model_file_path = model_file_path
        self.image_cache = {}
        self.cache_lock = Lock()  # Lock for thread-safe access to image_cache
        self.label_map = {}  # Consistent label map across batches

        if not self.save_path:
            raise ValueError("The save_path cannot be None. Please provide a valid directory path.")
        if not os.path.exists(self.save_path):
            os.makedirs(self.save_path)

        self._initialize_model()

    def _initialize_model(self):
        """Initialize the model, optimizer, and criterion."""
        info(f"Using device: {self.device}")
        self.model = InceptionResnetV1(pretrained='vggface2', classify=False).to(self.device)
        # Adding dropout layer after the final pooling layer
        self.model.dropout = nn.Dropout(p=0.5)
        self.model.logits = nn.Sequential(
            nn.Linear(self.model.last_linear.in_features, 512),
            nn.ReLU(),
            nn.Dropout(p=0.5),  # Additional dropout for regularization
            nn.Linear(512, self.num_classes)
        ).to(self.device)
        self.criterion = nn.CrossEntropyLoss()
        self.optimizer = optim.Adam(self.model.parameters(), lr=self.lr)

        if self.model_file_path and os.path.exists(self.model_file_path):
            self._load_model(self.model_file_path)

    def _load_model(self, model_file_path):
        """Load a pre-trained model if the model file exists."""
        checkpoint = torch.load(model_file_path)
        self.model.load_state_dict(checkpoint, strict=False)
        info(f"Model loaded from {model_file_path}")
        
    def _save_model(self, save_path):
        """Save the model state to a file."""
        if save_path:
            os.makedirs(os.path.dirname(save_path), exist_ok=True)
            torch.save(self.model.state_dict(), save_path)
            info(f"Model saved to {save_path}")

    def transform(self):
        """Return image transformation pipeline with augmentation."""
        return transforms.Compose([
            transforms.RandomHorizontalFlip(),
            transforms.RandomRotation(15),  # Random rotation within 15 degrees
            transforms.ColorJitter(brightness=0.2, contrast=0.2),  # Adjust brightness and contrast
            transforms.Resize((160, 160)),
            transforms.ToTensor(),
            transforms.Normalize([0.5, 0.5, 0.5], [0.5, 0.5, 0.5])
        ])

    def _load_images(self):
        """Load images and labels from the given path, creating a consistent label map."""
        image_paths, labels = [], []
        valid_extensions = ('.jpg', '.jpeg', '.png', '.bmp')

        if not os.path.exists(self.image_path) or not os.path.isdir(self.image_path):
            error(f"Invalid directory: {self.image_path}")
            return image_paths, labels

        for label in os.listdir(self.image_path):
            label_path = os.path.join(self.image_path, label)
            if os.path.isdir(label_path):
                for image_name in os.listdir(label_path):
                    image_path = os.path.join(label_path, image_name)
                    if image_path.lower().endswith(valid_extensions):
                        image_paths.append(image_path)
                        labels.append(label)
                    else:
                        info(f"Skipped non-image file: {image_path}")

        # Create a consistent label map across the dataset
        if labels:
            self.label_map = {label: idx for idx, label in enumerate(sorted(set(labels)))}
            info(f"Label map created: {self.label_map}")
        else:
            info("No labels found; check your dataset structure.")

        return image_paths, labels

    def _preprocess_image(self, image_path):
        """Preprocess an image for input to the model."""
        with self.cache_lock:
            if image_path in self.image_cache:
                return self.image_cache[image_path]
        try:
            image = Image.open(image_path).convert("RGB")
            transformed_image = self.transform()(image)
            with self.cache_lock:
                self.image_cache[image_path] = transformed_image
            return transformed_image
        except UnidentifiedImageError:
            info(f"Skipped non-image file: {image_path}")
            return None

    def _load_batch(self, batch_paths, batch_labels):
        """Load a batch of images and their corresponding labels."""
        batch_images, batch_targets = [], []
        with ThreadPoolExecutor() as executor:
            results = list(executor.map(self._preprocess_image, batch_paths))
        for result, label in zip(results, batch_labels):
            if result is not None:
                batch_images.append(result)
                batch_targets.append(self.label_map[label])  # Use consistent label mapping
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
        if not image_paths:
            error("No valid images found for training.")
            return

        train_image_paths, train_labels, val_image_paths, val_labels = self._split_dataset(image_paths, labels)
        
        best_val_acc = 0.0  # Initialize best validation accuracy

        for epoch in range(self.num_epochs):
            info(f"Epoch {epoch+1}/{self.num_epochs}")
            train_loss, train_acc = self._run_epoch(train_image_paths, train_labels)
            val_loss, val_acc = self._run_epoch(val_image_paths, val_labels, train=False)
            info(f"Train Loss: {train_loss:.4f}, Train Acc: {train_acc:.4f}, "
                 f"Val Loss: {val_loss:.4f}, Val Acc: {val_acc:.4f}")
        
            # Save best model based on validation accuracy
            if val_acc > best_val_acc:
                best_val_acc = val_acc
                self._save_model(self.model_file_path)
                info(f"New best model saved with validation accuracy: {best_val_acc:.4f}")

        info("Training completed")

    def _run_epoch(self, image_paths, labels, train=True):
        """Run a single epoch for training or validation."""
        self.model.train() if train else self.model.eval()
        epoch_loss, all_labels, all_preds = 0.0, [], []
        total_samples = 0

        for i in range(0, len(image_paths), self.batch_size):
            batch_paths = image_paths[i:i + self.batch_size]
            batch_labels = labels[i:i + self.batch_size]
            batch_images, batch_targets = self._load_batch(batch_paths, batch_labels)
            
            if not batch_images:
                continue

            total_samples += len(batch_images)
            images = torch.stack(batch_images).to(self.device)
            targets = torch.tensor(batch_targets, dtype=torch.long).to(self.device)

            self.optimizer.zero_grad()
            with torch.set_grad_enabled(train):
                outputs = self.model(images)
                loss = self.criterion(outputs, targets)
                if train:
                    loss.backward()
                    self.optimizer.step()

            epoch_loss += loss.item() * len(batch_images)
            _, preds = torch.max(outputs, 1)
            all_labels.extend(targets.cpu().numpy())
            all_preds.extend(preds.cpu().numpy())

        accuracy = accuracy_score(all_labels, all_preds)
        average_loss = epoch_loss / total_samples if total_samples > 0 else 0
        return average_loss, accuracy

    def verify_images(self, threshold=0.5, batch_size=32):
        """Verify images by comparing embeddings."""
        distances, labels = [], []
        for label_folder in os.listdir(self.image_path):
            folder_path = os.path.join(self.image_path, label_folder)
            if not os.path.isdir(folder_path):
                continue

            images = [os.path.join(folder_path, img) for img in os.listdir(folder_path)
                    if img.lower().endswith(('.jpg', '.jpeg', '.png', '.bmp'))]

            if len(images) < 2:
                continue

            reference_image = self._preprocess_image(images[0]).unsqueeze(0).to(self.device)
            reference_embedding = self.model(reference_image).detach().cpu().numpy().flatten()

            for i in tqdm(range(1, len(images), batch_size), desc=f"Verifying {label_folder}"):
                batch = images[i:i+batch_size]
                batch_images = [self._preprocess_image(img).unsqueeze(0) for img in batch]
                batch_tensor = torch.cat(batch_images).to(self.device)
                
                with torch.no_grad():
                    batch_embeddings = self.model(batch_tensor).detach().cpu().numpy()

                for _, embedding in enumerate(batch_embeddings):
                    distance = cosine(reference_embedding, embedding.flatten())
                    is_same = distance < threshold
                    distances.append(distance)
                    labels.append(1 if is_same else 0)
        
        return distances, labels

    def get_embeddings(self, image_paths):
        """Get embeddings for a list of image paths."""
        self.model.eval()  # Set the model to evaluation mode
        embeddings = []

        with torch.no_grad():  # Disable gradient computation
            for image_path in image_paths:
                image = self._preprocess_image(image_path)
                if image is not None:
                    image_tensor = image.unsqueeze(0).to(self.device)
                    embedding = self.model(image_tensor).cpu().numpy().flatten()
                    embeddings.append(embedding)
                else:
                    info(f"Skipped invalid image: {image_path}")

        return np.array(embeddings)
