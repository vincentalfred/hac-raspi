import os
import paho.mqtt.client as mqtt
from django.utils import timezone

machines = {}
machineData = {}

def on_connect(client, userdata, flags, rc):
	try:
		from apps.taps.models import Tap
		from apps.machines.models import Machine
	except Exception as e:
		print("err: {}".format(e))
	
	global machines, machineData
	
	machineData.clear()
	machines = Machine.objects.all()
	print("onconnect!")
	
	for machine in machines:
		topic = "{}/state/#".format(machine.id)
		client.subscribe(topic)
		print("subscribe to {}.".format(topic))
		machineData[machine.id] = {
			'ssr': 0,
			'card_uid': '0',
			'usage': 0,
			'start_time': timezone.now(),
		}
	

def on_message(client, userdata, msg):
	from apps.taps.models import Tap
	from apps.machines.models import Machine

	global machines, machineData

	print("Yeay! payload = "+str(msg.payload))
	msg.payload = msg.payload.decode("utf-8")

	for machine in machines:
		topic = "{}/state/carduid".format(machine.id)
		if msg.topic == topic:
			print(msg.topic+" "+str(msg.payload))
			card_uid = str(msg.payload)
			if card_uid == machineData[machine.id]['card_uid']:
				# extend

			else:
				# cek kartu terdaftar atau tidak
				if #terdaftar:
					# start yg baru
					src_machine = Machine.objects.get(pk=machine.id)
					tap_time = timezone.now()
					power_usage = 100
					tap = Tap(card_uid = card_uid, machine = src_machine, tap_time = tap_time, power_usage = power_usage)
					tap.save()
				else:
					# save ke tabel unregistered card

		topic = "{}/state/stop".format(machine.id)
		if msg.topic == topic:
			print(msg.topic+" "+str(msg.payload))
			if machineData[machine.id]['ssr'] == 1:
				machineData[machine.id]['ssr'] = 0
				pubtopic = "{}/command/ssr".format(machine.id)
				pubmessage = "0"
				client.publish(pubtopic, pubmessage, qos=2)

		topic = "{}/state/power".format(machine.id)
		if msg.topic == topic:
			print(msg.topic+" "+str(msg.payload))


def on_disconnect(client, userdata, rc):
	client.loop_stop(force=False)
	if rc != 0:
		print("Unexpected disconnection. rc={}".format(rc))
	else:
		print("Disconnected")


client = mqtt.Client(client_id="raspi", clean_session=True, userdata=None, transport="tcp")
client.on_connect = on_connect
client.on_message = on_message
client.on_disconnect = on_disconnect

mqtt_server = "127.0.0.1";
mqtt_port = 1883;

client.connect(mqtt_server, mqtt_port, 60)




# cur_time = timezone.now()
# pubtopic = "{}/command/timeleft" .format(machine.id)
# # todo: cari cara utk kurangin waktu/cari selisih
# timeleft = 30 - (cur_time - machineData[machine.id]['start_time'])
# client.publish(pubtopic, timeleft)

