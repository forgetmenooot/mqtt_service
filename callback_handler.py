from observer import Observer
import json

class MqttCallbackObserver(Observer):

	def __init__(self, webSocketHandler):
		Observer.__init__(self) 
		self.handler = webSocketHandler

	def handle_new_message_callback(self, data):
		self.handler.write_message(json.dumps({'action': 'on_message', 'status': 'success', 'client_id': self.handler.id, 'data': json.loads(data)}, indent=4))

	def handle_connect_callback(self, data):
		rc = json.loads(data)['rc']
		if rc == '0':
			result = 'success'
		else:
			result = 'error'
		self.handler.write_message(json.dumps({'action': 'on_connect', 'status': result, 'client_id': self.handler.id}, indent=4))

	def handle_disconnect_callback(self, data):
		rc = json.loads(data)['rc']
		if rc == '0':
			result = 'success'
		else:
			result = 'error'
		self.handler.write_message(json.dumps({'action': 'on_disconnect', 'status': result, 'client_id': self.handler.id}, indent=4))
		self.handler.connected = False