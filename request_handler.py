import json

class RequestHandler():

	def __init__(self, webSocketHandler):
		self.cursor = cursor;

	def authenticate(message):
		try:
			token = str(json.loads(message)['token'])
			try:
				self.cur.execute("SELECT * FROM access_tokens WHERE access_token  = %s" , (token,))
				for row in self.cur.fetchall():
					self.authenticated = True
					return json.dumps({'action': action, 'status': 'success', 'client_id': self.id}, indent=4)
				if self.authenticated == False:
					return json.dumps({'action': action, 'status': 'error', 'client_id': self.id, 'message': 'Unsucessfull authentication. Invalid token'}, indent=4)
			except:
					return json.dumps({'action': action, 'status': 'error', 'client_id': self.id, 'message': 'Can\'t perform request'}, indent=4)
		except KeyError, ValueError:
				return json.dumps({'action': action, 'status': 'error', 'client_id': self.id, 'message':'Token must be included to proceed request'}, indent=4)