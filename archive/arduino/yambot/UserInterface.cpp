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

  bool valid = false;

  while (!valid) {
    // reset count array to zero
    for (int j=0; j<7; j++) {
      countArray[j] = 0;
    }
    Serial.println("Enter face values ...");
    while (Serial.available()==0) {}
    char c = "";
    if (Serial.available() > 0) {
      while (c != '.') {
        c = Serial.read();
        char str[2] = {c, '\0'};
        int i = atoi(str);
        if ((1<=i) && (i<=6)) {
          countArray[i]+=1;
        }
      }
    }
    int s = 0;
    for (int faceValue=1; faceValue <= 6; faceValue++) {
      s += countArray[faceValue];
    }
    if (s==5) {
      valid = true;
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

void UserInterface::displayBoardToSerial(Board& b) {
  for (int i =0; i<14 ;i++) {
    Serial.print(Board::convertRowToCharArray(i));
    Serial.print("| ");
    for (int j=0; j<4 ; j++) {
      byte value = b.getMatrixAt(i, j);
      // depending on how big the number is we need to print more spaces
      if (value>=100) {
        Serial.print(" ");
      } else if (value>=10) {
        Serial.print("  ");
      } else {
        Serial.print("   ");
      }
      Serial.print(value);
    }
    Serial.println();
  }
}

void UserInterface::displayFeasibleToSerial(Board& b, bool announced, Row announcedRow) {
  for (int c=0; c<4; c++) {
    for (int r=0; r<14; r++) {
      if (b.isFeasible(r, c, announced, announcedRow)) {
        Serial.print("Feasible col, row: ");
        Serial.print(Board::convertColToCharArray(c));
        Serial.print(", ");
        Serial.println(Board::convertRowToCharArray(r));
      }
    }
  }
}


void UserInterface::recommendActionToSerial(Action a) {
  Serial.println();
}

Action UserInterface::getActionFromSerial(byte* countArray, byte rollNumber, Board& b, bool announced, Row announcedRow) {
  bool canRoll;
  bool canAnnounce;
  bool canFillIn;
  if (rollNumber == 1) {
    canRoll = true;
    canAnnounce = true;
    canFillIn = false;
  } else if (rollNumber == 2) {
    canRoll = true;
    canAnnounce = false;
    canFillIn = false;
  } else {
    canRoll = false;
    canAnnounce = false;
    canFillIn = true;
  }
  Serial.println("Getting action from user...");
  Action a;
  while (!isValid(a, countArray, rollNumber, b, announced, announcedRow, canRoll, canAnnounce, canFillIn)) {
    if (canRoll) {
      Serial.print("Ones to keep: ");
      a.onesToKeep = getIntFromSerial();
      Serial.print("Twos to keep: ");
      a.twosToKeep = getIntFromSerial();
      Serial.print("Threes to keep: ");
      a.threesToKeep = getIntFromSerial();
      Serial.print("Fours to keep: ");
      a.foursToKeep = getIntFromSerial();
      Serial.print("Fives to keep: ");
      a.fivesToKeep = getIntFromSerial();
      Serial.print("Sixes to keep: ");
      a.sixesToKeep= getIntFromSerial();
    }
    if (canAnnounce) {
      Serial.print("Announce: ");
      a.announce = getIntFromSerial();
      if (a.announce) {
        Serial.print("Announcement row: ");
        a.announcementRow = getIntFromSerial();
      }
    }
    if (canFillIn) {
      Serial.print("Col to fill in: ");
      a.colToFillIn = getIntFromSerial();
      Serial.print("Row to fill in: ");
      a.rowToFillIn = getIntFromSerial();
    }
    if (!isValid(a, countArray, rollNumber, b, announced, announcedRow, canRoll, canAnnounce, canFillIn)) {
      Serial.println(" INVALID ");
    }
  }
  Serial.println(actionToString(a, canRoll, canAnnounce, canFillIn));
  return a;
}

int UserInterface::getIntFromSerial() {
  int x;
  while (Serial.available()==0) {}
    if (Serial.available()) {
      x = Serial.parseInt();
  }
  Serial.println(x);
  return x;
}
