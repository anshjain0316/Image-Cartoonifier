import cv2
import numpy as np
import os
from flask import Flask, request, send_file, render_template, jsonify, send_from_directory
from werkzeug.utils import secure_filename

app = Flask(__name__)

# Configuring directories
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['CARTOON_FOLDER'] = 'cartoonized_images'
app.config['ALLOWED_EXTENSIONS'] = {'png', 'jpg', 'jpeg'}

# Function to check file extension
def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

# OpenCV cartoonization function
def cartoonize_image(image, k=8):
    # Convert to grayscale
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    
    # Apply median blur to the grayscale image
    gray = cv2.medianBlur(gray, 3)
    
    # Detect edges using adaptive thresholding
    edges = cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 9, 8)

    # Defining input data for clustering
    data = np.float32(image).reshape((-1, 3))

    # K-means clustering criteria
    criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 20, 1.0)

    # Apply k-means clustering
    _, label, center = cv2.kmeans(data, k, None, criteria, 10, cv2.KMEANS_RANDOM_CENTERS)
    center = np.uint8(center)

    # Recreate the image based on the clustered centers
    result = center[label.flatten()]
    result = result.reshape(image.shape)

    # Apply median blur to the clustered image
    blurred = cv2.medianBlur(result, 3)

    # Combine the edges with the blurred image to create the cartoon effect
    cartoon = cv2.bitwise_and(blurred, blurred, mask=edges)

    return cartoon

# Route to render the HTML page
@app.route('/')
def home():
    return render_template('index.html')

# Route to handle image upload and cartoonization
@app.route('/cartoonify', methods=['POST'])
def cartoonify():
    if 'image' not in request.files:
        return jsonify({"error": "No file provided"}), 400

    file = request.files['image']
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)

        # Load the uploaded image
        img = cv2.imread(filepath)

        # Apply cartoonization (You can choose which function to use)
        cartoon_img = cartoonize_image(img)  # or cartoonize(img, 8)    

        # Save the cartoonized image
        cartoon_filename = f"cartoon_{filename}"
        cartoon_filepath = os.path.join(app.config['CARTOON_FOLDER'], cartoon_filename)

        cv2.imwrite(cartoon_filepath, cartoon_img)

        # Return the cartoonized image to the client
        return send_file(cartoon_filepath, mimetype='image/jpeg')

    return jsonify({"error": "Invalid file"}), 400

@app.route('/cartoonized_images/<filename>')
def send_cartoonized_image(filename):
    return send_from_directory(app.config['CARTOON_FOLDER'], filename)

if __name__ == '__main__':
    # Ensure the upload and cartoonized folders exist
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    os.makedirs(app.config['CARTOON_FOLDER'], exist_ok=True)
    
    app.run(debug=True)
