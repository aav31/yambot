#include "UserInterface.h"

// SoftwareSerial softwareSerial(RX_PIN, TX_PIN); // define software serial connection to the speakers
DFRobotDFPlayerMini player;

UserInterface::UserInterface() {
}

void UserInterface::setup(void) {
  pinMode(PIN_COUNT_L, OUTPUT);
  pinMode(PIN_COUNT_M, OUTPUT);
  pinMode(PIN_COUNT_R, OUTPUT);
  pinMode(PIN_FACE_VALUE_L, OUTPUT);
  pinMode(PIN_FACE_VALUE_M, OUTPUT);
  pinMode(PIN_FACE_VALUE_R, OUTPUT);
  pinMode(PIN_BUTTON, INPUT_PULLUP);
  
  pixy.init();
  Serial.println("Pixy setup successful");

  // softwareSerial.begin(9600);
  // if (!player.begin(softwareSerial)) {
  //   Serial.println(F("Unable to begin:"));
  //   Serial.println(F("1.Please recheck the connection!"));
  //   Serial.println(F("2.Please insert the SD card!"));
  //   while (true);
  // }
  // player.setTimeOut(500);
  // player.volume(20); // Set volume (0~30).
  // Serial.println("Df player setup successful");
}

void UserInterface::getFaceValues(byte* countArray) {
  // wait for button to be pressed
  while (digitalRead(PIN_BUTTON) == 1) {
  }
  // grab blocks when button pressed
  pixy.ccc.getBlocks();
  Serial.println(pixy.ccc.numBlocks);
  // reset count array to zero
  for (int j=0; j<7; j++) {
    countArray[j] = 0;
  }
  // if there are 5 detected dice process
  if (pixy.ccc.numBlocks == 5)
  {
    for (int i=0; i<pixy.ccc.numBlocks; i++)
    {
      countArray[pixy.ccc.blocks[i].m_signature] += 1;
    }
    player.playFolder(2, 2);
    delay(2000);
    for (int faceValue=1; faceValue<=6; faceValue++) {
      digitalWrite(PIN_COUNT_L, bitRead(countArray[faceValue], 2));
      digitalWrite(PIN_COUNT_M, bitRead(countArray[faceValue], 1));
      digitalWrite(PIN_COUNT_R, bitRead(countArray[faceValue], 0));

      digitalWrite(PIN_FACE_VALUE_L, bitRead(faceValue, 2));
      digitalWrite(PIN_FACE_VALUE_M, bitRead(faceValue, 1));
      digitalWrite(PIN_FACE_VALUE_R, bitRead(faceValue, 0));

      for (int k=0; k<countArray[faceValue];k++) {
        player.playFolder(1, faceValue);
        delay(2000);
      }

    }
  }

  digitalWrite(PIN_COUNT_L, 0);
  digitalWrite(PIN_COUNT_M, 0);
  digitalWrite(PIN_COUNT_R, 0);
  digitalWrite(PIN_FACE_VALUE_L, 0);
  digitalWrite(PIN_FACE_VALUE_M, 0);
  digitalWrite(PIN_FACE_VALUE_R, 0);
}

void UserInterface::getFaceValuesFromSerial(byte *countArray) {
  // to use this you need to turn off softwareSerial(tx, rx)
  // reset count array to zero
  for (int j=0; j<7; j++) {
    countArray[j] = 0;
  }

  for (int d=0; d<5; d++) {
    while (Serial.available()==0) {}
    if (Serial.available()) {
      int faceValue = Serial.parseInt();
      countArray[faceValue]+=1;
      Serial.println(faceValue);
    }
  }

  Serial.print("Count array: ");
  for (int faceValue=1; faceValue<=6; faceValue++) {
    if (faceValue > 1) {
      Serial.print(", ");
    }
    Serial.print(faceValue);
    Serial.print(":");
    Serial.print(countArray[faceValue]);
  }
  Serial.println();
}
