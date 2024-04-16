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
  // brain.setup();
}

void loop() {
  if (turnNumber > 14*4) {
    // game is in end state - print the end state
    return;
  } else {
    turnNumber++;
  }

  Serial.print("Turn number: ");
  Serial.println(turnNumber);
  userInterface.displayBoardToSerial(board);
  bool announced = false;
  Row announcedRow = YAMB;
  Action action;

  // roll 1
  userInterface.getFaceValuesFromSerial(COUNT_ARRAY);
  userInterface.displayFeasibleToSerial(board, announced, announcedRow);
  action = userInterface.getActionFromSerial(COUNT_ARRAY, 1, board, announced, announcedRow);
  announced = action.announce;
  announcedRow = action.announcementRow;

  // roll 2
  userInterface.getFaceValuesFromSerial(COUNT_ARRAY);
  userInterface.displayFeasibleToSerial(board, announced, announcedRow);
  action = userInterface.getActionFromSerial(COUNT_ARRAY, 2, board, announced, announcedRow);
    
  // roll 3
  userInterface.getFaceValuesFromSerial(COUNT_ARRAY);
  userInterface.displayFeasibleToSerial(board, announced, announcedRow);
  action = userInterface.getActionFromSerial(COUNT_ARRAY, 3, board, announced, announcedRow);


  Serial.println("Updating board...");
  Serial.print("Score = ");
  Serial.println(board.scoreAt(action.rowToFillIn, COUNT_ARRAY));
  board.update(action.rowToFillIn, action.colToFillIn, COUNT_ARRAY);
}
