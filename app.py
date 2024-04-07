from flask import Flask, request, jsonify
import os
from PIL import Image
import pytesseract
import pandas as pd
from geopy.distance import geodesic
from datetime import datetime, timedelta

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

@app.route('/get_nearby_crimes', methods=['POST'])
def get_nearby_crimes():
    crime_df = pd.read_csv('crime_df.csv')

    # Get the latitude and longitude from the client
    latitude = float(request.form['latitude'])
    longitude = float(request.form['longitude'])
    
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
    return jsonify(nearby_crimes.to_dict(orient='records'))

@app.route("/")
def hello_world():
    return "<p>Hello, World!</p>"

if __name__ == '__main__':
    app.run(debug=True)