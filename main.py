# Import Packages
from flask import Flask, request, render_template
from firebase_admin import credentials, firestore
import firebase_admin
import googlemaps
import os


# Initialization
app = Flask(__name__)
cred = credentials.Certificate("service_account/firebase_admin") # Use ("/service_account/firebase_admin") for deploying in Cloud Run and call volume from Secret Manager
firebase_admin.initialize_app(cred)
db = firestore.client()
api_key = os.environ["API_KEY"]

# Routes
@app.route("/", methods=["GET"])
def index():
    show = {}
    database = db.collection("data_banjir").stream()
    for data in database:
        show[data.id] = data.to_dict()
    
    return show
    
@app.route("/maps/<id>", methods=["GET"])
def maps(id):
    show = {}
    database = db.collection("data_banjir").document(id)
    get_data = database.get()
    data = get_data.to_dict()
    
    return """"
    <iframe width="600" height="450" style="border:0" loading="lazy" allowfullscreen src="https://www.google.com/maps/embed/v1/place?q=""" + str(data["latitude"]) + """%2C%20""" + str(data["longitude"]) + """&key=""" + api_key + """"></iframe>
    """

@app.route("/update", methods=["POST"])
def update():
    location = request.form["lokasi"]
    status = request.form["status"]
    
    if status.lower() == "true" or status == "1":
        condition = True
        
    elif status.lower() == "false" or status == "0":
        condition = False
        
    database = db.collection("data_banjir").document(location)
    database.update(
    {
        "status": condition
    }
    )
    return "Sucess"

# APP Run
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080, debug=True)  
