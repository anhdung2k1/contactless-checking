import os
import random
import torch
from PIL import Image, UnidentifiedImageError
from torchvision import transforms
from facenet_pytorch import InceptionResnetV1
import torch.nn as nn
import torch.optim as optim
from sklearn.metrics import accuracy_score
import matplotlib.pyplot as plt
import logging
from concurrent.futures import ThreadPoolExecutor

# Get the current file's absolute path and root directory
file_location = os.path.abspath(__file__)
root_directory = os.path.dirname(file_location)

# Set the build directory and Roboflow dataset path
build_dir = os.path.join(root_directory, '..', 'build')
data_path = os.path.join(build_dir, 'dataset')

# Directory to save plots and model
save_path = os.path.join(build_dir, 'face_net_train')
model_file_path = os.path.join(save_path, 'facenet_model.pth')

# Create the directory if it doesn't exist
if not os.path.exists(save_path):
    os.makedirs(save_path)

# Configure logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)

# File handler
file_handler = logging.FileHandler(os.path.join(save_path, 'training.log'))
file_handler.setLevel(logging.INFO)

# Console handler
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.INFO)

# Formatter
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
file_handler.setFormatter(formatter)
console_handler.setFormatter(formatter)

# Add handlers to the logger
logger.addHandler(file_handler)
logger.addHandler(console_handler)

class FaceNetModel:
    def __init__(self, images_path='', batch_size=32, lr=0.01, num_epochs=20, device='cuda', save_path=None, model_file_path=None):
        self.images_path = images_path
        self.transform = transforms.Compose([
            transforms.Resize((160, 160)),  # Ensure size is 160x160 as expected by InceptionResnetV1
            transforms.ToTensor(),
            transforms.Normalize([0.5, 0.5, 0.5], [0.5, 0.5, 0.5])
        ])
        self.batch_size = batch_size
        self.lr = lr
        self.num_epochs = num_epochs
        self.device = device
        self.save_path = save_path
        self.model_file_path = model_file_path
        
        self.model = InceptionResnetV1(pretrained='vggface2', classify=False).to(self.device)  # Load model without final classification layer
        self.model.logits = nn.Linear(self.model.last_linear.in_features, 1).to(self.device)  # Add new classification layer
        
        if self.model_file_path and os.path.exists(self.model_file_path):
            self.load_model(self.model_file_path)
        
        self.criterion = nn.CrossEntropyLoss()
        self.optimizer = optim.Adam(self.model.parameters(), lr=self.lr)
        self.train_loss = []
        self.train_accuracy = []
        self.val_loss = []
        self.val_accuracy = []
        self.image_cache = {}

    def load_images(self):
        image_paths = []
        for image_name in os.listdir(self.images_path):
            image_path = os.path.join(self.images_path, image_name)
            if os.path.isfile(image_path):
                image_paths.append(image_path)
        logger.debug(f"Loaded {len(image_paths)} images from {self.images_path}")
        return image_paths

    def split_dataset(self, image_paths, split_ratio=0.8):
        random.shuffle(image_paths)
        split_index = int(len(image_paths) * split_ratio)
        train_paths = image_paths[:split_index]
        val_paths = image_paths[split_index:]
        logger.debug(f"Split dataset into {len(train_paths)} training images and {len(val_paths)} validation images")
        return train_paths, val_paths

    def preprocess_image(self, image_path):
        if image_path in self.image_cache:
            return self.image_cache[image_path]
        try:
            image = Image.open(image_path).convert("RGB")
            image = self.transform(image)
            self.image_cache[image_path] = image
            return image
        except UnidentifiedImageError:
            logger.warning(f"Skipped non-image file: {image_path}")
            return None

    def load_batch(self, batch_paths):
        batch_images = []
        batch_labels = []
        with ThreadPoolExecutor() as executor:
            results = list(executor.map(self.preprocess_image, batch_paths))
        for result in results:
            if result is not None:
                batch_images.append(result)
                batch_labels.append(0)  # Assuming single class. Adjust as needed.
        return batch_images, batch_labels

    def train(self):
        image_paths = self.load_images()
        train_image_paths, val_image_paths = self.split_dataset(image_paths)

        self.model.train()
        for epoch in range(self.num_epochs):
            logger.debug(f"Starting epoch {epoch+1}/{self.num_epochs}")
            running_loss = 0.0
            all_labels = []
            all_preds = []

            for i in range(0, len(train_image_paths), self.batch_size):
                batch_paths = train_image_paths[i:i + self.batch_size]
                batch_images, batch_labels = self.load_batch(batch_paths)

                if len(batch_images) == 0:
                    logger.debug(f"Skipping empty batch at index {i}")
                    continue

                images = torch.stack(batch_images).to(self.device)
                labels = torch.tensor(batch_labels).to(self.device)

                self.optimizer.zero_grad()

                outputs = self.model(images)
                loss = self.criterion(outputs, labels)
                loss.backward()
                self.optimizer.step()

                running_loss += loss.item()

                _, predicted = torch.max(outputs.data, 1)
                all_labels.extend(labels.cpu().numpy())
                all_preds.extend(predicted.cpu().numpy())

            epoch_loss = running_loss / (len(train_image_paths) // self.batch_size if len(train_image_paths) >= self.batch_size else 1)
            epoch_accuracy = accuracy_score(all_labels, all_preds)
            self.train_loss.append(epoch_loss)
            self.train_accuracy.append(epoch_accuracy)

            logger.info(f"Epoch [{epoch+1}/{self.num_epochs}], Training Loss: {epoch_loss:.4f}, Training Accuracy: {epoch_accuracy:.4f}")

            # Validation
            self.model.eval()
            val_running_loss = 0.0
            val_all_labels = []
            val_all_preds = []

            with torch.no_grad():
                for i in range(0, len(val_image_paths), self.batch_size):
                    batch_paths = val_image_paths[i:i + self.batch_size]
                    batch_images, batch_labels = self.load_batch(batch_paths)

                    if len(batch_images) == 0:
                        logger.debug(f"Skipping empty validation batch at index {i}")
                        continue

                    images = torch.stack(batch_images).to(self.device)
                    labels = torch.tensor(batch_labels).to(self.device)

                    outputs = self.model(images)
                    loss = self.criterion(outputs, labels)

                    val_running_loss += loss.item()

                    _, predicted = torch.max(outputs.data, 1)
                    val_all_labels.extend(labels.cpu().numpy())
                    val_all_preds.extend(predicted.cpu().numpy())

            val_epoch_loss = val_running_loss / (len(val_image_paths) // self.batch_size if len(val_image_paths) >= self.batch_size else 1)
            val_epoch_accuracy = accuracy_score(val_all_labels, val_all_preds)
            self.val_loss.append(val_epoch_loss)
            self.val_accuracy.append(val_epoch_accuracy)

            logger.info(f"Epoch [{epoch+1}/{self.num_epochs}], Validation Loss: {val_epoch_loss:.4f}, Validation Accuracy: {val_epoch_accuracy:.4f}")

        logger.info("Training Finished")
        self.plot_metrics(self.save_path)
        self.save_model(self.save_path)
        # Ensure all log messages are flushed
        for handler in logger.handlers:
            handler.flush()

    def plot_metrics(self, save_path=None):
        epochs = range(1, self.num_epochs + 1)

        plt.figure(figsize=(12, 5))

        plt.subplot(1, 2, 1)
        plt.plot(epochs, self.train_loss, 'bo-', label='Training loss')
        plt.plot(epochs, self.val_loss, 'go-', label='Validation loss')
        plt.title('Training and Validation loss')
        plt.xlabel('Epochs')
        plt.ylabel('Loss')
        plt.legend()

        plt.subplot(1, 2, 2)
        plt.plot(epochs, self.train_accuracy, 'bo-', label='Training accuracy')
        plt.plot(epochs, self.val_accuracy, 'go-', label='Validation accuracy')
        plt.title('Training and Validation accuracy')
        plt.xlabel('Epochs')
        plt.ylabel('Accuracy')
        plt.legend()

        if save_path:
            plt.savefig(os.path.join(save_path, 'training_validation_metrics.png'))
            logger.info(f"Metrics plot saved to {save_path}")
        plt.show()

    def save_model(self, save_path):
        if save_path:
            model_save_path = os.path.join(save_path, 'facenet_model.pth')
            torch.save(self.model.state_dict(), model_save_path)
            logger.info(f"Model saved to {model_save_path}")

    def load_model(self, model_file_path):
        self.model.load_state_dict(torch.load(model_file_path))
        self.model.to(self.device)
        logger.info(f"Model loaded from {model_file_path}")

def main():
    # Set fixed hyperparameters and paths
    batch_size = 32  # Updated batch size
    lr = 0.01
    num_epochs = 20
    device = 'cuda' if torch.cuda.is_available() else 'cpu'

    # Create directory to save plots and model if it doesn't exist
    if not os.path.exists(save_path):
        os.makedirs(save_path)

    # Initialize and train the FaceNet model
    facenet_model = FaceNetModel(images_path=os.path.join(data_path, 'train', 'images'), 
                                 batch_size=batch_size, lr=lr, num_epochs=num_epochs, 
                                 device=device, save_path=save_path, model_file_path=model_file_path)
    facenet_model.train()

if __name__ == "__main__":
    main()
