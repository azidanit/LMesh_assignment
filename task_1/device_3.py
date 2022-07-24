import paho.mqtt.client as mqttClient

device_id = 3

broker="192.168.100.58"
port=1884

def on_publish(client,userdata,result):             #create function for callback
    print("data published \n")
    pass

client2= mqttClient.Client("device_2")                           #create client object
client2.on_publish = on_publish                          #assign function to callback
client2.connect(broker,port)                                 #establish connection


while True:
    print("LIST OF COMMAND from device {}".format(device_id))
    print("1 : registration/enter")
    print("2 : registration/exit")
    print("3 : power/on")
    print("4 : power/off")
    print("----------------------------")
    print("0 : Exit Script")
    print("----------------------------")
    cmd_ = value = input("Please enter a cmd:\n")

    if(cmd_ == '1'):
        ret= client2.publish("registration/enter","{{\"device_id\":{} }}".format(device_id))
    elif(cmd_ == '2'):
        ret= client2.publish("registration/exit","{{\"device_id\":{} }}".format(device_id))
    elif (cmd_ == '3'):
        ret = client2.publish("power/on", "{{\"device_id\":{} }}".format(device_id))
    elif (cmd_ == '4'):
        ret = client2.publish("power/off", "{{\"device_id\":{} }}".format(device_id))
    elif (cmd_ == '0'):
        break
