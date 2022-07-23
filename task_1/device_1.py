import paho.mqtt.client as mqttClient
import time
import json
import libscrc
import struct
import serial

from threading import Thread


class SerialHandler:
    def __init__(self):
        self.device_name = "/dev/tty.usbmodem144302"
        self.device_baud = 9600
        self.read_thread = None

        self.connectToDevice()
        self.startReadThread()

    def connectToDevice(self):
        self.serial = serial.Serial(self.device_name, self.device_baud)


    def setPower(self, device_id_, condition):
        print("POWERING ", device_id_, condition)
        self.sendToDevice(bytes([0xff, 0x0B, 0x02, device_id_, condition]))
        pass

    def setRegistration(self, device_id_, condition):
        print("REGISTRATION ", device_id_, condition)

        pass

    def sendToDevice(self, msg_bytes):
        crc8_ = libscrc.crc8(msg_bytes)
        msg_crc8 = msg_bytes + bytes([crc8_]) + bytes([0x00])
        self.serial.write(msg_crc8)
        pass

    def startReadThread(self):
        if self.read_thread == None:
            self.read_thread = Thread(target=self.readFromDevice)
            self.read_thread.start()
            self.read_thread.join()

        else:
            self.read_thread.join()

    def readFromDevice(self):
        while True:
            self.setPower(0x01,0x01)
            time.sleep(0.1)
            print("done sending")
            line = self.serial.read()
            print(line)
        pass

class MQTTHandler:
    def __init__(self):
        self.serial_handler = SerialHandler()
        self.registered_device = []

        self.broker_address = "192.168.100.58"  # Broker address
        self.broker_port = 1884  # Broker port
        # user = "sonoff"  # Connection username
        # password = "sonoff"  # Connection password

        self.connect()


    def start(self):
        self.client.loop_forever()        #start the loop

    def connect(self):
        self.client = mqttClient.Client("Python", clean_session=False)  # create new instance
        # client.username_pw_set(user, password=password)  # set username and password
        self.client.on_connect = self.on_connect  # attach function to callback
        self.client.on_message = self.on_message  # attach function to callback

        is_mqtt_connected = False
        while not is_mqtt_connected:
            try:
                is_mqtt_connected = True
                self.client.connect(self.broker_address, port=self.broker_port)  # connect to broker
                print("CONNECTED")
            except:
                is_mqtt_connected = False
                print("cannot connect")
                time.sleep(1)

    def subscribeToTopic(self):
        self.client.on_message = self.on_message

        self.client.subscribe("registration/enter")
        self.client.subscribe("registration/exit")
        self.client.subscribe("power/on")
        self.client.subscribe("power/off")

    def on_message(self, client, userdata, message):
        # print("Message received: ", message.payload)
        # print("Message Topic: ", message.topic)

        if len(message.payload.decode()) > 0:
            json_obj = self.parseJSON(message.payload.decode())
            if json_obj != None:
                if message.topic.split('/')[0] == 'registration':
                    self.processRegistration(message.topic.split('/'), json_obj)
        else:
            print("Message from topic", message.topic ,"has no payload")


    def parseJSON(self, string_):
        try: #try to parse string as json
            return json.loads(string_)
        except:
            print("cannot parse json from string")
            return None

    def processPowerCommand(self, topic, json_data):
        # print(topic, json_data)
        if len(topic) > 1:
            if self.registered_device.count(json_data['device_id']) == 0:
                print("Device Not Registered, Command Rejected")
            else:
                if topic[1] == 'on':
                    if 'device_id' in json_data:
                        self.serial_handler.setPowerOn(json_data['device_id'], 0x01)
                    else:
                        print("NO DEVICE ID")

                elif topic[1] == 'off':
                    if 'device_id' in json_data:
                        self.serial_handler.setPower(json_data['device_id'], 0x00)
                    else:
                        print("NO DEVICE ID")


    def processRegistration(self, topic, json_data):
        # print(topic, json_data)
        if len(topic) > 1:
            if topic[1] == 'enter':
                if 'device_id' in json_data:
                    if self.registered_device.count(json_data['device_id']) == 0:
                        self.registered_device.append(json_data['device_id'])
                        print("DEVICE id ", json_data['device_id'], " successful registered")
                    else:
                        print("DEVICE id ", json_data['device_id'], " has been registered")
                else:
                    print("NO DEVICE ID")
            elif topic[1] == 'exit':
                if 'device_id' in json_data:
                    if self.registered_device.count(json_data['device_id']) > 0:
                        self.registered_device.remove(json_data['device_id'])
                        print("DEVICE id ", json_data['device_id'], " successful removed")
                    else:
                        print("DEVICE id ", json_data['device_id'], " not registered, cannot exit")
                else:
                    print("NO DEVICE ID")


    def on_connect(self, client, userdata, flags, rc):
        if rc == 0:
            print("Connected to broker")

            self.subscribeToTopic()
        else:

            print("Connection failed")


if __name__ == '__main__':
    # mqtt_hanlder_dev_1 = MQTTHandler()
    # mqtt_hanlder_dev_1.start()

    ser_hanlder = SerialHandler()
    time.sleep(20)



