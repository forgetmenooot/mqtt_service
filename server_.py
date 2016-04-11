from tornado import websocket, web, ioloop
from tornado.options import define, options, parse_command_line
from random import randint
from mqtt_server import MQQT_Server 
from callback_handler import MqttCallbackObserver
import json, sys, logging
import psycopg2

define("port", default=8888, help="run on the given port", type=int)
define("dbname", default='mqqtt_servive', help="dbname token are saved", type=str)
define("hostname", default='127.0.0.1', help="hostname of db", type=str)
define("actions", help="""use: {"action":"authenticate", "token": "1234567890"}
						possible actions and options:
						authenticate - token
						connect - token [client_id] 
						subscribe - topic [qos]
						publish - topic message [qos] [retain] 
						unsubscribe - topic
						disconnect""")

clients = {}

try:
	conn = psycopg2.connect("dbname=%s host=%s" % (options.dbname, options.hostname))
	cur = conn.cursor()
except:
	print "Unable to connect to the DB"
	sys.exit(1)

class ConnectHandler(web.RequestHandler):
	
	@web.asynchronous
	def get(self):
		self.write("This is your response")
		self.finish()

class WebSocketHandler(websocket.WebSocketHandler):

	def check_origin(self, origin):
		return True
	
	def open(self, *args):
		self.stream.set_nodelay(True)
		self.authenticated = False
		self.connected = False
		self.observer = MqttCallbackObserver(self)
		self.id = 'client_%s' % randint(1,10000000)
		clients[self.id] = {'id': self.id, 'object': self}

	def on_message(self, message):        
		print 'Client %s received message : %s' % (self.id, message)

		try:
			msg = json.loads(message)
			action = msg['action'] 
			if action == 'authenticate':
				try:
					token = str(msg['token'])
					try:
						cur.execute("SELECT * FROM access_tokens WHERE access_token  = %s" , (token,))
						for row in cur.fetchall():
							self.authenticated = True
							self.write_message(json.dumps({'action': action, 'status': 'success', 'client_id': self.id}, indent=4))
						if self.authenticated == False:
							self.write_message(json.dumps({'action': action, 'status': 'error', 'client_id': self.id, 'message': 'Unsucessfull authentication. Invalid token'}, indent=4))
					except:
						self.write_message(json.dumps({'action': action, 'status': 'error', 'client_id': self.id, 'message': 'Can\'t perform request'}, indent=4))
				except KeyError, ValueError:
					self.write_message(json.dumps({'action': action, 'status': 'error', 'client_id': self.id, 'message':'Token must be included to proceed request'}, indent=4))
			
			elif action == 'connect' and self.authenticated == True:
				try:
					if msg.has_key('client_id'):
						client_id = str(msg['client_id'])
						clean_session = False
					else:
						client_id = None
						clean_session = True
					self.server = MQQT_Server(client_id, clean_session)
					self.connected = True
					self.server.run()
					self.observer.observe("on_connect_" + str(self.server), self.observer.handle_connect_callback)
					self.observer.observe("on_disconnect_" + str(self.server), self.observer.handle_disconnect_callback)
					self.write_message(json.dumps({'action': action, 'status': 'success', 'client_id': self.id}, indent=4))
				except Exception, e:
					self.write_message(json.dumps({'action': action, 'status': 'error', 'client_id': self.id, 'message':str(e)}, indent=4))

			elif action == 'disconnect' and self.authenticated == True and self.connected == True:
				try:
					self.server.disconnect()
				except Exception, e:
					self.write_message(json.dumps({'action': action, 'status': 'error', 'client_id': self.id, 'message':str(e)}, indent=4))

			elif action == 'publish' and self.authenticated == True and self.connected == True:
				try:
					mes = str(msg['message'])
					topic = str(msg['topic'])
					if msg.has_key('qos'):
						qos = msg['qos']
					else:
						qos = 0
	   				if msg.has_key('retain'):
	   					retain = msg['retain']
	   				else:
	   					retain = False
					self.server.publish(mes, topic, qos, retain)
					self.write_message(json.dumps({'action': action, 'status': 'success', 'client_id': self.id, 'topic': topic, 'message': mes}, indent=4))
				except KeyError, ValueError:
					self.write_message(json.dumps({'action': action, 'status': 'error', 'client_id': self.id, 'message':'Message and topic must be included to proceed request'}, indent=4))
				except Exception, e:
					self.write_message(json.dumps({'action': action, 'status': 'error', 'client_id': self.id, 'message':str(e)}, indent=4))
			
			elif action  == 'subscribe' and self.authenticated == True and self.connected == True:
				try:
					if msg.has_key('qos'):
						qos = msg['qos']
					else:
						qos = 0
					topic = str(msg['topic'])
					self.server.subscribe(topic, qos)
					self.observer.observe('on_message_' + str(self.server), self.observer.handle_new_message_callback)
					self.write_message(json.dumps({'action': action, 'status': 'success', 'client_id': self.id, 'topic': topic}, indent=4))
				except KeyError, ValueError:
					self.write_message(json.dumps({'action': action, 'status': 'error', 'client_id': self.id, 'message':'Topic must be included to proceed request'}, indent=4))
				except Exception, e:
					self.write_message(json.dumps({'action': action, 'status': 'error', 'client_id': self.id, 'message':str(e)}, indent=4))

			elif action  == 'unsubscribe' and self.authenticated == True and self.connected == True:
				try:
					topic = str(msg['topic'])
					self.server.unsubscribe(topic)
					self.write_message(json.dumps({'action': action, 'status': 'success', 'client_id': self.id, 'topic': topic}, indent=4))
				except KeyError, ValueError:
					self.write_message(json.dumps({'action': action, 'status': 'error', 'client_id': self.id, 'message':'Topic must be included to proceed request'}, indent=4))
				except Exception, e:
					self.write_message(json.dumps({'action': action, 'status': 'error', 'client_id': self.id, 'message':str(e)}, indent=4))

			else:
				if self.authenticated == False:
					self.write_message(json.dumps({'action': action, 'status': 'error', 'client_id': self.id, 'message': 'Can\'t proceed request. Not authenticated'}, indent=4))
				elif self.connected == False:
					self.write_message(json.dumps({'action': action, 'status': 'error', 'client_id': self.id, 'message': 'Can\'t proceed request. Not connected'}, indent=4))
				else:
					self.write_message(json.dumps({'action': action, 'status': 'error', 'client_id': self.id, 'message':'Provided action is not supported'}, indent=4))

		except Exception:
			self.write_message(json.dumps({'status': 'error', 'client_id': self.id, 'message': 'Json is not valid'}, indent=4))

	def on_close(self):
		if self.id in clients:
			server = getattr(self, 'server', None)
			if server != None:
				self.server.disconnect()
			del clients[self.id]


app = web.Application([
	(r'/rest', ConnectHandler),
	(r'/ws', WebSocketHandler),
])

if __name__ == '__main__':
	parse_command_line()
	app.listen(options.port)
	ioloop.IOLoop.instance().start()
