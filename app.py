import requests
from flask import Flask, request, jsonify
import numpy as np
from PIL import Image
import tensorflow as tf
from tensorflow.keras.utils import img_to_array

url = "https://drive.google.com/uc?id=1MTntYoyzv_Y2veMiC90eQqwF8m7GYJmM"
model = requests.get(url)
with open("model.tflite", 'wb') as f:
    f.write(model.content)
model = tf.lite.Interpreter(model_path="model.tflite")
model.allocate_tensors()

def rescale(img):
    img2 = img_to_array(img)
    img2 = img2/255
    img2 = img2.reshape(1,224,224,3)
    return img2

def pred(model,img):
    input_details = model.get_input_details()
    output_details = model.get_output_details()
    model.set_tensor(input_details[0]['index'],img)
    model.invoke()
    output_data = model.get_tensor(output_details[0]['index'])
    return output_data

app = Flask(__name__)

@app.route('/predict',methods=['POST'])
def predict():
    image = request.files['file']
    image.save("img.jpg")
    img = Image.open('img.jpg')
    img = img.resize((224, 224))
    img = rescale(img)
    output = pred(model,img).argmax()
    return jsonify(output)

if __name__ == '__main__':
    app.run(debug=True)
