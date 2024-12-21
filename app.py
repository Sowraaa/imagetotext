from flask import Flask, request, render_template
from azure.cognitiveservices.vision.computervision import ComputerVisionClient
from msrest.authentication import CognitiveServicesCredentials
import firebase_admin
from firebase_admin import credentials, db
import os

app = Flask(__name__)

AZURE_ENDPOINT = "https://imagetotextt.cognitiveservices.azure.com/"
AZURE_API_KEY = "2CKhHje2aXQ649zrs0cRcoiNyOPL0sfE9ndRO5XyXpwARX22Ve9WJQQJ99ALACYeBjFXJ3w3AAAFACOGmwqr"
computervision_client = ComputerVisionClient(AZURE_ENDPOINT, CognitiveServicesCredentials(AZURE_API_KEY))

cred = credentials.Certificate("firebase-key.json")
firebase_admin.initialize_app(cred, {
    'databaseURL': 'https://image-to-text-5b18a-default-rtdb.firebaseio.com/'
})

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        if "image" not in request.files:
            return "Tidak ada file gambar yang diunggah", 400
        image = request.files["image"]
        image_path = os.path.join("static", image.filename)
        image.save(image_path)

        with open(image_path, "rb") as image_stream:
            analysis = computervision_client.analyze_image_in_stream(image_stream, visual_features=["Objects"])
        detected_objects = [obj.object_property for obj in analysis.objects]

        ref = db.reference('detection_results')
        ref.push({
            "image_name": image.filename,
            "detected_objects": detected_objects
        })

        return render_template("index.html", objects=detected_objects, image_url=image_path)

    return render_template("index.html", objects=None)

@app.route("/history")
def history():
    ref = db.reference('detection_results')
    results = ref.get()
    return render_template("history.html", results=results)

if __name__ == "__main__":
    app.run(debug=True)
