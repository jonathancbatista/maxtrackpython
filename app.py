import tornado
from tornado.web import Application, RequestHandler
from tornado.ioloop import IOLoop
from bson.json_util import dumps

from functions import getMetricaData, calculaMetricas, conn_denox

class CalculaMetricasHandler(RequestHandler):
  def get(self):
    self.clear()
    self.set_status(400)

  def post(self):
  	#getting data
  	serial = self.get_argument('serial', None)
  	datahora_inicio = self.get_argument('datahora_inicio', None)
  	datahora_fim = self.get_argument('datahora_fim', None)

  	#checking data
  	if not(serial and datahora_inicio and datahora_fim):
  		self.set_status(400)
  		self.write('check you data')
  		return None

  	#get data from DB
  	data = getMetricaData(serial, datahora_inicio, datahora_fim)

  	#performings analysis 
  	analise = calculaMetricas(data)

  	#saving to DB
  	db = conn_denox()
  	resultados = db['resultados_jonathan']
  	resultados.insert_one(analise)
  	#removing _id from data
  	del analise['_id']

  	#return post request
  	self.write(dumps(analise))



class RetornaMetricasHandler(RequestHandler):
  def get(self):
  	db = conn_denox()
  	#get all resultados from collection
  	resultados = db.resultados_jonathan.find({},{'_id': False})
  	#get the last inserted one
  	lastResultado = resultados.sort("_id", -1).limit(1)

  	self.write(dumps(lastResultado))



class WellcomeHandler(RequestHandler):
	def get(self):
		self.write('Olá! Estamos tudo funcionando bem! Você pode fazer suas requesições à nossa API')

def make_app():
  urls = [
  	("/", WellcomeHandler),
  	("/api/calcula_metricas", CalculaMetricasHandler),
  	("/api/retorna_metricas", RetornaMetricasHandler)
  ]
  return Application(urls, debug=True)
  
if __name__ == '__main__':
	app = make_app()
	app.listen(3000)
	IOLoop.instance().start()