from flask import Flask, request
from PIL import Image
import requests as req
import os

app = Flask(__name__)

@app.route('/', methods=['POST'])
def getPlate():
    if request.method == 'POST':
        img = Image.open(request.files['file'])
        import Start
        licensePlate = Start.main(img)
        data = {
            'plate_img': licensePlate[1],
            'plate_text': licensePlate[0]
        }
        req.post(os.environ['POLICESERVER_HOST'], files=data)
        return licensePlate[0]

        
