import json
import numpy as np
from keras.models import load_model
from flask import Flask, request, jsonify

model = load_model("./models/model.h5")

app = Flask(__name__)
@app.route('/predict', methods=['POST'])
def predict():
    data = request.get_json()

    ladder = [data['ladder']]
    ladder = np.array(ladder)

    result = model.predict(ladder, verbose=0)
    predicted = np.argmax(result[0]).tolist()
    return jsonify({"prediction": predicted})

app.run()