from cassandra.cluster import Cluster
import os



def createTable(table_name):
    return "CREATE TABLE IF NOT EXISTS "+table_name+"( Name varchar PRIMARY KEY, Cluster INT, Image blob)"

def insertTable(table_name):
    return "insert into "+table_name+"(Name,Cluster,Image) values(?,?,?)"

def getFiles():
    path = r"{}\archive\flower_images\flower_images".format(os.getcwd())
    os.chdir(path)
    flowers = []
    with os.scandir(path) as files:
            for file in files:
                if file.name.endswith('.png'):
                    flowers.append(file.name)
    return flowers

def creationKeySpace(host,port,keyspace):
    createKeySpace= " CREATE KEYSPACE IF NOT EXISTS "+keyspace+"  WITH REPLICATION = { 'class' : 'SimpleStrategy', 'replication_factor' : 1 }  AND durable_writes = true; "
    cluster = Cluster([host], port=port)
    session=cluster.connect()
    session.execute(createKeySpace)
    session.set_keyspace(keyspace)
    session=cluster.connect(keyspace)

def ingestServeur(host,port,flowers,keyspace) :
    table_name="images"
    cluster = Cluster([host], port=port)
    session=cluster.connect()
    session=cluster.connect(keyspace)
    session.execute(createTable(table_name))
    for i in range(len(flowers)):
        image = open(flowers[i], 'rb') 
        image_read = image.read()
        query=insertTable(table_name)
        pStatement = session.prepare(query)
        session.execute(pStatement,[flowers[i],-1,image_read])

def lancementDeIngestion():
    host = '127.0.0.1'
    port=9042
    keyspace='event'
    flowers=getFiles()
    creationKeySpace(host,port,keyspace)
    ingestServeur(host,port,flowers,keyspace)