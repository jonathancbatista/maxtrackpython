#suposições dados coletados em intervalos iguais (1 min). Salvos na base (MongoDB) de dados no formato:
# {
# 	"serial" : "1308811990", 
# 	"ignicao" : false, 
# 	"situacao_movimento" : false, 
# 	"velocidade" : 0.0, 
# 	"latitude" : -22.8146596, 
# 	"longitude" : -43.3127033, 
# 	"orientacao" : 298.0, 
# 	"datahora": 1556240947
# }

#imports
import math
import pandas as pd
import numpy as np
from sklearn.cluster import KMeans
import pymongo

# calculo distancia no globo
def calcDistance(lat1,lon1,lat2,lon2):
	R = 6373.0				#Raio da Terra

	#convertendo coordenadas para radianos
	lat1Rad = math.radians(lat1) 
	lon1Rad = math.radians(lon1)
	lat2Rad = math.radians(lat2)
	lon2Rad = math.radians(lon2)

	#calculo da variação das coordenadas
	dlon = lon2Rad - lon1Rad
	dlat = lat2Rad - lat1Rad

	#Formula de Haversine
	a = math.sin(dlat / 2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon / 2)**2
	c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
	distance = R * c
	return distance

def calculaMetricas(cursor):
	distancia_percorrida = 0
	tempo_movimento = 0
	tempo_parado = 0
	serial = int(cursor[1]['serial'])
	data = pd.DataFrame.from_records(cursor)
	# data = pd.DataFrame(list(cursor))

	for index, row in data.iterrows():
		if index != 0:
			distancia_percorrida += calcDistance(row['latitude'], row['longitude'], data.iloc[index - 1]['latitude'], data.iloc[index - 1]['longitude'])
			if row['situacao_movimento'] == True:
				tempo_movimento += 60
			else:
				tempo_parado += 60

	paradas = data.groupby(['latitude','longitude']).size()
	paradas = paradas[paradas > 1].index
	qtdParadas = paradas.size

	dataCoord = data[['latitude', 'longitude']]
	kmeans = KMeans(n_clusters=qtdParadas)
	kmeans.fit(dataCoord)
	centroids = kmeans.cluster_centers_

	analise = {
		'distancia_percorrida': distancia_percorrida,
		'tempo_movimento': tempo_movimento,
		'tempo_parado': tempo_parado,
		'centroides': centroids.tolist(),
		'serial': serial
	}

	return analise

def getMetricaData(serial, datahora_inicio, datahora_fim):
	serial = int(serial)
	datahora_inicio = int(datahora_inicio)
	datahora_fim = int(datahora_fim)

	db = conn_denox()
	dados = db.dados_rastreamento.find({"serial": serial, "datahora":{"$gte": datahora_inicio,"$lte": datahora_fim}}, {'_id': False})
	
	return dados

def connect_mongo(host, port, username=False, password=False):
	if username and password:
		mongo_uri = 'mongodb://%s:%s@%s:%s/%s' % (username, password, host, port, db)
		conn = pymongo.MongoClient(mongo_uri)
	else:
		conn = pymongo.MongoClient(host, port)
	return conn


def conn_denox():
	conn = connect_mongo("localhost", 27017)
	return conn.denox

# test = getMetricaData(1308811990,29052020120000,29052020126000)
# print(calculaMetricas(test))
# print(list(test))
# print(test.count_documents)

# data = pd.read_json('mock.json')
# print(distancia_percorrida, tempo_parado, tempo_movimento, qtdParadas)
# print(centroids)

