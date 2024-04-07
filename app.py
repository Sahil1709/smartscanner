from flask import Flask, request, jsonify
import os
from PIL import Image
import pytesseract
import pandas as pd
from geopy.distance import geodesic
from datetime import datetime, timedelta
import json

app = Flask(__name__)

# Set the path to the Tesseract OCR executable
# pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'


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

    # This response should come from llm
    llm_response = {
    "discreet response": "Yes",
    "explain": "\n\nThe parking sign, after combining all the OCR inputs, appears to say \"2 HOUR PARKING 8am to 6pm MON THRU FRI EXCEPT VEHICLES WITH AREA PERMITS.\" The time under consideration is Sat Apr 6 10:33:37 PM PDT 2024, which is well outside the restricted hours. Also, the day of the week is Saturday, and the restrictions mentioned are for Monday through Friday. \n\nThe OCR models provided different interpretations of the same sign, but all seem to agree on the essential details -restricted hours, the days of the week for those restrictions, and exceptions for area permits. The keras_ocr model seemed to struggle the most with the interpretation, providing \"9 hour parking\" and \"to bam\" which seems to be an error. The pytesseract model provided a somewhat clearer image, with \"HOUR PARKING 8am. 6e M MON THRU FRI\" which suggests a time restriction on parking from 8am to presumably 6pm, and on days from Monday through Friday. Finally, the easy_ocr model output seems to be the most accurate - \"2 HOUR PARKING To 8A.M_ 6P M_ MON THRU FRI\".\n\n Therefore, based on the present indications, parking should be permitted at the time of this query."
}

    # Remove the uploaded image file
    # os.remove(image_path)

    # Return the extracted text as a JSON response
    nearby_crimes = get_nearby_crimes(latitude, longitude)

    return jsonify({'text': text, 'nearby_crimes': nearby_crimes, 'llm_response':llm_response})

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
    app.run(debug=True)