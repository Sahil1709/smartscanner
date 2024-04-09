from flask import Flask, request, jsonify
import os
from PIL import Image
import pytesseract
import pandas as pd
from geopy.distance import geodesic
from datetime import datetime, timedelta
import json
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# Set the path to the Tesseract OCR executable
# pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

def run_bash_script(file_path):
    bash_script_path = "./run_scripts.sh"

    result = subprocess.run([bash_script_path, file_path], capture_output=True, text=True)

    if result.stdout:
        print("Output:", result.stdout)
    if result.stderr:
        print("Error:", result.stderr)


@app.route('/ocr', methods=['POST'])
def ocr():
    image_file = request.files['image']
    latitude = float(request.form['latitude'])
    longitude = float(request.form['longitude'])

    # Save the image file to the server
    image_path = os.path.join('uploads', image_file.filename)

    image_file.save(image_path)

    # Perform OCR on the image
    text = pytesseract.image_to_string(Image.open(image_path), lang="eng", config='--psm 11')

    file_path  = 'final.json'
    run_bash_script(img_path)
    with open(file_path, 'r') as file:
       data = json.load(file)
    # This response should come from llm
    llm_response = data

    # Remove the uploaded image file
    os.remove(image_path)

    # Return the extracted text as a JSON response
    nearby_crimes = get_nearby_crimes(latitude, longitude)

    return jsonify({'nearby_crimes': nearby_crimes, 'llm_response':llm_response})

def get_nearby_crimes(latitude, longitude):
    crime_df = pd.read_csv('crime_df.csv')
    
    # Define the search radius (in kilometers)
    search_radius = 1  # km
    
    # Create a function to calculate the distance between two coordinates
    def get_distance(lat1, lon1, lat2, lon2):
        return geodesic((lat1, lon1), (lat2, lon2)).km
    
    crime_df['Distance'] = crime_df.apply(lambda row: get_distance(row['Latitude'], row['Longitude'], latitude, longitude), axis=1)
    crime_df['Incident Datetime'] = pd.to_datetime(crime_df['Incident Datetime'])

    last_month_start = datetime.now().replace(day=1) - timedelta(days=1)
    last_month_start = last_month_start.replace(day=1)
    last_month_end = datetime.now().replace(day=1) - timedelta(days=1)

    last_month_start = pd.Timestamp(last_month_start)
    last_month_end = pd.Timestamp(last_month_end)

    nearby_crimes = crime_df[(crime_df['Distance'] < search_radius) & (crime_df['Incident Datetime'] >= last_month_start) & (crime_df['Incident Datetime'] <= last_month_end)]

    # Convert the DataFrame to a JSON response
    return nearby_crimes.to_dict(orient='records')

@app.route("/")
def hello_world():
    return "<p>Hello, World!</p>"

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)