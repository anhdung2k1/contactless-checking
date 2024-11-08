import torch
import torch.nn as nn
import numpy as np
import insightface
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class ArcFaceModel(nn.Module):
    def __init__(self, feature_dim, num_classes, model_dir):
        super(ArcFaceModel, self).__init__()
        self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        self.face_analysis = insightface.app.FaceAnalysis(name='buffalo_l', root=model_dir)
        self.face_analysis.prepare(ctx_id=0 if self.device == torch.device('cuda') else -1)

        logging.info(f"Model initialized on device: {self.device}")

        # Define trainable layers
        self.fc1 = nn.Linear(feature_dim, 256)
        self.fc2 = nn.Linear(256, num_classes)
        self.criterion = nn.CrossEntropyLoss()

        # Move model to the appropriate device
        self.to(self.device)

    def get_embedding(self, image):
        logging.info("Extracting embedding from image")
        image_np = image.squeeze(0).permute(1, 2, 0).cpu().numpy()  # Ensure tensor is on CPU before converting
        image_np = ((image_np + 1) / 2 * 255).astype(np.uint8)  # Denormalize
        face_info = self.face_analysis.get(image_np)
        if len(face_info) == 0:
            logging.error("No face detected")
            raise ValueError("No face detected")
        logging.info("Face detected and embedding extracted")
        return torch.tensor(face_info[0].embedding, dtype=torch.float32).unsqueeze(0).to(self.device)

    def forward(self, features):
        logging.info(f"Forward pass started on device: {features.device}")
        features = features.to(self.device)
        logging.info(f"Input features moved to device: {features.device}")

        x = self.fc1(features)
        logging.info(f"After fc1 - device: {x.device}")

        x = nn.ReLU()(x)
        logging.info("Applied ReLU activation")

        output = self.fc2(x)
        logging.info(f"Output generated - device: {output.device}")
        return output

    def predict(self, feature):
        logging.info("Prediction started")
        feature = feature.to(self.device)
        logging.info(f"Feature moved to device: {feature.device}")

        # Check if all model parameters are on the correct device
        for name, param in self.named_parameters():
            if param.device != self.device:
                logging.error(f"Parameter {name} is on {param.device}, expected {self.device}")

        x = self.fc1(feature)
        logging.info(f"After fc1 - device: {x.device}")

        x = nn.ReLU()(x)
        logging.info("Applied ReLU activation")

        output = self.fc2(x)
        logging.info(f"Output generated - device: {output.device}")

        # Ensure the result is on the correct device if needed
        _, predicted = torch.max(output, 1)
        logging.info(f"Prediction completed. Predicted class: {predicted.item()}")

        return predicted

    def resize_final_layer(self, num_classes):
        if self.fc2.out_features != num_classes:
            logging.info(f"Resizing final layer to {num_classes} classes")
            self.fc2 = nn.Linear(256, num_classes)
            self.num_classes = num_classes

    def load_state_dict(self, state_dict, strict=True):
        logging.info("Loading state dict")
        if 'fc2.weight' in state_dict and state_dict['fc2.weight'].size(0) != self.fc2.out_features:
            logging.info(f"Adjusting final layer size from {self.fc2.out_features} to {state_dict['fc2.weight'].size(0)}")
            self.resize_final_layer(state_dict['fc2.weight'].size(0))
        super().load_state_dict(state_dict, strict)
        logging.info("State dict loaded successfully")
