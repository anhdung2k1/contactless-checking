import torch
import torch.optim as optim
import torch.nn as nn
from logger import info

class ArcFaceTrainer:
    def __init__(self, model, features, labels, lr=0.01, momentum=0.9):
        self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        self.model = model.to(self.device)
        self.features = torch.tensor(features, dtype=torch.float32).to(self.device)
        self.labels = torch.tensor(labels, dtype=torch.long).to(self.device)
        self.optimizer = optim.SGD(model.parameters(), lr=lr, momentum=momentum)
        self.criterion = nn.CrossEntropyLoss()

    def train_epoch(self):
        self.model.train()
        self.optimizer.zero_grad()
        outputs = self.model(self.features)
        loss = self.criterion(outputs, self.labels)
        loss.backward()
        self.optimizer.step()

        # Calculate accuracy
        _, predicted = torch.max(outputs, 1)
        total = self.labels.size(0)
        correct = (predicted == self.labels).sum().item()
        accuracy = correct / total

        return loss.item(), accuracy
    
    def get_predictions(self):
        self.model.eval()
        with torch.no_grad():
            outputs = self.model(self.features)
            _, predicted = torch.max(outputs, 1)
        return predicted.cpu().numpy()

    def train(self, num_epochs=10):
        for epoch in range(num_epochs):
            loss, accuracy = self.train_epoch()
            info(f'Epoch [{epoch+1}/{num_epochs}], Loss: {loss:.4f}, Accuracy: {accuracy:.4f}')
