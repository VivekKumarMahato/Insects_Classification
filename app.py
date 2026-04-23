from flask import Flask, render_template, request, redirect, url_for, send_from_directory
from keras.models import load_model #type: ignore
from keras.preprocessing import image #type: ignore
import numpy as np
import io
import os
from PIL import Image
from datetime import datetime
from data import *
# Initialize Flask app
app = Flask(__name__)

# Define the upload folder for storing images
UPLOAD_FOLDER = 'uploaded_images'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Load the Keras model
model = load_model('model/insect_classifier.h5')

# Class labels
class_labels = {
    0: 'Africanized Honey Bees (Killer Bees)',
    1: 'Aphids',
    2: 'Armyworms',
    3: 'Brown Marmorated Stink Bugs',
    4: 'Cabbage Loopers',
    5: 'Citrus Canker',
    6: 'Colorado Potato Beetles',
    7: 'Corn Borers',
    8: 'Corn Earworms',
    9: 'Fall Armyworms',
    10: 'Fruit Flies',
    11: 'Spider Mites',
    12: 'Thrips',
    13: 'Tomato Hornworms',
    14: 'Western Corn Rootworms'
}

# Define the route for the HTML form
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/predict')
def predictrender():
    return render_template('predict.html')
# Define the route for prediction
@app.route('/predict', methods=['POST'])
def predict():
    # Get the file from the POST request
    file = request.files['image']
    
    if not file:
        return "No file uploaded", 400

    # Ensure the upload directory exists
    if not os.path.exists(app.config['UPLOAD_FOLDER']):
        os.makedirs(app.config['UPLOAD_FOLDER'])
    
    # Save the image with a unique name to avoid overwriting
    filename = datetime.now().strftime("%Y%m%d%H%M%S_") + ".webp"
    file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    file.save(file_path)

    # Convert the FileStorage object to a PIL Image object
    img = Image.open(file_path)
    
    # Preprocess the image
    img = img.resize((150,150))  # Resize the image to the required input size
    img_array = image.img_to_array(img)/255
    img_array = np.expand_dims(img_array, axis=0)  # Add batch dimension
    
    # Model prediction
    prediction = model.predict(img_array)
    predicted_class = np.argmax(prediction, axis=1)[0]
    number=predicted_class
    detail=data[number]
    # Get the label
    predicted_label = class_labels[predicted_class]
    
    # Render the prediction result page and pass the image filename and prediction
    return render_template('predict-result.html', prediction=predicted_label, number=number,detail=detail)

# Serve the uploaded images
@app.route('/uploads/<filename>')
def send_uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

# Run the Flask app
if __name__ == '__main__':
    app.run(debug=True)
