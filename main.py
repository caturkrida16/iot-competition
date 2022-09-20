 # Import Packages
from flask import Flask, request, render_template, jsonify
from firebase_admin import credentials, firestore
import firebase_admin
import googlemaps
import os


# Initialization
app = Flask(__name__)
cred = credentials.Certificate("/service_account/firebase_admin") # Use ("/service_account/firebase_admin") for deploying in Cloud Run and call volume from Secret Manager
firebase_admin.initialize_app(cred)
db = firestore.client()
api_key = os.environ["API_KEY"]

# Routes
@app.route("/", methods=["GET"])
def index():
    show = {}
    nama_lokasi = []
    database = db.collection("data_banjir").stream()
    
    for data in database:
        show[data.id] = data.to_dict()
        nama_lokasi.append(data.id)
        
    return """
    <div id="lokasi"></div>
    <script>
        var wrapper = document.getElementById("lokasi");
        const nama_lokasi = """ + str(nama_lokasi) + """;
        
        for (var i=0; i<""" + str(len(nama_lokasi)) + """; i++) {
            wrapper.innerHTML = '<a href="/maps/' + nama_lokasi[i] + '">' + nama_lokasi[i] + '</a> <br>'
        }
    </script>   
    """
    
@app.route("/maps/<id>", methods=["GET"])
def maps(id):
    show = {}
    database = db.collection("data_banjir").document(id)
    get_data = database.get()
    data = get_data.to_dict()
    
    return """
    <style>
    table, th, td {
        border: 1px solid black;
    }
    th {
        text-align: center;
    }
    </style>
    
    <iframe width="600" height="450" style="border:0" loading="lazy" allowfullscreen src="https://www.google.com/maps/embed/v1/place?q=""" + str(data["latitude"]) + """%2C%20""" + str(data["longitude"]) + """&key=""" + api_key + """"></iframe>
    <br>
    <br>
    <br>
    <table>
        <tr>
            <th> Lokasi </th>
            <th> Ketinggian Air </th>
        </tr>
        <tr>
            <td> """ + str(data["name"]) + """ </td>
            <td> """ + str(data["ketinggian_air"]) + """ meter </td>
        </tr>
    </table>
    """

@app.route("/update", methods=["POST"])
def update():
    id = request.form["id"]
    status = request.form["status"]
    
    if status.lower() == "true" or status == "1":
        condition = True
        
    elif status.lower() == "false" or status == "0":
        condition = False
        
    database = db.collection("data_banjir").document(id)
    database.update(
    {
        "status": condition
    }
    )
    return jsonify(
    {
        "Process": "Sucess"
    }
    )

# APP Run
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080) # Delete "debug=True" before deploying
