#include <WiFiNINA.h>
#include <utility/wifi_drv.h>

#include "CRC8.h"

CRC8 crc;
CRC8 crc_send;

void setup() {
  Serial.begin(57600);
  
  // initialize digital pin LED_BUILTIN as an output.
  pinMode(LED_BUILTIN, OUTPUT);

  WiFiDrv::pinMode(25, OUTPUT);  //GREEN
  WiFiDrv::pinMode(26, OUTPUT);  //RED
  WiFiDrv::pinMode(27, OUTPUT);  //BLUE
}

void resetLed(){
  WiFiDrv::analogWrite(25, 0);
  WiFiDrv::analogWrite(26, 0);
  WiFiDrv::analogWrite(27, 0);
}

bool checkCRC(short rec_crc){
  return crc.getCRC() == rec_crc;
}

int inByte; 
short cmd_id = 0, length_payload = 1, received_crc8 = 0;
char header_msg[3];
char payload[10];
short pointer_msg = 0;

void loop() {

  if (Serial.available() > 0) {
    resetLed();
    
    inByte = Serial.read();

    if (inByte == 0xff){ //start msg
      crc.restart();
      WiFiDrv::analogWrite(26, 50);
      header_msg[0] = 0xff;
      
      crc.add(inByte);
      
      pointer_msg = 1;     
      length_payload = 1;
       
    }else if(pointer_msg == 1){ //cmd id
      header_msg[1] = inByte;
      pointer_msg++;
      crc.add(inByte);
    }else if(pointer_msg == 2){ //lengght
      header_msg[2] = inByte;

      length_payload = inByte;
      
      pointer_msg++;
      crc.add(inByte);
    }else if(pointer_msg > 2 && pointer_msg < (3 + length_payload)){
      payload[pointer_msg-3] = inByte;
      pointer_msg++;
      crc.add(inByte);
    }else if(pointer_msg == 3 + length_payload){ //crc
      received_crc8 = inByte;
      pointer_msg++;
    }else if(inByte == 0x00 && pointer_msg == (4 + length_payload)){
      if (checkCRC(received_crc8)){
        char to_send[pointer_msg+1];
        crc_send.restart();
        header_msg[1] = 0x0C;
        for (int i = 0; i < 3; i++){
          to_send[i] = header_msg[i];
          crc_send.add(to_send[i]);
        }

        

        for (int i = 0; i < length_payload; i++){
          to_send[i+3] = payload[i];
          crc_send.add(to_send[i+3]);
        }

        to_send[3+length_payload] = crc_send.getCRC();
        to_send[4+length_payload] = 0x00;
        
        WiFiDrv::analogWrite(25, 50);
        Serial.write(to_send,7);
        delay(50);
      }else{
        WiFiDrv::analogWrite(27, 50);
      }

    }
    
  }


  delay(10);
  
  
}
