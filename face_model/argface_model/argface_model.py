import torch
import torch.nn as nn
import numpy as np
import insightface

class ArcFaceModel(nn.Module):
    def __init__(self, feature_dim, num_classes, model_dir):
        super(ArcFaceModel, self).__init__()
        self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        self.face_analysis = insightface.app.FaceAnalysis(name='buffalo_l', root=model_dir)
        self.face_analysis.prepare(ctx_id=0 if self.device == torch.device('cuda') else -1)

        # Define trainable layers
        self.fc1 = nn.Linear(feature_dim, 256)
        self.fc2 = nn.Linear(256, num_classes)
        self.criterion = nn.CrossEntropyLoss()

    def get_embedding(self, image):
        # Convert the image to numpy array
        image_np = image.squeeze(0).permute(1, 2, 0).numpy()
        image_np = ((image_np + 1) / 2 * 255).astype(np.uint8)  # Denormalize
        face_info = self.face_analysis.get(image_np)
        if len(face_info) == 0:
            raise ValueError("No face detected")
        return torch.tensor(face_info[0].embedding, dtype=torch.float32).unsqueeze(0).to(self.device)

    def forward(self, features):
        x = self.fc1(features)
        x = nn.ReLU()(x)
        output = self.fc2(x)
        return output

    def predict(self, feature):
        feature = feature.to(self.device)
        x = self.fc1(feature)
        x = nn.ReLU()(x)
        output = self.fc2(x)
        _, predicted = torch.max(output, 1)
        return predicted
    
    def resize_final_layer(self, num_classes):
        if self.fc2.out_features != num_classes:
            self.fc2 = nn.Linear(256, num_classes)
            self.num_classes = num_classes

    def load_state_dict(self, state_dict, strict=True):
        if 'fc2.weight' in state_dict and state_dict['fc2.weight'].size(0) != self.fc2.out_features:
            self.resize_final_layer(state_dict['fc2.weight'].size(0))
        super().load_state_dict(state_dict, strict)