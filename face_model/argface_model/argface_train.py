import torch
import torch.optim as optim
import torch.nn as nn

class ArcFaceTrainer:
    def __init__(self, model, features, labels, lr=0.01, momentum=0.9):
        self.model = model
        self.features = torch.tensor(features, dtype=torch.float32)
        self.labels = torch.tensor(labels, dtype=torch.long)
        self.optimizer = optim.SGD(model.parameters(), lr=lr, momentum=momentum)
        self.criterion = nn.CrossEntropyLoss()

    def train(self, num_epochs=10):
        self.model.train()
        for epoch in range(num_epochs):
            self.optimizer.zero_grad()
            output = self.model(self.features)
            loss = self.criterion(output, self.labels)
            loss.backward()
            self.optimizer.step()
            print(f'Epoch [{epoch+1}/{num_epochs}], Loss: {loss.item():.4f}')
