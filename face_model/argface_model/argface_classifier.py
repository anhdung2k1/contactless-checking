import os
import torch
import matplotlib.pyplot as plt
from PIL import Image
from torchvision import transforms
import seaborn as sns
from sklearn.metrics import accuracy_score, confusion_matrix, classification_report, mean_absolute_error, mean_squared_error, r2_score
import logging

from .argface_extract_features import FeatureExtractor
from .argface_model import ArcFaceModel
from .argface_train import ArcFaceTrainer

# Configure logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
handler = logging.StreamHandler()
handler.setLevel(logging.INFO)
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)

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
        self.training_losses = []
        self.training_accuracies = []

    def initialize_model(self, num_classes=None):
        self.extract_labels()
        if num_classes is None:
            num_classes = len(self.label_map) if self.label_map else 0
        if num_classes == 0:
            raise ValueError("Label map is not initialized. Call extract_labels() first.")
        feature_dim = 512
        self.model = ArcFaceModel(feature_dim=feature_dim, num_classes=num_classes, model_dir=arcface_model_dir)
        logger.info("Model initialized with %d classes", num_classes)

    def extract_labels(self):
        self.feature_extractor.extract_labels()
        self.label_map = self.feature_extractor.label_map
        logger.info("Labels extracted. Number of classes: %d", len(self.label_map))

    def extract_features(self):
        if self.model is None:
            raise ValueError("Model is not initialized. Call initialize_model() first.")
        self.feature_extractor.extract_features(self.model)
        self.features, self.labels = self.feature_extractor.get_features_and_labels()

        logger.info(f'Extracted features: {self.features.shape}')
        logger.info(f'Extracted labels: {self.labels.shape}')
        if self.features is None or self.labels is None:
            raise ValueError("Features or labels not extracted correctly.")
        if len(self.features) == 0 or len(self.labels) == 0:
            raise ValueError("Extracted features or labels are empty.")

    def train(self, num_epochs=100, lr=0.001, momentum=0.9):
        if self.features is None or self.labels is None:
            raise ValueError("Features or labels is None. Ensure they are extracted correctly.")
        trainer = ArcFaceTrainer(self.model, self.features, self.labels, lr, momentum)
        
        for epoch in range(num_epochs):
            loss, accuracy = trainer.train_epoch()
            self.training_losses.append(loss)
            self.training_accuracies.append(accuracy)
            logger.info(f'Epoch {epoch+1}/{num_epochs}, Loss: {loss:.4f}, Accuracy: {accuracy:.4f}')

        torch.save(self.model.state_dict(), model_save_path)
        self.print_evaluation_metrics(self.labels, trainer.get_predictions(), save_path=build_dir)

    def plot_training_metrics(self, save_path=None):
        epochs = range(1, len(self.training_losses) + 1)
        plt.figure(figsize=(10, 5))

        # Plot training loss
        plt.subplot(1, 2, 1)
        plt.plot(epochs, self.training_losses, 'b', label='Training loss')
        plt.title('Training Loss')
        plt.xlabel('Epochs')
        plt.ylabel('Loss')
        plt.legend()

        # Plot training accuracy
        plt.subplot(1, 2, 2)
        plt.plot(epochs, self.training_accuracies, 'r', label='Training Accuracy')
        plt.title('Training Accuracy')
        plt.xlabel('Epochs')
        plt.ylabel('Accuracy')
        plt.legend()

        if save_path:
            plt.savefig(save_path)
            logger.info(f'Plot saved to {save_path}')
        else:
            plt.show()
    
    def load_model(self):
        if not ArcFaceClassifier._model_loaded:
            self.initialize_model()
            self.model.load_state_dict(torch.load(model_save_path))
            ArcFaceClassifier._model_loaded = True
            logger.info(f"Model loaded: {model_save_path}")
        else:
            logger.info("Model already loaded, skipping reload.")

    def model_exists(self):
        exists = os.path.exists(model_save_path)
        logger.info(f"Model exists: {exists}")
        return exists

    def identify_person(self, image_file):
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
        
        logger.info(f"Identified person: {person_name} from image: {image_file}")
        return person_name
    
    def identify_person_from_embedding(self, embedding):
        embedding_tensor = torch.tensor(embedding, dtype=torch.float32).unsqueeze(0).to(self.model.device)
        predicted = self.model.predict(embedding_tensor)
        person_name = self.label_map[predicted.item()]
        
        logger.info(f"Identified person: {person_name} from embedding")
        return person_name

    def print_evaluation_metrics(self, true_labels, predicted_labels, save_path=None):
        conf_matrix = confusion_matrix(true_labels, predicted_labels)
        class_report = classification_report(true_labels, predicted_labels, output_dict=True)
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

        if save_path:
            plt.figure(figsize=(10, 7))
            sns.heatmap(conf_matrix, annot=True, fmt='d', cmap='Blues')
            plt.title('Confusion Matrix')
            plt.ylabel('Actual Label')
            plt.xlabel('Predicted Label')
            plt.savefig(os.path.join(save_path, 'confusion_matrix.png'))
            logger.info(f'Confusion matrix saved to {os.path.join(save_path, "confusion_matrix.png")}')

            plt.figure(figsize=(10, 7))
            plt.axis('off')
            plt.table(cellText=[[k, v] for k, v in class_report.items()], colLabels=["Class", "Metrics"], cellLoc='center', loc='center')
            plt.title('Classification Report')
            plt.savefig(os.path.join(save_path, 'classification_report.png'))
            logger.info(f'Classification report saved to {os.path.join(save_path, "classification_report.png")}')