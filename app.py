from flask import Flask, request, jsonify
import os
from PIL import Image
import pytesseract

app = Flask(__name__)

# Set the path to the Tesseract OCR executable
# pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

@app.route('/ocr', methods=['POST'])
def ocr():
    image_file = request.files['image']
    location_data = request.form.get('location')
    # Save the image file to the server
    image_path = os.path.join('uploads', image_file.filename)

    image_file.save(image_path)

    # Perform OCR on the image
    text = pytesseract.image_to_string(Image.open(image_path), lang="eng", config='--psm 11')

    # Remove the uploaded image file
    # os.remove(image_path)

    # Return the extracted text as a JSON response
    return jsonify({'text': text, 'location': location_data})

@app.route("/")
def hello_world():
    return "<p>Hello, World!</p>"

if __name__ == '__main__':
    app.run(debug=True)