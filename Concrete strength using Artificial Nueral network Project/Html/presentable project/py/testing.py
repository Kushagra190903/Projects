import torch
import torch.nn as nn  # Import torch.nn
import numpy as np

# Preprocessing parameters
mean_values = np.array([40.4434, 3808.96, 6.7604])
scale_values = np.array([33.3088, 560.98, 2.9706])

# Inputs
type_of_aggregates = 2  # Crushed
curing_age = 120
upv = 3533.3246
er = 16.007

# Normalize numerical features
numerical_features = np.array([curing_age, upv, er])
normalized_features = (numerical_features - mean_values) / scale_values

# Combine inputs
final_features = [type_of_aggregates] + normalized_features.tolist()
input_tensor = torch.tensor([final_features], dtype=torch.float32)

# Define the model
class ConcreteStrengthANN(nn.Module):
    def __init__(self, input_size=4, hidden_layer_size=128):
        super(ConcreteStrengthANN, self).__init__()
        self.fc1 = nn.Linear(input_size, hidden_layer_size)
        self.fc2 = nn.Linear(hidden_layer_size, hidden_layer_size)
        self.fc3 = nn.Linear(hidden_layer_size, hidden_layer_size)
        self.dropout = nn.Dropout(0.1)
        self.fc4 = nn.Linear(hidden_layer_size, 1)
        self.activation1 = nn.ReLU()
        self.activation2 = nn.Identity()

    def forward(self, x):
        x = self.activation1(self.fc1(x))
        x = self.dropout(x)
        x = self.activation1(self.fc2(x))
        x = self.dropout(x)
        x = self.activation1(self.fc3(x))
        x = self.dropout(x)
        x = self.activation2(self.fc4(x))
        return x

# Load the model
model_path = 'concrete_strength_model.pth'
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
model = ConcreteStrengthANN(input_size=4).to(device)
model.load_state_dict(torch.load(model_path, map_location=device))
model.eval()

# Predict
with torch.no_grad():
    prediction = model(input_tensor.to(device))
    print(f"Model Predicted Concrete Strength: {prediction.item()} Mpa")