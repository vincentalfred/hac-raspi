import os
import paho.mqtt.client as mqtt
from django.utils import timezone

machines = {}

def on_connect(client, userdata, flags, rc):
	from apps.taps.models import Tap
	from apps.machines.models import Machine

	global machines
	machines = Machine.objects.all();
	for machine in machines:
		topic = "{}/state/#".format(machine.id)
		client.subscribe(topic)
		print("subscribe to {}.". format(topic))

def on_message(client, userdata, msg):
	from apps.taps.models import Tap
	from apps.machines.models import Machine

	print("Yeay! payload = "+str(msg.payload))
	msg.payload = msg.payload.decode("utf-8")

	for machine in machines:
		topic = "{}/state/carduid".format(machine.id)
		if msg.topic == topic:
			print(msg.topic+" "+str(msg.payload))
			card_uid = str(msg.payload)
			src_machine = Machine.objects.get(pk=1)
			tap_time = timezone.now()
			power_usage = 100
			tap = Tap(card_uid = card_uid, machine = src_machine, tap_time = tap_time, power_usage = power_usage)
			tap.save()
		topic = "{}/state/power".format(machine.id)
		if msg.topic == topic:
			print(msg.topic+" "+str(msg.payload))


def on_disconnect(client, userdata, rc):
	client.loop_stop(force=False)
	if rc != 0:
		print("Unexpected disconnection.")
	else:
		print("Disconnected")

client = mqtt.Client(client_id="raspi", clean_session=True, userdata=None, transport="tcp")
client.on_connect = on_connect
client.on_message = on_message
client.on_disconnect = on_disconnect

mqtt_server = "127.0.0.1";
mqtt_port = 1883;

client.connect(mqtt_server, mqtt_port, 60)
# client.connect(mqtt_server)

