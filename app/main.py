from flask import Flask, request, jsonify, render_template
import numpy as np
from io import BytesIO
from PIL import Image
import tensorflow as tf
import pandas as pd
import cv2
import base64
app = Flask(__name__)

disease_df = pd.read_csv("./training/db.csv")

CLASS_NAMES = [
    "Pepper__bell___Bacterial_spot",
    "Pepper__bell___healthy",
    "Potato___Early_blight",
    "Potato___Late_blight",
    "Potato___healthy",
    "Tomato_Bacterial_spot",
    "Tomato_Early_blight",
    "Tomato_Late_blight",
    "Tomato_Leaf_Mold",
    "Tomato_Septoria_leaf_spot",
    "Tomato_Spider_mites_Two_spotted_spider_mite",
    "Tomato__Target_Spot",
    "Tomato__Tomato_YellowLeaf__Curl_Virus",
    "Tomato__Tomato_mosaic_virus",
    "Tomato_healthy",
]

try:
    MODEL = tf.keras.models.load_model("../models/1")
except Exception as e:
    raise Exception(f"Error loading model: {str(e)}")

captured_image = None

def read_file_as_image(data) -> np.ndarray:
    image = np.array(Image.open(BytesIO(data)))
    return image

def capture_image_from_webcam():
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        return None

    ret, frame = cap.read()
    cap.release()

    if ret:
        return frame
    else:
        return None

@app.route("/ping", methods=["GET"])
def ping():
    return "Hello, I am alive"

@app.route("/predict", methods=["POST"])
def predict():
    try:
        file = request.files["file"]
        if file:
            image = read_file_as_image(file.read())
            img_batch = np.expand_dims(image, 0)
            predictions = MODEL.predict(img_batch)
            predicted_class = CLASS_NAMES[np.argmax(predictions[0])]
            confidence = float(np.max(predictions[0]))
            disease_info = disease_df[disease_df['Disease_Name'] == predicted_class]
            
            if disease_info.empty:
                return jsonify({'error': 'Disease information not found'}), 404

            # Extract symptoms and cures from the DataFrame
            symptoms = disease_info['Symptoms'].values[0]
            cures = disease_info['Cures'].values[0]

            return jsonify({
                'class': predicted_class,
                'confidence': confidence,
                'symptoms': symptoms,
                'cures': cures
            })
        else:
            return jsonify({'error': 'No file provided'}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 500
@app.route("/capture_image", methods=["POST"])
def capture_image():
    global captured_image
    captured_image = capture_image_from_webcam()
    if captured_image is not None:
        # Encode the captured image as base64 for display in HTML
        _, buffer = cv2.imencode('.jpg', captured_image)
        captured_image_base64 = base64.b64encode(buffer).decode('utf-8')
        return jsonify({'message': 'Image captured successfully', 'image_base64': captured_image_base64})
    else:
        return jsonify({'error': 'Failed to capture image'}), 500 
@app.route("/")
def index():
    return render_template("index.html")

if __name__ == "__main__":
    app.run(host="localhost", port=3300)

# if __name__ == "__main__":
#     app.run(host="0.0.0.0", port=80, debug=True)



