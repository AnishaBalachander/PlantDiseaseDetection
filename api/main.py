from flask import Flask, request, jsonify
import numpy as np
from io import BytesIO
from PIL import Image
import tensorflow as tf
import pandas as pd

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


def read_file_as_image(data) -> np.ndarray:
    image = np.array(Image.open(BytesIO(data)))
    return image

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

if __name__ == "__main__":
    app.run(host="localhost", port=3300)
