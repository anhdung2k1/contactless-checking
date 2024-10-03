import os
import torch
import numpy as np
from PIL import Image, UnidentifiedImageError
from torchvision import transforms
from facenet_pytorch import InceptionResnetV1
import torch.nn as nn
import torch.optim as optim
from sklearn.metrics import accuracy_score, confusion_matrix, classification_report, mean_absolute_error, mean_squared_error, r2_score, roc_curve, auc, precision_recall_curve
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
import logging
from concurrent.futures import ThreadPoolExecutor
from scipy.spatial.distance import euclidean

# Set the build directory and dataset path
build_dir = os.path.join(os.path.dirname(__file__), '..', 'build')
data_path = os.path.join(build_dir, 'dataset')
data_test = os.path.join(build_dir, 'dataset_test')

# Directory to save logs and model
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
    def __init__(self, images_paths=[], batch_size=32, lr=0.001, num_epochs=20, num_classes=2, device='cuda', save_path=None, model_file_path=None):
        self.images_paths = images_paths
        self.transform = transforms.Compose([
            transforms.Resize((160, 160)),  # Ensure size is 160x160 as expected by InceptionResnetV1
            transforms.ToTensor(),
            transforms.Normalize([0.5, 0.5, 0.5], [0.5, 0.5, 0.5])
        ])
        self.batch_size = batch_size
        self.lr = lr
        self.num_epochs = num_epochs
        self.num_classes = num_classes
        self.device = device
        self.save_path = save_path
        self.model_file_path = model_file_path
        
        self.model = InceptionResnetV1(pretrained='vggface2', classify=False).to(self.device)  # Load model without final classification layer
        self.model.logits = nn.Linear(self.model.last_linear.in_features, self.num_classes).to(self.device)  # Adjust logits layer

        if self.model_file_path and os.path.exists(self.model_file_path):
            self.load_model(self.model_file_path)

        self.criterion = nn.CrossEntropyLoss()
        self.optimizer = optim.Adam(self.model.parameters(), lr=self.lr)
        self.train_loss = []
        self.train_accuracy = []
        self.val_loss = []
        self.val_accuracy = []
        self.image_cache = {}
        self.distances = []
        self.labels = []

    def load_model(self, model_file_path):
        checkpoint = torch.load(model_file_path)
        if 'logits.weight' in checkpoint:
            del checkpoint['logits.weight']
            del checkpoint['logits.bias']
        self.model.load_state_dict(checkpoint, strict=False)
        logger.info(f"Model loaded from {model_file_path}")

    def load_images(self):
        image_paths = []
        labels = []
        valid_extensions = ('.jpg', '.jpeg', '.png', '.bmp')  # Add more extensions if needed
        for path in self.images_paths:
            for label_name in os.listdir(path):
                label_path = os.path.join(path, label_name)
                if os.path.isdir(label_path):
                    for image_name in os.listdir(label_path):
                        image_path = os.path.join(label_path, image_name)
                        if os.path.isfile(image_path) and image_path.lower().endswith(valid_extensions):
                            image_paths.append(image_path)
                            labels.append(label_name)
                        else:
                            logger.warning(f"Skipped non-image file: {image_path}")
        logger.debug(f"Loaded {len(image_paths)} images from {self.images_paths}")
        return image_paths, labels

    def split_dataset(self, image_paths, labels, split_ratio=0.8):
        unique_labels = list(set(labels))
        train_paths = []
        train_labels = []
        val_paths = []
        val_labels = []

        for label in unique_labels:
            label_paths = [path for path, lbl in zip(image_paths, labels) if lbl == label]
            split_index = int(len(label_paths) * split_ratio)
            train_paths.extend(label_paths[:split_index])
            train_labels.extend([label] * split_index)
            val_paths.extend(label_paths[split_index:])
            val_labels.extend([label] * (len(label_paths) - split_index))

        logger.info(f"Split dataset into {len(train_paths)} training images and {len(val_paths)} validation images")
        return train_paths, train_labels, val_paths, val_labels

    def preprocess_image(self, image_path):
        if image_path in self.image_cache:
            return self.image_cache[image_path]
        try:
            logger.info(f"Opening image: {image_path}")
            image = Image.open(image_path).convert("RGB")
            image = self.transform(image)
            self.image_cache[image_path] = image
            return image
        except UnidentifiedImageError:
            logger.warning(f"Skipped non-image file: {image_path}")
            return None

    def load_batch(self, batch_paths, batch_labels):
        batch_images = []
        batch_targets = []
        label_map = {label: idx for idx, label in enumerate(set(batch_labels))}

        with ThreadPoolExecutor() as executor:
            results = list(executor.map(self.preprocess_image, batch_paths))
        for result, label in zip(results, batch_labels):
            if result is not None:
                batch_images.append(result)
                batch_targets.append(label_map[label])  # Map label to numeric index
        logger.info(f"Loaded batch of {len(batch_images)} images")
        return batch_images, batch_targets

    def train(self):
        logger.info("Starting training process")
        image_paths, labels = self.load_images()
        train_image_paths, train_labels, val_image_paths, val_labels = self.split_dataset(image_paths, labels)

        self.model.train()
        for epoch in range(self.num_epochs):
            logger.debug(f"Starting epoch {epoch+1}/{self.num_epochs}")
            running_loss = 0.0
            all_labels = []
            all_preds = []

            for i in range(0, len(train_image_paths), self.batch_size):
                batch_paths = train_image_paths[i:i + self.batch_size]
                batch_labels = train_labels[i:i + self.batch_size]
                batch_images, batch_targets = self.load_batch(batch_paths, batch_labels)

                if len(batch_images) == 0:
                    logger.debug(f"Skipping empty batch at index {i}")
                    continue

                images = torch.stack(batch_images).to(self.device)
                labels = torch.tensor(batch_targets, dtype=torch.long).to(self.device)

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
                    batch_labels = val_labels[i:i + self.batch_size]
                    batch_images, batch_targets = self.load_batch(batch_paths, batch_labels)

                    if len(batch_images) == 0:
                        logger.debug(f"Skipping empty validation batch at index {i}")
                        continue

                    images = torch.stack(batch_images).to(self.device)
                    labels = torch.tensor(batch_targets).to(self.device)

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
        self.print_evaluation_metrics(val_all_labels, val_all_preds, self.save_path)
        # Ensure all log messages are flushed
        for handler in logger.handlers:
            handler.flush()

    def verify_images_in_folder(self, threshold=0.5):
        self.distances = []
        self.labels = []

        try:
            for label in os.listdir(self.images_paths[0]):
                label_path = os.path.join(self.images_paths[0], label)
                if not os.path.isdir(label_path):
                    continue

                images = [os.path.join(label_path, img) for img in os.listdir(label_path) if img.lower().endswith(('.jpg', '.jpeg', '.png', '.bmp'))]
                if len(images) < 2:
                    logger.info(f"Not enough images in folder {label} to compare.")
                    continue

                first_image_path = images[0]
                first_image = self.preprocess_image(first_image_path)
                if first_image is None:
                    logger.warning(f"First image {first_image_path} could not be processed.")
                    continue
                first_image = first_image.unsqueeze(0).to(self.device)  # Ensure 4D input

                self.model.eval()
                with torch.no_grad():
                    first_embedding = self.model(first_image).cpu().numpy().flatten()  # Flatten to 1-D

                for img_path in images[1:]:
                    second_image = self.preprocess_image(img_path)
                    if second_image is None:
                        logger.warning(f"Test image {img_path} could not be processed.")
                        continue
                    second_image = second_image.unsqueeze(0).to(self.device)  # Ensure 4D input

                    with torch.no_grad():
                        second_embedding = self.model(second_image).cpu().numpy().flatten()  # Flatten to 1-D

                    distance = euclidean(first_embedding, second_embedding)
                    is_same = distance < threshold  # A lower distance indicates higher similarity
                    logger.info(f"Comparing {first_image_path} with {img_path}: Distance = {distance:.4f}, Same person: {is_same}")

                    self.distances.append(distance)
                    self.labels.append(1 if is_same else 0)

            # Ensure data was collected
            if not self.distances or not self.labels:
                logger.error("No data collected. Distances or labels array is empty.")
                return {
                    'status': 'error',
                    'message': 'No data collected'
                }

            # Check the distribution of labels
            label_counts = {0: self.labels.count(0), 1: self.labels.count(1)}
            logger.info(f"Label distribution: {label_counts}")

            if label_counts[0] == 0:
                logger.warning("No negative samples (different persons) detected in the verification results.")
            elif label_counts[1] == 0:
                logger.warning("No positive samples (same persons) detected in the verification results.")

            # Plot confusion matrix
            self.plot_confusion_matrix(self.labels, [1 if d < threshold else 0 for d in self.distances], self.save_path)

            return {
                'status': 'success',
                'distances': self.distances,
                'labels': self.labels
            }
        except Exception as e:
            logger.error(f"Error in verify_images_in_folder: {str(e)}")
            return {
                'status': 'error',
                'message': str(e)
            }

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

    def plot_verification_metrics(self, save_path=None):
        distances = np.array(self.distances)
        labels = np.array(self.labels)

        if distances.ndim != 1 or labels.ndim != 1 or len(distances) == 0 or len(labels) == 0:
            logger.error("Distances and labels must be non-empty 1-D arrays.")
            return

        logger.debug(f"Labels: {labels}")
        logger.debug(f"Distances: {distances}")

        assert set(labels) <= {0, 1}, "Labels should be binary (0 or 1)."

        if len(np.unique(labels)) == 1:
            logger.error("Only one class present in labels, unable to calculate meaningful metrics.")
            return

        plt.figure(figsize=(10, 5))
        sns.histplot(distances[labels == 1], bins=50, color='green', label='Same Person', kde=True)
        sns.histplot(distances[labels == 0], bins=50, color='red', label='Different Person', kde=True)
        plt.xlabel('Similarity')
        plt.ylabel('Frequency')
        plt.title('Distribution of Similarity Scores')
        plt.legend()
        if save_path:
            plt.savefig(os.path.join(save_path, 'similarity_distribution.png'))
            logger.info(f"Similarity distribution plot saved to {save_path}")
        plt.show()

        fpr, tpr, _ = roc_curve(labels, distances, pos_label=1)
        roc_auc = auc(fpr, tpr)

        plt.figure()
        plt.plot(fpr, tpr, color='darkorange', lw=2, label=f'ROC curve (area = {roc_auc:.2f})')
        plt.plot([0, 1], [0, 1], color='navy', lw=2, linestyle='--')
        plt.xlim([0.0, 1.0])
        plt.ylim([0.0, 1.05])
        plt.xlabel('False Positive Rate')
        plt.ylabel('True Positive Rate')
        plt.title('Receiver Operating Characteristic')
        plt.legend(loc="lower right")
        if save_path:
            plt.savefig(os.path.join(save_path, 'roc_curve.png'))
            logger.info(f"ROC curve plot saved to {save_path}")
        plt.show()

        precision, recall, _ = precision_recall_curve(labels, distances)
        plt.figure()
        plt.plot(recall, precision, marker='.', label=f'Precision-Recall curve (AUC = {roc_auc:.2f})')
        plt.xlabel('Recall')
        plt.ylabel('Precision')
        plt.title('Precision-Recall Curve')
        plt.legend()
        if save_path:
            plt.savefig(os.path.join(save_path, 'precision_recall_curve.png'))
            logger.info(f"Precision-Recall curve plot saved to {save_path}")
        plt.show()

    def save_model(self, save_path):
        if save_path:
            model_save_path = os.path.join(save_path, 'facenet_model.pth')
            torch.save(self.model.state_dict(), model_save_path)
            logger.info(f"Model saved to {model_save_path}")

    def load_model(self, model_file_path):
        checkpoint = torch.load(model_file_path)
        if 'logits.weight' in checkpoint:
            del checkpoint['logits.weight']
            del checkpoint['logits.bias']
        self.model.load_state_dict(checkpoint, strict=False)
        logger.info(f"Model loaded from {model_file_path}")

    def print_evaluation_metrics(self, true_labels, predicted_labels, save_path):
        # Ensure that both true_labels and predicted_labels are 1D arrays
        true_labels = np.array(true_labels).flatten()
        predicted_labels = np.array(predicted_labels).flatten()

        # Additional check for debugging
        if len(true_labels) != len(predicted_labels):
            logger.error(f"Mismatch in true and predicted labels length: {len(true_labels)} vs {len(predicted_labels)}")
            return

        conf_matrix = confusion_matrix(true_labels, predicted_labels)
        class_report = classification_report(true_labels, predicted_labels, output_dict=True, zero_division=1)
        acc_score = accuracy_score(true_labels, predicted_labels)
        mae = mean_absolute_error(true_labels, predicted_labels)
        mse = mean_squared_error(true_labels, predicted_labels)
        r2 = r2_score(true_labels, predicted_labels)

        logger.info(f"Confusion Matrix:\n{conf_matrix}")
        logger.info(f"Classification Report:\n{classification_report(true_labels, predicted_labels)}")
        logger.info(f"Accuracy Score: {acc_score:.4f}")
        logger.info(f"Mean Absolute Error: {mae:.4f}")
        logger.info(f"Mean Squared Error: {mse:.4f}")
        logger.info(f"R2 Score: {r2:.4f}")

        print(f"Confusion Matrix:\n{conf_matrix}")
        print(f"Classification Report:\n{classification_report(true_labels, predicted_labels)}")
        print(f"Accuracy Score: {acc_score:.4f}")
        print(f"Mean Absolute Error: {mae:.4f}")
        print(f"Mean Squared Error: {mse:.4f}")
        print(f"R2 Score: {r2:.4f}")

        # Save confusion matrix
        plt.figure(figsize=(10, 7))
        sns.heatmap(conf_matrix, annot=True, fmt='d', cmap='Blues')
        plt.title('Confusion Matrix')
        plt.ylabel('Actual Label')
        plt.xlabel('Predicted Label')
        plt.savefig(os.path.join(save_path, 'confusion_matrix.png'))
        logger.info(f'Confusion matrix saved to {os.path.join(save_path, "confusion_matrix.png")}')

        # Save classification report
        report_df = pd.DataFrame(class_report).transpose()
        plt.figure(figsize=(10, 7))
        sns.heatmap(report_df, annot=True, fmt=".2f", cmap="Blues", cbar=False)
        plt.title('Classification Report')
        plt.savefig(os.path.join(save_path, 'classification_report.png'))
        logger.info(f'Classification report saved to {os.path.join(save_path, "classification_report.png")}')

    def plot_confusion_matrix(self, true_labels, predicted_labels, save_path=None):
        # Calculate confusion matrix
        conf_matrix = confusion_matrix(true_labels, predicted_labels)

        # Plot confusion matrix using seaborn
        plt.figure(figsize=(10, 7))
        sns.heatmap(conf_matrix, annot=True, fmt='d', cmap='Blues')
        plt.title('Confusion Matrix')
        plt.ylabel('Actual Label')
        plt.xlabel('Predicted Label')

        # Save plot if save_path is provided
        if save_path:
            plt.savefig(os.path.join(save_path, 'confusion_matrix.png'))
            logger.info(f'Confusion matrix saved to {os.path.join(save_path, "confusion_matrix.png")}')
        plt.show()

def main():
    # Set fixed hyperparameters and paths
    batch_size = 32  # Updated batch size
    lr = 0.001
    num_epochs = 20
    device = 'cuda' if torch.cuda.is_available() else 'cpu'

    # Create directory to save plots and model if it doesn't exist
    if not os.path.exists(save_path):
        os.makedirs(save_path)
    
    model_trained = os.path.exists(model_file_path)

    # Initialize and train the FaceNet model
    facenet_model = FaceNetModel(images_paths=[data_test], 
                                 batch_size=batch_size, lr=lr, num_epochs=num_epochs, 
                                 device=device, save_path=save_path, model_file_path=model_file_path)
    
    if model_trained:
        logger.info("Loading model trained...")
        facenet_model.load_model(model_file_path)

    # facenet_model.train()
    facenet_model.verify_images_in_folder(threshold=0.05)

    # Plot verification metrics
    facenet_model.plot_verification_metrics(save_path)

if __name__ == "__main__":
    main()
