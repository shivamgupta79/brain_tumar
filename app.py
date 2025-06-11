import os
from flask import Flask, render_template, request, jsonify
import tensorflow as tf
import numpy as np
import cv2
from werkzeug.utils import secure_filename

app = Flask(__name__, template_folder='C:/Users/Gupta Family/Desktop/brain project/templates')

# Configure folder to save uploaded image
UPLOAD_FOLDER = 'static/uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Load the trained model
model = tf.keras.models.load_model('trained_model.h5')

# Define the homepage route
@app.route('/')
def home():
    return render_template('index.html')

# Define the prediction route
@app.route('/predict', methods=['POST'])
def predict():
    if 'file' not in request.files:
        return jsonify({'error': 'No file uploaded'}), 400

    file = request.files['file']
    if not file:
        return jsonify({'error': 'File upload error'}), 400

    # Save the uploaded image to the static/uploads folder
    filename = secure_filename(file.filename)
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    file.save(filepath)

    try:
        # Preprocess the uploaded image
        img = cv2.imread(filepath)  # Read the image from the saved file
        if img is None:
            return jsonify({'error': 'Failed to load image'}), 400

        img = cv2.resize(img, (224, 224))  # Resize to match model's input shape
        img = img / 255.0  # Normalize the image
        img = np.expand_dims(img, axis=0)  # Add batch dimension

        # Make a prediction
        predictions = model.predict(img)
        predicted_class = np.argmax(predictions, axis=1)

        # Class mapping (update based on your labels)
        class_map = {0: 'No Tumor', 1: 'Yes Tumor'}
        response = class_map.get(predicted_class[0], "Unknown")

        # Render the result template with the prediction and image path
        return render_template('result.html', prediction=response, image_url=filepath)

    except Exception as e:
        return jsonify({'error': f'An error occurred: {str(e)}'}), 500

if __name__ == '__main__':
    app.run(debug=True)
