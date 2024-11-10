import os
import torch
import matplotlib.pyplot as plt
from PIL import Image
from torchvision import transforms
import seaborn as sns
from sklearn.metrics import confusion_matrix, classification_report
from .argface_extract_features import FeatureExtractor
from .argface_model import ArcFaceModel
from .argface_train import ArcFaceTrainer
from logger import info

class ArcFaceClassifier:
    def __init__(self, data_path, arcface_model_dir, model_save_path):
        self.model_loaded = False
        self.data_path = data_path
        self.arcface_model_dir = arcface_model_dir
        self.model_save_path = model_save_path
        self.feature_extractor = FeatureExtractor(data_path)
        self.features, self.labels, self.label_map = None, None, None
        self.model = None
        self.training_losses = []
        self.training_accuracies = []

    def initialize_model(self, num_classes=None):
        info("Initializing model...")
        self.extract_labels()
        if num_classes is None:
            num_classes = len(self.label_map) if self.label_map else 0
        if num_classes == 0:
            raise ValueError("Label map is not initialized. Call extract_labels() first.")
        feature_dim = 512
        self.model = ArcFaceModel(feature_dim=feature_dim, num_classes=num_classes, model_dir=self.arcface_model_dir)
        info(f"Model initialized with {num_classes} classes.")

    def extract_labels(self):
        info("Extracting labels...")
        self.feature_extractor.extract_labels()
        self.label_map = self.feature_extractor.label_map
        info(f"Extracted label map: {self.label_map}")

    def extract_features(self):
        info("Extracting features...")
        if self.model is None:
            raise ValueError("Model is not initialized. Call initialize_model() first.")
        self.feature_extractor.extract_features(self.model)
        self.features, self.labels = self.feature_extractor.get_features_and_labels()

        if self.features is None or self.labels is None:
            raise ValueError("Features or labels not extracted correctly.")
        if len(self.features) == 0 or len(self.labels) == 0:
            raise ValueError("Extracted features or labels are empty.")
        info("Features and labels extracted successfully.")

    def train(self, num_epochs=100, lr=0.001, momentum=0.9):
        info("Starting training...")
        if self.features is None or self.labels is None:
            raise ValueError("Features or labels is None. Ensure they are extracted correctly.")
        trainer = ArcFaceTrainer(self.model, self.features, self.labels, lr, momentum)
        
        for epoch in range(num_epochs):
            info(f"Epoch {epoch + 1}/{num_epochs}...")
            loss, accuracy = trainer.train_epoch()
            self.training_losses.append(loss)
            self.training_accuracies.append(accuracy)
            info(f'Epoch {epoch+1}/{num_epochs}, Loss: {loss:.4f}, Accuracy: {accuracy:.4f}')

        torch.save(self.model.state_dict(), self.model_save_path)
        info("Training completed. Model saved.")
        self.print_evaluation_metrics(self.labels, trainer.get_predictions(), save_path=self.arcface_model_dir)

    def plot_training_metrics(self, save_path=None):
        info("Plotting training metrics...")
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
            info(f'Plot saved to {save_path}')
        else:
            plt.show()
        info("Training metrics plotted.")
    
    def load_model(self):
        info("Loading model...")
        if not self.model_loaded:
            self.initialize_model()
            self.model.load_state_dict(torch.load(self.model_save_path))
            self.model_loaded = True
            info(f"Model loaded: {self.model_save_path}")
        else:
            info("Model already loaded, skipping reload.")

    def model_exists(self):
        exists = os.path.exists(self.model_save_path)
        info(f"Model exists: {exists}")
        return exists

    def identify_person(self, image_file):
        info(f"Identifying person from image: {image_file}")
        if not os.path.exists(image_file):
            raise FileNotFoundError(f"Image file not found: {image_file}")

        transform = transforms.Compose([
            transforms.Resize((112, 112)),
            transforms.ToTensor(),
            transforms.Normalize([0.5, 0.5, 0.5], [0.5, 0.5, 0.5])
        ])
        image = Image.open(image_file).convert("RGB")  # Ensure image is in RGB format
        image_tensor = transform(image).unsqueeze(0).to(self.model.device)  # Move tensor to the correct device

        with torch.no_grad():
            embedding = self.model.get_embedding(image_tensor).to(self.model.device)  # Ensure the embedding is on the device
            info(f"Generated embedding: {embedding.shape}")
        predicted = self.model.predict(embedding)  # Ensure tensor is moved before prediction
        info(f"Prediction result: {predicted}")
        
        person_name = self.label_map[predicted.item()]
        info(f"Identified person: {person_name} from image: {image_file}")
        return person_name
    
    def identify_person_from_embedding(self, embedding):
        info("Identifying person from embedding...")
        embedding_tensor = torch.tensor(embedding, dtype=torch.float32).unsqueeze(0).to(self.model.device)
        info(f"Embedding tensor: {embedding_tensor}")
        predicted = self.model.predict(embedding_tensor)
        info(f"Prediction result: {predicted}")
        person_name = self.label_map[predicted.item()]
        
        info(f"Identified person: {person_name} from embedding")
        return person_name

    def print_evaluation_metrics(self, true_labels, predicted_labels, save_path=None):
        info("Calculating ArcFace evaluation metrics...")
        conf_matrix = confusion_matrix(true_labels, predicted_labels)
        class_report = classification_report(true_labels, predicted_labels, output_dict=True)

        info(f"ArcFace Confusion Matrix:\n{conf_matrix}")
        info(f"Classification Report:\n{class_report}")

        if save_path:
            info("Saving evaluation metrics plots...")
            plt.figure(figsize=(10, 7))
            sns.heatmap(conf_matrix, annot=True, fmt='d', cmap='Blues')
            plt.title('Confusion Matrix')
            plt.ylabel('Actual Label')
            plt.xlabel('Predicted Label')
            plt.savefig(os.path.join(save_path, 'confusion_matrix.png'))
            info(f'Classification report saved to {os.path.join(save_path, "classification_report.png")}')