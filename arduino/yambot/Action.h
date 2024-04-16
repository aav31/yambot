#ifndef ACTION_H
#define ACTION_H
#include <Arduino.h>
#include "Board.h"

struct Action {
    int onesToKeep {-1}; // only valid after rolls 1 and 2
    int twosToKeep {-1}; // only valid after rolls 1 and 2
    int threesToKeep {-1}; // only valid after rolls 1 and 2
    int foursToKeep {-1}; // only valid after rolls 1 and 2
    int fivesToKeep {-1}; // only valid after rolls 1 and 2
    int sixesToKeep {-1}; // only valid after rolls 1 and 2
    bool announce {false}; // only valid after roll 1
    Row announcementRow {13}; // only valid after roll 1
    int rowToFillIn {-1}; // only valid after roll 3
    int colToFillIn {-1}; // only valid after roll 3
};

String actionToString(Action a, bool canRoll, bool canAnnounce, bool canFillIn);

bool isValid(Action a, byte* countArray, byte rollNumber, Board& b, bool announced, Row announcedRow, bool canRoll, bool canAnnounce, bool canFillIn);

#endif // ACTION_H