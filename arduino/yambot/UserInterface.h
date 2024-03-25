#ifndef USERINTERFACE_H
#define USERINTERFACE_H
#include "Arduino.h"
#include <Pixy2.h>
#include "SoftwareSerial.h"
#include "DFRobotDFPlayerMini.h"

const byte PIN_COUNT_L = 2;
const byte PIN_COUNT_M = 3;
const byte PIN_COUNT_R = 4;

const byte PIN_FACE_VALUE_L = 5;
const byte PIN_FACE_VALUE_M = 6;
const byte PIN_FACE_VALUE_R = 7;

const byte PIN_BUTTON = A0;

#define RX_PIN 8  // Replace with your RX pin
#define TX_PIN 9  // Replace with your TX pin

class UserInterface {
  public:
    UserInterface();
    void setup(void);
    void getFaceValues(byte* countArray);
    void getFaceValuesFromSerial(byte* countArray);
  private:
    Pixy2 pixy;
};

#endif