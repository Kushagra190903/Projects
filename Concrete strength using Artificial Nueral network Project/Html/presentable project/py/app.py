import torch
import torch.nn as nn
from flask import Flask, request, jsonify, render_template
import numpy as np

# Define the ConcreteStrengthANN model
class ConcreteStrengthANN(nn.Module):
    def __init__(self, input_size, hidden_layer_size=256):
        super(ConcreteStrengthANN, self).__init__()
        self.fc1 = nn.Linear(input_size, hidden_layer_size)
        self.bn1 = nn.BatchNorm1d(hidden_layer_size)
        self.fc2 = nn.Linear(hidden_layer_size, hidden_layer_size)
        self.bn2 = nn.BatchNorm1d(hidden_layer_size)
        self.fc3 = nn.Linear(hidden_layer_size, hidden_layer_size)
        self.bn3 = nn.BatchNorm1d(hidden_layer_size)
        self.fc4 = nn.Linear(hidden_layer_size, hidden_layer_size // 2)
        self.bn4 = nn.BatchNorm1d(hidden_layer_size // 2)
        self.fc5 = nn.Linear(hidden_layer_size // 2, 1)
        self.dropout = nn.Dropout(0.2)
        self.activation = nn.Tanh()

    def forward(self, x):
        x = self.activation(self.bn1(self.fc1(x)))
        x = self.dropout(x)
        x = self.activation(self.bn2(self.fc2(x)))
        x = self.dropout(x)
        x = self.activation(self.bn3(self.fc3(x)))
        x = self.dropout(x)
        x = self.activation(self.bn4(self.fc4(x)))
        x = self.dropout(x)
        x = self.fc5(x)  # No activation on output layer
        return x

# Load the trained model
model_path = 'concrete_strength_model.pth'
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
loaded_model = ConcreteStrengthANN(input_size=4).to(device)
loaded_model.load_state_dict(torch.load(model_path, map_location=device))
loaded_model.eval()

# Scaling parameters
scaler_mean = np.array([40.4434, 3808.96, 6.7604])
scaler_scale = np.array([33.3088, 561.04, 2.9706])
target_scaler_mean = 31.1931
target_scaler_scale = 9.5888

# Mapping for categorical encoding
type_of_aggregates_mapping = {
    "Recycled": 1,
    "Volcanic": 3,
    "Crushed": 0,
    "Rounded": 2
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
        type_of_aggregates = request.form.get('type_of_aggregates', '').strip()
        curing_age = request.form.get('curing_age', '').strip()
        upv = request.form.get('upv', '').strip()
        er = request.form.get('er', '').strip()

        # Validate and process inputs
        if not type_of_aggregates or type_of_aggregates not in type_of_aggregates_mapping:
            raise ValueError("Invalid or missing value for 'Type of Aggregates'")
        if not curing_age.replace('.', '', 1).isdigit() or not upv.replace('.', '', 1).isdigit() or not er.replace('.', '', 1).isdigit():
            raise ValueError("Invalid numeric input for 'Curing Age', 'UPV', or 'ER'")

        type_of_aggregates_encoded = type_of_aggregates_mapping[type_of_aggregates]
        curing_age = float(curing_age)
        upv = float(upv)
        er = float(er)

        # Normalize numerical features
        numerical_features = np.array([curing_age, upv, er])
        normalized_features = (numerical_features - scaler_mean) / scaler_scale

        # Combine categorical and normalized numerical features
        final_features = [type_of_aggregates_encoded] + normalized_features.tolist()
        input_tensor = torch.tensor([final_features], dtype=torch.float32).to(device)

        # Make prediction
        with torch.no_grad():
            scaled_prediction = loaded_model(input_tensor)
            prediction = (scaled_prediction.cpu().numpy().tolist()[0][0] * target_scaler_scale) + target_scaler_mean

        # Render prediction result
        return render_template('index.html', prediction=round(prediction, 2))

    except Exception as e:
        return jsonify({'error': str(e)}), 400

if __name__ == '__main__':
    app.run(debug=True, port=5001)
