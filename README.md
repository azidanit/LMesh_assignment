# Lmseh_assignment

## _Task 1_



In task 1, there are 3 script named [device_1.py](task_1/device_1.py), [device_2.py](task_1/device_2.py), [device_3.py](task_1/device_3.py). The communication between the python script using MQTT. device_1 connected to arduino throuch serial communication. device_1 also act like a server, the device_1 subscribe to topic :
- registration/enter
- registration/exit
- power/on
- power/off

device_2 and device_3 act like a client, these two device publish a message through those topic above with payload containing device_id.

The Arduino flashed with this [source_code](task_1/lmesh_task_1.ino) to check the message and send back the message with command_id = 0x0c. The message template that used on serial communication between arduino and device_1:
| name | value | size|
| ------ | ------ |-------|
| Start byte| ```0xff``` |1 bytes |
|Command_id| ( ```0x0E``` = registration, ```0x0B``` = controller, ```0x0C``` = reply from arduino ) | 1 bytes |
|Length | example = ```0x02``` (lenght of following payload)|1 bytes |
|Payload | example = ```0x02, 0x01```(device_id, value) | lenght bytes |
|CRC8 | example = ```0xf4``` (checksum) | 1 bytes |
|End byte | ```0x00``` | 1 bytes |


Video Demonstration :
[![IMAGE ALT TEXT HERE](https://img.youtube.com/vi/pZLcRABrGjg/0.jpg)](https://www.youtube.com/watch?v=pZLcRABrGjg)
