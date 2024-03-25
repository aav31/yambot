#include "UserInterface.h"
#include "Board.h"
#include "Action.h"

UserInterface userInterface;
Board board;
byte COUNT_ARRAY[7] = {0}; // mapping of dice face value to number of occurunces k
byte turnNumber = 0;

void setup() {
  Serial.begin(115200);
  userInterface.setup();
  // Action action;
  // brain.setup();
  
}

void loop() {
  Serial.println("Enter face values ...");
  userInterface.getFaceValuesFromSerial(COUNT_ARRAY);
  Serial.println("Enter row...");
  int row = 0;
  while (Serial.available()==0) {}
  if (Serial.available()) {
    row = Serial.parseInt();
    Serial.println(row);
  }
  Serial.print("Score = ");
  Serial.println(board.scoreAt(row, COUNT_ARRAY));
  // if (turnNumber > 14*4) {
  //   // game is in end state - print the end state
  //   return;
  // } else {
  //   turnNumber++;
  // }

  // roll 1
  // userInterface.getFaceValues(COUNT_ARRAY);
  // action = brain.process(COUNT_ARRAY, &board, 1);
  // userInterface.respond(action);

  // roll 2
  // userInterface.getFaceValues(COUNT_ARRAY);
  // action = brain.process(COUNT_ARRAY, &board, 2);
  // userInterface.respond(action);
    
  // roll 3
  // userInterface.getFaceValues(COUNT_ARRAY);
  // action = brain.process(COUNT_ARRAY, &board, 3);
  // userInterface.respond(action);
  // board.update(action);
}
