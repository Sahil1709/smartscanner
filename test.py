import requests

url = 'http://localhost:5000/ocr'
files = {'image': open('image.png', 'rb')}
data = {'location': 'New York, NY'}

requests.post(url, files=files, data=data)
# print(response.json())