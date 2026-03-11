import torch
import torch.nn as nn
from flask import Flask, request, jsonify, render_template
from sklearn.preprocessing import StandardScaler
import numpy as np

# Define the ConcreteStrengthANN model
class ConcreteStrengthANN(nn.Module):
    def __init__(self, input_size=4, hidden_layer_size=128):
        super(ConcreteStrengthANN, self).__init__()
        self.fc1 = nn.Linear(input_size, hidden_layer_size)
        self.fc2 = nn.Linear(hidden_layer_size, hidden_layer_size)
        self.fc3 = nn.Linear(hidden_layer_size, hidden_layer_size)
        self.dropout = nn.Dropout(0.1)
        self.fc4 = nn.Linear(hidden_layer_size, 1)
        self.activation1 = nn.ReLU()
        self.activation2 = nn.Identity()  # Identity activation for output layer

    def forward(self, x):
        x = self.activation1(self.fc1(x))
        x = self.dropout(x)
        x = self.activation1(self.fc2(x))
        x = self.dropout(x)
        x = self.activation1(self.fc3(x))
        x = self.dropout(x)
        x = self.activation2(self.fc4(x))
        return x

# Load the trained model
model_path = 'concrete_strength_model.pth'
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
loaded_model = ConcreteStrengthANN(input_size=4).to(device)
loaded_model.load_state_dict(torch.load(model_path, map_location=device))
loaded_model.eval()

# Updated mean and scale values from training
mean_values = np.array([40.4434, 3808.96, 6.7604])  # Mean of [Curing Age, UPV, ER]
scale_values = np.array([33.3088, 560.98, 2.9706])  # Scale of [Curing Age, UPV, ER]

# Mapping for categorical encoding
type_of_aggregates_mapping = {
    "Recycled": 0,
    "Volcanic": 1,
    "Crushed": 2,
    "Rounded": 3
}

# Initialize Flask app
app = Flask(__name__)

@app.route('/', methods=['GET'])
def index():
    return render_template('index.html')

@app.route('/predict', methods=['POST'])
def predict():
    try:
        # Get input values from the form
        type_of_aggregates = request.form['type_of_aggregates']  # Categorical input
        curing_age = float(request.form['curing_age'])           # Float input for Curing Age
        upv = float(request.form['upv'])                         # Float input for UPV
        er = float(request.form['er'])                           # Float input for ER

        # Encode categorical feature
        if type_of_aggregates in type_of_aggregates_mapping:
            type_of_aggregates_encoded = type_of_aggregates_mapping[type_of_aggregates]
        else:
            raise ValueError(f"Invalid type_of_aggregates value: {type_of_aggregates}")

        # Normalize numerical features
        numerical_features = np.array([curing_age, upv, er])
        normalized_features = (numerical_features - mean_values) / scale_values

        # Combine categorical and normalized numerical features
        final_features = [type_of_aggregates_encoded] + normalized_features.tolist()

        # Convert to PyTorch tensor
        input_tensor = torch.tensor([final_features], dtype=torch.float32).to(device)

        # Make prediction
        with torch.no_grad():
            prediction = loaded_model(input_tensor)
            prediction_value = prediction.cpu().numpy().tolist()[0][0]

        # Render prediction result
        return render_template('index.html', prediction=round(prediction_value, 2))

    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, port=5001)