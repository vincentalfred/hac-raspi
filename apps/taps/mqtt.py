import os
import paho.mqtt.client as mqtt
from django.utils import timezone

from apps.taps.models import Tap
from apps.machines.models import Machine
from apps.cards.models import Card, Unregistered_card
from apps.usages.models import Usage

machines = {}
machineData = {}

def on_connect(client, userdata, flags, rc):
	global machines, machineData
	
	machineData.clear()
	machines = Machine.objects.all()
	print("@on_connect. Connected!")
	
	for machine in machines:
		topic = "{}/state/#".format(machine.id)
		client.subscribe(topic)
		print("Subscribe to {}.".format(topic))
		machineData[machine.id] = {
			'ssr'		: 0,
			'card_uid'	: 0,
			'user_id'	: 0,
			'usage'		: 0,
			'start_time': 0,
			'end_time'	: 0,
		}
	

def on_message(client, userdata, msg):
	global machines, machineData

	print("New Message! Payload = "+str(msg.payload))
	msg.payload = msg.payload.decode("utf-8")

	for machine in machines:
		topic = "{}/state/carduid".format(machine.id)
		if msg.topic == topic:
			print(msg.topic+" "+str(msg.payload))
			card_uid = str(msg.payload)
			if card_uid == machineData[machine.id]['card_uid']:
				# extend
				print("extending usage of {}." .format(card_uid))
			else:
				cardExist = 1
				try:
					card = Card.objects.get(card_uid=card_uid)
				except Card.DoesNotExist:
					print("{} is unregistered." .format(card_uid))
					cardExist = 0;
					new_card = Unregistered_card(machine=machine.id, card_uid=card_uid)
					new_card.save();
					
				if cardExist:
					print("Starting new session.");
					src_machine = Machine.objects.get(pk=machine.id)
					tap_time = timezone.now()
					power_usage = 100
					tap = Tap(card_uid = card_uid, machine = src_machine, tap_time = tap_time, power_usage = power_usage)
					tap.save()
					machineData[machine.id] = {
						'ssr'		: 1,
						'card_uid'	: str(card_uid),
						'user_id'	: User.objects.get(carduid=str(card_uid)),
						'usage'		: 0,
						'start_time': timezone.now(),
						'end_time'	: 0,
					}
					pubtopic = "{}/command/ssr".format(machine.id)
					pubmessage = "1"
					client.publish(pubtopic, pubmessage, qos=2)

		topic = "{}/state/stop".format(machine.id)
		if msg.topic == topic:
			print(msg.topic+" "+str(msg.payload))
			if machineData[machine.id]['ssr'] == 1:
				new_usage = Usage(
					user			= machineData[machine.id]['user_id'],
					machine_type	= machine.machine_type,
					machine			= machine.id,
					start_time		= machineData[machine.id]['start_time'],
					end_time		= timezone.now(),
					total_usage		= machineData[machine.id]['usage'],
				)
				new_usage.save()
				
				# reset machineData
				machineData[machine.id] = {
					'ssr'		: 0,
					'card_uid'	: 0,
					'user_id'	: 0,
					'usage'		: 0,
					'start_time': 0,
					'end_time'	: 0,
				}

				pubtopic = "{}/command/ssr".format(machine.id)
				pubmessage = "0"
				client.publish(pubtopic, pubmessage, qos=2)

		topic = "{}/state/usage".format(machine.id)
		if msg.topic == topic and machineData[machine.id]['ssr'] == 1:
			print(msg.topic+" "+str(msg.payload))
			machineData[machine.id]['usage'] = float(msg.payload);


def on_disconnect(client, userdata, rc):
	client.loop_stop(force=False)
	if rc != 0:
		print("Unexpected disconnection. rc={}".format(rc))
	else:
		print("Disconnected")
	machineData.clear();


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

