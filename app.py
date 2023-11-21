from flask import Flask, render_template, url_for,request
from kmeans_database import readClusterData, lancerLentrainementWithoutPrint
from werkzeug.utils import secure_filename
import os

app = Flask(__name__,template_folder='template')
chemin = os.getcwd()
chemin=chemin.replace("\\","/")
app.config['UPLOAD_FOLDER'] =  chemin+'/static/archive/flower_images/flower_images/'


def getImageUrls():
    clusterList=readClusterData()
    image_urls={}
    for cluster in clusterList:
        image_urls[cluster["Cluster"]]=[]
        for image in cluster["ImageList"] :
            image_urls[cluster["Cluster"]].append('/static/archive/flower_images/flower_images/'+image)
        image_urls[cluster["Cluster"]]=image_urls[cluster["Cluster"]][:10]
    return image_urls

@app.route('/')
def index():
    image_urls=getImageUrls()
    return render_template('index.html',image_urls=image_urls)

@app.route('/training')
def training():
    entrainementFini=True
    try : 
        lancerLentrainementWithoutPrint()
        image_urls=getImageUrls()
        return render_template('trainingpage.html',image_urls=image_urls,entrainementFini=entrainementFini)
    except :
        image_urls=getImageUrls()
        return render_template('trainingpage.html',image_urls=image_urls,entrainementFini=False)


@app.route('/upload', methods=['POST'])
def upload():
    files = request.files.getlist('images') 
    for file in files:
        filename = secure_filename(file.filename)
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename)) 
    image_urls=getImageUrls()
    return render_template('index.html',image_urls=image_urls)


if __name__ == "__main__":
    app.run(debug=True,host='0.0.0.0')