#ifndef ACTION_H
#define ACTION_H
#include "Board.h"

struct Action {
    byte countArrayKeep[7]; // mapping of dice face value to number of occurunces k that you should keep and not roll again - valid after roll 1, valid after roll 2, not valid after roll 3
    bool announce; // whether you should announce or not - valid after roll 1, not valid after roll 2, not valid after roll 3
    Row row; // which row and column should you fill out - not valid after roll 1, not valid after roll 2, valid after roll 3
    Column col; // which row and column should you fill out - not valid after roll 1, not valid after roll 2, valid after roll 3
    Action() {
      for (byte faceValue=1; faceValue <=6; faceValue++) {
        countArrayKeep[faceValue] = 0;
      }
      announce = false;
      row = 0;
      col = 0;
    }
};

#endif // ACTION_H