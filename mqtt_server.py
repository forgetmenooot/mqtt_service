import paho.mqtt.client as mqtt
import json, cmd
from observer import Event

class MQQT_Server():

	def __init__(self, client_id=None, clean_session=True):
		self.mqttc = mqtt.Client(client_id=client_id, clean_session=clean_session)
		self.mqttc.on_message = self.on_message
		self.mqttc.on_connect = self.on_connect
		self.mqttc.on_publish = self.on_publish
		self.mqttc.on_subscribe = self.on_subscribe	
		self.mqttc.on_publish = self.on_publish
		self.mqttc.on_unsubscribe = self.on_unsubscribe
		self.mqttc.on_disconnect = self.on_disconnect
		self.mqttc.on_log = self.on_log

	def publish(self, msg, topic, qos=0, retain=False):
		(result, mid) = self.mqttc.publish(topic, msg, qos) 
		# Event("publish_" + str(self), json.dumps({"result": str(result), "mid": str(mid)}))

	def unsubscribe(self, topic):
		(result, mid) = self.mqttc.unsubscribe(topic)
		# Event("unsubscribe_" + str(self), json.dumps({"result": str(result), "mid": str(mid)}))

	def on_unsubscribe(self, client, userdata, mid):
		pass
		# Event("on_unsubscribe_" + str(self), json.dumps({"mid": str(mid)}))

	def subscribe(self, topic, qos=0):
		(result, mid) = self.mqttc.subscribe(topic, qos)
		self.mqttc.loop_start()
		# Event("subscribe_" + str(self), json.dumps({"result": str(result), "mid": str(mid)}))

	def disconnect(self):
		self.mqttc.disconnect()

	def on_connect(self, mqttc, obj, flags, rc):
		Event("on_connect_"+str(self), json.dumps({"rc": str(rc)})) #after subscribe

	def on_message(self, mqttc, obj, msg):
		Event("on_message_" + str(self), json.dumps({"message": str(msg.payload), "topic": str(msg.topic)}))

	def on_subscribe(self, mqttc, obj, mid, granted_qos):
		pass
		# Event("on_subscribe_" + str(self), json.dumps({"mid": str(mid)}))

	def on_publish(self, mqttc, obj, mid):
		pass
		# Event("on_publish_" + str(self), json.dumps({"mid": str(mid)}))

	def on_log(self, mqttc, obj, level, string):
		pass

	def on_disconnect(self, mqttc, obj, rc):
		Event("on_disconnect_" + str(self), json.dumps({"rc" : str(rc)}))

	def run(self, host="127.0.0.1", port=1883, keepalive=20):
		self.mqttc.connect(host=host, port=port, keepalive=keepalive)
