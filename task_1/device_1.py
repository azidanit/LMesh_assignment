import paho.mqtt.client as mqttClient
import time
import json
import libscrc
import struct
import serial
import logging
import sys

from threading import Thread


class SerialHandler:
    def __init__(self):
        self.device_name = "/dev/tty.usbmodem144302"
        self.device_baud = 57600
        self.read_thread = None

        self.connectToDevice()
        self.startReadThread()

    def connectToDevice(self):
        self.serial = serial.Serial(self.device_name, self.device_baud, timeout=1)


    def setPower(self, device_id_, condition):
        logging.info("POWERING from device_id: {} to {}".format(device_id_, condition))
        self.sendToDevice(bytes([0xff, 0x0B, 0x02, device_id_, condition]))
        pass

    def setRegistration(self, device_id_, condition):
        logging.info("REGISTRATION from device_id: {} action {}".format(device_id_, condition))
        self.sendToDevice(bytes([0xff, 0x0E, 0x02, device_id_, condition]))
        pass

    def sendToDeviceRaw(self, msg_bytes):
        # print("SENDING TO DEVICE")
        self.serial.write(msg_bytes)
        pass

    def sendToDevice(self, msg_bytes):
        crc8_ = libscrc.crc8(msg_bytes)
        msg_crc8 = msg_bytes + bytes([crc8_]) + bytes([0x00])
        self.serial.write(msg_crc8)
        logging.info("Sending To Arduino {}".format(msg_crc8))
        ret_read = self.readFromDeviceOnceAndVerify()
        while not ret_read[0]: #sending again when it fails to read msg
            self.serial.write(msg_crc8)
            time.sleep(0.25)

        logging.info("Arduino send back the msg, Verified {}".format(ret_read[1]))


    def readFromDeviceOnceAndVerify(self):
        line = self.serial.read_until(size=7)
        if len(line) >= 6:
            if libscrc.crc8(line[:5]) == line[5]:
                # print("CORRECT CRC")
                return [True, line]
        else:
            # print("TIMEOUT NOT ENOUGH MSG")
            return [False,line]
        print(line)

    def startReadThread(self):
        if self.read_thread == None:
            self.read_thread = Thread(target=self.readFromDeviceThread)
            # self.read_thread.start()
        else:
            self.read_thread.join()

    def readFromDeviceThread(self):
        while True:
            line = self.serial.read_until(size=7)
            if libscrc.crc8(line[:5]) == line[5]:
                pass
                # print("CORRECT CRC")
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
                logging.info("CONNECTED to {} port {}".format(self.broker_address, self.broker_port))
            except:
                is_mqtt_connected = False
                logging.warning("cannot connect")
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
                elif message.topic.split('/')[0] == 'power':
                    self.processPowerCommand(message.topic.split('/'), json_obj)
        else:
            logging.warning("Message from topic {} has no payload".format(message.topic))


    def parseJSON(self, string_):
        try: #try to parse string as json
            return json.loads(string_)
        except:
            logging.error("cannot parse json from string")
            return None

    def processPowerCommand(self, topic, json_data):
        # print(topic, json_data)
        if len(topic) > 1:
            if self.registered_device.count(json_data['device_id']) == 0:
                logging.error("Device Not Registered, Command Rejected")
            else:
                if topic[1] == 'on':
                    if 'device_id' in json_data:
                        self.serial_handler.setPower(json_data['device_id'], 0x01)
                    else:
                        logging.error("NO DEVICE ID, Cannot Powering Action")

                elif topic[1] == 'off':
                    if 'device_id' in json_data:
                        self.serial_handler.setPower(json_data['device_id'], 0x00)
                    else:
                        logging.error("NO DEVICE ID, Cannot Powering Action")


    def processRegistration(self, topic, json_data):
        # print(topic, json_data)
        if len(topic) > 1:
            if topic[1] == 'enter':
                if 'device_id' in json_data:
                    if self.registered_device.count(json_data['device_id']) == 0:
                        self.registered_device.append(json_data['device_id'])
                        self.serial_handler.setRegistration(json_data['device_id'], 0x01)
                        logging.info("DEVICE id {} successful registered".format(json_data['device_id']))
                    else:
                        logging.error("DEVICE id {} has been registered, cannot be registered".format(json_data['device_id']))
                else:
                    logging.warning("NO DEVICE ID")
            elif topic[1] == 'exit':
                if 'device_id' in json_data:
                    if self.registered_device.count(json_data['device_id']) > 0:
                        self.registered_device.remove(json_data['device_id'])
                        self.serial_handler.setRegistration(json_data['device_id'], 0x00)
                        logging.info("DEVICE id {} successful removed to exit".format(json_data['device_id']))
                    else:
                        logging.error("DEVICE id {} not registered, cannot exit".format(json_data['device_id']))
                else:
                    logging.warning("NO DEVICE ID")


    def on_connect(self, client, userdata, flags, rc):
        if rc == 0:
            logging.info("Connected to broker")
            self.subscribeToTopic()
        else:
            logging.error("Connection failed")


if __name__ == '__main__':
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(message)s",
        handlers=[
            logging.FileHandler("general.log"),
            logging.StreamHandler(sys.stdout)
        ]
    )

    mqtt_hanlder_dev_1 = MQTTHandler()
    mqtt_hanlder_dev_1.start()

    # time.sleep(20)



