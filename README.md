# Lmseh_assignment

## _Task 1_


In task 1, there are 3 script named [device_1.py](task_1/device_1.py), [device_2.py](task_1/device_2.py), [device_3.py](task_1/device_3.py). device_1 connected to arduino throuch serial communication. device_1 also act like a server, the device_1 subscribe to topic :
- registration/enter
- registration/exit
- power/on
- power/off

device_2 and device_3 act like a client, these two device publish a message through those topic above with payload containing device_id
Video Demonstration :
[![IMAGE ALT TEXT HERE](https://img.youtube.com/vi/pZLcRABrGjg/0.jpg)](https://www.youtube.com/watch?v=pZLcRABrGjg)
