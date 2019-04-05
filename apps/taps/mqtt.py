import os
import paho.mqtt.client as mqtt
from django.utils import timezone

from apps.taps.models import Tap
from apps.machines.models import Machine
from apps.cards.models import Card, Unregistered_card
from apps.usages.models import Usage
from apps.certifications.models import Certification

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
					if Unregistered_card.objects.filter(card_uid=card_uid).exists():
						new_card = Unregistered_card.objects.get(card_uid=card_uid)
						new_card.machine = Machine.objects.get(id=machine.id)
						new_card.save()
						print("Unregistered card [{}] existed already." .format(new_card.card_uid))
						
					else:
						new_card = Unregistered_card(machine=machine, card_uid=card_uid)
						new_card.save()
						print("Save to unregistered card.")

					pubtopic = "{}/command/action".format(machine.id)
					pubmessage = "3"
					client.publish(pubtopic, pubmessage, qos=2)
					
				if cardExist:
					# check if certified or not
					print("Card Exist")
					print("{}-{}".format(card.user, machine.machine_type))
					if Certification.objects.filter(user=card.user, machine_type=machine.machine_type).exists():
						print("Starting new session.");
						machineData[machine.id]['ssr'] = 1
						machineData[machine.id]['card_uid'] = card_uid
						machineData[machine.id]['user_id'] = card.user
						machineData[machine.id]['usage'] = 0
						machineData[machine.id]['start_time'] = timezone.now()
						pubtopic = "{}/command/action".format(machine.id)
						pubmessage = "1"
						client.publish(pubtopic, pubmessage, qos=2)
						print(machineData[machine.id])
					else:
						print("not certified!")
						pubtopic = "{}/command/action".format(machine.id)
						pubmessage = "2"
						client.publish(pubtopic, pubmessage, qos=2)

		topic = "{}/state/stop".format(machine.id)
		if msg.topic == topic:
			print(msg.topic+" "+str(msg.payload))
			if machineData[machine.id]['ssr'] == 1:
				machineData[machine.id]['usage'] = float(msg.payload);
				new_usage = Usage(
					user			= machineData[machine.id]['user_id'],
					machine_type	= machine.machine_type,
					machine			= machine,
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
			print(machineData[machine.id])

		topic = "{}/state/connect".format(machine.id)
		if msg.topic == topic:
			print(msg.topic+" "+str(msg.payload))
			pubtopic = "{}/command/connect".format(machine.id)
			pubmessage = "1"
			client.publish(pubtopic, pubmessage, qos=2)


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

