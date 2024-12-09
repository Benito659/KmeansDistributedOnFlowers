from keras.applications.vgg16 import preprocess_input 
from keras.applications.vgg16 import VGG16 
from keras.models import Model
from sklearn.cluster import KMeans
from sklearn.decomposition import PCA
# from sklearn.neighbors import NearestNeighbors
from cassandra.cluster import Cluster
from ingestionImageCassandra import creationKeySpace

from PIL import Image
import pandas as pd
import numpy as np
import pickle
import io
import os


def createTable(table_name):
    return "CREATE TABLE IF NOT EXISTS "+table_name+"( Cluster Int PRIMARY KEY, ImageList list<text> )"

def insertTable(table_name):
    return "insert into "+table_name+"(Cluster,ImageList) values( %s, %s)"

def ingestCluster(host,port,groups,keyspace) :
    table_name="clusters"
    cluster = Cluster([host], port=port)
    session=cluster.connect()
    session=cluster.connect(keyspace)
    session.execute(createTable(table_name))
    for cle, valeur in groups.items():
        query=insertTable(table_name)
        valeur = [str(x) for x in valeur]
        session.execute(query,(cle,valeur))

def readFlowerFromDatabase():
    flowersData=[]
    host = '127.0.0.1'
    port=9042
    keyspace='event'
    cluster = Cluster([host], port=port)
    session=cluster.connect()
    session=cluster.connect(keyspace)
    rows = session.execute("SELECT * FROM images ;")
    for row in rows:
        flowersData.append({"Name":row.name,"Cluster":row.cluster,"Image":row.image})
    return flowersData

def extract_features_data(file, model):
    image = Image.open(io.BytesIO(file))
    resized_image = image.resize((224, 224))
    resized_image = resized_image.convert('RGB')
    img = np.array(resized_image) 
    reshaped_img = img.reshape(1,224,224,3) 
    imgx = preprocess_input(reshaped_img)
    features = model.predict(imgx, use_multiprocessing=True)
    return features

def getDataFeatures(flowers,model):
    data = {}
    p = r"{}\archive\flower_images\flower_images\flower_features.pkl".format(os.getcwd())
    for flower in flowers:
        try:
            feat = extract_features_data(flower["Image"],model)
            data[flower["Name"]] = feat
        except:
            with open(p,'wb') as file:
                pickle.dump(data,file)
    return data

def getGroups(filenames,kmeans):
    groups = {}
    for file, cluster in zip(filenames,kmeans.labels_):
        if cluster not in groups.keys():
            groups[cluster] = []
            groups[cluster].append(file)
        else:
            groups[cluster].append(file)
    return groups

def ingestionData(groups):
    host = '127.0.0.1'
    port=9042
    keyspace='clusterspace'
    creationKeySpace(host,port,keyspace)
    ingestCluster(host,port,groups,keyspace)

def readClusterData():
    clusters=[]
    host = '127.0.0.1'
    port=9042
    keyspace='clusterspace'
    cluster = Cluster([host], port=port)
    session=cluster.connect()
    session=cluster.connect(keyspace)
    rows = session.execute("SELECT * FROM clusters ;")
    for row in rows:
        clusters.append({"Cluster":row.cluster,"ImageList":row.imagelist})
    return clusters


def lancerLentrainement():
    path = r"{}\archive\flower_images\flower_images".format(os.getcwd())
    os.chdir(path)
    flowers = readFlowerFromDatabase()
    model = VGG16()
    model = Model(inputs=model.inputs, outputs=model.layers[-2].output)
    data = getDataFeatures(flowers,model)
    filenames = np.array(list(data.keys()))
    feat = np.array(list(data.values()))
    feat = feat.reshape(-1,4096)
    df = pd.read_csv('flower_labels.csv')
    label = df['label'].tolist()
    unique_labels = list(set(label))
    pca = PCA(n_components=100, random_state=22)
    pca.fit(feat)
    x = pca.transform(feat)
    kmeans = KMeans(n_clusters=len(unique_labels), random_state=22,n_init='auto')
    kmeans.fit(x)
    groups = getGroups(filenames,kmeans)
    ingestionData(groups)


def lancerLentrainementWithoutPrint():
    flowers = readFlowerFromDatabase()
    model = VGG16()
    model = Model(inputs=model.inputs, outputs=model.layers[-2].output)
    data = getDataFeatures(flowers,model)
    filenames = np.array(list(data.keys()))
    feat = np.array(list(data.values()))
    feat = feat.reshape(-1,4096)
    chemin = os.getcwd()
    chemin=chemin.replace("\\","/")
    df = pd.read_csv(chemin+'/static/archive/flower_images/flower_images/flower_labels.csv')
    label = df['label'].tolist()
    unique_labels = list(set(label))
    pca = PCA(n_components=100, random_state=22)
    pca.fit(feat)
    x = pca.transform(feat)
    kmeans = KMeans(n_clusters=len(unique_labels), random_state=22,n_init='auto')
    kmeans.fit(x)
    groups = getGroups(filenames,kmeans)
    ingestionData(groups)