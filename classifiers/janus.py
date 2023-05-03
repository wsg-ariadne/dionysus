from tensorflow.keras.models import load_model
from urllib.request import urlopen
import numpy as np
import cv2

class JanusModel:
    def __init__(self, model_path: str):
        self.model = load_model(model_path)

    def classify(self, img_uri: str) -> int:
        # Load image from data URI
        img_arr = np.asarray(bytearray(urlopen(img_uri).read()), dtype=np.uint8)
        img = cv2.imdecode(img_arr, cv2.IMREAD_COLOR)

        # Convert image to np array
        img = cv2.resize(img, (224, 224))
        img_arr = np.array([img])
        img_arr = img_arr / 225.0

        # Predict: 0 is absent, 1 is even, 2 is weighted
        return self.model.predict(img_arr).argmax(axis=1)[0]
